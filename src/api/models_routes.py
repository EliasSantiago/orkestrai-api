"""API routes for listing supported LLM models."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/models", tags=["models"])

# Top 3 models for each provider (best models prioritized)
# Based on OpenAI and Gemini official model listings
# These models are always returned by the API, regardless of availability
TOP_MODELS = {
    "openai": [
        "openai/gpt-4o",          # Best for coding and agent tasks (latest GPT-4)
        "openai/gpt-4o-mini",     # Faster and more economical version
        "openai/gpt-4-turbo",     # High performance alternative
    ],
    "gemini": [
        "gemini/gemini-3-pro-preview",  # Latest Pro model (Preview - testing phase)
        "gemini/gemini-2.5-pro",         # Pro version with advanced capabilities
        "gemini/gemini-2.5-flash",       # Fast and efficient version
    ],
}

# Fallback models when the preferred models are not available
# Maps preferred models to fallback models that actually exist
MODEL_FALLBACKS = {
    # OpenAI fallbacks
    "openai/gpt-4o": ["openai/gpt-4-turbo", "openai/gpt-4", "openai/gpt-3.5-turbo"],
    "openai/gpt-4o-mini": ["openai/gpt-4o", "openai/gpt-3.5-turbo"],
    "openai/gpt-4-turbo": ["openai/gpt-4o", "openai/gpt-4", "openai/gpt-3.5-turbo"],
    
    # Gemini fallbacks (if newer models don't exist, use older ones)
    "gemini/gemini-3-pro-preview": ["gemini/gemini-2.5-pro", "gemini/gemini-2.5-flash", "gemini/gemini-1.5-pro-latest"],
    "gemini/gemini-2.5-pro": ["gemini/gemini-2.5-flash", "gemini/gemini-1.5-pro-latest", "gemini/gemini-1.5-pro"],
    "gemini/gemini-2.5-flash": ["gemini/gemini-2.0-flash-exp", "gemini/gemini-1.5-flash", "gemini/gemini-1.5-pro"],
    "gemini/gemini-1.5-pro-latest": ["gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash", "gemini/gemini-2.5-flash"],
}


@router.get("")
async def list_supported_models():
    """
    List top 3 LLM models for OpenAI and Gemini providers.
    
    Returns only the best models from OpenAI and Gemini, excluding other providers
    like Ollama, Anthropic, etc.
    
    Always returns the models specified in TOP_MODELS, regardless of availability.
    
    Returns a dictionary mapping provider names to lists of top 3 models.
    """
    # Always return the top models specified in TOP_MODELS
    # These are the official recommended models from OpenAI and Gemini
    filtered_providers = {
        "openai": TOP_MODELS["openai"],
        "gemini": TOP_MODELS["gemini"],
    }
    
    return {
        "providers": filtered_providers,
        "message": "Top 3 models from OpenAI and Gemini providers."
    }

