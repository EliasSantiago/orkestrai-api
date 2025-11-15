# Cheat Sheet: Agentes On-Premise

Referência rápida para criar e gerenciar agentes usando provedor on-premise.

## 🚀 Quick Start (3 comandos)

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"seu@email.com","password":"senha"}' \
  | jq -r '.access_token')

# 2. Criar agente
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Meu Agente","model":"gpt-oss:20b","instruction":"Você é um assistente útil."}'

# 3. Conversar
curl -X POST http://localhost:8001/api/agents/1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Olá!","session_id":"test"}'
```

## 📋 Scripts Disponíveis

```bash
# Listar modelos disponíveis na API on-premise
python scripts/list_onpremise_models.py

# Criar agentes interativamente
python scripts/create_onpremise_agents.py

# Setup rápido (Bash)
./scripts/quick_setup_onpremise.sh

# Testar configuração
python scripts/test_onpremise_provider.py
```

## 🔐 Autenticação

### Obter Token

```bash
# Usando curl
curl -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@email.com","password":"senha123"}'

# Resposta:
# {"access_token":"eyJhbGc...","token_type":"bearer"}
```

### Usar Token

```bash
# Salvar em variável
export TOKEN="eyJhbGc..."

# Ou extrair automaticamente
TOKEN=$(curl -s -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@email.com","password":"pass"}' \
  | jq -r '.access_token')
```

## 🤖 Criar Agentes

### Template Básico

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nome do Agente",
    "description": "Descrição opcional",
    "model": "gpt-oss:20b",
    "instruction": "Suas instruções aqui",
    "tools": []
  }'
```

### Modelos Válidos

```bash
# Com dois-pontos (recomendado)
"model": "gpt-oss:20b"
"model": "llama-2:7b"
"model": "mixtral:8x7b"

# Com prefixo
"model": "local-custom"
"model": "onpremise-model"

# Personalizado (se configurado em ONPREMISE_MODELS)
"model": "seu-modelo-customizado"
```

### Com Ferramentas

```bash
# Apenas calculadora
"tools": ["calculator"]

# Calculadora + tempo
"tools": ["calculator", "time"]

# Todas as ferramentas
"tools": ["calculator", "time", "web_search"]
```

## 📦 Exemplos Prontos

### 1. Assistente Geral

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Geral",
    "model": "gpt-oss:20b",
    "instruction": "Você é um assistente útil que responde em português.",
    "tools": ["calculator", "time"]
  }'
```

### 2. Programador Python

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Expert Python",
    "model": "llama-2:7b",
    "instruction": "Você é expert em Python. Ajude com código e debugging.",
    "tools": []
  }'
```

### 3. Pesquisador Web

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pesquisador",
    "model": "gpt-oss:20b",
    "instruction": "Você é um pesquisador. Use busca web para informações atualizadas.",
    "tools": ["web_search", "time"]
  }'
```

### 4. Analista de Dados

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Analista de Dados",
    "model": "onpremise-analyst:latest",
    "instruction": "Você é analista de dados. Ajude com estatísticas e análises.",
    "tools": ["calculator"]
  }'
```

### 5. Atendente Virtual

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Atendente Virtual",
    "model": "local-customer-service:latest",
    "instruction": "Você é atendente virtual simpático e profissional.",
    "tools": ["time"]
  }'
```

## 💬 Conversar com Agentes

### Chat Básico

```bash
curl -X POST http://localhost:8001/api/agents/1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá! Como você está?",
    "session_id": "minha-sessao"
  }'
```

### Chat com Parâmetros

```bash
curl -X POST http://localhost:8001/api/agents/1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explique IA de forma simples",
    "session_id": "minha-sessao",
    "temperature": 0.5,
    "num_predict": 1000,
    "top_p": 0.9,
    "top_k": 40
  }'
```

### Parâmetros Disponíveis

```json
{
  "temperature": 0.1,      // 0.0-1.0 (criatividade)
  "top_p": 0.15,           // 0.0-1.0 (nucleus sampling)
  "top_k": 0,              // 0+ (top-k sampling)
  "num_predict": 500,      // max tokens
  "repeat_penalty": 1.1,   // 0.0-2.0
  "num_ctx": 4096,         // tamanho contexto
  "seed": 42               // reprodutibilidade
}
```

## 📋 Gerenciar Agentes

### Listar Todos

```bash
curl -X GET http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN"
```

### Ver Detalhes

```bash
curl -X GET http://localhost:8001/api/agents/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Atualizar

