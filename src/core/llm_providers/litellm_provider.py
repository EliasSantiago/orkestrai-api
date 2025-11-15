"""LiteLLM provider for unified LLM access."""

import logging
import os
from typing import List, Optional, AsyncIterator, Dict, Any
from litellm import acompletion
from src.core.llm_provider import LLMProvider, LLMMessage
from src.config import Config

logger = logging.getLogger(__name__)


class LiteLLMProvider(LLMProvider):
    """
    LiteLLM provider for unified access to 100+ LLM providers.
    
    This provider uses LiteLLM to provide a unified interface to multiple LLM providers
    including OpenAI, Anthropic, Google (Gemini), Ollama, and many more.
    
    Features:
    - Unified interface across all providers
    - Automatic retries and fallbacks
    - Cost tracking
    - Load balancing
    - Support for streaming responses
    
    Documentation: https://docs.litellm.ai/docs/
    """
    
    def __init__(self):
        """Initialize LiteLLM provider."""
        # Check if LiteLLM is enabled
        if not Config.LITELLM_ENABLED:
            raise ValueError("LiteLLM is not enabled. Set LITELLM_ENABLED=true in .env")
        
        # Configure LiteLLM settings
        import litellm
        import ssl
        
        # Set verbose mode for debugging (optional)
        litellm.set_verbose = Config.LITELLM_VERBOSE
        
        # Configure drop_params - ignore unsupported parameters instead of failing
        litellm.drop_params = True
        
        # Configure SSL verification for environments with self-signed certificates
        if not Config.VERIFY_SSL:
            logger.warning("⚠️  SSL verification is DISABLED. This is insecure and should only be used in development!")
            # Disable SSL verification for OpenAI client (used by LiteLLM)
            import httpx
            
            # Create custom SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Configure LiteLLM to use custom SSL context
            # This affects the underlying httpx client
            litellm.ssl_verify = False
        
        # Supported models - this is a broad list as LiteLLM supports 100+ providers
        # We define the most common ones here
        self.supported_models = self._get_supported_models()
        
        logger.info(f"✓ LiteLLM provider initialized with {len(self.supported_models)} models")
    
    def _get_supported_models(self) -> List[str]:
        """
        Get list of supported models based on configured API keys.
        
        Returns:
            List of supported model names
        """
        models = []
        
        # Google Gemini models (if API key is configured)
        if Config.GOOGLE_API_KEY:
            models.extend([
                "gemini/gemini-2.5-flash",
                "gemini/gemini-2.0-flash-exp",
                "gemini/gemini-2.0-flash-thinking-exp",
                "gemini/gemini-1.5-pro",
                "gemini/gemini-1.5-pro-latest",
                "gemini/gemini-1.5-flash",
                "gemini/gemini-1.5-flash-8b",
                "gemini/gemini-1.0-pro",
            ])
        
        # OpenAI models (if API key is configured)
        if Config.OPENAI_API_KEY:
            models.extend([
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "openai/gpt-4-turbo",
                "openai/gpt-4",
                "openai/gpt-3.5-turbo",
            ])
        
        # Ollama models (if base URL is configured)
        if Config.OLLAMA_API_BASE_URL:
            models.extend([
                "ollama/llama2",
                "ollama/llama3",
                "ollama/llama3.1",
                "ollama/mistral",
                "ollama/mixtral",
                "ollama/codellama",
                "ollama/gemma",
                "ollama/gemma2",
                "ollama/phi",
                "ollama/phi3",
                "ollama/qwen",
                "ollama/deepseek-coder",
            ])
        
        # Anthropic models (if API key is configured)
        if Config.LITELLM_ANTHROPIC_API_KEY:
            models.extend([
                "anthropic/claude-3-opus-20240229",
                "anthropic/claude-3-sonnet-20240229",
                "anthropic/claude-3-haiku-20240307",
                "anthropic/claude-2.1",
                "anthropic/claude-2",
            ])
        
        return models
    
    def supports_model(self, model: str) -> bool:
        """
        Check if this provider supports the given model.
        
        LiteLLM supports a wide range of models, so we use a flexible matching approach:
        1. Check if model is in our predefined list
        2. Check if model starts with a known provider prefix
        3. Allow any model if LiteLLM is configured (fallback)
        
        Args:
            model: Model name to check
            
        Returns:
            True if model is supported, False otherwise
        """
        # Direct match in supported models list
        if model in self.supported_models:
            return True
        
        # Check for provider prefixes
        provider_prefixes = [
            "gemini/", "openai/", "anthropic/", "ollama/", 
            "azure/", "huggingface/", "cohere/", "replicate/",
            "bedrock/", "vertex_ai/", "palm/", "together_ai/",
            "openrouter/", "ai21/", "nlp_cloud/", "aleph_alpha/",
            "baseten/", "vllm/", "xinference/", "mistral/",
            "deepinfra/", "perplexity/", "groq/", "anyscale/",
            "deepseek/", "sambanova/", "fireworks_ai/", "voyage/"
        ]
        
        for prefix in provider_prefixes:
            if model.startswith(prefix):
                return True
        
        # If model doesn't have a prefix but matches a pattern, allow it
        # This handles cases like "gpt-4o" -> "openai/gpt-4o"
        return False
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported model names."""
        return self.supported_models.copy()
    
    def _convert_messages_to_litellm_format(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """
        Convert LLMMessage objects to LiteLLM format.
        
        Args:
            messages: List of LLMMessage objects
            
        Returns:
            List of message dictionaries in LiteLLM format
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Chat with the LLM using LiteLLM.
        
        Args:
            messages: List of messages in the conversation
            model: Model name to use (e.g., "gemini/gemini-2.0-flash-exp", "openai/gpt-4o")
            tools: Optional list of tools/functions (not yet implemented)
            **kwargs: Additional LiteLLM parameters (temperature, max_tokens, etc.)
            
        Yields:
            Response chunks as strings
            
        Note:
            - Model name should include the provider prefix (e.g., "gemini/", "openai/")
            - If no prefix is provided, LiteLLM will try to infer the provider
            - Streaming is enabled by default
        """
        try:
            # Convert messages to LiteLLM format
            litellm_messages = self._convert_messages_to_litellm_format(messages)
            
            # Prepare LiteLLM parameters
            litellm_params = {
                "model": model,
                "messages": litellm_messages,
                "stream": True,  # Always stream for consistent behavior
            }
            
            # Add optional parameters
            if "temperature" in kwargs:
                litellm_params["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                litellm_params["max_tokens"] = kwargs["max_tokens"]
            if "top_p" in kwargs:
                litellm_params["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                litellm_params["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                litellm_params["presence_penalty"] = kwargs["presence_penalty"]
            
            # Configure API keys based on model provider
            if model.startswith("gemini/"):
                litellm_params["api_key"] = Config.GOOGLE_API_KEY
            elif model.startswith("openai/"):
                litellm_params["api_key"] = Config.OPENAI_API_KEY
            elif model.startswith("anthropic/"):
                litellm_params["api_key"] = Config.LITELLM_ANTHROPIC_API_KEY
            elif model.startswith("ollama/"):
                litellm_params["api_base"] = Config.OLLAMA_API_BASE_URL
            
            # Configure retry settings
            litellm_params["num_retries"] = Config.LITELLM_NUM_RETRIES
            litellm_params["timeout"] = Config.LITELLM_REQUEST_TIMEOUT
            
            logger.info(f"Making LiteLLM request to model: {model}")
            
            # Make streaming request to LiteLLM
            response = await acompletion(**litellm_params)
            
            # Stream the response
            async for chunk in response:
                # Extract text from the chunk
                # LiteLLM returns chunks in OpenAI format
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"Error in LiteLLM chat: {str(e)}")
            # Provide helpful error message
            error_message = f"LiteLLM Error: {str(e)}"
            if "API key" in str(e):
                error_message += "\n\nPlease check your API keys in the .env file."
            elif "timeout" in str(e):
                error_message += "\n\nThe request timed out. Try increasing LITELLM_REQUEST_TIMEOUT."
            elif "model" in str(e).lower():
                error_message += f"\n\nModel '{model}' may not be available. Check the model name and your API access."
            
            yield error_message
            raise


# Utility function to list all available LiteLLM models
def list_litellm_models() -> Dict[str, List[str]]:
    """
    List all available LiteLLM models grouped by provider.
    
    Returns:
        Dictionary mapping provider names to lists of available models
    """
    models = {}
    
    if Config.GOOGLE_API_KEY:
        models["Google Gemini"] = [
            "gemini/gemini-2.5-flash",
            "gemini/gemini-2.0-flash-exp",
            "gemini/gemini-1.5-pro",
            "gemini/gemini-1.5-flash",
        ]
    
    if Config.OPENAI_API_KEY:
        models["OpenAI"] = [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
        ]
    
    if Config.OLLAMA_API_BASE_URL:
        models["Ollama (Local)"] = [
            "ollama/llama2",
            "ollama/llama3",
            "ollama/mistral",
            "ollama/codellama",
        ]
    
    if Config.LITELLM_ANTHROPIC_API_KEY:
        models["Anthropic"] = [
            "anthropic/claude-3-opus-20240229",
            "anthropic/claude-3-sonnet-20240229",
            "anthropic/claude-3-haiku-20240307",
        ]
    
    return models

