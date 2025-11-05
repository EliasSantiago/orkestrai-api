"""
Redis client for managing conversation context and session data.
"""

import json
import redis
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from src.config import Config


class RedisClient:
    """Redis client for conversation context management."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
        except redis.ConnectionError as e:
            print(f"⚠ Warning: Could not connect to Redis: {e}")
            print("  Conversation context will not be persisted")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def _get_session_key(self, user_id: int, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"conversation:user:{user_id}:session:{session_id}"
    
    def _get_user_sessions_key(self, user_id: int) -> str:
        """Generate Redis key for user sessions list."""
        return f"sessions:user:{user_id}"
    
    def add_message(
        self,
        user_id: int,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to the conversation history.
        
        Args:
            user_id: User ID
            session_id: Session ID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            bool: True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            session_key = self._get_session_key(user_id, session_id)
            user_sessions_key = self._get_user_sessions_key(user_id)
            
            # Create message object
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add to conversation history (list)
            self.client.rpush(session_key, json.dumps(message))
            
            # Trim list to max history
            self.client.ltrim(session_key, -Config.MAX_CONVERSATION_HISTORY, -1)
            
            # Set expiration on session key
            self.client.expire(session_key, Config.CONVERSATION_TTL)
            
            # Add session to user's session list
            self.client.sadd(user_sessions_key, session_id)
            self.client.expire(user_sessions_key, Config.CONVERSATION_TTL)
            
            return True
        except Exception as e:
            print(f"✗ Error adding message to Redis: {e}")
            return False
    
    def get_conversation_history(
        self,
        user_id: int,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            user_id: User ID
            session_id: Session ID
            limit: Optional limit on number of messages
            
        Returns:
            List of message dictionaries
        """
        if not self.is_connected():
            return []
        
        try:
            session_key = self._get_session_key(user_id, session_id)
            
            # Get messages from Redis list
            if limit:
                messages = self.client.lrange(session_key, -limit, -1)
            else:
                messages = self.client.lrange(session_key, 0, -1)
            
            # Parse JSON messages
            history = []
            for msg_json in messages:
                try:
                    history.append(json.loads(msg_json))
                except json.JSONDecodeError:
                    continue
            
            return history
        except Exception as e:
            print(f"✗ Error getting conversation history: {e}")
            return []
    
    def get_user_sessions(self, user_id: int) -> List[str]:
        """
        Get all session IDs for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of session IDs
        """
        if not self.is_connected():
            return []
        
        try:
            user_sessions_key = self._get_user_sessions_key(user_id)
            sessions = self.client.smembers(user_sessions_key)
            return list(sessions)
        except Exception as e:
            print(f"✗ Error getting user sessions: {e}")
            return []
    
    def clear_session(self, user_id: int, session_id: str) -> bool:
        """
        Clear a specific session's conversation history.
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            bool: True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            session_key = self._get_session_key(user_id, session_id)
            user_sessions_key = self._get_user_sessions_key(user_id)
            
            # Delete session data
            self.client.delete(session_key)
            
            # Remove from user's session list
            self.client.srem(user_sessions_key, session_id)
            
            return True
        except Exception as e:
            print(f"✗ Error clearing session: {e}")
            return False
    
    def clear_user_sessions(self, user_id: int) -> bool:
        """
        Clear all sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            user_sessions_key = self._get_user_sessions_key(user_id)
            sessions = self.client.smembers(user_sessions_key)
            
            for session_id in sessions:
                session_key = self._get_session_key(user_id, session_id)
                self.client.delete(session_key)
            
            self.client.delete(user_sessions_key)
            return True
        except Exception as e:
            print(f"✗ Error clearing user sessions: {e}")
            return False
    
    def get_session_info(self, user_id: int, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information (message count, last activity, etc.).
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            Dictionary with session info or None
        """
        if not self.is_connected():
            return None
        
        try:
            session_key = self._get_session_key(user_id, session_id)
            
            message_count = self.client.llen(session_key)
            ttl = self.client.ttl(session_key)
            
            if message_count == 0:
                return None
            
            # Get last message for timestamp
            last_message_json = self.client.lindex(session_key, -1)
            if last_message_json:
                last_message = json.loads(last_message_json)
                last_activity = last_message.get("timestamp")
            else:
                last_activity = None
            
            return {
                "session_id": session_id,
                "message_count": message_count,
                "last_activity": last_activity,
                "ttl": ttl
            }
        except Exception as e:
            print(f"✗ Error getting session info: {e}")
            return None


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get or create Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client

