"""Database models for conversation persistence."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database import Base


class ConversationSession(Base):
    """Conversation session model for persistent storage."""
    
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    message_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    session_metadata = Column(JSONB, nullable=True, default={})  # Metadata: title, description, avatar, pinned, etc.
    
    # Relationship with user
    user = relationship("User", backref="conversation_sessions")
    
    # Relationship with messages
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan", order_by="ConversationMessage.created_at")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_active_sessions', 'user_id', 'is_active', 'last_activity'),
    )
    
    def __repr__(self):
        return f"<ConversationSession(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"


class ConversationMessage(Base):
    """Individual message in a conversation session."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("conversation_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (SQLAlchemy reserved word)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship with session
    session = relationship("ConversationSession", back_populates="messages")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_session_messages', 'session_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, session_id={self.session_id}, role={self.role})>"

