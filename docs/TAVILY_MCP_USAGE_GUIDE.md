# 🔧 Como Usar Ferramentas Avançadas do Tavily MCP

## 📋 Processo Completo

### 1️⃣ Conectar ao Tavily MCP

Use o endpoint `POST /api/mcp/connect` para conectar:

```bash
curl -X 'POST' \
  'http://localhost:8001/api/mcp/connect' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "tavily",
    "credentials": {
      "api_key": "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"
    }
  }'
```

**Resposta esperada:**
```json
{
  "id": 1,
  "provider": "tavily",
  "is_active": true,
  "connected_at": "2025-11-10T10:00:00",
  "last_used_at": null,
  "metadata": {}
}
```

### 2️⃣ Verificar Ferramentas Disponíveis

Use o endpoint `GET /api/mcp/tools/tavily` para ver todas as ferramentas:

```bash
curl -X 'GET' \
  'http://localhost:8001/api/mcp/tools/tavily' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

**Resposta esperada:**
```json
{
  "tools": [
    {
      "name": "tavily_tavily-search",
      "description": "Search the web for information",
      "parameters": {...}
    },
    {
      "name": "tavily_tavily-extract",
      "description": "Extract data from web pages",
      "parameters": {...}
    },
    {
      "name": "tavily_tavily-map",
      "description": "Create structured map of websites",
      "parameters": {...}
    },
    {
      "name": "tavily_tavily-crawl",
      "description": "Systematically crawl websites",
      "parameters": {...}
    }
  ],
  "total": 4,
  "message": "Found 4 tools from tavily"
}
```

### 3️⃣ Adicionar Ferramentas ao Agente

Adicione as ferramentas desejadas ao campo `tools` do agente:

**Opção A: Criar novo agente**
```json
{
  "name": "Assistente Avançado Tavily",
  "description": "Agente com todas as ferramentas do Tavily",
  "instruction": "Use as ferramentas do Tavily para buscar, extrair, mapear e fazer crawling...",
  "model": "gemini-2.5-flash",
  "tools": [
    "get_current_time",
    "tavily_tavily-search",
    "tavily_tavily-extract",
    "tavily_tavily-map",
    "tavily_tavily-crawl"
  ],
  "use_file_search": false
}
```

**Opção B: Atualizar agente existente**
```bash
curl -X 'PUT' \
  'http://localhost:8001/api/agents/{agent_id}' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "tools": [
      "get_current_time",
      "tavily_tavily-search",
      "tavily_tavily-extract"
    ]
  }'
```

### 4️⃣ Usar o Chat Normalmente

Agora você pode usar o chat normalmente. O agente terá acesso às ferramentas do Tavily MCP:

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 9,
    "message": "Extraia os dados principais desta página: https://example.com",
    "session_id": "sua-session-id"
  }'
```

## 📋 Ferramentas Disponíveis

### `tavily_tavily-search`
- **Uso**: Buscar informações na web
- **Quando usar**: Notícias, previsões, informações atualizadas
- **Alternativa simples**: Use `tavily_web_search` (não precisa MCP)

### `tavily_tavily-extract`
- **Uso**: Extrair dados específicos de uma página web
- **Quando usar**: Quando você tem uma URL específica e quer extrair dados estruturados
- **Exemplo**: "Extraia o preço e especificações deste produto: https://..."

### `tavily_tavily-map`
- **Uso**: Mapear a estrutura de um website
- **Quando usar**: Entender a organização de um site, encontrar todas as páginas
- **Exemplo**: "Mapeie a estrutura do site https://example.com"

### `tavily_tavily-crawl`
- **Uso**: Fazer crawling sistemático de websites
- **Quando usar**: Análise profunda de um site, coletar dados de múltiplas páginas
- **Exemplo**: "Faça crawling do site https://example.com e me dê um resumo"

## ✅ Checklist Rápido

- [ ] Conectei ao Tavily MCP (`POST /api/mcp/connect`)
- [ ] Verifiquei as ferramentas disponíveis (`GET /api/mcp/tools/tavily`)
- [ ] Adicionei as ferramentas desejadas ao agente (campo `tools`)
- [ ] Testei o agente via chat

## 🔍 Verificar Status da Conexão

Use `GET /api/mcp/status/tavily` para verificar se está conectado:

```bash
curl -X 'GET' \
  'http://localhost:8001/api/mcp/status/tavily' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

**Resposta esperada:**
```json
{
  "connected": true,
  "message": "tavily connected and working",
  "connected_at": "2025-11-10T10:00:00",
  "last_used_at": "2025-11-10T10:05:00"
}
```

## 🔄 Desconectar

Se precisar desconectar:

```bash
curl -X 'DELETE' \
  'http://localhost:8001/api/mcp/disconnect/tavily' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

## 💡 Dica

- **Para busca simples**: Use `tavily_web_search` (não precisa MCP, só `.env`)
- **Para ferramentas avançadas**: Use MCP (`tavily_tavily-extract`, `tavily_tavily-map`, `tavily_tavily-crawl`)

## ⚠️ Importante

- A conexão MCP é **por usuário** - cada usuário precisa conectar sua própria conta
- A API key é criptografada e armazenada no banco de dados
- Você só precisa conectar **uma vez** - a conexão permanece ativa
- Se desconectar, as ferramentas MCP não estarão mais disponíveis para o agente

