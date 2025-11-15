# 🚀 LobeChat + Sua API - Quick Start

## ⚡ Início Rápido (3 minutos)

### 1. Inicie sua API

```bash
cd /home/vdilinux/aplicações/api-adk-google-main
./scripts/start_backend.sh
```

✅ API rodando em: `http://localhost:8001`

---

### 2. Configure o LobeChat

Abra o LobeChat e configure conforme a imagem que você mostrou:

#### No campo "Chave de API personalizada":
```
your-api-key-here
```
(Pode ser qualquer valor por enquanto)

#### No campo "URL Base" (se disponível):
```
http://localhost:8001/v1
```

---

### 3. Teste!

Envie uma mensagem no LobeChat:
```
Olá! Como você está?
```

✅ Deve funcionar! O LobeChat vai usar sua API como backend.

---

## 🔧 Configuração Detalhada

### Se o LobeChat estiver online (https://lobehub.com)

**⚠️ Importante:** Para o LobeChat online acessar sua API local, você precisa expor sua API para a internet.

#### Opção 1: Ngrok (Mais Rápido)

```bash
# 1. Instale o ngrok
sudo snap install ngrok

# 2. Autentique (crie conta em https://ngrok.com)
ngrok authtoken YOUR_TOKEN

# 3. Exponha sua API
ngrok http 8001
```

Copie a URL gerada (ex: `https://abc123.ngrok.io`) e use no LobeChat:

```
Base URL: https://abc123.ngrok.io/v1
API Key: your-api-key-here
```

---

### Se você quer hospedar o LobeChat localmente

#### Docker (Recomendado)

```bash
docker run -d \
  --name lobechat \
  -p 3210:3210 \
  -e OPENAI_API_KEY=your-api-key-here \
  -e API_BASE_URL=http://host.docker.internal:8001/v1 \
  lobehub/lobe-chat:latest
```

Acesse: `http://localhost:3210`

---

## 📋 Modelos Disponíveis

Sua API suporta estes modelos via LiteLLM:

### Google Gemini
```
gemini/gemini-2.0-flash-exp
gemini/gemini-2.5-flash
gemini/gemini-1.5-pro
gemini/gemini-1.5-flash
```

### OpenAI
```
openai/gpt-4o
openai/gpt-4o-mini
openai/gpt-4-turbo
openai/gpt-3.5-turbo
```

### Anthropic Claude
```
anthropic/claude-3-opus-20240229
anthropic/claude-3-sonnet-20240229
anthropic/claude-3-haiku-20240307
```

### Ollama (Local)
```
ollama/llama2
ollama/llama3
ollama/mistral
ollama/codellama
```

---

## 🧪 Testar API Manualmente

### Listar Modelos

```bash
curl -X GET http://localhost:8001/v1/models \
  -H "Authorization: Bearer test-key"
```

### Chat

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini/gemini-2.0-flash-exp",
    "messages": [
      {"role": "user", "content": "Olá!"}
    ]
  }'
```

---

## 🐛 Problemas Comuns

### "Connection Refused"

**Solução:** Verifique se a API está rodando:
```bash
curl http://localhost:8001/health
```

### "Invalid API Key"

**Solução:** Use qualquer valor como API key:
```
Authorization: Bearer your-api-key-here
```

### "Model not found"

**Solução:** Use o formato correto:
- ✅ `gemini/gemini-2.0-flash-exp`
- ❌ `gemini-2.0-flash-exp`

### LobeChat não conecta

**Se LobeChat está no Docker:**
- Use `http://host.docker.internal:8001/v1` em vez de `http://localhost:8001/v1`

**Se LobeChat está online:**
- Use ngrok ou cloudflare tunnel para expor sua API com HTTPS

---

## 📚 Documentação Completa

Para configuração avançada, consulte:
- [`docs/LOBECHAT_INTEGRATION.md`](./docs/LOBECHAT_INTEGRATION.md) - Guia completo
- [`docs/arquitetura/litellm/`](./docs/arquitetura/litellm/) - Documentação LiteLLM

---

## ✅ Checklist

- [ ] API está rodando (`./scripts/start_backend.sh`)
- [ ] Configurou o LobeChat com a Base URL correta
- [ ] Configurou uma API Key (qualquer valor)
- [ ] Testou enviando uma mensagem
- [ ] Funciona! 🎉

---

**Dúvidas?** Consulte `docs/LOBECHAT_INTEGRATION.md` para troubleshooting detalhado.

**Última atualização:** 2025-11-12

