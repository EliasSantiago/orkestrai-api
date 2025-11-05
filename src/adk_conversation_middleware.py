"""
Middleware for integrating ADK conversations with Redis.

This module provides hooks to capture and store ADK conversation messages
in Redis for context persistence.
"""

from typing import Optional, Dict, Any
from src.conversation_service import ConversationService
from src.redis_client import get_redis_client


class ADKConversationMiddleware:
    """Middleware to capture and store ADK conversations."""
    
    @staticmethod
    def get_user_id_from_session(session_id: str) -> Optional[int]:
        """
        Extract user_id from session metadata.
        
        This is a placeholder - in a real implementation, you would need to:
        1. Store user_id when session is created
        2. Retrieve it from session metadata or a mapping
        
        For now, we'll use a simple approach: store user_id in Redis
        with the session_id as key.
        """
        redis_client = get_redis_client()
        if not redis_client.is_connected():
            return None
        
        try:
            user_id_str = redis_client.client.get(f"session:user_id:{session_id}")
            if user_id_str:
                return int(user_id_str)
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def set_user_id_for_session(session_id: str, user_id: int) -> bool:
        """Associate a user_id with a session."""
        redis_client = get_redis_client()
        if not redis_client.is_connected():
            return False
        
        try:
            redis_client.client.setex(
                f"session:user_id:{session_id}",
                86400,  # 24 hours
                str(user_id)
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def save_user_message(
        session_id: str,
        content: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save a user message to Redis."""
        if user_id is None:
            user_id = ADKConversationMiddleware.get_user_id_from_session(session_id)
        
        if user_id is None:
            # Cannot save without user_id
            return False
        
        return ConversationService.add_user_message(
            user_id=user_id,
            session_id=session_id,
            content=content,
            metadata=metadata
        )
    
    @staticmethod
    def save_assistant_message(
        session_id: str,
        content: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save an assistant message to Redis."""
        if user_id is None:
            user_id = ADKConversationMiddleware.get_user_id_from_session(session_id)
        
        if user_id is None:
            return False
        
        return ConversationService.add_assistant_message(
            user_id=user_id,
            session_id=session_id,
            content=content,
            metadata=metadata
        )
    
    @staticmethod
    def get_conversation_context(
        session_id: str,
        user_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> list:
        """Get conversation context for a session."""
        if user_id is None:
            user_id = ADKConversationMiddleware.get_user_id_from_session(session_id)
        
        if user_id is None:
            return []
        
        history = ConversationService.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            limit=limit
        )
        
        # Format for LLM context
        return ConversationService.format_history_for_llm(history)


# Global instance
_adk_middleware = ADKConversationMiddleware()


def get_adk_middleware() -> ADKConversationMiddleware:
    """Get ADK conversation middleware instance."""
    return _adk_middleware

