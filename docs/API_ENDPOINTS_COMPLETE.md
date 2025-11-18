# 📡 Lista Completa de Endpoints da API

**Base URL:** `http://localhost:8001` (desenvolvimento) ou sua URL de produção  
**Autenticação:** Todos os endpoints (exceto login/register) requerem `Authorization: Bearer <token>` no header

---

## 🔐 Autenticação (`/api/auth`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/register` | Registrar novo usuário | ❌ |
| POST | `/api/auth/login` | Login e obter token | ❌ |
| GET | `/api/auth/me` | Obter usuário autenticado | ✅ |
| POST | `/api/auth/forgot-password` | Solicitar reset de senha | ❌ |
| POST | `/api/auth/reset-password` | Resetar senha com token | ❌ |

### Detalhes

**POST `/api/auth/register`**
```json
Request: {
  "name": "Nome do Usuário",
  "email": "user@example.com",
  "password": "senha123",
  "password_confirm": "senha123"
}
Response: {
  "id": 1,
  "name": "Nome do Usuário",
  "email": "user@example.com",
  "is_active": true
}
```

**POST `/api/auth/login`**
```json
Request: {
  "email": "user@example.com",
  "password": "senha123"
}
Response: {
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

**GET `/api/auth/me`**
```json
Response: {
  "id": 1,
  "name": "Nome do Usuário",
  "email": "user@example.com",
  "is_active": true,
  "preferences": {}
}
```

---

## 🤖 Agentes (`/api/agents`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/agents` | Listar todos os agentes do usuário | ✅ |
| GET | `/api/agents/{agent_id}` | Obter agente específico | ✅ |
| POST | `/api/agents` | Criar novo agente | ✅ |
| PUT | `/api/agents/{agent_id}` | Atualizar agente | ✅ |
| DELETE | `/api/agents/{agent_id}` | Deletar agente | ✅ |
| POST | `/api/agents/chat` | Chat com agente | ✅ |

### Detalhes

**GET `/api/agents`**
```json
Response: [
  {
    "id": 1,
    "name": "Suporte",
    "description": "Atende dúvidas gerais",
    "instruction": "Você é um agente...",
    "model": "gpt-4o-mini",
    "tools": ["web_search", "file_search"],
    "use_file_search": true,
    "user_id": 1,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
]
```

**POST `/api/agents`**
```json
Request: {
  "name": "Suporte",
  "description": "Atende dúvidas gerais",
  "instruction": "Você é um agente de suporte...",
  "model": "gpt-4o-mini",
  "tools": ["web_search"],
  "use_file_search": true
}
Response: AgentResponse (mesmo formato do GET)
```

**POST `/api/agents/chat`**
```json
Request: {
  "message": "Olá, como você está?",
  "agent_id": 1,  // Opcional: usa primeiro agente se não fornecido
  "session_id": "uuid-optional",
  "model": "gpt-4o-mini"  // Opcional: override do modelo do agente
}
Response: {
  "response": "Olá! Como posso ajudar?",
  "agent_id": 1,
  "agent_name": "Suporte",
  "session_id": "uuid-gerado",
  "model_used": "gpt-4o-mini"
}
```

---

## 💬 Conversas e Sessões (`/api/conversations`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/conversations/sessions` | Listar IDs de todas as sessões | ✅ |
| GET | `/api/conversations/sessions/{session_id}` | Histórico de mensagens da sessão | ✅ |
| GET | `/api/conversations/sessions/{session_id}/info` | Informações da sessão | ✅ |
| POST | `/api/conversations/sessions/{session_id}/messages` | Adicionar mensagem à sessão | ✅ |
| DELETE | `/api/conversations/sessions/{session_id}` | Deletar sessão específica | ✅ |
| DELETE | `/api/conversations/sessions` | Deletar todas as sessões | ✅ |

### Detalhes

**GET `/api/conversations/sessions`**
```json
Response: [
  "session-id-1",
  "session-id-2"
]
```

