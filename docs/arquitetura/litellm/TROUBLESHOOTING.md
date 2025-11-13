# LiteLLM - Guia de Troubleshooting

Este guia ajuda a resolver problemas comuns ao usar o LiteLLM.

---

## 🔴 Problema: SSL Certificate Verification Failed

### Sintoma

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
```

### Causa

Este erro ocorre em **ambientes corporativos** que usam:
- Proxies SSL/TLS
- Certificados auto-assinados
- Interceptação SSL para inspeção de tráfego

### Solução

**⚠️ IMPORTANTE**: Esta solução é para ambientes de **desenvolvimento/staging apenas**. **NÃO** use em produção!

#### 1. Edite seu arquivo `.env`:

```bash
# SSL/TLS Configuration
# WARNING: Only disable SSL verification in development environments!
VERIFY_SSL=false
```

#### 2. Reinicie o servidor:

```bash
./scripts/start_backend.sh
```

#### 3. Verifique os logs:

Você deve ver esta mensagem no startup:

```
⚠️  SSL verification is DISABLED. This is insecure and should only be used in development!
```

### Solução para Produção

Em produção, **NÃO desabilite SSL**. Em vez disso:

1. **Instale o certificado CA corporativo**:

```bash
# Ubuntu/Debian
sudo cp seu-certificado-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

2. **Configure variáveis de ambiente Python**:

```bash
# No seu .env
REQUESTS_CA_BUNDLE=/path/to/your/ca-bundle.crt
SSL_CERT_FILE=/path/to/your/ca-bundle.crt
```

3. **Use proxy corporativo corretamente**:

```bash
# No seu .env
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=http://proxy.empresa.com:8080
NO_PROXY=localhost,127.0.0.1
```

---

## 🔴 Problema: Requested tools not found

### Sintoma

```
Requested tools not found: ['web_search', 'time']
```

### Causa

O agente está configurado para usar ferramentas (tools) que não estão disponíveis no sistema.

### Solução

#### Opção 1: Configurar as ferramentas faltantes

Para **web_search** usando Tavily (recomendado):

1. **Obtenha uma API key do Tavily**:
   - Acesse: https://tavily.com/
   - Crie uma conta gratuita
   - Copie sua API key

2. **Configure no `.env`**:

```bash
# Tavily API (Web Search optimized for AI)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxx
```

3. **Reinicie o servidor**

4. **Crie um novo agente** usando os exemplos:
   - `examples/agents/tavily_web_researcher.json`
   - `examples/agents/tavily_news_analyst.json`

#### Opção 2: Remover ferramentas do agente

Se você não precisa das ferramentas, **edite o agente** via API:

```bash
# Listar agentes
curl -X GET http://localhost:8001/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN"

# Atualizar agente (remover tools)
curl -X PUT http://localhost:8001/api/agents/8 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tools": []
  }'
```

#### Opção 3: Criar um novo agente sem ferramentas

Use os exemplos em `examples/agents/`:
- `gemini_assistant.json` - Simples, sem ferramentas
- `gpt4o_assistant.json` - GPT-4, sem ferramentas
- `claude_opus_writer.json` - Claude, sem ferramentas

```bash
# Criar agente sem ferramentas
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @examples/agents/gemini_assistant.json
```

---

## 🔴 Problema: Invalid Model Error

### Sintoma

```
InvalidModelError: Model 'gemini-2.5-flash' is not supported. 
Available models: {'LiteLLM': ['gemini/gemini-2.5-flash', ...]}
```

### Causa

O nome do modelo está no **formato antigo** (sem prefixo do provider).

### Solução

Use o formato **`provider/model-name`**:

❌ **Errado**:
```json
{
  "model": "gemini-2.5-flash"
}
```

✅ **Correto**:
```json
{
  "model": "gemini/gemini-2.5-flash"
}
```

### Tabela de Conversão

| Formato Antigo | Formato LiteLLM |
|---------------|----------------|
| `gemini-2.5-flash` | `gemini/gemini-2.5-flash` |
| `gpt-4o-mini` | `openai/gpt-4o-mini` |
| `gpt-4o` | `openai/gpt-4o` |
| `llama2` | `ollama/llama2` |
| `mistral` | `ollama/mistral` |

