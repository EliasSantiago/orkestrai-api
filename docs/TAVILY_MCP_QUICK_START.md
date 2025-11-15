# 🚀 Tavily MCP - Quick Start Guide

## ⚠️ Problema: Agente não consegue buscar na internet

Se o agente está dizendo que não consegue buscar informações, verifique:

### 1. ✅ Você conectou ao Tavily MCP?

**IMPORTANTE**: Antes de usar as ferramentas do Tavily, você **DEVE** conectar sua conta:

```bash
curl -X POST 'http://localhost:8001/api/mcp/connect' \
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

### 2. ✅ Verifique se está conectado

```bash
curl -X GET 'http://localhost:8001/api/mcp/status/tavily' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

Deve retornar:
```json
{
  "connected": true,
  "message": "tavily connected and working"
}
```

### 3. ✅ Liste as ferramentas disponíveis

```bash
curl -X GET 'http://localhost:8001/api/mcp/tools/tavily' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

Deve retornar uma lista de ferramentas como:
```json
{
  "tools": [
    {
      "name": "tavily_tavily-search",
      "description": "...",
      "parameters": {...}
    },
    ...
  ]
}
```

### 4. ✅ Verifique se o agente tem as ferramentas no campo `tools`

O agente **DEVE** ter as ferramentas do Tavily listadas no campo `tools`:

```json
{
  "name": "Assistente de Pesquisa",
  "tools": [
    "get_current_time",
    "tavily_tavily-search"
  ]
}
```

### 5. ✅ Verifique os logs

Quando você fizer uma requisição ao agente, verifique os logs. Você deve ver:

```
INFO: Loaded X tools from tavily MCP for user Y
INFO: Agent Z requested tools: ['tavily_tavily-search', ...]
INFO: Available tools in tool_map: ['calculator', 'get_current_time', 'tavily_tavily-search', ...]
INFO: Loaded N tools for agent Z
```

Se você ver:
```
WARNING: MCP tools for provider tavily not available: ...
```

Isso indica um problema na conexão ou na API do Tavily.

## 🔍 Troubleshooting

### Erro: "tavily not connected"

**Solução**: Conecte ao Tavily MCP primeiro (passo 1 acima).

### Erro: "tavily connection exists but is not working"

**Possíveis causas**:
1. API key inválida ou expirada
2. Problema de rede/conectividade
3. Servidor MCP do Tavily temporariamente indisponível

**Solução**: 
1. Verifique se a API key está correta
2. Tente reconectar: `DELETE /api/mcp/disconnect/tavily` e depois `POST /api/mcp/connect` novamente

### Ferramentas não aparecem no agente

**Possíveis causas**:
1. Agente não tem as ferramentas no campo `tools`
2. Nome das ferramentas está incorreto (deve ser `tavily_tavily-search`, não `tavily-search`)

**Solução**:
1. Verifique o campo `tools` do agente
2. Use `GET /api/mcp/tools/tavily` para ver os nomes corretos
3. Atualize o agente com os nomes corretos

### Agente diz que não consegue buscar, mas está conectado

**Possíveis causas**:
1. As ferramentas não foram carregadas corretamente
2. O agente não tem as ferramentas no campo `tools`
3. Erro na chamada da ferramenta

**Solução**:
1. Verifique os logs para ver se as ferramentas foram carregadas
2. Verifique se o agente tem `tavily_tavily-search` no campo `tools`
3. Teste a ferramenta diretamente: `GET /api/mcp/tools/tavily`

## 📝 Checklist Rápido

- [ ] Conectei ao Tavily MCP (`POST /api/mcp/connect`)
- [ ] Verifiquei que está conectado (`GET /api/mcp/status/tavily`)
- [ ] Liste as ferramentas disponíveis (`GET /api/mcp/tools/tavily`)
- [ ] Adicionei as ferramentas ao agente (campo `tools`)
- [ ] Verifiquei os logs ao usar o agente

## 🆘 Ainda não funciona?

1. Verifique os logs completos do servidor
2. Teste a conexão: `GET /api/mcp/status/tavily`
3. Teste listar ferramentas: `GET /api/mcp/tools/tavily`
4. Verifique se o agente tem as ferramentas corretas no campo `tools`

