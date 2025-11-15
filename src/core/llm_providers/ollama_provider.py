"""Ollama LLM provider for locally hosted Ollama models."""

import httpx
import json
from typing import List, Optional, AsyncIterator
from src.core.llm_provider import LLMProvider, LLMMessage
from src.config import Config


class OllamaProvider(LLMProvider):
    """Ollama LLM provider for locally hosted models."""
    
    def __init__(self):
        # Get Ollama API configuration
        self.base_url = Config.OLLAMA_API_BASE_URL
        
        if not self.base_url:
            raise ValueError("OLLAMA_API_BASE_URL not configured in environment")
        
        # Remove trailing slash if present
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
        
        # Get supported models from config (optional)
        self.supported_models = Config.OLLAMA_MODELS.split(",") if Config.OLLAMA_MODELS else []
    
    def supports_model(self, model: str) -> bool:
        """
        Check if model is supported by Ollama provider.
        
        If OLLAMA_MODELS is configured, only those models are supported.
        Otherwise, only accepts models with SPECIFIC Ollama prefixes to avoid conflicts.
        """
        # If models list is configured, only accept those
        if self.supported_models:
            return model in self.supported_models
        
        # If no list configured, ONLY accept models with known Ollama prefixes
        # This prevents Ollama from capturing all models with ":" (which would conflict with on-premise)
        model_lower = model.lower()
        
        # Reject OpenAI models
        if model_lower.startswith("gpt-") or model_lower.startswith("openai-"):
            return False
        
        # Reject Gemini models (note: gemma is different from gemini)
        if model_lower.startswith("gemini-"):
            return False
        
        # ONLY accept models with SPECIFIC Ollama prefixes
        # NOTE: Do NOT include "qwen", "deepseek", "gpt-oss" as they are used by on-premise
        # Those models will be handled by OnPremiseProvider
        ollama_prefixes = [
            "llama",      # llama2, llama3, llama3.1, llama3.2
            "mistral",    # mistral, mixtral
            "gemma",      # gemma2, gemma3 (Google's Gemma models)
            "phi",        # phi2, phi3, phi4
            "codellama",  # codellama
            "neural-chat",
            "starling",
            "orca",
            "vicuna",
            "wizard",
            "nous",       # nous-hermes
            "openchat",
            "solar",
            "yi",
        ]
        
        for prefix in ollama_prefixes:
            if model_lower.startswith(prefix):
                return True
        
        # Don't accept models just because they have ":"
        # This prevents capturing on-premise models
        # Models like "qwen3:30b", "deepseek-r1:14b", "gpt-oss:20b" should go to OnPremiseProvider
        
        return False
    
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported Ollama models.
        
        If OLLAMA_MODELS is configured, returns that list.
        Otherwise, returns empty list (meaning any model name is accepted).
        """
        if self.supported_models:
            return self.supported_models.copy()
        return []
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Chat using Ollama API."""
        # Convert messages to a single prompt
        # Ollama uses a single prompt string, not a messages array
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Prepare request payload (Ollama format)
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40),
                "repeat_penalty": kwargs.get("repeat_penalty", 1.1),
                "num_ctx": kwargs.get("num_ctx", 1024),
            }
        }
        
        # Add custom options if provided
        if kwargs.get("options"):
            payload["options"].update(kwargs.get("options"))
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Configure SSL verification
        verify_ssl = Config.VERIFY_SSL
        if not verify_ssl:
            import warnings
            warnings.warn(
                "⚠️ SSL verification is disabled for Ollama provider. This is insecure!",
                UserWarning
            )
        
        # Ollama endpoint
        api_endpoint = f"{self.base_url}/api/generate"
        
        print(f"🦙 Chamando Ollama API: {api_endpoint}")
        print(f"📦 Payload: model={model}, prompt_length={len(prompt)}")
        
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
                        raise Exception(f"Ollama API error: {response.status_code} - {error_msg}")
                    
                    # Ollama returns JSON lines (one JSON object per line)
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        try:
                            data = json.loads(line)
                            
                            # Ollama response format: {"response": "text chunk", "done": false}
                            if "response" in data:
                                yield data["response"]
                            
                            # Check if done
                            if data.get("done", False):
                                break
                                
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
                            
            except httpx.TimeoutException:
                raise Exception(
                    "Timeout ao conectar com a API Ollama. "
                    "O servidor pode estar lento ou indisponível. "
                    "Verifique se o servidor Ollama está rodando e acessível em: " + self.base_url
                )
            except httpx.ConnectError as e:
                error_msg = str(e)
                if "CERTIFICATE_VERIFY_FAILED" in error_msg or "certificate verify failed" in error_msg.lower():
                    raise Exception(
                        "Erro de certificado SSL ao conectar à API Ollama. "
                        "Se estiver usando certificado autoassinado, adicione no .env: VERIFY_SSL=false "
                        "(⚠️ ATENÇÃO: Isso desabilita verificação SSL e é inseguro)"
                    )
                else:
                    raise Exception(
                        f"Erro de conexão com a API Ollama: {error_msg}. "
                        f"Verifique se o servidor Ollama está rodando e acessível em: {self.base_url}"
                    )
            except Exception as e:
                error_type = type(e).__name__
                error_message = str(e)
                
                # Generic error handling
                raise Exception(
                    f"Erro ao comunicar com a API Ollama: {error_message}. "
                    f"Verifique se o servidor Ollama está configurado corretamente em: {self.base_url}"
                )

