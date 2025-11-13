"""Factory for creating LLM providers.

Architecture: LiteLLM as the ONLY unified proxy.
All models (Gemini, OpenAI, Claude, Ollama, etc.) are routed through LiteLLM.
"""

from typing import Optional, List
from src.core.llm_provider import LLMProvider
from src.core.llm_providers.litellm_provider import LiteLLMProvider


class LLMFactory:
    """Factory to create appropriate LLM provider based on model name."""
    
    _providers: Optional[List[LLMProvider]] = None
    
    @classmethod
    def _get_providers(cls) -> List[LLMProvider]:
        """
        Get list of available providers.
        
        ARCHITECTURE CHANGE (2025-11-12):
        ===================================
        We use LiteLLM as the ONLY unified proxy for all LLM providers.
        
        LiteLLM provides:
        - Unified interface for 100+ LLM providers (Gemini, OpenAI, Claude, Ollama, etc.)
        - Automatic retries and fallbacks
        - Load balancing
        - Cost tracking
        - Observability
        
        Requirements:
        - Set LITELLM_ENABLED=true in .env
        - Configure API keys (GOOGLE_API_KEY, OPENAI_API_KEY, etc.)
        - Use model format: "provider/model" (e.g., "gemini/gemini-2.0-flash-exp")
        
        Documentation: docs/arquitetura/litellm/README.md
        """
        if cls._providers is None:
            cls._providers = []
            
            # LiteLLM - ÚNICO proxy unificado para todos os providers
            litellm_provider = LiteLLMProvider()
            cls._providers.append(litellm_provider)
            
            print("✓ LiteLLM provider initialized (unified LLM gateway)")
            print("  → All models will be routed through LiteLLM")
            print("  → Supported: Gemini, OpenAI, Claude, Ollama, Azure, and 100+ more")
            print("  → Documentation: docs/arquitetura/litellm/README.md")
        
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

