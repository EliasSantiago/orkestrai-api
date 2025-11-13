# Como Adicionar um Novo Provedor LLM

Este guia explica passo a passo como adicionar um novo provedor LLM à aplicação.

## 📋 Visão Geral

Para adicionar um novo provedor, você precisa:

1. ✅ Criar um arquivo em `src/core/llm_providers/`
2. ✅ Implementar a interface `LLMProvider`
3. ✅ Registrar o provider na `LLMFactory`
4. ✅ Adicionar configurações no `config.py` (se necessário)

## 🔧 Passo a Passo

### 1. Criar o Arquivo do Provider

Crie um novo arquivo em `src/core/llm_providers/` com o nome do provedor:

**Exemplo:** `src/core/llm_providers/anthropic_provider.py`

```python
"""Anthropic Claude LLM provider."""

from typing import List, Optional, AsyncIterator
from anthropic import AsyncAnthropic
from src.core.llm_provider import LLMProvider, LLMMessage
from src.core.config import Config


class AnthropicProvider(LLMProvider):
    """Anthropic provider for Claude models."""
    
    def __init__(self):
        api_key = Config.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.supported_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
    
    def supports_model(self, model: str) -> bool:
        """Check if model is an Anthropic model."""
        return model.startswith("claude-") or model in self.supported_models
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Anthropic models."""
        return self.supported_models.copy()
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Chat using Anthropic API."""
        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = None
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Create stream
        async with self.client.messages.stream(
            model=model,
            max_tokens=kwargs.get("max_tokens", 1024),
            system=system_message,
            messages=anthropic_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
```

### 2. Registrar no `__init__.py`

Adicione o import em `src/core/llm_providers/__init__.py`:

```python
from src.core.llm_providers.anthropic_provider import AnthropicProvider

__all__ = [
    "ADKProvider",
    "OpenAIProvider",
    "OnPremiseProvider",
    "AnthropicProvider",  # ← Adicionar aqui
]
```

### 3. Registrar na Factory

Adicione o provider em `src/core/llm_factory.py`:

```python
from src.core.llm_providers.anthropic_provider import AnthropicProvider

class LLMFactory:
    @classmethod
    def _get_providers(cls) -> List[LLMProvider]:
        if cls._providers is None:
            cls._providers = []
            
            # ... providers existentes ...
            
            # Add Anthropic provider
            try:
                cls._providers.append(AnthropicProvider())
            except Exception as e:
                print(f"⚠ Warning: Could not initialize Anthropic provider: {e}")
        
        return cls._providers
```

### 4. Adicionar Configuração (se necessário)

Se o provider precisar de configuração, adicione em `src/config.py`:

```python
# Anthropic API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
```

E no `.env`:

```env
ANTHROPIC_API_KEY=sua_chave_aqui
```

### 5. Adicionar Dependências (se necessário)

Se o provider precisar de uma biblioteca específica, adicione em `requirements.txt`:

```txt
anthropic>=0.18.0
```

## 📝 Template Completo

Aqui está um template completo que você pode usar:

```python
"""Nome do Provider LLM provider."""

from typing import List, Optional, AsyncIterator
from src.core.llm_provider import LLMProvider, LLMMessage
from src.core.config import Config


class MeuProvider(LLMProvider):
    """Descrição do provider."""
    
    def __init__(self):
        # Inicializar cliente/API do provedor
        # Verificar se configuração está presente
        api_key = Config.MEU_PROVIDER_API_KEY
        if not api_key:
            raise ValueError("MEU_PROVIDER_API_KEY not configured")
        
        # Inicializar cliente
        # self.client = ...
        
        # Lista de modelos suportados
        self.supported_models = [
            "modelo-1",
            "modelo-2",
        ]
    
    def supports_model(self, model: str) -> bool:
        """Verifica se o modelo é suportado."""
        return model in self.supported_models or model.startswith("prefixo-")
    
    def get_supported_models(self) -> List[str]:
        """Retorna lista de modelos suportados."""
        return self.supported_models.copy()
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Chat usando o provider.
        
        Args:
            messages: Lista de mensagens da conversa
            model: Nome do modelo a usar
            tools: Lista opcional de ferramentas
            **kwargs: Parâmetros adicionais específicos do provider
            
        Yields:
            Chunks de texto da resposta
        """
        # Converter mensagens para formato do provider
        # Fazer requisição para API
        # Yield chunks da resposta
        
        # Exemplo básico:
        # async for chunk in self.client.chat(...):
        #     yield chunk
        
        raise NotImplementedError("Implementar método chat")
```

## ✅ Checklist

Ao adicionar um novo provider, certifique-se de:

- [ ] Criar arquivo em `src/core/llm_providers/`
- [ ] Implementar todos os métodos da interface `LLMProvider`
- [ ] Adicionar import em `__init__.py`
- [ ] Registrar na `LLMFactory`
- [ ] Adicionar configurações no `config.py` (se necessário)
- [ ] Adicionar variáveis de ambiente no `.env.example` (se necessário)
- [ ] Adicionar dependências no `requirements.txt` (se necessário)
- [ ] Testar o provider criando um agente com um modelo suportado

## 🧪 Testando

Após adicionar o provider:

1. Configure as variáveis de ambiente
2. Reinicie a aplicação
3. Verifique se aparece em `/api/models`:
   ```bash
   curl http://localhost:8001/api/models
   ```
4. Crie um agente com um modelo do novo provider
5. Teste o chat

## 📚 Exemplos de Providers

### Provider Simples (HTTP)

Se o provider usar apenas HTTP, você pode usar `httpx` (já incluído):

```python
import httpx

async def chat(self, messages, model, **kwargs):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "https://api.exemplo.com/chat",
            json={"model": model, "messages": messages},
            headers={"Authorization": f"Bearer {api_key}"}
        ) as response:
            async for line in response.aiter_lines():
                # Processar resposta
                yield chunk
```

### Provider com Biblioteca Específica

Se o provider tiver uma biblioteca Python oficial:

```python
from provider_library import AsyncClient

async def chat(self, messages, model, **kwargs):
    async with AsyncClient(api_key=api_key) as client:
        async for chunk in client.chat.stream(model=model, messages=messages):
            yield chunk
```

## ⚠️ Notas Importantes

1. **Tratamento de Erros**: Sempre trate erros e forneça mensagens claras
2. **Rate Limiting**: A aplicação já tem retry automático, mas você pode adicionar lógica específica
3. **Streaming**: O método `chat` deve ser um `AsyncIterator` que yield chunks
4. **Tools**: Nem todos os providers suportam tools - implemente se o provider suportar

## 🔍 Por que httpx?

O `httpx` é usado pelo `OnPremiseProvider` para fazer requisições HTTP assíncronas para APIs locais. É necessário porque:

- ✅ Suporta streaming assíncrono
- ✅ Compatível com APIs OpenAI-compatible
- ✅ Mais leve que outras alternativas
- ✅ Suporta timeouts e retries

Se seu provider usar uma biblioteca específica (como `openai` ou `anthropic`), você não precisa usar `httpx` diretamente.

