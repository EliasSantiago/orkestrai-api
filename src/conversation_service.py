"""
Service for managing conversation context with Redis.
"""

from typing import List, Dict, Optional, Any
from src.redis_client import get_redis_client


class ConversationService:
    """Service for managing conversation context."""
    
    @staticmethod
    def add_user_message(
        user_id: int,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a user message to the conversation."""
        redis_client = get_redis_client()
        return redis_client.add_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=content,
            metadata=metadata
        )
    
    @staticmethod
    def add_assistant_message(
        user_id: int,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add an assistant message to the conversation."""
        redis_client = get_redis_client()
        return redis_client.add_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=content,
            metadata=metadata
        )
    
    @staticmethod
    def get_conversation_history(
        user_id: int,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        redis_client = get_redis_client()
        return redis_client.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            limit=limit
        )
    
    @staticmethod
    def get_user_sessions(user_id: int) -> List[str]:
        """Get all session IDs for a user."""
        redis_client = get_redis_client()
        return redis_client.get_user_sessions(user_id)
    
    @staticmethod
    def clear_session(user_id: int, session_id: str) -> bool:
        """Clear a specific session."""
        redis_client = get_redis_client()
        return redis_client.clear_session(user_id, session_id)
    
    @staticmethod
    def get_session_info(user_id: int, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        redis_client = get_redis_client()
        return redis_client.get_session_info(user_id, session_id)
    
    @staticmethod
    def format_history_for_llm(history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format conversation history for LLM context.
        
        Returns a simplified format with only role and content.
        """
        formatted = []
        for msg in history:
            formatted.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        return formatted

