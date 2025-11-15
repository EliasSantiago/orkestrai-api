"""
Automatic Context Wrapper for ADK Agents

This module provides a wrapper that automatically integrates Redis conversation
context with Google ADK agents. It follows best practices for maintainability
and extensibility.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import wraps
import inspect

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adk_conversation_middleware import get_adk_middleware


class AgentContextWrapper:
    """
    Wrapper for ADK agents that automatically manages conversation context.
    
    This wrapper intercepts agent calls and:
    1. Retrieves conversation history from Redis before processing
    2. Injects history into the agent's context
    3. Saves messages to Redis after processing
    """
    
    def __init__(self, agent, session_id: Optional[str] = None, user_id: Optional[int] = None):
        """
        Initialize wrapper with an ADK agent.
        
        Args:
            agent: The ADK Agent instance to wrap
            session_id: Optional session ID for context management
            user_id: Optional user ID for context management
        """
        self._agent = agent
        self._session_id = session_id
        self._user_id = user_id
        self._middleware = get_adk_middleware()
        self._enabled = True
        
        # Copy agent attributes to maintain compatibility
        self._copy_agent_attributes()
    
    def _copy_agent_attributes(self):
        """Copy agent attributes to wrapper for compatibility."""
        for attr in ['name', 'description', 'model', 'tools']:
            if hasattr(self._agent, attr):
                setattr(self, attr, getattr(self._agent, attr))
    
    def enable_context(self):
        """Enable automatic context integration."""
        self._enabled = True
    
    def disable_context(self):
        """Disable automatic context integration."""
        self._enabled = False
    
    def set_session_id(self, session_id: str):
        """Set session ID for context management."""
        self._session_id = session_id
    
    def set_user_id(self, user_id: int):
        """Set user ID for context management."""
        self._user_id = user_id
    
    def _get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history from Redis."""
        if not self._enabled or not self._session_id:
            return []
        
        try:
            # Resolve user_id from session if not provided
            user_id = self._user_id
            if not user_id:
                user_id = self._middleware.get_user_id_from_session(self._session_id)
            
            if not user_id:
                return []
            
            # Get conversation context
            history = self._middleware.get_conversation_context(
                session_id=self._session_id,
                user_id=user_id,
                limit=None  # Get all history, agent will handle windowing
            )
            
            return history
        except Exception as e:
            print(f"⚠ Warning: Error getting conversation history: {e}")
            return []
    
    def _save_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Save a message to Redis."""
        if not self._enabled or not self._session_id:
            return
        
        try:
            # Resolve user_id from session if not provided
            user_id = self._user_id
            if not user_id:
                user_id = self._middleware.get_user_id_from_session(self._session_id)
            
            if not user_id:
                return
            
            # Save message
            if role == "user":
                self._middleware.save_user_message(
                    session_id=self._session_id,
                    content=content,
                    user_id=user_id,
                    metadata=metadata
                )
            elif role == "assistant":
                self._middleware.save_assistant_message(
                    session_id=self._session_id,
                    content=content,
                    user_id=user_id,
                    metadata=metadata
                )
        except Exception as e:
            print(f"⚠ Warning: Error saving message: {e}")
    
    def _inject_context_into_agent(self, user_message: str) -> str:
        """
        Inject conversation history into agent instruction or context.
        
        This method modifies the agent's instruction to include conversation history.
        The actual implementation depends on how ADK handles context.
        """
        if not self._enabled:
            return user_message
        
        history = self._get_conversation_history()
        
        if not history:
            return user_message
        
        # Format history as context
        context_lines = ["\n\n## Histórico da Conversa:\n"]
        for msg in history[-20:]:  # Last 20 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                context_lines.append(f"Usuário: {content}\n")
            elif role == "assistant":
                context_lines.append(f"Assistente: {content}\n")
        
        context = "".join(context_lines)
        
        # Prepend context to user message
        # Note: This is a simple approach. In production, you might want to
        # modify the agent's instruction or use ADK's built-in context mechanism
        enhanced_message = f"{context}\n\nNova mensagem do usuário: {user_message}"
        
        return enhanced_message
    
    def __getattr__(self, name):
        """
        Delegate attribute access to wrapped agent.
        
        This allows the wrapper to behave like the original agent.
        """
        attr = getattr(self._agent, name)
        
        # If it's a callable method, wrap it to add context handling
        if callable(attr) and name in ['chat', 'run', 'respond', '__call__']:
            return self._wrap_agent_method(attr, name)
        
        return attr
    
    def _wrap_agent_method(self, method, method_name: str):
        """Wrap agent method to add context handling."""
        @wraps(method)
        def wrapper(*args, **kwargs):
            # Extract user message from args/kwargs
            user_message = None
            if args:
                user_message = str(args[0])
            elif 'message' in kwargs:
                user_message = kwargs['message']
            elif 'content' in kwargs:
                user_message = kwargs['content']
            elif 'input' in kwargs:
                user_message = kwargs['input']
            
            if not user_message:
                # No message found, call original method
                return method(*args, **kwargs)
            
            # Inject conversation context
            enhanced_message = self._inject_context_into_agent(user_message)
            
            # Update args/kwargs with enhanced message
            if args:
                args = (enhanced_message,) + args[1:]
            else:
                kwargs['message'] = enhanced_message
            
            # Call original method
            try:
                response = method(*args, **kwargs)
                
                # Extract assistant response
                assistant_message = None
                if isinstance(response, str):
                    assistant_message = response
                elif isinstance(response, dict):
                    assistant_message = response.get("message") or response.get("content") or str(response)
                else:
                    assistant_message = str(response)
                
                # Save messages to Redis
                if assistant_message:
                    self._save_message("user", user_message)
                    self._save_message("assistant", assistant_message)
                
                return response
            except Exception as e:
                print(f"⚠ Warning: Error in wrapped agent method: {e}")
                # Fallback to original method
                return method(*args, **kwargs)
        
        return wrapper
    
    def chat(self, message: str, **kwargs):
        """
        Chat with agent, automatically managing conversation context.
        
        This is the main method to use for conversations.
        """
        # Get conversation history
        history = self._get_conversation_history()
        
        # Inject context
        enhanced_message = self._inject_context_into_agent(message)
        
        # Call agent's chat method
        try:
            if hasattr(self._agent, 'chat'):
                response = self._agent.chat(enhanced_message, **kwargs)
            elif hasattr(self._agent, 'run'):
                response = self._agent.run(enhanced_message, **kwargs)
            elif callable(self._agent):
                response = self._agent(enhanced_message, **kwargs)
            else:
                raise AttributeError("Agent does not support chat/run methods")
            
            # Extract assistant response
            if isinstance(response, str):
                assistant_message = response
            elif isinstance(response, dict):
                assistant_message = response.get("message") or response.get("content") or str(response)
            else:
                assistant_message = str(response)
            
            # Save messages to Redis
            self._save_message("user", message)
            if assistant_message:
                self._save_message("assistant", assistant_message)
            
            return response
        except Exception as e:
            print(f"✗ Error in agent chat: {e}")
            raise


def wrap_agent_with_context(
    agent,
    session_id: Optional[str] = None,
    user_id: Optional[int] = None
) -> AgentContextWrapper:
    """
    Convenience function to wrap an ADK agent with automatic context management.
    
    Args:
        agent: The ADK Agent instance to wrap
        session_id: Optional session ID for context management
        user_id: Optional user ID for context management
    
    Returns:
        AgentContextWrapper instance
    """
    return AgentContextWrapper(agent, session_id=session_id, user_id=user_id)