### Migrar agentes existentes

Use o script de migração:

```bash
# Backup do banco primeiro!
python scripts/migrate_models_to_litellm_format.py
```

---

## 🔴 Problema: Connection Timeout

### Sintoma

```
InternalServerError: OpenAIException - Connection timeout
```

### Solução

Aumente o timeout no `.env`:

```bash
# LiteLLM Configuration
LITELLM_REQUEST_TIMEOUT=1200  # 20 minutos (padrão: 600)
```

---

## 🔴 Problema: API Key Invalid

### Sintoma

```
AuthenticationError: Invalid API key provided
```

### Solução

1. **Verifique suas API keys** no `.env`:

```bash
# Google Gemini
GOOGLE_API_KEY=AIzaSy...

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...
```

2. **Teste as API keys**:

```bash
# Testar Gemini
curl https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY

# Testar OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

3. **Verifique se as variáveis estão carregadas**:

```bash
# No terminal onde roda a API
echo $GOOGLE_API_KEY
echo $OPENAI_API_KEY
```

---

## 🔴 Problema: Model Not Available

### Sintoma

```
Model 'gemini/gemini-2.5-flash' may not be available
```

### Solução

1. **Verifique se o modelo existe**:
   - Consulte: https://docs.litellm.ai/docs/providers

2. **Use um modelo alternativo**:

```bash
# Modelos Gemini disponíveis
- gemini/gemini-2.0-flash-exp  # Experimental (pode mudar)
- gemini/gemini-1.5-pro        # Estável
- gemini/gemini-1.5-flash      # Rápido

# Modelos OpenAI disponíveis
- openai/gpt-4o                # Latest GPT-4
- openai/gpt-4o-mini           # Mais barato
- openai/gpt-3.5-turbo         # Legacy
```

3. **Verifique sua quota/billing**:
   - Google AI Studio: https://aistudio.google.com/apikey
   - OpenAI: https://platform.openai.com/usage

---

## 🔴 Problema: Retries Esgotados

### Sintoma

```
LiteLLM Retried: 3 times
```

### Causa

Falha de rede ou API indisponível.

### Solução

1. **Aumente o número de retries**:

```bash
# .env
LITELLM_NUM_RETRIES=5  # Padrão: 3
```

2. **Verifique conectividade**:

```bash
# Testar conexão com OpenAI
ping api.openai.com

# Testar conexão com Google
ping generativelanguage.googleapis.com
```

3. **Use proxy se necessário**:

```bash
# .env
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=http://proxy.empresa.com:8080
```

---

## 🔍 Debug Mode

Para obter **mais informações** sobre erros:

```bash
# .env
LITELLM_VERBOSE=true
```

Isso exibirá logs detalhados de todas as requisições LiteLLM.

---

## 📞 Precisa de Ajuda?

1. **Documentação LiteLLM**: https://docs.litellm.ai/docs/
2. **Issues LiteLLM**: https://github.com/BerriAI/litellm/issues
3. **Documentação interna**: `docs/arquitetura/litellm/`
4. **Exemplos**: `examples/agents/`

---

## ✅ Checklist de Diagnóstico

Use este checklist para diagnosticar problemas:

- [ ] Verificou se `LITELLM_ENABLED=true` no `.env`
- [ ] Verificou as API keys (GOOGLE_API_KEY, OPENAI_API_KEY)
- [ ] Usou o formato correto do modelo (`provider/model-name`)
- [ ] Verificou conectividade de rede
- [ ] Verificou se há proxy/firewall bloqueando
- [ ] Habilitou `LITELLM_VERBOSE=true` para debug
- [ ] Verificou se o problema é SSL (certificado auto-assinado)
- [ ] Verificou se as ferramentas (tools) existem
- [ ] Reiniciou o servidor após mudar `.env`
- [ ] Verificou os logs do terminal para mensagens de erro

---

**Última atualização**: 2025-11-12
