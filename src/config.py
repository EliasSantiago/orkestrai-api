"""Configuration module for the application."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Google Gemini API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # PostgreSQL Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://agentuser:agentpass@localhost:5432/agentsdb"
    )
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    
    # Conversation Context Settings
    CONVERSATION_TTL = int(os.getenv("CONVERSATION_TTL", "86400"))  # 24 hours in seconds
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "100"))  # Max messages per session
    
    # Model defaults
    DEFAULT_MODEL_GEMINI = os.getenv("DEFAULT_MODEL_GEMINI", "gemini-2.0-flash-exp")
    DEFAULT_MODEL_OPENAI = os.getenv("DEFAULT_MODEL_OPENAI", "gpt-4o-mini")
    
    # JWT Secret Key (in production, use a strong random key)
    SECRET_KEY = os.getenv("SECRET_KEY", DATABASE_URL)  # Fallback to DATABASE_URL
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        missing = []
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        return True