```bash
curl -X PUT http://localhost:8001/api/agents/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Nova instrução aqui",
    "tools": ["calculator", "time", "web_search"]
  }'
```

### Deletar

```bash
curl -X DELETE http://localhost:8001/api/agents/1 \
  -H "Authorization: Bearer $TOKEN"
```

## 🎯 Casos de Uso: Parâmetros Recomendados

### Respostas Criativas

```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40
}
```

### Respostas Precisas

```json
{
  "temperature": 0.1,
  "top_p": 0.15,
  "top_k": 0
}
```

### Conversas Longas

```json
{
  "num_predict": 2000,
  "num_ctx": 8192
}
```

### Respostas Determinísticas

```json
{
  "temperature": 0.0,
  "seed": 42
}
```

## 🔍 Verificações

### Testar Conexão

```bash
curl http://localhost:8001/health
```

### Ver Modelos Suportados

```bash
# Via script Python
python scripts/list_onpremise_models.py

# Ou diretamente na API on-premise
curl -X GET "https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/models" \
  -H "Authorization: Bearer OAUTH_TOKEN" \
  --insecure
```

### Testar OAuth

```bash
python scripts/test_onpremise_provider.py
```

## 🐍 Python: Criar Agente

```python
import requests

# Login
response = requests.post(
    "http://localhost:8001/api/login",
    json={"email": "user@email.com", "password": "pass"}
)
token = response.json()["access_token"]

# Criar agente
response = requests.post(
    "http://localhost:8001/api/agents",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "name": "Meu Agente",
        "model": "gpt-oss:20b",
        "instruction": "Você é um assistente útil.",
        "tools": ["calculator", "time"]
    }
)
agent = response.json()
print(f"Agente criado: {agent['id']}")

# Conversar
response = requests.post(
    f"http://localhost:8001/api/agents/{agent['id']}/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "Olá!",
        "session_id": "test"
    }
)
print(response.json())
```

## 🐚 Bash: Script Completo

```bash
#!/bin/bash

# Configuração
API="http://localhost:8001"
EMAIL="seu@email.com"
PASS="sua_senha"

# Login
TOKEN=$(curl -s -X POST "$API/api/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# Criar agente
AGENT_ID=$(curl -s -X POST "$API/api/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Assistente Teste",
    "model":"gpt-oss:20b",
    "instruction":"Você é um assistente útil.",
    "tools":["calculator"]
  }' | jq -r '.id')

echo "Agente criado: ID $AGENT_ID"

# Conversar
curl -X POST "$API/api/agents/$AGENT_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message":"Olá! Está funcionando?",
    "session_id":"test"
  }'
```

## ⚠️ Troubleshooting

### Erro 401: Unauthorized
```bash
# Token expirado ou inválido - faça login novamente
TOKEN=$(curl -s -X POST http://localhost:8001/api/login ...)
```

### Erro 404: Agent not found
```bash
# Verifique o ID do agente
curl -X GET http://localhost:8001/api/agents -H "Authorization: Bearer $TOKEN"
```

### Erro 400: Model not supported
```bash
# Use formato correto: modelo:versão ou local-/onpremise- prefixo
"model": "gpt-oss:20b"  # ✓
"model": "local-model"  # ✓
"model": "my-model"     # ✗
```

### Erro de OAuth
```bash
# Teste a configuração
python scripts/test_onpremise_provider.py
```

## 📚 Documentação Completa

- Setup completo: `docs/ONPREMISE_PROVIDER_SETUP.md`
- Quick start: `docs/ONPREMISE_QUICK_START.md`
- Exemplos: `docs/ONPREMISE_CREATE_AGENTS_EXAMPLES.md`
- Implementação: `docs/ONPREMISE_IMPLEMENTATION_SUMMARY.md`

## 🆘 Ajuda Rápida

```bash
# Listar modelos
python scripts/list_onpremise_models.py

# Criar agentes interativamente
python scripts/create_onpremise_agents.py

# Setup rápido
./scripts/quick_setup_onpremise.sh

# Testar provedor
python scripts/test_onpremise_provider.py

# API docs
open http://localhost:8001/docs
```

---

**Tudo pronto! Basta copiar e colar os comandos.** 🚀