**GET `/api/conversations/sessions/{session_id}?limit=100`**
```json
Response: {
  "session_id": "session-id",
  "messages": [
    {
      "role": "user",
      "content": "Olá",
      "timestamp": "2025-01-01T10:00:00Z",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Olá! Como posso ajudar?",
      "timestamp": "2025-01-01T10:00:05Z",
      "metadata": {}
    }
  ]
}
```

**GET `/api/conversations/sessions/{session_id}/info`**
```json
Response: {
  "session_id": "session-id",
  "message_count": 10,
  "last_activity": "2025-01-01T10:00:00Z",
  "ttl": 3600
}
```

**POST `/api/conversations/sessions/{session_id}/messages`**
```json
Request: {
  "content": "Nova mensagem",
  "metadata": {
    "source": "web"
  }
}
Response: {
  "status": "success",
  "message": "Message saved"
}
```

---

## 🔗 Integração ADK (`/api/adk`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/adk/sessions/{session_id}/associate` | Associar sessão ao usuário | ✅ |

### Detalhes

**POST `/api/adk/sessions/{session_id}/associate`**
```json
Response: {
  "status": "success",
  "message": "Session associated with user"
}
```

---

## 👤 Usuário e Preferências (`/api/user`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/user/preferences` | Obter preferências do usuário | ✅ |
| PUT | `/api/user/preferences` | Atualizar preferências | ✅ |
| DELETE | `/api/user/preferences` | Resetar preferências | ✅ |
| GET | `/api/user/profile` | Obter perfil do usuário | ✅ |

### Detalhes

**GET `/api/user/preferences`**
```json
Response: {
  "theme": "dark",
  "language": "pt-BR",
  "layout": "compact",
  "notifications": true,
  "sidebar_expanded": false,
  "message_sound": true,
  "font_size": "medium"
}
```

**PUT `/api/user/preferences`**
```json
Request: {
  "theme": "dark",
  "language": "pt-BR"
}
Response: {
  "theme": "dark",
  "language": "pt-BR",
  // ... outras preferências existentes
}
```

---

## 🔌 LobeChat Compatibility (`/api`)

Endpoints compatíveis com frontend LobeChat (tRPC):

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/messages` | Obter mensagens (compatível com message.getMessages) | ✅ |
| GET | `/api/sessions/grouped` | Sessões agrupadas por data | ✅ |
| GET | `/api/topics` | Tópicos (retorna vazio) | ✅ |
| GET | `/api/plugins` | Plugins locais (retorna vazio) | ✅ |
| GET | `/api/market` | Marketplace (retorna vazio) | ✅ |

### Detalhes

**GET `/api/messages?session_id={id}&limit=100`**
```json
Response: [
  {
    "role": "user",
    "content": "Mensagem",
    "timestamp": "2025-01-01T10:00:00Z",
    "metadata": {}
  }
]
```

**GET `/api/sessions/grouped`**
```json
Response: [
  {
    "date": "2025-01-01",
    "sessions": [
      {
        "session_id": "session-id",
        "title": "Título da sessão",
        "message_count": 10,
        "last_activity": "2025-01-01T10:00:00Z",
        "ttl": 3600
      }
    ]
  }
]
```

---

## 📁 File Search / RAG (`/api/file-search`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/file-search/stores` | Listar stores de arquivos | ✅ |
| GET | `/api/file-search/stores/{store_id}` | Obter store específico | ✅ |
| POST | `/api/file-search/stores` | Criar novo store | ✅ |
| DELETE | `/api/file-search/stores/{store_id}` | Deletar store | ✅ |
| GET | `/api/file-search/stores/{store_id}/files` | Listar arquivos do store | ✅ |
| GET | `/api/file-search/stores/{store_id}/files/{file_id}` | Obter arquivo específico | ✅ |
| POST | `/api/file-search/stores/{store_id}/files` | Adicionar arquivo ao store | ✅ |
| DELETE | `/api/file-search/stores/{store_id}/files/{file_id}` | Deletar arquivo | ✅ |

