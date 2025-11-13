# Como Adicionar Novos Modelos LLM

Este guia explica como adicionar suporte para novos modelos LLM na aplicação.

## 📋 Visão Geral

A aplicação atualmente usa o **Google ADK (Agents Development Kit)**, que suporta nativamente modelos **Google Gemini**. Para adicionar modelos de outros provedores (OpenAI, Anthropic, etc.), é necessário criar uma camada de abstração.

## 🎯 Opção 1: Adicionar Novos Modelos Gemini (Mais Fácil)

O Google ADK suporta vários modelos Gemini. Para usar um modelo Gemini diferente:

### Passos:

1. **Adicione a API Key no `.env`** (se ainda não tiver):
   ```env
   GOOGLE_API_KEY=sua_chave_aqui
   ```

2. **Ao criar um agente, passe o nome do modelo desejado**:
   ```json
   {
     "name": "Meu Agente",
     "description": "Descrição do agente",
     "instruction": "Você é um assistente útil...",
     "model": "gemini-2.0-flash-exp",  // ou outro modelo Gemini
     "tools": []
   }
   ```

### Modelos Gemini Disponíveis:

- `gemini-2.0-flash-exp` (padrão)
- `gemini-2.0-flash-thinking-exp`
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- `gemini-1.5-flash-8b`
- E outros modelos Gemini disponíveis

**Nota:** Basta passar o nome do modelo como string no campo `model` ao criar o agente. Não é necessário alterar código!

## 🔧 Opção 2: Adicionar Modelos de Outros Provedores (OpenAI, Anthropic, etc.)

Para usar modelos de outros provedores, você precisa criar uma camada de abstração que permita escolher entre ADK (Gemini) e outros provedores.

### Arquitetura Proposta:

```
┌─────────────────┐
│   API Routes    │
└────────┬────────┘
         │
┌────────▼─────────────────┐
│  LLM Provider Factory    │  ← Nova camada
└────────┬─────────────────┘
         │
    ┌────┴────┬──────────────┐
    │        │              │
┌───▼───┐ ┌──▼────┐    ┌────▼────┐
│  ADK  │ │OpenAI│    │Anthropic│
│(Gemini)│ │      │    │         │
└───────┘ └──────┘    └─────────┘
```

### Implementação Passo a Passo:

#### 1. Criar Interface/Abstração para LLM

Crie `src/core/llm_provider.py`:

```python
"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Message in a conversation."""
    role: str  # "user", "assistant", "system"
    content: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Chat with the LLM.
        
        Args:
            messages: List of messages in the conversation
            model: Model name to use
            tools: Optional list of tools/functions
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Response chunks as strings
        """
        pass
    
    @abstractmethod
    def supports_model(self, model: str) -> bool:
        """Check if this provider supports the given model."""
        pass
```

#### 2. Implementar Provider para Google ADK (Gemini)

Crie `src/core/llm_providers/adk_provider.py`:

```python
"""Google ADK (Gemini) LLM provider."""

from typing import List, Optional, AsyncIterator
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from src.core.llm_provider import LLMProvider, LLMMessage


class ADKProvider(LLMProvider):
    """Google ADK provider for Gemini models."""
    
    def __init__(self):
        self.supported_models = [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
        ]
    
    def supports_model(self, model: str) -> bool:
        """Check if model is a Gemini model."""
        return model.startswith("gemini-") or model in self.supported_models
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Chat using Google ADK."""
        # Convert messages to ADK format
        instruction = ""
        conversation = []
        
        for msg in messages:
            if msg.role == "system":
                instruction += msg.content + "\n"
            else:
                conversation.append(
                    types.Content(
                        parts=[types.Part(text=msg.content)],
                        role=msg.role
                    )
                )
        
        # Create ADK agent
        agent = Agent(
            model=model,
            name="chat_agent",
            description="Chat agent",
            instruction=instruction or "You are a helpful assistant.",
            tools=tools or []
        )
        
        # Create runner
        runner = InMemoryRunner(agent=agent, app_name="chat_app")
        
        # Get last user message
        if conversation:
            last_message = conversation[-1]
        else:
            raise ValueError("No messages provided")
        
        # Run agent
        async for event in runner.run_async(
            user_id=kwargs.get("user_id", "default"),
            session_id=kwargs.get("session_id", "default"),
            new_message=last_message
        ):
            if hasattr(event, 'content') and event.content:
                for content in event.content if isinstance(event.content, list) else [event.content]:
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                yield part.text
```

#### 3. Implementar Provider para OpenAI

Crie `src/core/llm_providers/openai_provider.py`:

