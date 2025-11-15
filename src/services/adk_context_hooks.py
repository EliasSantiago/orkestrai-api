"""
Hook module for ADK agents to automatically integrate with Redis context.

This module is injected into generated agent.py files to provide
automatic context management.
"""

import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.adk_conversation_middleware import get_adk_middleware
    from src.config import Config
except ImportError:
    # If imports fail, disable context
    get_adk_middleware = None
    Config = None


def get_session_id_from_env() -> Optional[str]:
    """Extract session_id from environment variables."""
    # ADK may pass session info via environment
    return os.environ.get("ADK_SESSION_ID") or os.environ.get("SESSION_ID")


def get_user_id_from_env() -> Optional[int]:
    """Extract user_id from environment variables."""
    user_id_str = os.environ.get("ADK_USER_ID") or os.environ.get("USER_ID")
    if user_id_str:
        try:
            return int(user_id_str)
        except:
            return None
    return None


# Global storage for session context (can be set by middleware)
_global_session_context = {}
_global_user_context = {}


def set_session_context(session_id: str, user_id: Optional[int] = None):
    """
    Set global session context for context injection.
    
    This can be called by middleware or external code to set context
    that will be used when injecting context into agents.
    
    Args:
        session_id: Session ID
        user_id: Optional user ID
    """
    import threading
    thread_id = threading.current_thread().ident
    if thread_id:
        _global_session_context[thread_id] = session_id
        if user_id:
            _global_user_context[thread_id] = user_id


def get_session_context() -> Tuple[Optional[str], Optional[int]]:
    """Get current session context from global storage."""
    import threading
    thread_id = threading.current_thread().ident
    if thread_id:
        session_id = _global_session_context.get(thread_id)
        user_id = _global_user_context.get(thread_id)
        return session_id, user_id
    return None, None


def inject_context_into_agent(agent, session_id: Optional[str] = None, user_id: Optional[int] = None):
    """
    Inject conversation context into an ADK Agent.
    
    This function modifies the agent's instruction to include conversation history.
    
    Args:
        agent: ADK Agent instance
        session_id: Optional session ID (will be retrieved from env/global if not provided)
        user_id: Optional user ID (will be retrieved from env/global if not provided)
    """
    if not get_adk_middleware:
        return  # Context disabled
    
    # Try to get session_id from various sources
    if not session_id:
        session_id, _ = get_session_context()
    
    if not session_id:
        session_id = get_session_id_from_env()
    
    if not session_id:
        return  # Cannot inject context without session_id
    
    # Try to get user_id from various sources
    if not user_id:
        _, user_id = get_session_context()
    
    if not user_id:
        user_id = get_user_id_from_env()
    
    # If still no user_id, try to get from session association
    if not user_id and session_id:
        try:
            middleware = get_adk_middleware()
            user_id = middleware.get_user_id_from_session(session_id)
        except:
            pass
    
    # If we have session_id but no user_id, we can still try to inject context
    # The context will be empty, but at least the agent will be ready
    # when user_id becomes available
    
    try:
        middleware = get_adk_middleware()
        
        # Get conversation context
        context = middleware.get_conversation_context(
            session_id=session_id,
            user_id=user_id,
            limit=Config.MAX_CONVERSATION_HISTORY if Config else 50
        )
        
        if context:
            # Format context
            context_lines = []
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    context_lines.append(f"Usuário: {content}")
                elif role == "assistant":
                    context_lines.append(f"Assistente: {content}")
            
            context_text = "\n".join(context_lines)
            
            # Inject into instruction
            original_instruction = agent.instruction
            enhanced_instruction = f"""{original_instruction}

CONVERSATION CONTEXT:
Below is the recent conversation history. Use this context to provide relevant and coherent responses.

{context_text}

---
Continue the conversation naturally, using the context above to maintain coherence.
"""
            
            # Update agent instruction
            try:
                agent.instruction = enhanced_instruction
            except:
                # If instruction is read-only, store it separately
                agent._enhanced_instruction = enhanced_instruction
                agent._use_enhanced_context = True
    except Exception as e:
        print(f"⚠ Warning: Could not inject context: {e}")


def save_message_to_redis(
    session_id: str,
    role: str,
    content: str,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Save a message to Redis.
    
    Args:
        session_id: Session ID
        role: Message role ('user' or 'assistant')
        content: Message content
        user_id: Optional user ID
        metadata: Optional metadata
    """
    if not get_adk_middleware:
        return False
    
    try:
        middleware = get_adk_middleware()
        
        if role == "user":
            return middleware.save_user_message(
                session_id=session_id,
                content=content,
                user_id=user_id,
                metadata=metadata
            )
        elif role == "assistant":
            return middleware.save_assistant_message(
                session_id=session_id,
                content=content,
                user_id=user_id,
                metadata=metadata
            )
    except Exception as e:
        print(f"⚠ Warning: Could not save message to Redis: {e}")
        return False
    
    return False