---

## 🔌 MCP (Model Context Protocol) (`/api/mcp`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/mcp/connect` | Conectar a um provider MCP | ✅ |
| DELETE | `/api/mcp/disconnect/{provider}` | Desconectar de um provider | ✅ |
| GET | `/api/mcp/connections` | Listar conexões MCP ativas | ✅ |
| GET | `/api/mcp/status/{provider}` | Status de um provider | ✅ |
| GET | `/api/mcp/tools/{provider}` | Listar tools de um provider | ✅ |

---

## 📅 Google Calendar OAuth (`/api/mcp/google-calendar/oauth`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/mcp/google-calendar/oauth/authorize` | Iniciar fluxo OAuth | ✅ |
| GET | `/api/mcp/google-calendar/oauth/callback` | Callback OAuth (Google redireciona) | ❌ |
| GET | `/api/mcp/google_calendar/oauth/authorize` | Legacy path (compatibilidade) | ✅ |
| GET | `/api/mcp/google_calendar/oauth/callback` | Legacy callback | ❌ |

---

## 🤖 Modelos LLM (`/api/models`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/models` | Listar modelos suportados por provider | ❌ |

### Detalhes

**GET `/api/models`**
```json
Response: {
  "providers": {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro"],
    "anthropic": ["claude-3-5-sonnet-latest"]
  },
  "message": "These are the LLM models currently supported..."
}
```

---

## 🔄 OpenAI Compatible API (`/api/openai`)

Endpoints compatíveis com OpenAI para integração com LobeChat, LibreChat, etc:

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/openai/models` | Listar modelos (formato OpenAI) | ❌ |
| POST | `/api/openai/chat/completions` | Chat completions (formato OpenAI) | ✅ |

---

## 🏥 Health & Info

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/` | Informações da API | ❌ |
| GET | `/health` | Health check | ❌ |
| GET | `/docs` | Swagger UI | ❌ |
| GET | `/redoc` | ReDoc documentation | ❌ |

---

## 📊 Resumo por Categoria

| Categoria | Total de Endpoints | Com Auth | Sem Auth |
|-----------|-------------------|---------|----------|
| Autenticação | 5 | 1 | 4 |
| Agentes | 6 | 6 | 0 |
| Conversas | 6 | 6 | 0 |
| ADK | 1 | 1 | 0 |
| Usuário | 4 | 4 | 0 |
| LobeChat Compat | 5 | 5 | 0 |
| File Search | 8 | 8 | 0 |
| MCP | 5 | 5 | 0 |
| Google Calendar | 4 | 2 | 2 |
| Modelos | 1 | 0 | 1 |
| OpenAI Compat | 2 | 1 | 1 |
| Health | 4 | 0 | 4 |
| **TOTAL** | **51** | **39** | **12** |

---

## 🔒 Formato de Erro Padronizado

Todos os erros seguem o formato compatível com LobeChat:

```json
{
  "detail": [
    {
      "msg": "Mensagem de erro legível"
    }
  ],
  "message": "Mensagem de erro legível"
}
```

O frontend tenta ler `error.detail[0].msg` primeiro, depois `error.message` como fallback.

---

## 📝 Notas Importantes

1. **Autenticação**: Use `Authorization: Bearer <token>` no header para endpoints protegidos
2. **Base URL**: Configure `NEXT_PUBLIC_CUSTOM_API_BASE_URL` no frontend
3. **CORS**: API aceita requisições de qualquer origem (configurável em produção)
4. **Formato de Data**: Todas as datas são em formato ISO 8601 (`2025-01-01T10:00:00Z`)
5. **Session IDs**: Usam formato UUID v4
6. **Paginação**: Alguns endpoints suportam `limit` como query parameter

---

## 🔗 Documentação Adicional

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **CUSTOM_BACKEND_ENDPOINTS.md**: Contrato detalhado para LobeChat
- **LOBECHAT_COMPAT_API.md**: Documentação dos endpoints de compatibilidade

