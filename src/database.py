"""Database connection and setup."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import Config

# Create database engine
engine = create_engine(Config.DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db():
    """Initialize database tables."""
    # Import models here to avoid circular imports
    # Models are automatically registered with Base when defined
    from src.models import User, Agent, PasswordResetToken, MCPConnection, FileSearchStore, FileSearchFile, Plan, UserTokenBalance, TokenUsageHistory  # noqa: F401
    from src.models_conversation import ConversationSession, ConversationMessage  # noqa: F401
    
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.fetchone() is not None
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

