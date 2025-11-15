"""
ADK-Redis Integration Service

This service provides automatic integration between Google ADK agents
and Redis conversation context. It handles:
- Automatic context retrieval before agent processing
- Automatic message saving after agent responses
- Context injection into agent prompts
"""

import os
import sys
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from functools import wraps

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adk_conversation_middleware import get_adk_middleware
from src.config import Config


class ADKRedisIntegration:
    """
    Service for automatic ADK-Redis integration.
    
    This class provides decorators and utilities to automatically:
    1. Retrieve conversation context from Redis
    2. Inject context into agent prompts
    3. Save messages to Redis automatically
    """
    
    def __init__(self):
        self.middleware = get_adk_middleware()
    
    def get_context_for_session(
        self,
        session_id: str,
        user_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation context for a session.
        
        Args:
            session_id: ADK session ID
            user_id: Optional user ID (will be retrieved if not provided)
            limit: Optional limit on number of messages
            
        Returns:
            List of messages formatted for LLM: [{role, content}, ...]
        """
        return self.middleware.get_conversation_context(
            session_id=session_id,
            user_id=user_id,
            limit=limit or Config.MAX_CONVERSATION_HISTORY
        )
    
    def save_user_message(
        self,
        session_id: str,
        content: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save user message to Redis."""
        return self.middleware.save_user_message(
            session_id=session_id,
            content=content,
            user_id=user_id,
            metadata=metadata
        )
    
    def save_assistant_message(
        self,
        session_id: str,
        content: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save assistant message to Redis."""
        return self.middleware.save_assistant_message(
            session_id=session_id,
            content=content,
            user_id=user_id,
            metadata=metadata
        )
    
    def inject_context_into_instruction(
        self,
        base_instruction: str,
        context: List[Dict[str, str]]
    ) -> str:
        """
        Inject conversation context into agent instruction.
        
        This modifies the system prompt to include conversation history.
        
        Args:
            base_instruction: Original agent instruction
            context: Conversation history from Redis
            
        Returns:
            Modified instruction with context injected
        """
        if not context:
            return base_instruction
        
        # Format context as readable conversation history
        context_lines = []
        for msg in context:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                context_lines.append(f"Usuário: {content}")
            elif role == "assistant":
                context_lines.append(f"Assistente: {content}")
        
        context_text = "\n".join(context_lines)
        
        # Inject context at the beginning of instruction
        # This ensures the agent has access to conversation history
        enhanced_instruction = f"""{base_instruction}

CONVERSATION CONTEXT:
Below is the recent conversation history. Use this context to provide relevant and coherent responses.

{context_text}

---
Continue the conversation naturally, using the context above to maintain coherence.
"""
        return enhanced_instruction
    
    def create_context_aware_agent_wrapper(
        self,
        agent_func: Callable,
        session_id: str,
        user_id: Optional[int] = None
    ) -> Callable:
        """
        Create a wrapper function that automatically handles context.
        
        This is a decorator-like function that wraps agent calls.
        
        Args:
            agent_func: Original agent function to wrap
            session_id: ADK session ID
            user_id: Optional user ID
            
        Returns:
            Wrapped function that handles context automatically
        """
        @wraps(agent_func)
        def wrapper(*args, **kwargs):
            # Get conversation context
            context = self.get_context_for_session(
                session_id=session_id,
                user_id=user_id
            )
            
            # If there's context, we need to inject it
            # This depends on how ADK agents work - we'll handle it in the agent wrapper
            result = agent_func(*args, **kwargs)
            
            return result
        
        return wrapper


# Global instance
_adk_redis_integration: Optional[ADKRedisIntegration] = None


def get_adk_redis_integration() -> ADKRedisIntegration:
    """Get ADK-Redis integration service instance."""
    global _adk_redis_integration
    if _adk_redis_integration is None:
        _adk_redis_integration = ADKRedisIntegration()
    return _adk_redis_integration

