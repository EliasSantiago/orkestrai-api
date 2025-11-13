# 🔧 Guia Rápido: Corrigir Erro SSL Certificate Verification

Este guia mostra **passo a passo** como corrigir o erro SSL que você está enfrentando.

---

## 🔴 Erro que você está vendo:

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: self-signed certificate in certificate chain
```

---

## ✅ Solução (3 minutos)

### Passo 1: Edite seu arquivo `.env`

Abra o arquivo `.env` na raiz do projeto e adicione ou modifique a seguinte linha:

```bash
# SSL/TLS Configuration
# WARNING: Only disable SSL verification in development environments!
VERIFY_SSL=false
```

**💡 Dica**: Se a linha `VERIFY_SSL` já existir, apenas mude para `false`.

### Passo 2: Reinicie o servidor

Pare o servidor atual (`Ctrl+C`) e reinicie:

```bash
./scripts/start_backend.sh
```

### Passo 3: Verifique os logs

Você deve ver esta mensagem no startup:

```
⚠️  SSL verification is DISABLED. This is insecure and should only be used in development!
✓ LiteLLM provider initialized (unified LLM gateway)
```

### Passo 4: Teste o chat novamente

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 8,
    "message": "Olá!",
    "session_id": ""
  }'
```

---

## 🔒 Por que isso acontece?

Você está em um **ambiente corporativo** que usa:
- **Proxy SSL/TLS** para interceptar tráfego HTTPS
- **Certificados auto-assinados** (self-signed certificates)
- **Inspeção SSL** para segurança corporativa

O Python/LiteLLM não confia nesses certificados por padrão, causando o erro.

---

## ⚠️ Importante: Segurança

### Para Desenvolvimento/Staging: ✅ OK usar `VERIFY_SSL=false`

Esta é a solução mais rápida e funciona bem para desenvolvimento.

### Para Produção: ❌ NÃO use `VERIFY_SSL=false`

Em produção, você **DEVE** usar uma das seguintes alternativas:

#### Opção 1: Instalar Certificado CA Corporativo

```bash
# Ubuntu/Debian
sudo cp certificado-ca-empresa.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Depois reinicie a API
./scripts/start_backend.sh
```

#### Opção 2: Configurar CA Bundle

No seu `.env`:

```bash
VERIFY_SSL=true
REQUESTS_CA_BUNDLE=/caminho/para/ca-bundle.crt
SSL_CERT_FILE=/caminho/para/ca-bundle.crt
```

#### Opção 3: Configurar Proxy Corretamente

No seu `.env`:

```bash
VERIFY_SSL=true
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=http://proxy.empresa.com:8080
NO_PROXY=localhost,127.0.0.1
```

---

## 📋 Configuração Completa do .env

Seu arquivo `.env` deve ter **no mínimo**:

```bash
# ==============================================
# LiteLLM Configuration (OBRIGATÓRIO)
# ==============================================

LITELLM_ENABLED=true
LITELLM_VERBOSE=false
LITELLM_NUM_RETRIES=3
LITELLM_REQUEST_TIMEOUT=600

# ==============================================
# SSL/TLS (Para corrigir erro SSL)
# ==============================================

VERIFY_SSL=false  # ⚠️  Apenas em desenvolvimento!

# ==============================================
# LLM Provider API Keys (pelo menos 1)
# ==============================================

# Google Gemini (https://aistudio.google.com/apikey)
GOOGLE_API_KEY=AIzaSy...

# OpenAI (https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-...

# Ollama (local)
OLLAMA_API_BASE_URL=http://localhost:11434

# ==============================================
# Web Search (Opcional mas recomendado)
# ==============================================

# Tavily API (https://tavily.com/)
TAVILY_API_KEY=tvly-...

# ==============================================
# Database & Redis
# ==============================================

DATABASE_URL=postgresql://agentuser:agentpass@localhost:5432/agentsdb
REDIS_HOST=localhost
REDIS_PORT=6379

# ==============================================
# JWT
# ==============================================

SECRET_KEY=sua-chave-secreta-aqui
```

---

## 🧪 Como testar se funcionou

### Teste 1: Verificar startup

Após reiniciar, deve aparecer:

```
✓ LiteLLM provider initialized (unified LLM gateway)
  → All models will be routed through LiteLLM
  → Supported: Gemini, OpenAI, Claude, Ollama, Azure, and 100+ more
```

### Teste 2: Fazer requisição de chat

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 8,
    "message": "Teste de conexão",
    "session_id": ""
  }'
```

**Sucesso**: Você deve receber uma resposta do LLM (não um erro 500).

---

## 🐛 Outros problemas comuns

### Problema: "Requested tools not found: ['web_search']"

**Solução**: Configure a API do Tavily:

```bash
# No .env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxx
```

Depois crie um agente com a ferramenta correta:

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @examples/agents/tavily_web_researcher.json
```

### Problema: "Invalid Model Error"

**Solução**: Use o formato `provider/model-name`:

❌ Errado: `"model": "gpt-4o-mini"`  
✅ Correto: `"model": "openai/gpt-4o-mini"`

❌ Errado: `"model": "gemini-2.5-flash"`  
✅ Correto: `"model": "gemini/gemini-2.5-flash"`

---

## 📚 Próximos passos

1. ✅ **Correção SSL aplicada** (você está aqui)
2. 📖 Leia: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Outros problemas comuns
3. 🎯 Teste: [USAGE_EXAMPLES.md](../../../examples/agents/USAGE_EXAMPLES.md) - Exemplos práticos
4. 🔧 Configure: [SETUP.md](./SETUP.md) - Setup completo

---

## 💬 Precisa de ajuda?

- **Documentação completa**: `docs/arquitetura/litellm/`
- **Exemplos de agentes**: `examples/agents/`
- **LiteLLM oficial**: https://docs.litellm.ai/docs/

---

**Última atualização**: 2025-11-12

