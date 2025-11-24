"""
Hybrid conversation service: Redis (cache) + PostgreSQL (persistence).

Strategy:
- Write-through: Write to both Redis and PostgreSQL
- Read-through: Read from Redis, fallback to PostgreSQL if not found
- Redis: Fast access for active sessions (TTL: 24h)
- PostgreSQL: Permanent storage for all conversations
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.redis_client import get_redis_client
from src.config import Config
from src.models_conversation import ConversationSession, ConversationMessage


class HybridConversationService:
    """
    Hybrid conversation service using Redis as cache and PostgreSQL as persistent storage.
    
    Benefits:
    - Fast access for active sessions (Redis)
    - Permanent storage (PostgreSQL)
    - Automatic fallback if Redis unavailable
    - Scalable for thousands of concurrent sessions
    """
    
    @staticmethod
    def add_user_message(
        user_id: int,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> bool:
        """
        Add a user message to conversation.
        Write-through: saves to both Redis (cache) and PostgreSQL (persistent).
        """
        # Write to Redis (cache) - fast access
        redis_client = get_redis_client()
        redis_success = redis_client.add_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=content,
            metadata=metadata
        )
        
        # Write to PostgreSQL (persistent storage)
        if db:
            try:
                # Get or create session
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id,
                    ConversationSession.user_id == user_id
                ).first()
                
                if not session:
                    # Create new session with agent_id in metadata
                    session_metadata = {}
                    if agent_id:
                        session_metadata["agent_id"] = agent_id
                    
                    session = ConversationSession(
                        session_id=session_id,
                        user_id=user_id,
                        message_count=0,
                        session_metadata=session_metadata
                    )
                    db.add(session)
                else:
                    # Update existing session metadata with agent_id if provided
                    if agent_id:
                        session_metadata = session.session_metadata or {}
                        if "agent_id" not in session_metadata:
                            session_metadata["agent_id"] = agent_id
                            session.session_metadata = session_metadata
                
                # Create message
                message = ConversationMessage(
                    session_id=session_id,
                    role="user",
                    content=content,
                    message_metadata=metadata or {}
                )
                db.add(message)
                
                # Update session stats
                session.message_count += 1
                session.last_activity = datetime.utcnow()
                session.updated_at = datetime.utcnow()
                session.is_active = True
                
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                print(f"✗ Error saving message to PostgreSQL: {e}")
                # Return True if Redis succeeded (graceful degradation)
                return redis_success
        
        return redis_success
    
    @staticmethod
    def add_assistant_message(
        user_id: int,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> bool:
        """
        Add an assistant message to conversation.
        Write-through: saves to both Redis (cache) and PostgreSQL (persistent).
        """
        # Write to Redis (cache)
        redis_client = get_redis_client()
        redis_success = redis_client.add_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=content,
            metadata=metadata
        )
        
        # Write to PostgreSQL (persistent storage)
        if db:
            try:
                # Get or create session
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id,
                    ConversationSession.user_id == user_id
                ).first()
                
                if not session:
                    session = ConversationSession(
                        session_id=session_id,
                        user_id=user_id,
                        message_count=0
                    )
                    db.add(session)
                
                # Create message
                message = ConversationMessage(
                    session_id=session_id,
                    role="assistant",
                    content=content,
                    message_metadata=metadata or {}
                )
                db.add(message)
                
                # Update session stats
                session.message_count += 1
                session.last_activity = datetime.utcnow()
                session.updated_at = datetime.utcnow()
                session.is_active = True
                
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                print(f"✗ Error saving message to PostgreSQL: {e}")
                return redis_success
        
        return redis_success
    
    @staticmethod
    def get_conversation_history(
        user_id: int,
        session_id: str,
        limit: Optional[int] = None,
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        Read-through: tries Redis first, falls back to PostgreSQL if not found.
        """
        # Try Redis first (fast cache)
        redis_client = get_redis_client()
        if redis_client.is_connected():
            history = redis_client.get_conversation_history(
                user_id=user_id,
                session_id=session_id,
                limit=limit
            )
            if history:
                return history
        
        # Fallback to PostgreSQL if Redis unavailable or empty
        if db:
            try:
                # Verify session belongs to user
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id,
                    ConversationSession.user_id == user_id
                ).first()
                
                if not session:
                    return []
                
                # Get messages
                query = db.query(ConversationMessage).filter(
                    ConversationMessage.session_id == session_id
                ).order_by(ConversationMessage.created_at)
                
                if limit:
                    query = query.limit(limit)
                
                messages = query.all()
                
                # Convert to dict format with full message details
                history = []
                for msg in messages:
                    created_at_ms = int(msg.created_at.timestamp() * 1000) if msg.created_at else None
                    updated_at_ms = created_at_ms  # Use created_at as updated_at if no updated_at field
                    
                    msg_dict = {
                        "id": f"msg-{msg.id}",  # Format: msg-{database_id}
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.created_at.isoformat() + "Z" if msg.created_at else None,
                        "createdAt": created_at_ms,
                        "updatedAt": updated_at_ms,
                        "metadata": msg.message_metadata or {}
                    }
                    
                    # Add model/provider if available in metadata
                    if isinstance(msg.message_metadata, dict):
                        if "model" in msg.message_metadata:
                            msg_dict["model"] = msg.message_metadata["model"]
                        if "provider" in msg.message_metadata:
                            msg_dict["provider"] = msg.message_metadata["provider"]
                        if "parent_id" in msg.message_metadata:
                            msg_dict["parentId"] = msg.message_metadata["parent_id"]
                    
                    history.append(msg_dict)
                
                # Optionally: warm up Redis cache with recent data
                if history and redis_client.is_connected():
                    # Only cache if session is recent (active in last 24h)
                    if session.last_activity > datetime.utcnow() - timedelta(hours=24):
                        for msg in history[-limit:] if limit else history:
                            redis_client.add_message(
                                user_id=user_id,
                                session_id=session_id,
                                role=msg["role"],
                                content=msg["content"],
                                metadata=msg.get("metadata")
                            )
                
                return history
            except Exception as e:
                print(f"✗ Error reading from PostgreSQL: {e}")
        
        return []
    
    @staticmethod
    def get_user_sessions(
        user_id: int, 
        db: Optional[Session] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Tuple[List[str], int]:
        """
        Get session IDs for a user with pagination support.
        Uses PostgreSQL as the source of truth for pagination.
        Redis sessions are included but pagination is based on PostgreSQL.
        
        Returns:
            tuple: (list of session IDs, total count)
        """
        total_count = 0
        session_list = []
        
        if db:
            try:
                # Get total count from PostgreSQL
                total_count = db.query(ConversationSession.session_id).filter(
                    ConversationSession.user_id == user_id,
                    ConversationSession.is_active == True
                ).count()
                
                # Get paginated sessions from PostgreSQL
                query = db.query(ConversationSession.session_id).filter(
                    ConversationSession.user_id == user_id,
                    ConversationSession.is_active == True
                ).order_by(desc(ConversationSession.last_activity))
                
                if limit:
                    query = query.limit(limit).offset(offset)
                
                db_sessions = query.all()
                
                # Extract session IDs
                for (session_id,) in db_sessions:
                    session_list.append(session_id)
            except Exception as e:
                print(f"✗ Error reading sessions from PostgreSQL: {e}")
                # Fallback: get from Redis if PostgreSQL fails
                redis_client = get_redis_client()
                if redis_client.is_connected():
                    session_list = redis_client.get_user_sessions(user_id)
                    total_count = len(session_list)
        
        return session_list, total_count
    
    @staticmethod
    def clear_session(user_id: int, session_id: str, db: Optional[Session] = None) -> bool:
        """
        Clear a session.
        Marks as inactive in PostgreSQL, deletes from Redis.
        """
        # Clear from Redis
        redis_client = get_redis_client()
        redis_success = redis_client.clear_session(user_id, session_id)
        
        # Mark as inactive in PostgreSQL (soft delete)
        if db:
            try:
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id,
                    ConversationSession.user_id == user_id
                ).first()
                
                if session:
                    session.is_active = False
                    session.updated_at = datetime.utcnow()
                    db.commit()
                    return True
            except Exception as e:
                db.rollback()
                print(f"✗ Error clearing session in PostgreSQL: {e}")
        
        return redis_success
    
    @staticmethod
    def get_session_info(user_id: int, session_id: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """Get session information."""
        # Try Redis first
        redis_client = get_redis_client()
        if redis_client.is_connected():
            info = redis_client.get_session_info(user_id, session_id)
            if info:
                return info
        
        # Fallback to PostgreSQL
        if db:
            try:
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id,
                    ConversationSession.user_id == user_id
                ).first()
                
                if not session:
                    return None
                
                # Get metadata
                metadata = session.session_metadata or {}
                
                return {
                    "session_id": session.session_id,
                    "message_count": session.message_count,
                    "last_activity": session.last_activity.isoformat() + "Z" if session.last_activity else None,
                    "created_at": session.created_at.isoformat() + "Z" if session.created_at else None,
                    "ttl": None,  # No TTL in PostgreSQL
                    "title": metadata.get("title"),
                    "description": metadata.get("description"),
                    "avatar": metadata.get("avatar"),
                    "pinned": metadata.get("pinned", False),
                    "agent_id": metadata.get("agent_id")  # Include agent_id from metadata
                }
            except Exception as e:
                print(f"✗ Error getting session info from PostgreSQL: {e}")
        
        return None
    
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
    
    @staticmethod
    def archive_old_sessions(db: Session, days_inactive: int = 30) -> int:
        """
        Archive old inactive sessions (mark as inactive).
        Useful for cleanup jobs.
        
        Args:
            db: Database session
            days_inactive: Days of inactivity before archiving
        
        Returns:
            Number of sessions archived
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
            
            sessions = db.query(ConversationSession).filter(
                ConversationSession.is_active == True,
                ConversationSession.last_activity < cutoff_date
            ).all()
            
            count = 0
            for session in sessions:
                session.is_active = False
                count += 1
            
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            print(f"✗ Error archiving sessions: {e}")
            return 0

