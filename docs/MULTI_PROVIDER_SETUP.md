# Configuração de Múltiplos Provedores LLM

Este documento explica como configurar e usar múltiplos provedores LLM na aplicação.

## 📋 Provedores Suportados

A aplicação agora suporta três tipos de provedores LLM:

1. **Google ADK (Gemini)** - Modelos Gemini via Google ADK
2. **OpenAI** - Modelos GPT via OpenAI API
3. **On-Premise** - Modelos LLM locais via API compatível com OpenAI

## 🔧 Configuração

### 1. Google Gemini (ADK)

Adicione no `.env`:
```env
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

Modelos suportados:
- `gemini-2.0-flash-exp`
- `gemini-2.0-flash-thinking-exp`
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- `gemini-1.5-flash-8b`
- E outros modelos Gemini

### 2. OpenAI

Adicione no `.env`:
```env
OPENAI_API_KEY=sua_chave_openai_aqui
```

Modelos suportados:
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`
- `o1-preview`
- `o1-mini`

### 3. On-Premise (Modelos Locais)

Adicione no `.env`:
```env
# URL base da API (deve ser compatível com OpenAI API)
ONPREMISE_API_BASE_URL=http://localhost:1234

# Chave de API (opcional, algumas APIs locais não precisam)
ONPREMISE_API_KEY=opcional

# Lista de modelos disponíveis (separados por vírgula)
ONPREMISE_MODELS=llama-2-7b,mixtral-8x7b,llama-3-70b
```

**Nota:** A API on-premise deve ser compatível com a especificação OpenAI API (endpoint `/v1/chat/completions`).

## 🚀 Uso

### Criar um Agente com Modelo Específico

Ao criar um agente, você pode especificar qualquer modelo suportado:

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente Gemini",
    "model": "gemini-2.0-flash-exp",
    "description": "Agente usando Gemini",
    "instruction": "Você é um assistente útil."
  }'
```

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente OpenAI",
    "model": "gpt-4o-mini",
    "description": "Agente usando OpenAI",
    "instruction": "Você é um assistente útil."
  }'
```

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente Local",
    "model": "llama-2-7b",
    "description": "Agente usando modelo local",
    "instruction": "Você é um assistente útil."
  }'
```

### Listar Modelos Suportados

```bash
curl http://localhost:8001/api/models
```

Resposta:
```json
{
  "providers": {
    "ADK": [
      "gemini-2.0-flash-exp",
      "gemini-1.5-pro",
      ...
    ],
    "OpenAI": [
      "gpt-4o",
      "gpt-4o-mini",
      ...
    ],
    "OnPremise": [
      "llama-2-7b",
      "mixtral-8x7b",
      ...
    ]
  }
}
```

### Chat com Agente

O chat funciona automaticamente com qualquer modelo:

```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, como você pode me ajudar?",
    "agent_id": 1
  }'
```

A aplicação automaticamente:
1. Identifica o modelo do agente
2. Seleciona o provider apropriado
3. Executa a requisição usando o provider correto

## 🏗️ Arquitetura

```
┌─────────────────┐
│  API Routes     │
└────────┬────────┘
         │
┌────────▼─────────────┐
│   LLM Factory        │  ← Escolhe o provider
└────────┬─────────────┘
         │
    ┌────┴────┬──────────────┐
    │        │              │
┌───▼───┐ ┌──▼────┐    ┌────▼────┐
│  ADK  │ │OpenAI│    │OnPremise│
│(Gemini)│ │      │    │          │
└───────┘ └──────┘    └─────────┘
```

## 🔍 Detalhes Técnicos

### Como Funciona

1. **Factory Pattern**: A `LLMFactory` verifica qual provider suporta o modelo solicitado
2. **Provider Abstraction**: Cada provider implementa a interface `LLMProvider`
3. **Automatic Selection**: A aplicação escolhe automaticamente o provider baseado no nome do modelo

### Adicionar Novo Provedor

Para adicionar um novo provedor (ex: Anthropic Claude):

1. Crie `src/core/llm_providers/anthropic_provider.py`
2. Implemente a classe herdando de `LLMProvider`
3. Adicione no `LLMFactory._get_providers()`
4. Configure as variáveis de ambiente necessárias

## ⚠️ Notas Importantes

1. **Contexto de Conversa**: 
   - Modelos Gemini (ADK) têm suporte completo para contexto via Redis
   - Outros provedores também suportam contexto, mas podem ter limitações

2. **Ferramentas (Tools)**:
   - Modelos Gemini (ADK) têm suporte completo para tools
   - OpenAI suporta function calling
   - On-premise depende da implementação da API

3. **Rate Limiting**:
   - Todos os providers têm retry automático para erros 429
   - Backoff exponencial: 2s, 4s, 8s

## 🧪 Testando

1. Configure pelo menos um provedor no `.env`
2. Inicie a aplicação: `./scripts/start_backend.sh`
3. Liste modelos: `curl http://localhost:8001/api/models`
4. Crie um agente com o modelo desejado
5. Teste o chat

## 📚 Referências

- [Google ADK Documentation](https://github.com/google/adk)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI-Compatible API Spec](https://platform.openai.com/docs/api-reference)

