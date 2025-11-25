"""Database models for users and agents."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, BigInteger, JSON, Float, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database import Base
from cryptography.fernet import Fernet
import os
import base64


class Plan(Base):
    """Subscription plan model for token limits."""
    
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # free, pro, plus
    description = Column(Text, nullable=True)
    price_month = Column(Numeric(10, 2), nullable=False, default=0.0)  # Monthly price in USD
    price_year = Column(Numeric(10, 2), nullable=False, default=0.0)  # Yearly price in USD
    monthly_token_limit = Column(BigInteger, nullable=False)  # Monthly token limit
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with users
    users = relationship("User", back_populates="plan")
    
    def __repr__(self):
        return f"<Plan(id={self.id}, name={self.name}, monthly_token_limit={self.monthly_token_limit})>"


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)  # URL to user's avatar image
    occupation = Column(String(255), nullable=True)  # User's occupation/job title
    bio = Column(Text, nullable=True)  # User's bio/about me
    
    # Plan relationship
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True, index=True)
    plan = relationship("Plan", back_populates="users")
    
    # User preferences (theme, language, layout, etc)
    # Stored as JSONB for flexibility and better performance
    preferences = Column(JSONB, nullable=True, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with agents
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    
    # Relationship with token balance
    token_balance = relationship("UserTokenBalance", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Relationship with token usage history
    token_usage_history = relationship("TokenUsageHistory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"


class Agent(Base):
    """Agent model following ADK structure.
    
    Supports multiple agent types:
    - llm: LLM agent with tools (default)
    - sequential: Workflow agent that executes agents in sequence
    - loop: Workflow agent that loops until condition is met
    - parallel: Workflow agent that executes agents in parallel
    - custom: Custom agent with user-defined logic
    """
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Agent type: llm, sequential, loop, parallel, custom
    agent_type = Column(String(50), nullable=False, default="llm", index=True)
    
    # LLM Agent fields
    instruction = Column(Text, nullable=True)  # Made nullable for workflow agents
    model = Column(String(100), nullable=True, default="gemini-2.0-flash-exp")  # Made nullable for workflow agents
    
    # Tools are stored as JSON array of tool names
    # Tools are imported from the tools/ directory
    tools = Column(JSON, nullable=True, default=list)
    
    # File Search (RAG) configuration
    # If True, agent will have access to user's File Search Stores for RAG
    # If False, agent will not use File Search even if stores are available
    use_file_search = Column(Boolean, default=False, nullable=False)
    
    # Workflow Agent configuration (for sequential, loop, parallel)
    # Stores agent IDs or names to execute, conditions, etc.
    workflow_config = Column(JSON, nullable=True)
    # Example for sequential: {"agents": ["agent1", "agent2", "agent3"]}
    # Example for loop: {"agent": "agent1", "condition": "...", "max_iterations": 5}
    # Example for parallel: {"agents": ["agent1", "agent2", "agent3"], "merge_strategy": "concat"}
    
    # Custom Agent code/configuration
    custom_config = Column(JSON, nullable=True)
    # Example: {"code": "...", "runtime": "python", "entry_point": "main"}
    
    # Owner relationship
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("User", back_populates="agents")
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False, nullable=False)  # Favorite flag for quick access
    icon = Column(String(100), nullable=True)  # Icon name from lucide-react library
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, type={self.agent_type}, user_id={self.user_id})>"


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


class UserTokenBalance(Base):
    """
    User token balance model for tracking monthly token usage.
    
    Each user has one active balance record per month.
    The balance resets at the beginning of each month.
    """
    
    __tablename__ = "user_token_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Token tracking
    tokens_used_this_month = Column(BigInteger, default=0, nullable=False)  # Tokens used in current month
    month = Column(Integer, nullable=False, index=True)  # Month (1-12)
    year = Column(Integer, nullable=False, index=True)  # Year (e.g., 2025)
    
    # Metadata
    last_reset_at = Column(DateTime, default=datetime.utcnow)  # When balance was last reset
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="token_balance")
    
    def __repr__(self):
        return f"<UserTokenBalance(id={self.id}, user_id={self.user_id}, tokens_used={self.tokens_used_this_month}, month={self.month}/{self.year})>"


class TokenUsageHistory(Base):
    """
    Token usage history model for tracking individual API calls.
    
    Records each LLM API call with token counts and costs.
    """
    
    __tablename__ = "token_usage_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Request information
    model = Column(String(100), nullable=False)  # Model used (e.g., gpt-4, gemini-pro)
    endpoint = Column(String(255), nullable=True)  # API endpoint called
    session_id = Column(String(100), nullable=True, index=True)  # Session/conversation ID
    
    # Token counts
    prompt_tokens = Column(Integer, default=0, nullable=False)  # Input tokens
    completion_tokens = Column(Integer, default=0, nullable=False)  # Output tokens
    total_tokens = Column(Integer, default=0, nullable=False)  # Total tokens used
    
    # Cost tracking
    cost_usd = Column(Numeric(10, 6), nullable=True)  # Cost in USD (up to 6 decimal places)
    
    # Request metadata
    request_metadata = Column(JSON, nullable=True)  # Additional metadata (agent_id, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="token_usage_history")
    
    def __repr__(self):
        return f"<TokenUsageHistory(id={self.id}, user_id={self.user_id}, model={self.model}, total_tokens={self.total_tokens})>"

