"""Database models for users and agents."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, BigInteger, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database import Base
from cryptography.fernet import Fernet
import os
import base64


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # User preferences (theme, language, layout, etc)
    # Stored as JSONB for flexibility and better performance
    preferences = Column(JSONB, nullable=True, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with agents
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"


class Agent(Base):
    """Agent model following ADK structure."""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    instruction = Column(Text, nullable=False)
    model = Column(String(100), nullable=False, default="gemini-2.0-flash-exp")
    
    # Tools are stored as JSON array of tool names
    # Tools are imported from the tools/ directory
    tools = Column(JSON, nullable=True, default=list)
    
    # File Search (RAG) configuration
    # If True, agent will have access to user's File Search Stores for RAG
    # If False, agent will not use File Search even if stores are available
    use_file_search = Column(Boolean, default=False, nullable=False)
    
    # Owner relationship
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("User", back_populates="agents")
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, user_id={self.user_id})>"


class PasswordResetToken(Base):
    """Password reset token model."""
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user = relationship("User")
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at}, used={self.used})>"


class MCPConnection(Base):
    """
    MCP Connection model for storing user-specific MCP credentials.
    
    This model stores encrypted credentials for MCP integrations
    on a per-user basis, allowing each user to connect their own accounts.
    """
    
    __tablename__ = "mcp_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # MCP provider type (e.g., "provider_name", "github", "slack")
    provider = Column(String(50), nullable=False, index=True)
    
    # Encrypted credentials (API keys, tokens, etc.)
    encrypted_credentials = Column(Text, nullable=False)
    
    # Connection metadata
    is_active = Column(Boolean, default=True, nullable=False)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # For OAuth tokens that expire
    
    # Additional metadata stored as JSON
    # Note: Using 'meta_data' instead of 'metadata' to avoid conflict with SQLAlchemy's reserved attribute
    meta_data = Column(JSON, nullable=True, default=dict)  # e.g., workspace_id, user_info, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with user
    user = relationship("User")
    
    # Encryption key (should be in environment variable)
    @staticmethod
    def _get_encryption_key() -> bytes:
        """Get encryption key from environment or generate a default one."""
        key = os.getenv("MCP_ENCRYPTION_KEY", "")
        if not key:
            # Generate a key if not set (for development only)
            # In production, this should always be set in environment
            key = Fernet.generate_key().decode()
            print(f"⚠️  WARNING: MCP_ENCRYPTION_KEY not set. Generated temporary key: {key}")
            print("⚠️  Set MCP_ENCRYPTION_KEY in .env for production use!")
        else:
            # Ensure key is bytes
            if isinstance(key, str):
                key = key.encode()
        return key
    
    def encrypt_credentials(self, credentials: dict) -> str:
        """Encrypt credentials dictionary."""
        import json
        key = self._get_encryption_key()
        fernet = Fernet(key)
        credentials_json = json.dumps(credentials)
        encrypted = fernet.encrypt(credentials_json.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_credentials(self) -> dict:
        """Decrypt and return credentials dictionary."""
        import json
        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = base64.b64decode(self.encrypted_credentials.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return json.loads(decrypted.decode())
    
    def set_credentials(self, credentials: dict):
        """Set encrypted credentials."""
        self.encrypted_credentials = self.encrypt_credentials(credentials)
    
    def get_credentials(self) -> dict:
        """Get decrypted credentials."""
        return self.decrypt_credentials()
    
    def __repr__(self):
        return f"<MCPConnection(id={self.id}, user_id={self.user_id}, provider={self.provider}, is_active={self.is_active})>"


class FileSearchStore(Base):
    """
    File Search Store model for RAG (Retrieval-Augmented Generation).
    
    Each user can create multiple stores to organize their documents.
    Stores are isolated per user - users can only see their own stores.
    """
    
    __tablename__ = "file_search_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Store information
    display_name = Column(String(255), nullable=False)  # User-friendly name
    google_store_name = Column(String(500), nullable=False, unique=True)  # Full Google name (projects/.../fileSearchStores/...)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    files = relationship("FileSearchFile", back_populates="store", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FileSearchStore(id={self.id}, user_id={self.user_id}, display_name={self.display_name})>"


class FileSearchFile(Base):
    """
    File in a File Search Store.
    
    Represents a file that has been uploaded and indexed in a File Search Store.
    Files are isolated per user through the store relationship.
    """
    
    __tablename__ = "file_search_files"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("file_search_stores.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    display_name = Column(String(255), nullable=True)  # User-friendly name
    google_file_name = Column(String(500), nullable=True, unique=True)  # Full Google name (projects/.../files/...)
    # Note: nullable=True allows multiple files without google_file_name (when extraction fails)
    # unique=True ensures uniqueness when google_file_name is provided
    
    # File metadata
    file_type = Column(String(100), nullable=True)  # MIME type
    size_bytes = Column(BigInteger, nullable=True)  # File size in bytes
    
    # Processing status
    status = Column(String(50), default="processing", nullable=False)  # processing, completed, failed
    error_message = Column(Text, nullable=True)  # Error message if status is failed
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    store = relationship("FileSearchStore", back_populates="files")
    
    def __repr__(self):
        return f"<FileSearchFile(id={self.id}, store_id={self.store_id}, display_name={self.display_name}, status={self.status})>"