```python
"""OpenAI LLM provider."""

import os
from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI
from src.core.llm_provider import LLMProvider, LLMMessage
from src.core.config import Config


class OpenAIProvider(LLMProvider):
    """OpenAI provider for GPT models."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.supported_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]
    
    def supports_model(self, model: str) -> bool:
        """Check if model is an OpenAI model."""
        return model.startswith("gpt-") or model in self.supported_models
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Chat using OpenAI API."""
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Create stream
        stream = await self.client.chat.completions.create(
            model=model,
            messages=openai_messages,
            tools=tools,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

#### 4. Criar Factory para Escolher o Provider

Crie `src/core/llm_factory.py`:

```python
"""Factory for creating LLM providers."""

from typing import Optional
from src.core.llm_provider import LLMProvider
from src.core.llm_providers.adk_provider import ADKProvider
from src.core.llm_providers.openai_provider import OpenAIProvider


class LLMFactory:
    """Factory to create appropriate LLM provider based on model name."""
    
    _providers: list[LLMProvider] = None
    
    @classmethod
    def _get_providers(cls) -> list[LLMProvider]:
        """Get list of available providers."""
        if cls._providers is None:
            cls._providers = [
                ADKProvider(),
                OpenAIProvider(),
                # Add more providers here
            ]
        return cls._providers
    
    @classmethod
    def get_provider(cls, model: str) -> Optional[LLMProvider]:
        """
        Get the appropriate provider for a given model.
        
        Args:
            model: Model name (e.g., "gpt-4o", "gemini-2.0-flash-exp")
            
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
```

#### 5. Atualizar `agent_chat_routes.py` para Usar a Factory

Modifique `src/api/agent_chat_routes.py`:

```python
# Adicione no topo
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage

# No endpoint chat_with_agent, substitua a criação do Agent por:

# Determinar qual provider usar baseado no modelo
provider = LLMFactory.get_provider(agent_model.model)
if not provider:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Model '{agent_model.model}' is not supported"
    )

# Obter histórico de conversa
history = HybridConversationService.get_conversation_history(
    user_id=user_id,
    session_id=session_id,
    db=db
)

# Converter histórico para formato LLMMessage
messages = []
for msg in history:
    messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

# Adicionar mensagem atual
messages.append(LLMMessage(role="user", content=request.message))

# Obter tools
tool_map = {
    "calculator": calculator,
    "get_current_time": get_current_time,
}
tool_names = agent_model.tools or []
tools = [tool_map[name] for name in tool_names if name in tool_map]

# Chamar provider
response_chunks = []
async for chunk in provider.chat(
    messages=messages,
    model=agent_model.model,
    tools=tools if tools else None,
    user_id=str(user_id),
    session_id=session_id
):
    response_chunks.append(chunk)

response = ''.join(response_chunks)
```

### 6. Adicionar Nova API Key no `.env`

```env
# Google Gemini (já existe)
GOOGLE_API_KEY=sua_chave_gemini

# OpenAI (adicionar)
OPENAI_API_KEY=sua_chave_openai

# Outros provedores (quando adicionar)
ANTHROPIC_API_KEY=sua_chave_anthropic
```

### 7. Atualizar `config.py`

Adicione as novas chaves de API:

```python
# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Anthropic API (quando adicionar)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
```

## 📝 Resumo: O Que Você Precisa Fazer

### Para Modelos Gemini (Fácil):
1. ✅ Adicione `GOOGLE_API_KEY` no `.env`
2. ✅ Passe o nome do modelo ao criar o agente
3. ✅ Pronto! Funciona imediatamente

### Para Outros Provedores (Requer Código):
1. ✅ Criar interface `LLMProvider`
2. ✅ Implementar providers (OpenAI, Anthropic, etc.)
3. ✅ Criar factory para escolher provider
4. ✅ Atualizar `agent_chat_routes.py` para usar factory
5. ✅ Adicionar API keys no `.env`
6. ✅ Testar!

## 🧪 Testando

Após implementar, teste criando um agente com diferentes modelos:

```bash
# Gemini
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente Gemini",
    "model": "gemini-2.0-flash-exp",
    "instruction": "Você é útil"
  }'

# OpenAI
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente OpenAI",
    "model": "gpt-4o-mini",
    "instruction": "Você é útil"
  }'
```

## 🔍 Verificando Modelos Suportados

Você pode adicionar um endpoint para listar modelos suportados:

```python
@router.get("/models")
async def list_supported_models():
    """List all supported models."""
    models = {}
    for provider in LLMFactory._get_providers():
        models[provider.__class__.__name__] = provider.supported_models
    return models
```

## 📚 Referências

- [Google ADK Documentation](https://github.com/google/adk)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)

