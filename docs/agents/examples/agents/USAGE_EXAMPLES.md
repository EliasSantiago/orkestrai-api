# Exemplos de Uso dos Agentes

## 🚀 Como Criar Agentes

### Via cURL

```bash
# 1. Faça login primeiro
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "sua-senha"
  }'

# Isso retorna um token. Use-o nos próximos comandos.
export TOKEN="seu-token-aqui"

# 2. Crie um agente
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @examples/agents/gemini_assistant.json

# Isso retorna algo como:
# {
#   "id": 10,
#   "name": "Assistente Gemini Flash",
#   "model": "gemini/gemini-2.0-flash-exp",
#   ...
# }
```

### Via Swagger UI

1. Acesse: http://localhost:8001/docs
2. Clique em "Authorize" (cadeado no topo)
3. Faça login: `POST /api/auth/login`
4. Copie o token retornado
5. Cole no campo "Authorization" (formato: apenas o token, sem "Bearer")
6. Clique em "POST /api/agents"
7. Cole o JSON de um dos exemplos
8. Execute!

---

## 💬 Como Conversar com Agentes

### Chat Simples

```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 10,
    "message": "Olá! Como você pode me ajudar?",
    "session_id": ""
  }'
```

### Chat com Override de Modelo

```bash
# Usar GPT-4o-mini mesmo se o agente usa outro modelo
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 10,
    "message": "Me explique inteligência artificial",
    "model": "openai/gpt-4o-mini",
    "session_id": ""
  }'
```

### Chat com Continuidade (Session)

```bash
# Primeira mensagem - gera session_id automaticamente
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 10,
    "message": "Meu nome é João",
    "session_id": ""
  }'

# Isso retorna algo como:
# {
#   "response": "Olá João! Como posso ajudar?",
#   "session_id": "cc9e7f12-0413-49bc-91dd-7a5f6f2500da"
# }

# Use o mesmo session_id para continuar a conversa
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 10,
    "message": "Qual é o meu nome?",
    "session_id": "cc9e7f12-0413-49bc-91dd-7a5f6f2500da"
  }'

# O agente vai lembrar: "Seu nome é João!"
```

---

## 📝 Exemplos Práticos

### 1. Assistente de Programação

```bash
# Criar agente
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -d @examples/agents/gemini_coding_assistant.json

# Usar
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 11,
    "message": "Como fazer um loop em Python?",
    "session_id": ""
  }'
```

### 2. Assistente com RAG (Busca em Documentos)

```bash
# 1. Criar agente com File Search
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -d @examples/agents/rag_file_search_agent.json

# 2. Upload de documentos (via Swagger UI em /api/file-search/upload)

# 3. Fazer perguntas sobre os documentos
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 12,
    "message": "O que dizem os documentos sobre vendas em 2024?",
    "session_id": ""
  }'
```

### 3. Assistente com Busca Web

```bash
# Criar agente
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -d @examples/agents/web_search_agent.json

# Usar
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 13,
    "message": "Quais são as últimas notícias sobre IA?",
    "session_id": ""
  }'
```

### 4. Comparar Diferentes Modelos

```bash
# Mesmo agente, diferentes modelos via override
export AGENT_ID=10

# GPT-4o (OpenAI - mais poderoso)
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": '$AGENT_ID',
    "message": "Explique inteligência artificial",
    "model": "openai/gpt-4o"
  }'

# GPT-4o-mini (OpenAI - rápido e barato)
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": '$AGENT_ID',
    "message": "Explique inteligência artificial",
    "model": "openai/gpt-4o-mini"
  }'

# Gemini Flash (Google - muito rápido)
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": '$AGENT_ID',
    "message": "Explique inteligência artificial",
    "model": "gemini/gemini-2.0-flash-exp"
  }'

# Claude Haiku (Anthropic - balanceado)
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": '$AGENT_ID',
    "message": "Explique inteligência artificial",
    "model": "anthropic/claude-3-haiku-20240307"
  }'
```

---

## 🔧 Gerenciamento de Agentes

### Listar Todos os Agentes

```bash
curl -X GET http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN"
```

### Obter Agente Específico

```bash
curl -X GET http://localhost:8001/api/agents/10 \
  -H "Authorization: Bearer $TOKEN"
```

### Atualizar Agente

```bash
curl -X PUT http://localhost:8001/api/agents/10 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Novo Nome",
    "model": "openai/gpt-4o",
    "instruction": "Nova instrução aqui"
  }'
```

### Deletar Agente

```bash
curl -X DELETE http://localhost:8001/api/agents/10 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Dicas de Uso

### 1. Escolhendo o Modelo Certo

| Caso de Uso | Modelo Recomendado | Por quê? |
|-------------|-------------------|----------|
| Tarefas gerais | `gemini/gemini-2.0-flash-exp` | Rápido e gratuito (quota generosa) |
| Análise complexa | `openai/gpt-4o` | Mais poderoso |
| Respostas rápidas | `openai/gpt-4o-mini` | Muito rápido e barato |
| Escrita criativa | `anthropic/claude-3-opus-20240229` | Excelente em criação |
| Desenvolvimento | `gemini/gemini-2.5-flash` | Ótimo para código |
| Offline/Local | `ollama/llama2` | Roda localmente, sem API |

### 2. Usando Tools

- `calculator`: Para cálculos matemáticos
- `time`: Para informações de data/hora
- `web_search`: Para informações atualizadas (requer Tavily API key)
- `google_calendar`: Para acesso ao calendário (requer OAuth)

### 3. File Search / RAG

- ✅ **Apenas Gemini** suporta File Search
- Ótimo para: Análise de documentos, Q&A sobre PDFs, busca em base de conhecimento
- Configure `"use_file_search": true` no agente

### 4. Session Management

- Deixe `session_id` vazio na primeira mensagem
- Use o `session_id` retornado para continuar a conversa
- Sessões duram 4 horas por padrão

---

## 📚 Referências

- [API Docs (Swagger)](http://localhost:8001/docs)
- [Documentação LiteLLM](../../docs/arquitetura/litellm/README.md)
- [Modelos Suportados](../../docs/arquitetura/litellm/USAGE.md#nomenclatura-de-modelos)
- [Troubleshooting](../../docs/arquitetura/litellm/TROUBLESHOOTING.md)

---

**Última atualização**: 2025-11-12

