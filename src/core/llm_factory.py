"""Factory for creating LLM providers.

Architecture: 
- Google ADK (direct) for Gemini models
- LiteLLM for other providers (OpenAI, Claude, Ollama, etc.)
"""

from typing import Optional, List
from src.core.llm_provider import LLMProvider
from src.core.llm_providers.adk_provider import ADKProvider
from src.core.llm_providers.litellm_provider import LiteLLMProvider
from src.config import Config


class LLMFactory:
    """Factory to create appropriate LLM provider based on model name."""
    
    _providers: Optional[List[LLMProvider]] = None
    
    @classmethod
    def _get_providers(cls) -> List[LLMProvider]:
        """
        Get list of available providers.
        
        ARCHITECTURE (2025-11-27):
        ===========================
        - Google ADK (direct) for Gemini models - uses Google ADK SDK directly
        - LiteLLM for other providers (OpenAI, Claude, Ollama, etc.)
        
        This ensures:
        - Gemini models use native Google ADK (better compatibility, no LiteLLM issues)
        - Other models use LiteLLM (unified interface for 100+ providers)
        - Automatic retries and fallbacks via LiteLLM for non-Gemini models
        - Cost tracking and observability
        
        Requirements:
        - Set LITELLM_ENABLED=true in .env (for non-Gemini models)
        - Configure API keys (GOOGLE_API_KEY, OPENAI_API_KEY, etc.)
        - Gemini models: use format "gemini/gemini-3-pro-preview" or just "gemini-3-pro-preview"
        - Other models: use format "provider/model" (e.g., "openai/gpt-4o")
        
        Documentation: docs/arquitetura/litellm/README.md
        """
        if cls._providers is None:
            cls._providers = []
            
            # Google ADK - Direct provider for Gemini models (priority)
            # This ensures Gemini models use native Google ADK SDK, avoiding LiteLLM issues
            adk_provider = ADKProvider()
            cls._providers.append(adk_provider)
            print("✓ Google ADK provider initialized (direct Gemini SDK)")
            print("  → Gemini models will use Google ADK directly")
            print("  → Supported: gemini-3-pro-preview, gemini-2.5-pro, gemini-2.5-flash, etc.")
            
            # LiteLLM - For other providers (OpenAI, Claude, Ollama, etc.)
            if Config.LITELLM_ENABLED:
                litellm_provider = LiteLLMProvider()
                cls._providers.append(litellm_provider)
                print("✓ LiteLLM provider initialized (for non-Gemini models)")
                print("  → Other models (OpenAI, Claude, Ollama) will be routed through LiteLLM")
                print("  → Supported: OpenAI, Claude, Ollama, Azure, and 100+ more")
            else:
                print("⚠ LiteLLM is disabled - only Gemini models will work")
        
        return cls._providers
    
    @classmethod
    def get_provider(cls, model: str) -> Optional[LLMProvider]:
        """
        Get the appropriate provider for a given model.
        
        Args:
            model: Model name (e.g., "gpt-4o", "gemini-2.0-flash-exp", "local-llama-2")
            
        Returns:
            LLMProvider instance or None if no provider supports the model
        """
        for provider in cls._get_providers():
            if provider.supports_model(model):
                return provider
        return None
    
    @classmethod
    def is_model_supported(cls, model: str) -> bool:
        """Check if a model is supported by any provider."""
        return cls.get_provider(model) is not None
    
    @classmethod
    def get_all_supported_models(cls) -> dict:
        """
        Get all supported models grouped by provider.
        
        Returns:
            Dictionary mapping provider names to lists of supported models
        """
        models = {}
        for provider in cls._get_providers():
            provider_name = provider.__class__.__name__.replace("Provider", "")
            models[provider_name] = provider.get_supported_models()
        return models
    
    @classmethod
    def reset(cls):
        """Reset the providers cache (useful for testing or reconfiguration)."""
        cls._providers = None

