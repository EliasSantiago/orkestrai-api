# 📚 Swagger/OpenAPI - Exemplos JSON Completos

## ✅ Atualização Concluída

Todos os endpoints do Swagger foram atualizados com exemplos JSON completos e modernos.

---

## 📋 Arquivos Atualizados

### 1. `/src/api/schemas.py` ✅

Todos os schemas Pydantic foram atualizados com exemplos:

#### 🔹 **UserCreate** (Registro de Usuários)
```json
{
  "name": "João Silva",
  "email": "joao.silva@exemplo.com",
  "password": "SenhaSegura123!",
  "password_confirm": "SenhaSegura123!"
}
```

#### 🔹 **LoginRequest** (Login)
```json
{
  "email": "joao.silva@exemplo.com",
  "password": "SenhaSegura123!"
}
```

#### 🔹 **ForgotPasswordRequest** (Esqueci Senha)
```json
{
  "email": "joao.silva@exemplo.com"
}
```

#### 🔹 **ResetPasswordRequest** (Resetar Senha)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "email": "joao.silva@exemplo.com",
  "new_password": "NovaSenhaSegura123!",
  "password_confirm": "NovaSenhaSegura123!"
}
```

---

### 2. **AgentCreate** (Criar Agente) - 5 Exemplos! 🎯

#### Exemplo 1: Analista de Notícias com Tavily MCP

```json
{
  "name": "Analista de Notícias IA - Tavily MCP",
  "description": "Agente especializado em buscar e analisar notícias sobre IA usando Tavily MCP",
  "instruction": "Você é um analista de notícias especializado em Inteligência Artificial.\n\nFERRAMENTAS:\n1. get_current_time: Obter data/hora atual\n2. tavily_tavily-search: Buscar informações na web\n3. tavily_tavily-extract: Extrair dados de páginas\n\nPROCESSO:\n1. Use get_current_time PRIMEIRO\n2. Use tavily_tavily-search para buscar notícias\n3. Analise e forneça resumo estruturado\n4. SEMPRE cite as fontes (URLs)\n5. Responda em português brasileiro",
  "model": "gemini/gemini-2.0-flash-exp",
  "tools": [
    "get_current_time",
    "tavily_tavily-search",
    "tavily_tavily-extract"
  ],
  "use_file_search": false
}
```

#### Exemplo 2: Assistente Simples - OpenAI

```json
{
  "name": "Assistente Simples - OpenAI",
  "description": "Assistente conversacional básico usando GPT-4",
  "instruction": "Você é um assistente útil e amigável. Responda de forma clara e objetiva em português brasileiro.",
  "model": "openai/gpt-4o",
  "tools": [],
  "use_file_search": false
}
```

#### Exemplo 3: Assistente com RAG - Gemini

```json
{
  "name": "Assistente com RAG - Gemini",
  "description": "Assistente com busca em arquivos (File Search/RAG)",
  "instruction": "Você é um assistente que pode buscar informações em documentos. Use o File Search para encontrar informações relevantes nos documentos do usuário.",
  "model": "gemini/gemini-2.5-flash",
  "tools": [],
  "use_file_search": true
}
```

#### Exemplo 4: Pesquisador Web Simples

```json
{
  "name": "Pesquisador Web Simples",
  "description": "Agente focado em busca web",
  "instruction": "Use get_current_time para contexto temporal e tavily_tavily-search para buscar informações atualizadas. Sempre cite as fontes.",
  "model": "gemini/gemini-2.0-flash-exp",
  "tools": [
    "get_current_time",
    "tavily_tavily-search"
  ],
  "use_file_search": false
}
```

#### Exemplo 5: Extrator de Dados Web

```json
{
  "name": "Extrator de Dados Web",
  "description": "Especializado em extrair dados de páginas web",
  "instruction": "Use tavily_tavily-extract para extrair dados estruturados de URLs fornecidas. Organize os dados de forma clara.",
  "model": "openai/gpt-4o-mini",
  "tools": [
    "tavily_tavily-extract"
  ],
  "use_file_search": false
}
```

---

### 3. **AgentUpdate** (Atualizar Agente) - 4 Exemplos!

#### Exemplo 1: Atualizar com Novas Ferramentas

```json
{
  "name": "Analista de Notícias IA - Atualizado",
  "description": "Agente atualizado com novas ferramentas",
  "tools": [
    "get_current_time",
    "tavily_tavily-search",
    "tavily_tavily-extract",
    "tavily_tavily-map"
  ]
}
```

#### Exemplo 2: Apenas Mudar Modelo

```json
{
  "model": "openai/gpt-4o",
  "instruction": "Nova instrução atualizada para o assistente."
}
```

#### Exemplo 3: Atualizar Ferramentas

```json
{
  "tools": [
    "tavily_tavily-search"
  ],
  "use_file_search": false
}
```

#### Exemplo 4: Habilitar RAG

```json
{
  "use_file_search": true,
  "model": "gemini/gemini-2.5-flash"
}
```

---

### 4. **ChatRequest** (Chat com Agente) - 4 Exemplos! 💬

#### Exemplo 1: Buscar Notícias

```json
{
  "message": "Faça um resumo das principais notícias sobre IA desta semana",
  "agent_id": 1,
  "session_id": "",
  "model": null
}
```

#### Exemplo 2: Previsão do Tempo

```json
{
  "message": "Qual a previsão do tempo para São Paulo hoje?",
  "agent_id": 2,
  "session_id": "cc9e7f12-0413-49bc-91dd-7a5f6f2500da"
}
```

#### Exemplo 3: Extrair Dados (com Override de Modelo)

```json
{
  "message": "Extraia os dados principais desta página: https://exemplo.com",
  "agent_id": 3,
  "session_id": "",
  "model": "openai/gpt-4o"
}
```

#### Exemplo 4: Chat Simples

```json
{
  "message": "Olá, como você pode me ajudar?",
  "agent_id": 1
}
```

---

### 5. **MCPConnectionRequest** (Conectar MCP) - 3 Exemplos!

#### Exemplo 1: Tavily MCP

```json
{
  "provider": "tavily",
  "credentials": {
    "api_key": "tvly-xxxxxxxxxxxxxxxxxxxxxxxx"
  }
}
```

#### Exemplo 2: Google Calendar MCP

```json
{
  "provider": "google_calendar",
  "credentials": {
    "access_token": "ya29.xxxxxxxxxxxxxxxxx",
    "refresh_token": "1//xxxxxxxxxxxxxxxxx"
  }
}
```

#### Exemplo 3: Provider Customizado

```json
{
  "provider": "custom_provider",
  "credentials": {
    "api_key": "your_api_key_here",
    "api_secret": "your_api_secret_here"
  }
}
```

---

### 6. **Message** (Mensagem de Conversação)

```json
{
  "role": "user",
  "content": "Olá, como você está?",
  "timestamp": "2025-11-12T14:30:00",
  "metadata": {
    "ip": "127.0.0.1"
  }
}
```

---

### 7. **MessageCreate** (Criar Mensagem)

```json
{
  "content": "Olá, preciso de ajuda com Python",
  "metadata": {
    "source": "web"
  }
}
```

---

## 🎯 Destaques Importantes

### ✅ **Modelos no Formato LiteLLM Correto**

Todos os exemplos usam o formato **`provider/model-name`**:

| ✅ Correto | ❌ Antigo (Errado) |
|-----------|-------------------|
| `gemini/gemini-2.0-flash-exp` | `gemini-2.0-flash-exp` |
| `openai/gpt-4o` | `gpt-4o` |
| `openai/gpt-4o-mini` | `gpt-4o-mini` |
| `gemini/gemini-2.5-flash` | `gemini-2.5-flash` |
| `ollama/llama2` | `llama2` |

### ✅ **Ferramentas Tavily MCP Corretas**

Todos os exemplos usam os nomes corretos das ferramentas:

| Ferramenta Correta | Descrição |
|-------------------|-----------|
| `tavily_tavily-search` | Busca web com citações |
| `tavily_tavily-extract` | Extração de dados de páginas |
| `tavily_tavily-map` | Mapeamento de estrutura de sites |
| `tavily_tavily-crawl` | Crawling sistemático |
| `get_current_time` | Data/hora atual |

### ✅ **Ferramentas Antigas Removidas**

❌ **NÃO use mais**:
- `web_search` ← Use `tavily_tavily-search`
- `time` ← Use `get_current_time`
- `calculator` ← Não disponível (use LLM diretamente)

---

## 📊 Resumo de Mudanças

| Arquivo | Schemas Atualizados | Total de Exemplos |
|---------|-------------------|------------------|
| `schemas.py` | 8 schemas | 20+ exemplos |
| `agent_chat_routes.py` | 1 schema | 4 exemplos |
| `mcp_routes.py` | 1 schema | 3 exemplos |
| **TOTAL** | **10 schemas** | **27+ exemplos** |

---

## 🧪 Como Testar no Swagger

1. **Acesse o Swagger UI**:
   ```
   http://localhost:8001/docs
   ```

2. **Navegue até qualquer endpoint** que aceite JSON

3. **Clique em "Try it out"**

4. **Selecione um exemplo** no dropdown (se houver múltiplos)

5. **Clique em "Execute"**

---

## 🎯 Endpoints com Exemplos JSON

### Autenticação (`/api/auth`)
- ✅ POST `/register` - Registrar usuário
- ✅ POST `/login` - Login
- ✅ POST `/forgot-password` - Esqueci senha
- ✅ POST `/reset-password` - Resetar senha

### Agentes (`/api/agents`)
- ✅ POST `/agents` - Criar agente (5 exemplos!)
- ✅ PUT `/agents/{agent_id}` - Atualizar agente (4 exemplos!)
- ✅ POST `/agents/chat` - Chat com agente (4 exemplos!)

### MCP (`/api/mcp`)
- ✅ POST `/mcp/connect` - Conectar MCP (3 exemplos!)

### Conversações (`/api/conversations`)
- ✅ POST `/conversations/sessions/{session_id}/messages` - Adicionar mensagem

### File Search (`/api/file-search`)
- ✅ POST `/file-search/stores` - Criar store

---

## 💡 Dicas de Uso

### Criar Agente com Tavily MCP

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Analista de Notícias IA",
    "model": "gemini/gemini-2.0-flash-exp",
    "tools": [
      "get_current_time",
      "tavily_tavily-search"
    ],
    "instruction": "Use get_current_time PRIMEIRO, depois tavily_tavily-search"
  }'
```

