# Configuração de Endpoint para API On-Premise

## 📍 Endpoint Atual vs Endpoint Correto

### Problema

A aplicação estava usando o endpoint padrão OpenAI:
```
https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/v1/chat/completions
```

Mas sua API usa um endpoint diferente:
```
https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/api/chat
```

## ✅ Solução

Adicione a variável `ONPREMISE_CHAT_ENDPOINT` no seu `.env`:

```env
# URL base da API
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/

# Endpoint de chat customizado
ONPREMISE_CHAT_ENDPOINT=/api/chat
```

## 🔧 Como Funciona

### Sem Configuração (Padrão OpenAI)

Se você **NÃO** configurar `ONPREMISE_CHAT_ENDPOINT`:

```env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
# ONPREMISE_CHAT_ENDPOINT não configurado
```

**Endpoint usado:**
```
https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/v1/chat/completions
```

### Com Configuração Customizada

Se você **configurar** `ONPREMISE_CHAT_ENDPOINT`:

```env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/api/chat
```

**Endpoint usado:**
```
https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/api/chat
```

## 📋 Exemplos de Configuração

### Exemplo 1: `/api/chat`

```env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/api/chat
```

**Resultado:**
```
https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/api/chat
```

### Exemplo 2: `/chat`

```env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/chat
```

**Resultado:**
```
https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/chat
```

### Exemplo 3: Endpoint Completo

```env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/v2/chat/completions
```

**Resultado:**
```
https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/v2/chat/completions
```

## 🔍 Como Descobrir o Endpoint Correto

### Opção 1: Documentação da API

Consulte a documentação da sua API on-premise para ver qual endpoint usar.

### Opção 2: Teste Manual

Teste os endpoints manualmente:

```bash
# Teste /api/chat
curl -X POST https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/api/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-oss:20b", "messages": [{"role": "user", "content": "teste"}]}'

# Teste /chat
curl -X POST https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-oss:20b", "messages": [{"role": "user", "content": "teste"}]}'
```

O que funcionar é o endpoint correto.

### Opção 3: Verificar Logs

Após configurar, verifique os logs da aplicação:

```
🌐 Chamando API on-premise: https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/api/chat
```

## ⚙️ Configuração Completa Recomendada

Para sua API, use:

```env
# API On-Premise
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/api/chat

# OAuth
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa
ONPREMISE_OAUTH_GRANT_TYPE=client_credentials

# SSL
VERIFY_SSL=false
```

## ✅ Verificação

Após configurar, reinicie a aplicação e teste. Os logs devem mostrar:

```
🌐 Chamando API on-premise: https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/api/chat
📡 Resposta recebida: HTTP 200
```

Se ainda receber 404, verifique:
1. Se o endpoint está correto na documentação da API
2. Se a URL base está correta
3. Se o endpoint precisa de autenticação diferente

