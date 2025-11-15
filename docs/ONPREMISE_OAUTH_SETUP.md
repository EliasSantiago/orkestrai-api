# Configuração de OAuth para API On-Premise

Este guia explica como configurar autenticação OAuth para APIs on-premise que exigem tokens Bearer.

## 📋 Visão Geral

A aplicação suporta autenticação OAuth para APIs on-premise usando o fluxo **OAuth 2.0 Password Grant**. O token é gerado automaticamente e cacheado para melhor performance.

## 🔧 Configuração

### 1. Adicionar Variáveis no `.env`

Adicione as seguintes variáveis de ambiente:

```env
# URL base da API on-premise
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/

# Endpoint de chat (OPCIONAL - padrão: /v1/chat/completions)
# Use se sua API não seguir o padrão OpenAI
# Exemplos: "/api/chat" ou "/chat"
ONPREMISE_CHAT_ENDPOINT=/api/chat

# URL para gerar token OAuth
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token

# Consumer Key e Secret (para autenticação OAuth)
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa

# Grant Type (padrão: client_credentials - não precisa de username/password)
ONPREMISE_OAUTH_GRANT_TYPE=client_credentials

# Username e Password (apenas se usar grant_type=password)
# ONPREMISE_USERNAME=seu_usuario
# ONPREMISE_PASSWORD=sua_senha

# Lista de modelos disponíveis (OPCIONAL - separados por vírgula)
# Se não configurar, qualquer nome de modelo será aceito (a API validará)
# ONPREMISE_MODELS=modelo1,modelo2,modelo3

# SSL Verification (se necessário desabilitar)
VERIFY_SSL=false
```

### 2. Estrutura da API

A API deve seguir o padrão OpenAI-compatible:

- **Endpoint de Chat:** `{ONPREMISE_API_BASE_URL}/v1/chat/completions`
- **Método:** POST
- **Headers:** 
  - `Content-Type: application/json`
  - `Authorization: Bearer {token}`
- **Body:** Formato OpenAI (veja exemplo abaixo)

### 3. Exemplo de Requisição

A aplicação faz requisições no formato:

```json
{
  "model": "nome-do-modelo",
  "messages": [
    {"role": "system", "content": "Instrução do agente"},
    {"role": "user", "content": "Mensagem do usuário"}
  ],
  "stream": true,
  "temperature": 0.7
}
```

## 🔐 Como Funciona

### Geração de Token

1. **Primeira Requisição:**
   - A aplicação gera um token OAuth usando consumer key/secret
   - Token é cacheado em memória

2. **Requisições Subsequentes:**
   - Token cacheado é reutilizado
   - Renovação automática quando próximo do vencimento

3. **Renovação:**
   - Token é renovado automaticamente antes de expirar
   - Margem de segurança de 60 segundos

### Fluxo de Autenticação

```
┌─────────────┐
│  Aplicação  │
└──────┬──────┘
       │
       │ 1. POST /token (com consumer key/secret)
       ▼
┌─────────────┐
│ Token Server│
└──────┬──────┘
       │
       │ 2. Retorna access_token
       ▼
┌─────────────┐
│  Aplicação  │
└──────┬──────┘
       │
       │ 3. POST /v1/chat/completions (com Bearer token)
       ▼
┌─────────────┐
│  API LLM    │
└─────────────┘
```

## 📝 Exemplo de Configuração Completa

```env
# API On-Premise
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa
ONPREMISE_USERNAME=seu_usuario
ONPREMISE_PASSWORD=sua_senha
ONPREMISE_MODELS=modelo1,modelo2

# SSL (se necessário)
VERIFY_SSL=false
```

## 🧪 Testando

### 1. Verificar Configuração

```bash
# Verificar se o provider está configurado
curl http://localhost:8001/api/models
```

### 2. Criar Agente com Modelo On-Premise

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente On-Premise",
    "model": "modelo1",
    "description": "Agente usando modelo on-premise",
    "instruction": "Você é um assistente útil."
  }'
```

### 3. Testar Chat

```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "message": "Olá, como você pode me ajudar?"
  }'
```

## 🔍 Troubleshooting

### Erro: "Failed to generate OAuth token"

**Causa:** Problema ao gerar token OAuth

**Soluções:**
1. Verifique se `ONPREMISE_TOKEN_URL` está correto
2. Verifique se `ONPREMISE_CONSUMER_KEY` e `ONPREMISE_CONSUMER_SECRET` estão corretos
3. Verifique se `ONPREMISE_USERNAME` e `ONPREMISE_PASSWORD` estão corretos
4. Verifique conectividade com o servidor
5. Se usar certificado autoassinado, adicione `VERIFY_SSL=false`

### Erro: "Erro de certificado SSL"

**Solução:** Adicione no `.env`:
```env
VERIFY_SSL=false
```

### Token não está sendo usado

**Verifique:**
1. Se todas as variáveis OAuth estão configuradas
2. Se o provider on-premise está sendo usado (verifique o modelo do agente)
3. Logs da aplicação para mensagens de erro

## 🔒 Segurança

- **Nunca** commite o arquivo `.env` com credenciais
- **Use** variáveis de ambiente em produção
- **Rotacione** consumer keys/secrets regularmente
- **Monitore** logs para detectar tentativas de acesso não autorizadas

## 📚 Referências

- [OAuth 2.0 Password Grant](https://oauth.net/2/grant-types/password/)
- [OpenAI-Compatible API Spec](https://platform.openai.com/docs/api-reference)

