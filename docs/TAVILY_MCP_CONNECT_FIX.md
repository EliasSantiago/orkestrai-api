# 🔧 Correção: Conectar ao Tavily MCP

## ✅ Correções Aplicadas

1. **Aceita ambos `api_key` e `access_token`** - O código agora aceita qualquer um dos dois
2. **Mensagens de erro melhoradas** - Agora mostra o erro específico do Tavily MCP
3. **Logs mais detalhados** - Para facilitar diagnóstico

## 📝 Como Conectar

### Opção 1: Usando `api_key` (Recomendado)

```bash
curl -X 'POST' \
  'http://localhost:8001/api/mcp/connect' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "tavily",
    "credentials": {
      "api_key": "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"
    }
  }'
```

### Opção 2: Usando `access_token` (Também funciona agora)

```bash
curl -X 'POST' \
  'http://localhost:8001/api/mcp/connect' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "tavily",
    "credentials": {
      "access_token": "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"
    }
  }'
```

## 🔍 Verificar Erros

Se ainda houver erro, verifique os logs do servidor. Agora eles mostram:
- Status HTTP da resposta
- Resposta completa do servidor Tavily
- Erro específico do Tavily MCP

## ⚠️ Possíveis Problemas

1. **API Key inválida**: Verifique se a chave está correta
2. **Servidor Tavily indisponível**: Pode ser temporário
3. **Problema de rede**: Verifique conectividade

## ✅ Teste Rápido

Depois de conectar, teste listar as ferramentas:

```bash
curl -X 'GET' \
  'http://localhost:8001/api/mcp/tools/tavily' \
  -H 'Authorization: Bearer SEU_TOKEN'
```

Se retornar uma lista de ferramentas, está funcionando! 🎉

