"""On-premise LLM provider (OpenAI-compatible API)."""

import os
from typing import List, Optional, AsyncIterator
import httpx
from src.core.llm_provider import LLMProvider, LLMMessage
from src.config import Config


class OnPremiseProvider(LLMProvider):
    """On-premise LLM provider for locally hosted models (OpenAI-compatible API)."""
    
    def __init__(self):
        # Get on-premise API configuration
        self.base_url = Config.ONPREMISE_API_BASE_URL
        self.chat_endpoint = Config.ONPREMISE_CHAT_ENDPOINT  # Custom endpoint (e.g., "/api/chat" or "/chat")
        self.api_key = Config.ONPREMISE_API_KEY or "not-needed"  # Some local APIs don't need keys
        
        if not self.base_url:
            raise ValueError("ONPREMISE_API_BASE_URL not configured in environment")
        
        self.supported_models = Config.ONPREMISE_MODELS.split(",") if Config.ONPREMISE_MODELS else []
        
        # Initialize OAuth token manager if OAuth is configured
        self.oauth_manager = None
        if Config.ONPREMISE_TOKEN_URL and Config.ONPREMISE_CONSUMER_KEY and Config.ONPREMISE_CONSUMER_SECRET:
            try:
                from src.core.oauth_token_manager import OAuthTokenManager
                self.oauth_manager = OAuthTokenManager()
            except ValueError as e:
                # OAuth not fully configured, but that's OK - we'll use API key if available
                print(f"⚠ Warning: OAuth not fully configured for on-premise provider: {e}")
                self.oauth_manager = None
    
    def supports_model(self, model: str) -> bool:
        """
        Check if model is supported by on-premise provider.
        
        If ONPREMISE_MODELS is configured, only those models are supported.
        Otherwise, accepts models that look like on-premise (have indicators like ":" or specific prefixes).
        This prevents conflicts with OpenAI/Gemini models.
        """
        # If models list is configured, only accept those
        if self.supported_models:
            return model in self.supported_models
        
        # If no list configured, accept models that look like on-premise
        # Indicators of on-premise models:
        # - Contains ":" (e.g., "gpt-oss:20b", "llama3.1:8b", "qwen3-coder:30b", "deepseek-r1:14b")
        # - Starts with "local-" or "onpremise-"
        # - Not a known OpenAI pattern (gpt-4o, gpt-3.5-turbo, etc.) WITHOUT ":"
        # - Not a known Gemini pattern (gemini-*) - note: gemma3: is different from gemini-
        
        # Reject known OpenAI models (without ":")
        if model in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1-preview", "o1-mini"]:
            return False
        
        # Reject known OpenAI patterns WITHOUT ":" (but allow on-premise variants WITH ":")
        if model.startswith("gpt-4") or model.startswith("gpt-3.5") or model.startswith("o1-"):
            # If it has ":" it's on-premise (e.g., "gpt-oss:20b")
            if ":" in model:
                return True
            return False
        
        # Reject known Gemini patterns (gemini-* but NOT gemma*)
        # gemini-2.0-flash → Google Gemini (reject)
        # gemma3:12b → On-premise Gemma (accept because has ":")
        if model.startswith("gemini-"):
            return False
        
        # Accept models with ":" (common on-premise indicator)
        # Examples: qwen3-coder:30b, deepseek-r1:14b, llama3.1:8b, gemma3:latest, phi4:14b
        if ":" in model:
            return True
        
        # Accept models with on-premise prefixes
        if model.startswith("local-") or model.startswith("onpremise-"):
            return True
        
        # If no clear indicator, don't accept (let other providers check first)
        # This prevents OnPremiseProvider from capturing all models
        return False
    
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported on-premise models.
        
        If ONPREMISE_MODELS is configured, returns that list.
        Otherwise, returns empty list (meaning any model name is accepted).
        """
        if self.supported_models:
            return self.supported_models.copy()
        # Return empty list to indicate "any model" is supported
        # This is more flexible - the API will validate the model name
        return []
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Chat using on-premise API."""
        # Convert messages to API format
        # The on-premise API uses a format similar to Ollama but with messages array
        api_messages = []
        for msg in messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare request payload in the format expected by the on-premise API
        # This format is similar to Ollama's /api/chat endpoint
        payload = {
            "model": model,
            "messages": api_messages,
            "stream": True,  # Enable streaming for real-time responses
            "options": {
                "temperature": kwargs.get("temperature", 0.1),  # Default 0.1 as per API spec
                "top_p": kwargs.get("top_p", 0.15),  # Default 0.15 as per API spec
                "top_k": kwargs.get("top_k", 0),  # Default 0 as per API spec
                "num_predict": kwargs.get("num_predict") or kwargs.get("max_tokens", 500),  # Max tokens to generate
                "repeat_penalty": kwargs.get("repeat_penalty", 1.1),  # Penalty for repetition
                "num_ctx": kwargs.get("num_ctx", 4096),  # Context window size
            }
        }
        
        # Add optional seed for reproducibility
        if kwargs.get("seed"):
            payload["options"]["seed"] = kwargs.get("seed")
        
        # Add optional format (e.g., "json" for JSON responses)
        if kwargs.get("format"):
            payload["format"] = kwargs.get("format")
        
        # Add optional keep_alive parameter
        if kwargs.get("keep_alive"):
            payload["keep_alive"] = kwargs.get("keep_alive")
        
        # Note: We don't send tools in the payload
        # The ADK framework manages tools locally via function calling
        # Tools are NOT sent to the on-premise API
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Get authorization token (OAuth or API key)
        if self.oauth_manager:
            # Use OAuth token
            try:
                print(f"🔐 Gerando token OAuth para modelo: {model}")
                token = await self.oauth_manager.get_token()
                headers["Authorization"] = f"Bearer {token}"
                print(f"✓ Token OAuth gerado com sucesso")
            except Exception as oauth_error:
                # If OAuth fails, try to use API key as fallback
                if self.api_key and self.api_key != "not-needed":
                    print(f"⚠ Warning: OAuth token generation failed, using API key: {oauth_error}")
                    headers["Authorization"] = f"Bearer {self.api_key}"
                else:
                    raise Exception(
                        f"Falha ao gerar token OAuth e nenhuma API key configurada: {oauth_error}"
                    )
        elif self.api_key and self.api_key != "not-needed":
            # Use API key
            print(f"🔑 Usando API key para autenticação")
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            print(f"⚠ Warning: Nenhuma autenticação configurada para on-premise provider")
        
        # Configure SSL verification
        verify_ssl = Config.VERIFY_SSL
        if not verify_ssl:
            import warnings
            warnings.warn(
                "⚠️ SSL verification is disabled for on-premise provider. This is insecure!",
                UserWarning
            )
        
        # Determine the API endpoint
        # If custom chat endpoint is configured, use it
        if self.chat_endpoint:
            # Custom endpoint specified (e.g., "/api/chat" or "/chat")
            if self.chat_endpoint.startswith("/"):
                # Endpoint starts with /, append to base_url
                if self.base_url.endswith("/"):
                    api_endpoint = f"{self.base_url.rstrip('/')}{self.chat_endpoint}"
                else:
                    api_endpoint = f"{self.base_url}{self.chat_endpoint}"
            else:
                # Endpoint doesn't start with /, treat as relative path
                if self.base_url.endswith("/"):
                    api_endpoint = f"{self.base_url}{self.chat_endpoint}"
                else:
                    api_endpoint = f"{self.base_url}/{self.chat_endpoint}"
        else:
            # Use OpenAI-compatible endpoint by default
            base_url_lower = self.base_url.lower()
            if "/v1/chat/completions" in base_url_lower or "/chat/completions" in base_url_lower:
                # Full endpoint already provided
                api_endpoint = self.base_url
            elif self.base_url.endswith("/"):
                # Append standard OpenAI-compatible endpoint
                api_endpoint = f"{self.base_url}v1/chat/completions"
            else:
                # Append standard endpoint with slash
                api_endpoint = f"{self.base_url}/v1/chat/completions"
        
        print(f"🌐 Chamando API on-premise: {api_endpoint}")
        print(f"📦 Payload: model={model}, messages={len(api_messages)}")
        
        # Log detalhado do payload completo
        import json
        print("=" * 80)
        print("🔍 PAYLOAD COMPLETO ENVIADO PARA API ON-PREMISE:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("=" * 80)
        print(f"🔑 Headers:")
        # Mascarar token para segurança
        safe_headers = {k: ("Bearer ***" if k == "Authorization" else v) for k, v in headers.items()}
        print(json.dumps(safe_headers, indent=2))
        print("=" * 80)
        
        # Make streaming request
        async with httpx.AsyncClient(timeout=300.0, verify=verify_ssl) as client:
            try:
                async with client.stream(
                    "POST",
                    api_endpoint,
                    json=payload,
                    headers=headers
                ) as response:
                    print(f"📡 Resposta recebida: HTTP {response.status_code}")
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = error_text.decode() if error_text else "No error message"
                        print(f"✗ Erro da API: {response.status_code} - {error_msg}")
                        raise Exception(f"On-premise API error: {response.status_code} - {error_msg}")
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        try:
                            import json
                            # Try to parse as JSON (could be SSE format or plain JSON)
                            data_str = line
                            
                            # Handle SSE format (Server-Sent Events)
                            if line.startswith("data: "):
                                data_str = line[6:]  # Remove "data: " prefix
                                
                                if data_str.strip() == "[DONE]":
                                    break
                            
                            # Parse JSON
                            data = json.loads(data_str)
                            
                            # Handle different response formats:
                            # 1. OpenAI format: {"choices": [{"delta": {"content": "..."}}]}
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    yield delta["content"]
                            
                            # 2. Ollama /api/chat format: {"message": {"role": "assistant", "content": "..."}}
                            elif "message" in data and isinstance(data["message"], dict):
                                content = data["message"].get("content", "")
                                if content:
                                    yield content
                                # Check if done
                                if data.get("done", False):
                                    break
                            
                            # 3. Simple format: {"response": "...", "done": false} (Ollama /api/generate)
                            elif "response" in data:
                                if data["response"]:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            
                            # 4. Direct content format: {"content": "..."}
                            elif "content" in data and data["content"]:
                                yield data["content"]
                                
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
            except httpx.TimeoutException:
                raise Exception(
                    "Timeout ao conectar com a API on-premise. "
                    "O servidor pode estar lento ou indisponível. "
                    "Verifique se o servidor está rodando e acessível em: " + self.base_url
                )
            except httpx.ConnectError as e:
                error_msg = str(e)
                if "CERTIFICATE_VERIFY_FAILED" in error_msg or "certificate verify failed" in error_msg.lower():
                    raise Exception(
                        "Erro de certificado SSL ao conectar à API on-premise. "
                        "Se estiver usando certificado autoassinado, adicione no .env: VERIFY_SSL=false "
                        "(⚠️ ATENÇÃO: Isso desabilita verificação SSL e é inseguro)"
                    )
                else:
                    raise Exception(
                        f"Erro de conexão com a API on-premise: {error_msg}. "
                        f"Verifique se o servidor está acessível em: {self.base_url}"
                    )
            except Exception as e:
                error_type = type(e).__name__
                error_message = str(e)
                
                # Generic error handling
                raise Exception(
                    f"Erro ao comunicar com a API on-premise: {error_message}. "
                    f"Verifique se o servidor está configurado corretamente em: {self.base_url}"
                )

