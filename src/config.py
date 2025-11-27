"""Configuration module for the application."""

import os
from dotenv import load_dotenv

load_dotenv()


def get_int_env(key: str, default: str) -> int:
    """Get integer environment variable, removing inline comments."""
    value = os.getenv(key, default)
    # Remove inline comments (anything after # or //)
    if isinstance(value, str):
        value = value.split('#')[0].split('//')[0].strip()
    return int(value)


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
    REDIS_PORT = get_int_env("REDIS_PORT", "6379")
    REDIS_DB = get_int_env("REDIS_DB", "0")
    REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    
    # Conversation Context Settings
    # Conversation TTL in Redis (seconds)
    # Reduced from 24h to 4h for better security and GDPR/LGPD compliance
    # This reduces exposure window for personal data while maintaining good UX
    CONVERSATION_TTL = get_int_env("CONVERSATION_TTL", "14400")  # 4 hours in seconds (was 24h)
    MAX_CONVERSATION_HISTORY = get_int_env("MAX_CONVERSATION_HISTORY", "100")  # Max messages per session
    
    # Model defaults
    DEFAULT_MODEL_GEMINI = os.getenv("DEFAULT_MODEL_GEMINI", "gemini-2.0-flash-exp")
    DEFAULT_MODEL_OPENAI = os.getenv("DEFAULT_MODEL_OPENAI", "gpt-4o-mini")
    
    # On-premise LLM Configuration (for locally hosted models)
    ONPREMISE_API_BASE_URL = os.getenv("ONPREMISE_API_BASE_URL", "")  # e.g., "http://localhost:1234"
    ONPREMISE_CHAT_ENDPOINT = os.getenv("ONPREMISE_CHAT_ENDPOINT", "")  # Optional: Custom chat endpoint (e.g., "/api/chat" or "/chat"). If empty, uses OpenAI-compatible "/v1/chat/completions"
    ONPREMISE_API_KEY = os.getenv("ONPREMISE_API_KEY", "")  # Optional, some local APIs don't need keys
    ONPREMISE_MODELS = os.getenv("ONPREMISE_MODELS", "")  # Optional: Comma-separated list to restrict allowed models, e.g., "llama-2,mixtral-8x7b". If empty, any model name is accepted.
    
    # Ollama LLM Configuration (for locally hosted Ollama models)
    OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "")  # e.g., "http://localhost:11434"
    OLLAMA_MODELS = os.getenv("OLLAMA_MODELS", "")  # Optional: Comma-separated list to restrict allowed models, e.g., "gemma-2b-light:latest,llama2:latest". If empty, any model name is accepted.
    
    # LiteLLM Configuration (unified LLM gateway)
    # Documentation: https://docs.litellm.ai/docs/
    LITELLM_ENABLED = os.getenv("LITELLM_ENABLED", "false").lower() == "true"  # Enable/disable LiteLLM provider
    LITELLM_VERBOSE = os.getenv("LITELLM_VERBOSE", "false").lower() == "true"  # Enable verbose logging for debugging
    LITELLM_NUM_RETRIES = get_int_env("LITELLM_NUM_RETRIES", "3")  # Number of retries for failed requests
    LITELLM_REQUEST_TIMEOUT = get_int_env("LITELLM_REQUEST_TIMEOUT", "600")  # Request timeout in seconds (10 minutes)
    LITELLM_CONFIG_PATH = os.getenv("LITELLM_CONFIG_PATH", "litellm_config.yaml")  # Path to LiteLLM config file
    
    # Additional LiteLLM provider API keys (optional)
    LITELLM_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")  # For Claude models
    LITELLM_COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")  # For Cohere models
    LITELLM_HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")  # For HuggingFace models
    LITELLM_REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "")  # For Replicate models
    
    # On-premise OAuth Configuration (for APIs that require OAuth tokens)
    ONPREMISE_TOKEN_URL = os.getenv("ONPREMISE_TOKEN_URL", "")  # e.g., "https://apidesenv.go.gov.br/token"
    ONPREMISE_CONSUMER_KEY = os.getenv("ONPREMISE_CONSUMER_KEY", "")  # Consumer key for OAuth
    ONPREMISE_CONSUMER_SECRET = os.getenv("ONPREMISE_CONSUMER_SECRET", "")  # Consumer secret for OAuth
    ONPREMISE_OAUTH_GRANT_TYPE = os.getenv("ONPREMISE_OAUTH_GRANT_TYPE", "client_credentials")  # OAuth grant type: "password" or "client_credentials"
    ONPREMISE_USERNAME = os.getenv("ONPREMISE_USERNAME", "")  # Username for OAuth password grant (required only for password grant)
    ONPREMISE_PASSWORD = os.getenv("ONPREMISE_PASSWORD", "")  # Password for OAuth password grant (required only for password grant)
    
    # SSL/TLS Configuration (for environments with self-signed certificates)
    # WARNING: Disabling SSL verification is insecure and should only be used in development
    VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"
    
    # JWT Secret Key (in production, use a strong random key)
    SECRET_KEY = os.getenv("SECRET_KEY", DATABASE_URL)  # Fallback to DATABASE_URL
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days
    
    # Email Configuration (for password reset)
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = get_int_env("SMTP_PORT", "587")
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Agents ADK API")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # Password Reset Settings
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS = get_int_env("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", "24")
    PASSWORD_RESET_BASE_URL = os.getenv("PASSWORD_RESET_BASE_URL", "http://localhost:8001")
    
    # CORS Configuration
    # When allow_credentials=True, you cannot use allow_origins=["*"]
    # Must specify exact origins. Use comma-separated list in CORS_ORIGINS env var
    # Default includes common development and production origins
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    if cors_origins_env:
        # Parse comma-separated origins and strip whitespace
        CORS_ORIGINS = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    else:
        # Default origins for development and common production setups
        CORS_ORIGINS = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://136.111.4.62:3000",  # Common production IP
            "http://localhost:3210",  # LobeChat default
        ]
    
    # MCP (Model Context Protocol) Configuration
    # MCP providers are configured per-user via the API
    # No global MCP configuration needed
    
    # Google Calendar OAuth Configuration
    GOOGLE_CALENDAR_CLIENT_ID = os.getenv("GOOGLE_CALENDAR_CLIENT_ID", "")
    GOOGLE_CALENDAR_CLIENT_SECRET = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", "")
    # Note: Use legacy path (/google_calendar/) to match Google Cloud Console redirect URI
    GOOGLE_CALENDAR_REDIRECT_URI = os.getenv(
        "GOOGLE_CALENDAR_REDIRECT_URI",
        "http://localhost:8001/api/mcp/google_calendar/oauth/callback"
    )
    
    # Web Search Configuration
    # Tavily Search API (recommended - optimized for AI agents)
    # Get your API key at: https://tavily.com/
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    
    # Google Custom Search API (fallback option)
    # Requires: 1) Create Custom Search Engine at https://programmablesearchengine.google.com/
    #          2) Get API key from Google Cloud Console
    GOOGLE_CUSTOM_SEARCH_API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY", "")
    GOOGLE_CUSTOM_SEARCH_ENGINE_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID", "")
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        # At least one LLM provider must be configured
        has_provider = (
            cls.GOOGLE_API_KEY or 
            cls.OPENAI_API_KEY or 
            cls.ONPREMISE_API_BASE_URL or
            cls.OLLAMA_API_BASE_URL
        )
        
        if not has_provider:
            raise ValueError(
                "At least one LLM provider must be configured. "
                "Set GOOGLE_API_KEY, OPENAI_API_KEY, ONPREMISE_API_BASE_URL, or OLLAMA_API_BASE_URL"
            )
        
        return True

