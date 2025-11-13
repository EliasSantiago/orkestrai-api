# 🔧 Solução para o Erro SSL

## 🔴 Problema Identificado

Você está enfrentando um **erro de certificado SSL** ao tentar usar o chat com o agente:

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: self-signed certificate in certificate chain
```

**Causa**: Ambiente corporativo com proxy SSL ou certificados auto-assinados.

---

## ✅ Solução Rápida (Escolha uma)

### Opção 1: Script Automático (Recomendado - 30 segundos)

Execute o script que criei para você:

```bash
./scripts/fix_ssl_error.sh
```

Este script irá:
- ✅ Fazer backup do seu `.env`
- ✅ Adicionar/atualizar `VERIFY_SSL=false`
- ✅ Mostrar instruções de como reiniciar

### Opção 2: Manual (2 minutos)

1. **Edite o arquivo `.env`** na raiz do projeto

2. **Adicione ou modifique** a seguinte linha:

```bash
# SSL/TLS Configuration
VERIFY_SSL=false
```

3. **Salve o arquivo**

---

## 🚀 Após aplicar a correção

### Passo 1: Reinicie o servidor

Pare o servidor atual (`Ctrl+C`) e reinicie:

```bash
./scripts/start_backend.sh
```

### Passo 2: Verifique os logs

Você deve ver:

```
⚠️  SSL verification is DISABLED. This is insecure and should only be used in development!
✓ LiteLLM provider initialized (unified LLM gateway)
  → All models will be routed through LiteLLM
  → Supported: Gemini, OpenAI, Claude, Ollama, Azure, and 100+ more
```

### Passo 3: Teste o chat

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 8,
    "message": "Olá! Teste de conexão.",
    "session_id": ""
  }'
```

**✅ Sucesso**: Você deve receber uma resposta do LLM (não um erro 500).

---

## 🐛 Outros Problemas Identificados

### Problema 2: Ferramentas não encontradas

Você também viu este aviso nos logs:

```
Requested tools not found: ['web_search', 'time']
```

**Solução**: Configure a API do Tavily para habilitar web search.

#### Como configurar Tavily:

1. **Obtenha uma API key gratuita**:
   - Acesse: https://tavily.com/
   - Crie uma conta (tier gratuito disponível)
   - Copie sua API key

2. **Adicione ao `.env`**:

```bash
# Tavily API (Web Search for AI)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxx
```

3. **Reinicie o servidor**

4. **Use os exemplos prontos**:
   - `examples/agents/tavily_web_researcher.json`
   - `examples/agents/tavily_news_analyst.json`
   - `examples/agents/tavily_fact_checker.json`
   - `examples/agents/tavily_tech_scout.json`

#### Criar agente com Tavily:

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d @examples/agents/tavily_web_researcher.json
```

---

## 📋 Checklist de Configuração Completa

Seu `.env` deve ter:

```bash
# ==============================================
# LiteLLM (OBRIGATÓRIO)
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
# API Keys (pelo menos 1)
# ==============================================

# Google Gemini
GOOGLE_API_KEY=AIzaSy...

# OpenAI
OPENAI_API_KEY=sk-...

# Ollama (opcional - para modelos locais)
OLLAMA_API_BASE_URL=http://localhost:11434

# ==============================================
# Web Search (Opcional mas recomendado)
# ==============================================
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

## ⚠️ Importante: Segurança

### Para Desenvolvimento: ✅ OK

```bash
VERIFY_SSL=false  # OK para desenvolvimento
```

### Para Produção: ❌ NÃO USE

**Nunca desabilite SSL em produção!**

Em produção, use uma destas alternativas:

#### Opção 1: Instalar certificado CA corporativo

