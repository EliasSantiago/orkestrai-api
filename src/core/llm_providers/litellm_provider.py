"""LiteLLM provider for unified LLM access."""

import logging
import os
import base64
import json
import inspect
from typing import List, Optional, AsyncIterator, Dict, Any
from litellm import acompletion
from src.core.llm_provider import LLMProvider, LLMMessage, FilePart
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
        
        # Force direct Gemini API (not Vertex AI) for all Gemini models
        # This ensures we always use the direct API endpoint
        import os
        # Remove Vertex AI detection by ensuring these are not set during initialization
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            logger.info("GOOGLE_APPLICATION_CREDENTIALS detected - will be temporarily removed for Gemini API calls")
        
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
                # Latest models (2025)
                # Gemini 3 Pro - Preview version (according to official docs: gemini-3-pro-preview)
                "gemini/gemini-3-pro-preview",
                "gemini/gemini-3-pro",  # Alias for convenience (will map to preview)
                "gemini/gemini-2.5-pro",
                "gemini/gemini-2.5-flash",
                # Experimental models
                "gemini/gemini-2.0-flash-exp",
                "gemini/gemini-2.0-flash-thinking-exp",
                # Stable models
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
    
    def _convert_tools_to_litellm_format(self, tools: List) -> Optional[List[Dict[str, Any]]]:
        """
        Convert Python functions to LiteLLM/OpenAI function calling format.
        
        LiteLLM uses the same format as OpenAI for function calling.
        
        Args:
            tools: List of Python function objects
            
        Returns:
            List of tool definitions in OpenAI format, or None if no tools
        """
        if not tools:
            return None
        
        litellm_tools = []
        
        for tool in tools:
            if not callable(tool):
                continue
                
            # Get function name
            func_name = getattr(tool, '__name__', 'unknown')
            
            # Get description from docstring
            docstring = inspect.getdoc(tool) or ""
            # Extract first line or paragraph as description
            description = docstring.split('\n\n')[0].strip() if docstring else f"Tool: {func_name}"
            
            # Get function signature
            sig = inspect.signature(tool)
            parameters = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                # Skip user_id as it's injected automatically
                if param_name == 'user_id':
                    continue
                    
                param_info = {
                    "type": "string"  # Default type
                }
                
                # Try to infer type from annotation
                if param.annotation != inspect.Parameter.empty:
                    ann_str = str(param.annotation)
                    if 'int' in ann_str or 'Integer' in ann_str:
                        param_info["type"] = "integer"
                    elif 'float' in ann_str or 'Float' in ann_str:
                        param_info["type"] = "number"
                    elif 'bool' in ann_str or 'Boolean' in ann_str:
                        param_info["type"] = "boolean"
                    elif 'list' in ann_str.lower() or 'List' in ann_str or 'Array' in ann_str:
                        param_info["type"] = "array"
                        param_info["items"] = {"type": "string"}
                        if 'Dict' in ann_str or 'dict' in ann_str.lower():
                            param_info["items"] = {"type": "object"}
                        elif 'int' in ann_str:
                            param_info["items"] = {"type": "integer"}
                    elif 'dict' in ann_str.lower() or 'Dict' in ann_str or 'object' in ann_str.lower():
                        param_info["type"] = "object"
                        param_info["additionalProperties"] = True
                
                # Get description from docstring if available
                if docstring:
                    if "Args:" in docstring or "Arguments:" in docstring:
                        lines = docstring.split('\n')
                        in_args_section = False
                        for i, line in enumerate(lines):
                            line_stripped = line.strip()
                            if line_stripped.startswith("Args:") or line_stripped.startswith("Arguments:"):
                                in_args_section = True
                                continue
                            if in_args_section:
                                if line_stripped.startswith(f"{param_name}:") or line_stripped.startswith(f"{param_name} "):
                                    if ':' in line_stripped:
                                        desc = line_stripped.split(':', 1)[1].strip()
                                        if desc:
                                            param_info["description"] = desc
                                            break
                                    elif i + 1 < len(lines):
                                        next_line = lines[i + 1].strip()
                                        if next_line and not next_line.startswith(('Args:', 'Returns:', 'Example:')):
                                            param_info["description"] = next_line
                                            break
                            if line_stripped.startswith(("Returns:", "Example:", "Raises:")):
                                break
                
                # If no description found, create a default one
                if "description" not in param_info:
                    param_info["description"] = f"Parameter {param_name}"
                
                parameters[param_name] = param_info
                
                # Check if parameter is required
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
            
            # Build function schema
            function_schema = {
                "name": func_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                }
            }
            
            if required:
                function_schema["parameters"]["required"] = required
            
            litellm_tools.append({
                "type": "function",
                "function": function_schema
            })
        
        logger.info(f"🔧 Converted {len(litellm_tools)} tools to LiteLLM format: {[t['function']['name'] for t in litellm_tools]}")
        return litellm_tools if litellm_tools else None
    
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
        # Normalize model aliases (e.g., gemini-3-pro -> gemini-3-pro-preview)
        model_aliases = {
            "gemini/gemini-3-pro": "gemini/gemini-3-pro-preview",
        }
        normalized_model = model_aliases.get(model, model)
        
        # Direct match in supported models list (check both original and normalized)
        if model in self.supported_models or normalized_model in self.supported_models:
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
    
    def _convert_messages_to_litellm_format(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Convert LLMMessage objects to LiteLLM format.
        
        Args:
            messages: List of LLMMessage objects
            
        Returns:
            List of message dictionaries in LiteLLM format with file support
        """
        litellm_messages = []
        
        logger.info(f"🔄 Converting {len(messages)} messages to LiteLLM format...")
        
        for idx, msg in enumerate(messages):
            logger.info(f"📨 Message {idx+1}: role={msg.role}, has_content={bool(msg.content)}, has_files={bool(msg.files)}, files_count={len(msg.files) if msg.files else 0}")
            
            message_dict = {"role": msg.role}
            
            # Build content array (text + files)
            content_parts = []
            
            # Add text content
            if msg.content:
                content_parts.append({
                    "type": "text",
                    "text": msg.content
                })
                print(f"  ✅ Added user message text: {len(msg.content)} chars")
                print(f"     Preview: {msg.content[:200]}...")
                logger.info(f"  ✅ Added text content: {len(msg.content)} chars")
            
            # Add file content if present
            if msg.files:
                logger.info(f"  📎 Processing {len(msg.files)} file(s)...")
                for file_idx, file_part in enumerate(msg.files):
                    logger.info(f"    📄 File {file_idx+1}: {file_part.file_name} (type={file_part.type}, mime={file_part.mime_type}, data_len={len(file_part.data) if isinstance(file_part.data, str) else 'bytes'})")
                    
                    if file_part.type == "image" and file_part.mime_type and file_part.mime_type.startswith("image/"):
                        # For images that haven't been converted (OCR failed or not attempted)
                        # Use base64 data URL format for direct image viewing
                        image_url = f"data:{file_part.mime_type or 'image/png'};base64,{file_part.data}"
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        })
                        logger.info(f"    ✅ Added image as image_url (URL length: {len(image_url)})")
                    elif file_part.type == "text" or file_part.mime_type == "text/plain":
                        # For text files (including converted files from PDF, DOCX, etc.)
                        try:
                            text_content = base64.b64decode(file_part.data).decode('utf-8')
                            # IMPORTANTE: Incluir o texto do arquivo diretamente na mensagem
                            # Não adicionar como parte separada, mas concatenar com a mensagem do usuário
                            # Ou adicionar como parte separada mas de forma clara
                            file_text = f"\n\n=== CONTEÚDO DO ARQUIVO: {file_part.file_name} ===\n{text_content}\n=== FIM DO ARQUIVO ===\n"
                            content_parts.append({
                                "type": "text",
                                "text": file_text
                            })
                            print(f"    ✅ Added text file content: {len(text_content)} chars from {file_part.file_name}")
                            print(f"    📝 Text preview (first 300 chars): {text_content[:300]}...")
                            logger.info(f"    ✅ Added text file content: {len(text_content)} chars from {file_part.file_name}")
                            logger.info(f"    📝 Text preview (first 200 chars): {text_content[:200]}...")
                        except Exception as e:
                            print(f"    ⚠️ ERROR decoding file {file_part.file_name}: {e}")
                            logger.warning(f"    ⚠️ Could not decode file {file_part.file_name}: {e}")
                            import traceback
                            logger.warning(f"    Traceback: {traceback.format_exc()}")
                            # Fallback: mention the file
                            content_parts.append({
                                "type": "text",
                                "text": f"\n[File: {file_part.file_name} - Unable to read content: {str(e)}]"
                            })
                    else:
                        # For other file types, try to decode as text
                        try:
                            text_content = base64.b64decode(file_part.data).decode('utf-8')
                            file_text = f"\n[File: {file_part.file_name}]\n{text_content}"
                            content_parts.append({
                                "type": "text",
                                "text": file_text
                            })
                            logger.info(f"    ✅ Added file as text: {len(text_content)} chars")
                        except Exception as e:
                            logger.warning(f"    ⚠️ Could not decode file {file_part.file_name}: {e}")
                            # Fallback: mention the file
                            content_parts.append({
                                "type": "text",
                                "text": f"\n[File: {file_part.file_name} - Unable to read content]"
                            })
            else:
                logger.info(f"  ℹ️ No files in message {idx+1}")
            
            # Set content based on structure
            # IMPORTANTE: Se houver arquivos convertidos, sempre usar formato array
            # para garantir que o texto do arquivo seja incluído junto com a mensagem
            if len(content_parts) == 1 and content_parts[0]["type"] == "text" and not msg.files:
                # Simple text message (sem arquivos)
                message_dict["content"] = content_parts[0]["text"]
                logger.info(f"  ✅ Message {idx+1} formatted as simple text")
            else:
                # Multi-part message (text + files) - SEMPRE usar array quando houver arquivos
                message_dict["content"] = content_parts
                logger.info(f"  ✅ Message {idx+1} formatted as multi-part ({len(content_parts)} parts)")
                # Log detalhado do conteúdo
                for part_idx, part in enumerate(content_parts):
                    if part.get("type") == "text":
                        text_preview = part.get("text", "")[:200] + "..." if len(part.get("text", "")) > 200 else part.get("text", "")
                        logger.info(f"    Part {part_idx+1} (text): {len(part.get('text', ''))} chars - Preview: {text_preview}")
                    elif part.get("type") == "image_url":
                        logger.info(f"    Part {part_idx+1} (image): URL length {len(part.get('image_url', {}).get('url', ''))}")
            
            litellm_messages.append(message_dict)
        
        logger.info(f"✅ Converted {len(litellm_messages)} messages to LiteLLM format")
        return litellm_messages
    
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
            tools: Optional list of Python function objects to be converted to function calling format
            **kwargs: Additional LiteLLM parameters (temperature, max_tokens, etc.)
            
        Yields:
            Response chunks as strings
            
        Note:
            - Model name should include the provider prefix (e.g., "gemini/", "openai/")
            - If no prefix is provided, LiteLLM will try to infer the provider
            - Streaming is enabled by default
        """
        try:
            # Normalize model name (e.g., gemini-3-pro -> gemini-3-pro-preview)
            # IMPORTANT: gemini-3-pro is NOT a valid model name in the API
            # It must be either gemini-3-pro-preview (preview) or gemini-3-pro (stable, when available)
            # For now, we map gemini-3-pro to gemini-3-pro-preview since stable is not yet available
            model_aliases = {
                "gemini/gemini-3-pro": "gemini/gemini-3-pro-preview",
            }
            normalized_model = model_aliases.get(model, model)
            
            # Log model normalization
            if normalized_model != model:
                logger.info(f"🔄 Model normalized: {model} → {normalized_model}")
                print(f"🔄 Modelo normalizado: {model} → {normalized_model}")
            
            # Convert messages to LiteLLM format
            logger.info(f"🔄 Converting messages for model: {normalized_model}")
            litellm_messages = self._convert_messages_to_litellm_format(messages)
            
            # Log final message structure
            print(f"\n📤 FINAL LITELLM MESSAGES STRUCTURE:")
            logger.info(f"📤 Final LiteLLM messages structure:")
            for idx, msg in enumerate(litellm_messages):
                content_info = "text" if isinstance(msg.get("content"), str) else f"array({len(msg.get('content', []))} parts)"
                print(f"  Message {idx+1}: role={msg.get('role')}, content_type={content_info}")
                logger.info(f"  Message {idx+1}: role={msg.get('role')}, content_type={content_info}")
                if isinstance(msg.get("content"), list):
                    print(f"    Total parts: {len(msg.get('content', []))}")
                    for part_idx, part in enumerate(msg.get("content", [])):
                        if part.get("type") == "image_url":
                            url_preview = part.get("image_url", {}).get("url", "")[:100] + "..." if len(part.get("image_url", {}).get("url", "")) > 100 else part.get("image_url", {}).get("url", "")
                            print(f"    Part {part_idx+1}: type=image_url, url_length={len(part.get('image_url', {}).get('url', ''))}")
                            logger.info(f"    Part {part_idx+1}: type=image_url, url_length={len(part.get('image_url', {}).get('url', ''))}, url_preview={url_preview}")
                        elif part.get("type") == "text":
                            text_content = part.get("text", "")
                            text_preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                            print(f"    Part {part_idx+1}: type=text, text_length={len(text_content)}")
                            print(f"      Preview: {text_preview}")
                            logger.info(f"    Part {part_idx+1}: type=text, text_length={len(text_content)}, text_preview={text_preview}")
                elif isinstance(msg.get("content"), str):
                    text_content = msg.get("content", "")
                    print(f"    Text content: {len(text_content)} chars")
                    print(f"      Preview: {text_content[:200]}...")
            
            # Convert tools to LiteLLM format (OpenAI function calling format)
            litellm_tools = None
            if tools:
                litellm_tools = self._convert_tools_to_litellm_format(tools)
                if litellm_tools:
                    logger.info(f"🔧 Passing {len(litellm_tools)} tools to LiteLLM for function calling")
            
            # Prepare LiteLLM parameters
            litellm_params = {
                "model": normalized_model,
                "messages": litellm_messages,
                "stream": True,  # Always stream for consistent behavior
            }
            
            # Add tools if available
            if litellm_tools:
                litellm_params["tools"] = litellm_tools
                # For Gemini models, we might need tool_choice
                if normalized_model.startswith("gemini/"):
                    # Let Gemini decide when to use tools (auto)
                    litellm_params["tool_choice"] = "auto"
            
            logger.info(f"🚀 Calling LiteLLM with model={normalized_model}, messages={len(litellm_messages)}")
            logger.info(f"📋 LiteLLM params: {json.dumps({k: v if k != 'messages' else f'[{len(v)} messages]' for k, v in litellm_params.items()}, indent=2)}")
            
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
            import os
            vertex_creds_key = "GOOGLE_APPLICATION_CREDENTIALS"
            original_vertex_env_vars = {}
            vertex_creds_removed = False
            
            if normalized_model.startswith("gemini/"):
                litellm_params["api_key"] = Config.GOOGLE_API_KEY
                
                # ALWAYS force direct Gemini API (not Vertex AI)
                # According to official docs: https://ai.google.dev/gemini-api/docs/pricing#gemini-3-pro-preview
                # gemini-3-pro-preview is ONLY available via direct Gemini API (Google AI Studio)
                # NOT available via Vertex AI
                # Remove ALL Vertex AI credentials to ensure we use direct API
                vertex_env_var_names = [
                    "GOOGLE_APPLICATION_CREDENTIALS",
                    "GOOGLE_CLOUD_PROJECT",
                    "GOOGLE_CLOUD_REGION",
                    "GCLOUD_PROJECT",
                ]
                
                # Save original values and temporarily unset ALL Vertex AI environment variables
                for var_name in vertex_env_var_names:
                    if var_name in os.environ:
                        original_vertex_env_vars[var_name] = os.environ[var_name]
                        del os.environ[var_name]
                        vertex_creds_removed = True
                        logger.info(f"Temporarily unset {var_name} to force direct Gemini API")
                
                # CRITICAL: Force direct Gemini API by explicitly setting api_base
                # For gemini-3-pro-preview and gemini-3-pro, MUST use direct API (not Vertex AI)
                # LiteLLM will use Vertex AI if it detects credentials, even with gemini/ prefix
                # Solution: Explicitly set api_base to direct Gemini API endpoint for ALL Gemini models
                # This ensures we always use the direct API, not Vertex AI
                if "gemini-3-pro-preview" in normalized_model or "gemini-3-pro" in normalized_model:
                    # Force direct Gemini API endpoint (Google AI Studio)
                    # This ensures we use https://generativelanguage.googleapis.com instead of Vertex AI
                    litellm_params["api_base"] = "https://generativelanguage.googleapis.com"
                    logger.info(f"🔧 Forcing direct Gemini API for {normalized_model} (not Vertex AI)")
                    print(f"🔧 Forçando API direta do Gemini para {normalized_model} (não Vertex AI)")
                else:
                    # For other Gemini models, also force direct API to avoid Vertex AI issues
                    # This prevents LiteLLM from trying Vertex AI first
                    litellm_params["api_base"] = "https://generativelanguage.googleapis.com"
                    logger.info(f"🔧 Using direct Gemini API for {normalized_model} (not Vertex AI)")
                
                # Ensure we're using the direct Gemini API endpoint
                # The gemini/ prefix with api_base set to direct API ensures we don't use Vertex AI
                
                # For Gemini 3 Pro, add thinking_level parameter (default: high)
                # According to docs: https://ai.google.dev/gemini-api/docs/gemini-3
                if "gemini-3-pro" in normalized_model:
                    # thinking_level: low (fast), high (deep reasoning, default)
                    # Can be passed via kwargs if needed, default is high
                    if "thinking_level" not in kwargs:
                        # Use high by default for Gemini 3 Pro (better reasoning)
                        litellm_params["thinking_level"] = "high"
                        logger.info(f"Using thinking_level=high for {normalized_model} (default for Gemini 3 Pro)")
                    else:
                        litellm_params["thinking_level"] = kwargs["thinking_level"]
                
                logger.info(f"✅ Configured to use direct Gemini API (not Vertex AI) for {normalized_model}")
                logger.info(f"   API Base: {litellm_params.get('api_base', 'default (direct API)')}")
                print(f"🔧 Configurado para usar API direta do Gemini (não Vertex AI) para {normalized_model}")
            elif model.startswith("openai/"):
                litellm_params["api_key"] = Config.OPENAI_API_KEY
            elif model.startswith("anthropic/"):
                litellm_params["api_key"] = Config.LITELLM_ANTHROPIC_API_KEY
            elif model.startswith("ollama/"):
                litellm_params["api_base"] = Config.OLLAMA_API_BASE_URL
            
            # Configure retry settings
            litellm_params["num_retries"] = Config.LITELLM_NUM_RETRIES
            litellm_params["timeout"] = Config.LITELLM_REQUEST_TIMEOUT
            
            logger.info(f"Making LiteLLM request to model: {normalized_model} (original: {model})")
            if normalized_model != model:
                print(f"🔄 Modelo normalizado: {model} → {normalized_model}")
            print(f"🚀 Iniciando requisição ao modelo LLM: {normalized_model}")
            
            # Create tool map for execution
            tool_map = {}
            if tools:
                for tool in tools:
                    if callable(tool):
                        tool_map[getattr(tool, '__name__', 'unknown')] = tool
            
            try:
                # For function calling, use non-streaming first to handle tool calls properly
                # Then we can stream the final response
                if litellm_tools and tool_map:
                    logger.info(f"🔧 Using non-streaming mode for function calling with {len(litellm_tools)} tools")
                    # Make non-streaming request to handle tool calls
                    non_stream_params = {**litellm_params, "stream": False}
                    response = await acompletion(**non_stream_params)
                    
                    # Handle function calling loop
                    max_iterations = 5
                    iteration = 0
                    
                    while iteration < max_iterations:
                        choice = response.choices[0] if hasattr(response, 'choices') and response.choices else None
                        if not choice:
                            break
                            
                        message = choice.message if hasattr(choice, 'message') else None
                        if not message:
                            break
                        
                        # Check if model wants to call a function
                        tool_calls = getattr(message, 'tool_calls', None) or getattr(message, 'function_calls', None)
                        if tool_calls:
                            logger.info(f"🔧 Tool calls detected: {len(tool_calls)} calls")
                            
                            # Add assistant message with tool calls
                            litellm_messages.append({
                                "role": "assistant",
                                "content": getattr(message, 'content', None),
                                "tool_calls": [
                                    {
                                        "id": getattr(tc, 'id', f"call_{i}"),
                                        "type": getattr(tc, 'type', 'function'),
                                        "function": {
                                            "name": getattr(tc.function, 'name', '') if hasattr(tc, 'function') else getattr(tc, 'name', ''),
                                            "arguments": getattr(tc.function, 'arguments', '') if hasattr(tc, 'function') else getattr(tc, 'arguments', '{}')
                                        }
                                    }
                                    for i, tc in enumerate(tool_calls)
                                ]
                            })
                            
                            # Execute tool calls
                            for tool_call in tool_calls:
                                func_name = getattr(tool_call.function, 'name', '') if hasattr(tool_call, 'function') else getattr(tool_call, 'name', '')
                                func_args_str = getattr(tool_call.function, 'arguments', '{}') if hasattr(tool_call, 'function') else getattr(tool_call, 'arguments', '{}')
                                tool_call_id = getattr(tool_call, 'id', f"call_{iteration}")
                                
                                if func_name in tool_map:
                                    try:
                                        func_args = json.loads(func_args_str) if isinstance(func_args_str, str) else func_args_str
                                        tool_func = tool_map[func_name]
                                        logger.info(f"🔧 Executing tool {func_name} with args: {func_args}")
                                        
                                        # Execute tool
                                        import concurrent.futures
                                        import threading
                                        
                                        tool_result = None
                                        tool_exception = None
                                        
                                        def execute_tool():
                                            nonlocal tool_result, tool_exception
                                            try:
                                                tool_result = tool_func(**func_args)
                                            except Exception as e:
                                                tool_exception = e
                                        
                                        thread = threading.Thread(target=execute_tool)
                                        thread.start()
                                        thread.join(timeout=30)
                                        
                                        if tool_exception:
                                            raise tool_exception
                                        if thread.is_alive():
                                            raise TimeoutError("Tool execution timed out")
                                        
                                        # Convert result to string
                                        if isinstance(tool_result, dict):
                                            tool_result_str = json.dumps(tool_result, ensure_ascii=False, indent=2)
                                        else:
                                            tool_result_str = str(tool_result)
                                        
                                        logger.info(f"✅ Tool {func_name} result: {tool_result_str[:200]}...")
                                        
                                        # Add tool result to messages
                                        litellm_messages.append({
                                            "role": "tool",
                                            "tool_call_id": tool_call_id,
                                            "content": tool_result_str
                                        })
                                    except Exception as e:
                                        logger.error(f"❌ Error executing tool {func_name}: {e}", exc_info=True)
                                        error_response = json.dumps({
                                            "status": "error",
                                            "error": str(e),
                                            "tool": func_name
                                        }, ensure_ascii=False)
                                        litellm_messages.append({
                                            "role": "tool",
                                            "tool_call_id": tool_call_id,
                                            "content": error_response
                                        })
                                else:
                                    logger.warning(f"⚠️ Tool {func_name} not found in tool_map")
                                    litellm_messages.append({
                                        "role": "tool",
                                        "tool_call_id": tool_call_id,
                                        "content": json.dumps({"status": "error", "error": f"Tool {func_name} not found"}, ensure_ascii=False)
                                    })
                            
                            # Make another call with tool results
                            iteration += 1
                            non_stream_params = {
                                "model": normalized_model,
                                "messages": litellm_messages,
                                "tools": litellm_tools,
                                "stream": False,
                            }
                            if normalized_model.startswith("gemini/"):
                                non_stream_params["api_key"] = Config.GOOGLE_API_KEY
                                # Force direct Gemini API for all Gemini models (not Vertex AI)
                                non_stream_params["api_base"] = "https://generativelanguage.googleapis.com"
                                if "gemini-3-pro" in normalized_model:
                                    non_stream_params["thinking_level"] = "high"
                            response = await acompletion(**non_stream_params)
                        else:
                            # No more tool calls, break and stream the final response
                            break
                    
                    # Now stream the final response
                    if hasattr(response, 'choices') and response.choices:
                        final_message = response.choices[0].message
                        final_content = getattr(final_message, 'content', '') or ''
                        if final_content:
                            # Yield the final response character by character to simulate streaming
                            for char in final_content:
                                yield char
                            return
                
                # No tools or no tool calls - use streaming
                response = await acompletion(**litellm_params)
                print(f"✅ Resposta recebida do modelo: {normalized_model}")
            finally:
                # Restore Vertex AI credentials if they were temporarily removed
                if normalized_model.startswith("gemini/") and vertex_creds_removed and original_vertex_env_vars:
                    for var_name, var_value in original_vertex_env_vars.items():
                        os.environ[var_name] = var_value
                        logger.debug(f"Restored {var_name}")
            
            # Stream the response
            chunk_count = 0
            async for chunk in response:
                # Extract text from the chunk
                # LiteLLM returns chunks in OpenAI format
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
                        
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error in LiteLLM chat: {error_str}")
            
            # Check if it's a quota/rate limit error (429)
            is_quota_error = (
                "429" in error_str or 
                "rate limit" in error_str.lower() or
                "quota" in error_str.lower() or
                "resource_exhausted" in error_str.lower() or
                "free_tier" in error_str.lower()
            )
            
            # Check if it's a model not found error (404)
            is_model_not_found = (
                "404" in error_str or
                "not found" in error_str.lower() or
                "does not exist" in error_str.lower() or
                "invalid model" in error_str.lower()
            )
            
            # Check if it's a Vertex AI error (should use direct API instead)
            is_vertex_ai_error = (
                "vertex_ai" in error_str.lower() or 
                "v1beta" in error_str.lower()
            )
            
            # If it's a quota error or model not found, suggest fallback
            if (is_quota_error or is_model_not_found or is_vertex_ai_error) and normalized_model.startswith("gemini/"):
                fallback_models = [
                    "gemini/gemini-2.5-pro",
                    "gemini/gemini-2.5-flash",
                    "gemini/gemini-1.5-pro-latest",
                    "gemini/gemini-1.5-flash"
                ]
                
                if is_quota_error:
                    # Check if it's specifically a free tier quota error
                    is_free_tier_error = "free_tier" in error_str.lower() or "limit: 0" in error_str
                    
                    if is_free_tier_error and "gemini-3-pro" in normalized_model:
                        error_msg = (
                            f"Modelo '{normalized_model}' não está disponível no tier gratuito.\n"
                            f"O Gemini 3 Pro requer um plano pago da Google.\n"
                            f"Mais informações: https://ai.google.dev/gemini-api/docs/rate-limits\n\n"
                            f"O sistema tentará automaticamente modelos alternativos:\n"
                            + "\n".join(f"  - {m}" for m in fallback_models)
                        )
                    else:
                        error_msg = (
                            f"Modelo '{normalized_model}' excedeu a quota/limite de taxa.\n"
                            f"Erro: {error_str[:500]}\n\n"
                            f"Modelos alternativos disponíveis:\n"
                            + "\n".join(f"  - {m}" for m in fallback_models)
                        )
                elif is_vertex_ai_error:
                    error_msg = (
                        f"Erro ao acessar modelo '{normalized_model}' via Vertex AI.\n"
                        f"Tentando usar API direta do Gemini...\n"
                        f"Erro: {error_str[:500]}\n\n"
                        f"Modelos alternativos disponíveis:\n"
                        + "\n".join(f"  - {m}" for m in fallback_models)
                    )
                else:
                    error_msg = (
                        f"Modelo '{normalized_model}' não está disponível ou não foi encontrado.\n"
                        f"Erro: {error_str[:500]}\n\n"
                        f"Modelos alternativos disponíveis:\n"
                        + "\n".join(f"  - {m}" for m in fallback_models)
                    )
                
                logger.error(error_msg)
                raise ValueError(error_msg) from e
            
            # Check if it's an OpenAI API key error
            if model.startswith("openai/") and ("api key" in error_str.lower() or "authentication" in error_str.lower() or "unauthorized" in error_str.lower()):
                error_msg = (
                    f"Erro de autenticação OpenAI para o modelo '{model}'.\n"
                    f"Verifique se OPENAI_API_KEY está configurada corretamente no arquivo .env.\n"
                    f"Erro original: {error_str}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg) from e
            
            # Check if it's an OpenAI model not found error
            if model.startswith("openai/") and ("not found" in error_str.lower() or "does not exist" in error_str.lower() or "invalid model" in error_str.lower()):
                fallback_models = [
                    "openai/gpt-4o",
                    "openai/gpt-4o-mini",
                    "openai/gpt-4-turbo",
                    "openai/gpt-3.5-turbo"
                ]
                error_msg = (
                    f"Modelo OpenAI '{model}' não encontrado ou não disponível.\n"
                    f"Erro: {error_str}\n\n"
                    f"Modelos alternativos disponíveis:\n"
                    + "\n".join(f"  - {m}" for m in fallback_models)
                )
                logger.error(error_msg)
                raise ValueError(error_msg) from e
            
            # Provide helpful error message for other errors
            error_message = f"LiteLLM Error: {error_str}"
            if "API key" in error_str or "authentication" in error_str.lower():
                provider = model.split("/")[0] if "/" in model else "unknown"
                error_message += f"\n\nVerifique se a chave de API do {provider} está configurada corretamente no arquivo .env."
            elif "timeout" in error_str:
                error_message += "\n\nA requisição expirou. Tente aumentar LITELLM_REQUEST_TIMEOUT."
            elif "model" in error_str.lower() or "not found" in error_str.lower():
                error_message += f"\n\nModelo '{model}' pode não estar disponível. Verifique o nome do modelo e seu acesso à API."
            
            raise ValueError(error_message) from e


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