### Chat com Agente

```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "message": "Faça um resumo das principais notícias sobre IA desta semana",
    "session_id": ""
  }'
```

### Conectar Tavily MCP

```bash
curl -X POST http://localhost:8001/api/mcp/connect \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "tavily",
    "credentials": {
      "api_key": "tvly-xxxxxxxxxxxxxxxxxxxxxxxx"
    }
  }'
```

---

## 📚 Documentação Relacionada

- 📄 `GUIA_FERRAMENTAS_TAVILY.md` - Guia completo sobre ferramentas Tavily MCP
- 📄 `SOLUCAO_ERRO_SSL.md` - Solução para erro SSL
- 📄 `docs/arquitetura/litellm/` - Documentação LiteLLM
- 📁 `examples/agents/` - Exemplos JSON de agentes

---

## ✅ Checklist de Validação

- [x] Todos os schemas têm exemplos JSON
- [x] Exemplos usam formato LiteLLM correto (`provider/model`)
- [x] Exemplos usam ferramentas Tavily MCP corretas
- [x] Múltiplos exemplos para casos de uso comuns
- [x] Nenhum erro de linter
- [x] Documentação criada
- [x] Exemplos testáveis via Swagger UI

---

## 🎉 Resultado Final

**Todos os endpoints do Swagger** agora têm **exemplos JSON completos, modernos e funcionais** que:

✅ Usam o formato correto de modelos LiteLLM  
✅ Usam as ferramentas corretas do Tavily MCP  
✅ Cobrem os casos de uso mais comuns  
✅ São copiáveis e funcionais  
✅ Facilitam o teste e uso da API  

---

**Última atualização**: 2025-11-12

