"""
Middleware for integrating ADK conversations with Redis and PostgreSQL.

This module provides hooks to capture and store ADK conversation messages
in both Redis (cache) and PostgreSQL (persistent storage).
"""

from typing import Optional, Dict, Any
from src.hybrid_conversation_service import HybridConversationService
from src.redis_client import get_redis_client
from src.database import SessionLocal


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
            from src.config import Config
            redis_client.client.setex(
                f"session:user_id:{session_id}",
                Config.CONVERSATION_TTL,  # Use configured TTL (default: 4 hours)
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
        """Save a user message to Redis + PostgreSQL."""
        if user_id is None:
            user_id = ADKConversationMiddleware.get_user_id_from_session(session_id)
        
        if user_id is None:
            # Cannot save without user_id
            return False
        
        # Use hybrid service (Redis + PostgreSQL)
        db = SessionLocal()
        try:
            return HybridConversationService.add_user_message(
                user_id=user_id,
                session_id=session_id,
                content=content,
                metadata=metadata,
                db=db
            )
        finally:
            db.close()
    
    @staticmethod
    def save_assistant_message(
        session_id: str,
        content: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save an assistant message to Redis + PostgreSQL."""
        if user_id is None:
            user_id = ADKConversationMiddleware.get_user_id_from_session(session_id)
        
        if user_id is None:
            return False
        
        # Use hybrid service (Redis + PostgreSQL)
        db = SessionLocal()
        try:
            return HybridConversationService.add_assistant_message(
                user_id=user_id,
                session_id=session_id,
                content=content,
                metadata=metadata,
                db=db
            )
        finally:
            db.close()
    
    @staticmethod
    def get_conversation_context(
        session_id: str,
        user_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> list:
        """Get conversation context for a session (from Redis or PostgreSQL)."""
        if user_id is None:
            user_id = ADKConversationMiddleware.get_user_id_from_session(session_id)
        
        if user_id is None:
            return []
        
        # Use hybrid service (tries Redis first, falls back to PostgreSQL)
        db = SessionLocal()
        try:
            history = HybridConversationService.get_conversation_history(
                user_id=user_id,
                session_id=session_id,
                limit=limit,
                db=db
            )
            
            # Format for LLM context
            return HybridConversationService.format_history_for_llm(history)
        finally:
            db.close()


# Global instance
_adk_middleware = ADKConversationMiddleware()


def get_adk_middleware() -> ADKConversationMiddleware:
    """Get ADK conversation middleware instance."""
    return _adk_middleware

