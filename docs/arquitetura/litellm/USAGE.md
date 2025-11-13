# LiteLLM - Guia de Uso

Este guia mostra como usar o LiteLLM na prática dentro da aplicação.

---

## 📋 Sumário

1. [Uso Básico](#uso-básico)
2. [Criando Agentes com LiteLLM](#criando-agentes-com-litellm)
3. [Exemplos Práticos](#exemplos-práticos)
4. [Nomenclatura de Modelos](#nomenclatura-de-modelos)
5. [Parâmetros Avançados](#parâmetros-avançados)
6. [Integração com API](#integração-com-api)

---

## Uso Básico

### 1. Usando Diretamente o LiteLLMProvider

```python
import asyncio
from src.core.llm_providers.litellm_provider import LiteLLMProvider
from src.core.llm_provider import LLMMessage

async def exemplo_basico():
    # Criar provider
    provider = LiteLLMProvider()
    
    # Criar mensagens
    messages = [
        LLMMessage(role="user", content="Explique o que é Python em 2 frases.")
    ]
    
    # Fazer chat (streaming)
    print("Resposta: ", end="")
    async for chunk in provider.chat(
        messages=messages,
        model="gemini/gemini-2.0-flash-exp"
    ):
        print(chunk, end="", flush=True)
    
    print("\n")

# Executar
asyncio.run(exemplo_basico())
```

### 2. Usando o LLMFactory (Recomendado)

```python
import asyncio
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage

async def exemplo_com_factory():
    # O Factory escolhe automaticamente o provider correto
    provider = LLMFactory.get_provider("gemini/gemini-2.0-flash-exp")
    
    if not provider:
        print("Modelo não suportado!")
        return
    
    messages = [
        LLMMessage(role="user", content="Qual é a capital do Brasil?")
    ]
    
    async for chunk in provider.chat(
        messages=messages,
        model="gemini/gemini-2.0-flash-exp"
    ):
        print(chunk, end="", flush=True)

asyncio.run(exemplo_com_factory())
```

---

## Criando Agentes com LiteLLM

### Exemplo 1: Agente Simples com Gemini via LiteLLM

```python
from src.application.use_cases.agents.create_agent import CreateAgentUseCase
from src.infrastructure.database.agent_repository_impl import AgentRepositoryImpl
from src.domain.services.validation_service import ValidationService
from src.database import SessionLocal

# Criar sessão do banco
db = SessionLocal()

try:
    # Criar dependências
    repository = AgentRepositoryImpl(db)
    validator = ValidationService()
    create_agent = CreateAgentUseCase(repository, validator)
    
    # Criar agente usando modelo via LiteLLM
    agent = create_agent.execute(
        user_id=1,
        name="Assistente Gemini (LiteLLM)",
        description="Assistente que usa Gemini via LiteLLM",
        instruction="Você é um assistente útil e amigável.",
        model="gemini/gemini-2.0-flash-exp",  # Formato LiteLLM
        tools=[]
    )
    
    print(f"✅ Agente criado: ID {agent.id}")
    print(f"   Nome: {agent.name}")
    print(f"   Modelo: {agent.model}")
    
finally:
    db.close()
```

### Exemplo 2: Agente com OpenAI via LiteLLM

```python
agent = create_agent.execute(
    user_id=1,
    name="Assistente GPT-4o",
    description="Assistente que usa GPT-4o via LiteLLM",
    instruction="Você é um expert em programação Python.",
    model="openai/gpt-4o",  # OpenAI via LiteLLM
    tools=[]
)
```

### Exemplo 3: Agente com Ollama Local

```python
agent = create_agent.execute(
    user_id=1,
    name="Assistente Llama Local",
    description="Assistente que usa Llama2 local via Ollama e LiteLLM",
    instruction="Você é um assistente offline.",
    model="ollama/llama2",  # Ollama via LiteLLM
    tools=[]
)
```

---

## Exemplos Práticos

### 1. Chat com Histórico de Conversa

```python
import asyncio
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage

async def chat_com_historico():
    provider = LLMFactory.get_provider("gemini/gemini-2.0-flash-exp")
    
    # Conversa com múltiplas mensagens
    messages = [
        LLMMessage(role="user", content="Meu nome é João."),
        LLMMessage(role="assistant", content="Olá João! Como posso ajudar?"),
        LLMMessage(role="user", content="Qual é o meu nome?")
    ]
    
    print("Resposta: ")
    async for chunk in provider.chat(
        messages=messages,
        model="gemini/gemini-2.0-flash-exp"
    ):
        print(chunk, end="", flush=True)
    print("\n")

asyncio.run(chat_com_historico())
```

### 2. Usando System Message

```python
async def chat_com_system_message():
    provider = LLMFactory.get_provider("openai/gpt-4o-mini")
    
    messages = [
        LLMMessage(
            role="system", 
            content="Você é um poeta. Responda sempre em versos."
        ),
        LLMMessage(role="user", content="Como está o dia hoje?")
    ]
    
    async for chunk in provider.chat(
        messages=messages,
        model="openai/gpt-4o-mini"
    ):
        print(chunk, end="", flush=True)

asyncio.run(chat_com_system_message())
```

### 3. Controlando Parâmetros (temperatura, max_tokens)

```python
async def chat_com_parametros():
    provider = LLMFactory.get_provider("gemini/gemini-2.0-flash-exp")
    
    messages = [
        LLMMessage(role="user", content="Escreva uma história curta sobre um robô.")
    ]
    
    async for chunk in provider.chat(
        messages=messages,
        model="gemini/gemini-2.0-flash-exp",
        temperature=0.9,  # Mais criativo
        max_tokens=500    # Limitar tamanho
    ):
        print(chunk, end="", flush=True)

asyncio.run(chat_com_parametros())
```

### 4. Comparando Respostas de Diferentes Modelos

```python
async def comparar_modelos():
    prompt = "Explique inteligência artificial em uma frase."
    
    modelos = [
        "gemini/gemini-2.0-flash-exp",
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku-20240307",
    ]
    
    for modelo in modelos:
        provider = LLMFactory.get_provider(modelo)
        if not provider:
            continue
        
        print(f"\n{'='*60}")
        print(f"Modelo: {modelo}")
        print('='*60)
        
        messages = [LLMMessage(role="user", content=prompt)]
        
        try:
            async for chunk in provider.chat(messages=messages, model=modelo):
                print(chunk, end="", flush=True)
            print("\n")
        except Exception as e:
            print(f"Erro: {e}")

asyncio.run(comparar_modelos())
```

---

## Nomenclatura de Modelos

O LiteLLM usa o formato `provider/model-name`. Aqui estão os principais:

### Google Gemini

```python
"gemini/gemini-2.5-flash"
"gemini/gemini-2.0-flash-exp"
"gemini/gemini-2.0-flash-thinking-exp"
"gemini/gemini-1.5-pro"
"gemini/gemini-1.5-flash"
"gemini/gemini-1.5-flash-8b"
```

### OpenAI

```python
"openai/gpt-4o"
"openai/gpt-4o-mini"
"openai/gpt-4-turbo"
"openai/gpt-4"
"openai/gpt-3.5-turbo"
```

### Anthropic Claude

```python
"anthropic/claude-3-opus-20240229"
"anthropic/claude-3-sonnet-20240229"
"anthropic/claude-3-haiku-20240307"
```

### Ollama (Local)

```python
"ollama/llama2"
"ollama/llama3"
"ollama/mistral"
"ollama/codellama"
"ollama/gemma"
"ollama/phi"
```

### Outros Providers

```python
# Azure OpenAI
"azure/gpt-4o"

# Cohere
"cohere/command-r-plus"

# HuggingFace
"huggingface/meta-llama/Llama-2-7b-chat-hf"

# Replicate
"replicate/meta/llama-2-70b-chat"

# Ver lista completa: https://docs.litellm.ai/docs/providers
```

---

## Parâmetros Avançados

### Parâmetros Suportados

```python
async for chunk in provider.chat(
    messages=messages,
    model="gemini/gemini-2.0-flash-exp",
    
    # Controle de geração
    temperature=0.7,        # 0.0 a 1.0 (criatividade)
    max_tokens=2048,        # Máximo de tokens na resposta
    top_p=0.9,              # Nucleus sampling
    frequency_penalty=0.0,  # Penalidade por repetição
    presence_penalty=0.0,   # Penalidade por tópicos já mencionados
    
    # Outros parâmetros (dependem do provider)
    stop=["END"],           # Tokens de parada
    seed=42,                # Para reprodutibilidade
):
    print(chunk, end="")
```

### Descrição dos Parâmetros

| Parâmetro | Descrição | Faixa | Padrão |
|-----------|-----------|-------|---------|
| `temperature` | Controla a aleatoriedade. Maior = mais criativo | 0.0 - 1.0 | 0.7 |
| `max_tokens` | Máximo de tokens na resposta | 1 - ∞ | Varia por modelo |
| `top_p` | Nucleus sampling (alternativa ao temperature) | 0.0 - 1.0 | 1.0 |
| `frequency_penalty` | Penaliza repetição de tokens | -2.0 - 2.0 | 0.0 |
| `presence_penalty` | Penaliza tópicos já mencionados | -2.0 - 2.0 | 0.0 |

---

## Integração com API

> **⚠️ IMPORTANTE**: O exemplo abaixo é **apenas didático** para mostrar como usar LiteLLM diretamente.  
> **Sua aplicação JÁ TEM endpoints de chat muito superiores!** Veja [ARCHITECTURE_ANALYSIS.md](./ARCHITECTURE_ANALYSIS.md)

### Seus Endpoints Existentes (RECOMENDADO)

Você já possui endpoints completos e integrados com LiteLLM:

#### 1. Chat com Agente

```bash
# Endpoint existente: POST /api/agents/chat
curl -X POST http://localhost:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Olá, como você pode me ajudar?",
    "agent_id": 1,
    "session_id": "abc123",
    "model": "gemini/gemini-2.0-flash-exp"
  }'
```

**Features**:
- ✅ Autenticação JWT
- ✅ Gestão de sessões e histórico
- ✅ Model override
- ✅ Retry logic
- ✅ Tool support
- ✅ File Search/RAG

#### 2. Criar Agente

```bash
# Endpoint existente: POST /api/agents
curl -X POST http://localhost:8000/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Meu Agente",
    "instruction": "Você é um assistente",
    "model": "gemini/gemini-2.0-flash-exp"
  }'
```

**Veja mais**: [ARCHITECTURE_ANALYSIS.md](./ARCHITECTURE_ANALYSIS.md) - Análise completa da sua arquitetura

---

### Exemplo Didático (Apenas para Referência)

O exemplo abaixo é apenas para demonstrar o uso básico do LiteLLM.  
**Não é necessário** implementar este endpoint se você já tem `POST /api/agents/chat`.

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage

router = APIRouter()

class ChatRequest(BaseModel):
    model: str
    messages: List[dict]
    temperature: float = 0.7
    max_tokens: int = 2048

@router.post("/chat")
async def chat(request: ChatRequest):
    """Endpoint DIDÁTICO para chat usando LiteLLM."""
    
    # Obter provider
    provider = LLMFactory.get_provider(request.model)
    if not provider:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' is not supported"
        )
    
    # Converter mensagens
    messages = [
        LLMMessage(role=msg["role"], content=msg["content"])
        for msg in request.messages
    ]
    
    # Stream response
    from fastapi.responses import StreamingResponse
    
    async def generate():
        async for chunk in provider.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/plain")
```

> **💡 Nota**: Este é um exemplo simples. Seu endpoint `POST /api/agents/chat` já tem:
> - ✅ Autenticação
> - ✅ Gestão de conversas
> - ✅ Retry logic
> - ✅ Tool support
> - ✅ File Search/RAG
> - ✅ E muito mais!

---

## 🎯 Boas Práticas

### 1. Tratamento de Erros

```python
async def chat_seguro():
    try:
        provider = LLMFactory.get_provider("gemini/gemini-2.0-flash-exp")
        v
        if not provider:
            print("Modelo não suportado")
            return
        
        messages = [LLMMessage(role="user", content="Olá")]
        
        async for chunk in provider.chat(messages=messages, model="gemini/gemini-2.0-flash-exp"):
            print(chunk, end="")
            
    except Exception as e:
        print(f"Erro ao fazer chat: {e}")
        # Log do erro
        import logging
        logging.error(f"Chat error: {e}", exc_info=True)
```

### 2. Verificar Modelo Antes de Usar

```python
def verificar_modelo(model_name: str) -> bool:
    return LLMFactory.is_model_supported(model_name)

# Uso
if verificar_modelo("gemini/gemini-2.0-flash-exp"):
    print("Modelo suportado!")
else:
    print("Modelo não disponível")
```

### 3. Listar Modelos Disponíveis

```python
from src.core.llm_factory import LLMFactory

# Listar todos os modelos por provider
all_models = LLMFactory.get_all_supported_models()

for provider_name, models in all_models.items():
    print(f"\n{provider_name}:")
    for model in models:
        print(f"  - {model}")
```

---

## 📚 Exemplos Completos

Veja também:
- [01_AGENTES_EXEMPLOS_COMPLETOS.md](../../01_AGENTES_EXEMPLOS_COMPLETOS.md)
- [AGENT_CREATION_GUIDE.md](../../AGENT_CREATION_GUIDE.md)

---

**Última atualização**: 2025-11-12