```bash
sudo cp certificado-ca-empresa.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

#### Opção 2: Configurar CA Bundle

```bash
# No .env
VERIFY_SSL=true
REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
SSL_CERT_FILE=/path/to/ca-bundle.crt
```

#### Opção 3: Configurar proxy

```bash
# No .env
VERIFY_SSL=true
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=http://proxy.empresa.com:8080
```

---

## 📚 Documentação Completa

Criei documentação detalhada para você:

### Guias de Troubleshooting:

1. **[SSL_FIX_GUIDE.md](docs/arquitetura/litellm/SSL_FIX_GUIDE.md)**
   - Guia passo a passo para corrigir SSL (3 minutos)
   - Explicação detalhada do problema
   - Soluções para produção

2. **[TROUBLESHOOTING.md](docs/arquitetura/litellm/TROUBLESHOOTING.md)**
   - Todos os problemas comuns
   - SSL Certificate Error ✅
   - Tools not found ✅
   - Invalid Model Error
   - Connection Timeout
   - API Key Invalid
   - E muito mais...

### Exemplos de Agentes:

Criei 20+ exemplos prontos em `examples/agents/`:

**Agentes básicos:**
- `gemini_assistant.json` - Google Gemini
- `gpt4o_assistant.json` - OpenAI GPT-4
- `claude_opus_writer.json` - Anthropic Claude
- `ollama_llama2.json` - Ollama (local)

**Agentes com Web Search (Tavily):**
- `tavily_web_researcher.json` - Pesquisador web
- `tavily_news_analyst.json` - Analista de notícias
- `tavily_fact_checker.json` - Verificador de fatos
- `tavily_tech_scout.json` - Scout de tecnologia

**Agentes avançados:**
- `rag_file_search_agent.json` - RAG / File Search
- `multi_tool_agent.json` - Multi-tool
- `gemini_thinking.json` - Deep thinking

### Documentação LiteLLM:

- `docs/arquitetura/litellm/README.md` - Overview completo
- `docs/arquitetura/litellm/SETUP.md` - Setup passo a passo
- `docs/arquitetura/litellm/USAGE.md` - Como usar
- `docs/arquitetura/litellm/CONFIGURATION.md` - Configuração avançada
- `docs/arquitetura/litellm/ARCHITECTURE_CHANGE.md` - Mudanças arquiteturais
- `docs/arquitetura/litellm/MIGRATION_GUIDE.md` - Guia de migração

---

## 🧪 Como testar tudo

### Teste 1: Verificar configuração

```bash
# Ver modelos disponíveis
curl http://localhost:8001/api/agents/supported-models \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Teste 2: Criar agente simples

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste SSL Fix",
    "instruction": "Você é um assistente útil.",
    "model": "gemini/gemini-2.0-flash-exp"
  }'
```

### Teste 3: Chat com agente

```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": SEU_AGENT_ID,
    "message": "Olá! Estou testando após correção SSL.",
    "session_id": ""
  }'
```

---

## 🎯 Resumo

### O que foi feito:

1. ✅ **Identificado o problema**: SSL Certificate Verification Error
2. ✅ **Atualizado código**: Adicionado suporte a `VERIFY_SSL` no LiteLLM provider
3. ✅ **Criado script automático**: `scripts/fix_ssl_error.sh`
4. ✅ **Documentação completa**: 2 novos guias de troubleshooting
5. ✅ **Exemplos práticos**: 20+ exemplos de agentes prontos
6. ✅ **Identificado problema secundário**: Ferramentas não encontradas (Tavily)

### Próximos passos:

1. ⚙️ Execute: `./scripts/fix_ssl_error.sh`
2. 🔄 Reinicie: `./scripts/start_backend.sh`
3. ✅ Teste: Use o curl de exemplo acima
4. 📖 Configure: Tavily API key (opcional mas recomendado)
5. 🚀 Use: Exemplos em `examples/agents/`

---

## 💬 Precisa de ajuda?

- **Documentação**: `docs/arquitetura/litellm/`
- **Exemplos**: `examples/agents/`
- **LiteLLM oficial**: https://docs.litellm.ai/docs/

---

**Última atualização**: 2025-11-12

