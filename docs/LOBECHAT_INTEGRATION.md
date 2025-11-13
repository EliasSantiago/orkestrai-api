# 🎨 Integração com LobeChat

## 📋 Visão Geral

Este guia mostra como usar sua **API FastAPI com LiteLLM** como backend para o **LobeChat**.

**O que foi implementado:**
- ✅ Endpoints compatíveis com OpenAI API (`/v1/models`, `/v1/chat/completions`)
- ✅ Suporte a streaming e non-streaming
- ✅ Roteamento automático via LiteLLM para 100+ modelos
- ✅ Autenticação via Bearer token

---

## 🏗️ Arquitetura

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│             │         │                  │         │                 │
│  LobeChat   │ ──────> │  Sua API FastAPI │ ──────> │    LiteLLM      │
│  (Frontend) │         │  (Backend/Proxy) │         │    (Roteador)   │
│             │         │                  │         │                 │
└─────────────┘         └──────────────────┘         └─────────────────┘
      │                        │                             │
      │                        │                             │
      │                        │                             ├─> Gemini
      │                        │                             ├─> OpenAI
      │                        │                             ├─> Claude
      │                        │                             ├─> Ollama
      └────────────────────────┴─────────────────────────────┴─> Azure
                                                              
```

**Fluxo:**
1. LobeChat envia requisição para `/v1/chat/completions`
2. Sua API valida autenticação
3. LiteLLM roteia para o modelo correto
4. Resposta é enviada de volta ao LobeChat

---

## 🚀 Passo a Passo

### 1. Certifique-se de que sua API está rodando

```bash
# Inicie o servidor
./scripts/start_backend.sh
```

Sua API estará disponível em: `http://localhost:8001`

### 2. Endpoints OpenAI-Compatible Disponíveis

#### **GET /v1/models** - Listar modelos

```bash
curl -X GET http://localhost:8001/v1/models \
  -H "Authorization: Bearer your-api-key-here"
```

**Resposta:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "gemini/gemini-2.0-flash-exp",
      "object": "model",
      "created": 1699500000,
      "owned_by": "litellm"
    },
    {
      "id": "openai/gpt-4o",
      "object": "model",
      "created": 1699500000,
      "owned_by": "litellm"
    }
    // ... mais modelos
  ]
}
```

#### **POST /v1/chat/completions** - Chat

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini/gemini-2.0-flash-exp",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "stream": true
  }'
```

---

## 🎨 Configurar LobeChat

### Opção 1: Usando LobeChat Hospedado (Mais Fácil)

Se você está usando o LobeChat hospedado em https://lobehub.com ou outra instância online:

1. **Acesse as Configurações** no LobeChat

2. **Vá para "Configurações de Modelo"** ou "Model Provider"

3. **Selecione "Custom OpenAI"** ou "OpenAI Compatible"

4. **Configure:**
   - **Base URL:** `http://SEU_IP:8001/v1`
   - **API Key:** Qualquer valor (ex: `your-api-key-here`)
   - **Model:** `gemini/gemini-2.0-flash-exp` (ou outro modelo)

5. **Salve e teste!**

### Opção 2: Self-Hosting LobeChat (Controle Total)

Se você quer hospedar o LobeChat você mesmo:

#### Usando Docker (Recomendado)

```bash
# 1. Clone o repositório do LobeChat
git clone https://github.com/lobehub/lobe-chat.git
cd lobe-chat

# 2. Crie arquivo .env
cat > .env << 'EOF'
# API Configuration
OPENAI_API_KEY=your-api-key-here
API_BASE_URL=http://localhost:8001/v1

# Database (opcional)
DATABASE_URL=postgresql://user:password@localhost:5432/lobechat

# Other settings
ACCESS_CODE=your-access-code
EOF

# 3. Inicie com Docker
docker-compose up -d
```

#### Usando Docker Run

```bash
docker run -d \
  --name lobechat \
  -p 3210:3210 \
  -e OPENAI_API_KEY=your-api-key-here \
  -e API_BASE_URL=http://host.docker.internal:8001/v1 \
  -e ACCESS_CODE=your-access-code \
  lobehub/lobe-chat:latest
```

**⚠️ Importante:** Use `host.docker.internal` em vez de `localhost` se o LobeChat estiver no Docker e sua API no host.

#### Configuração Avançada

Crie `docker-compose.yml`:

```yaml
version: '3.8'

services:
  lobechat:
    image: lobehub/lobe-chat:latest
    container_name: lobechat
    ports:
      - "3210:3210"
    environment:
      # API Backend
      OPENAI_API_KEY: "your-api-key-here"
      API_BASE_URL: "http://host.docker.internal:8001/v1"
      
      # Access Control
      ACCESS_CODE: "your-access-code"
      
      # Optional: Database
      # DATABASE_URL: "postgresql://user:password@postgres:5432/lobechat"
      
      # Optional: Analytics
      # ENABLE_OAUTH_SSO: "true"
      # NEXTAUTH_URL: "http://localhost:3210"
    restart: unless-stopped
```

Depois execute:

```bash
docker-compose up -d
```

---

## 🔧 Configuração via Interface do LobeChat

### Passo 1: Acessar Configurações

1. Abra o LobeChat: `http://localhost:3210`
2. Clique no ícone de ⚙️ (Configurações)
3. Vá para **"Configurações do Modelo"** ou **"Model Settings"**

### Passo 2: Adicionar Provider Customizado

1. Clique em **"Adicionar Provider"** ou **"Add Provider"**
2. Selecione **"Custom OpenAI"**
3. Preencha:

```
Nome: Minha API LiteLLM
Base URL: http://localhost:8001/v1
API Key: your-api-key-here
```

### Passo 3: Adicionar Modelos

Adicione os modelos que você quer usar:

```
gemini/gemini-2.0-flash-exp
openai/gpt-4o
openai/gpt-4o-mini
anthropic/claude-3-opus-20240229
ollama/llama2
```

### Passo 4: Testar

1. Crie uma nova conversa
2. Selecione o modelo que você configurou
3. Envie uma mensagem
4. ✅ Deve funcionar!

---

## 🌐 Expor para Internet (Produção)

### Opção 1: Ngrok (Desenvolvimento/Teste)

```bash
# Instale o ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Autentique (crie conta em https://ngrok.com)
ngrok authtoken YOUR_AUTH_TOKEN

# Exponha sua API
ngrok http 8001
```

Copie a URL gerada (ex: `https://abc123.ngrok.io`) e use no LobeChat:

```
Base URL: https://abc123.ngrok.io/v1
```

### Opção 2: Cloudflare Tunnel (Produção)

```bash
# Instale o cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Autentique
cloudflared tunnel login

# Crie um tunnel
cloudflared tunnel create my-api

# Configure
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: my-api
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: api.seudominio.com
    service: http://localhost:8001
  - service: http_status:404
EOF

# Inicie o tunnel
cloudflared tunnel run my-api
```

### Opção 3: Nginx Reverse Proxy (Produção)

```nginx
server {
    listen 80;
    server_name api.seudominio.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Depois configure HTTPS com Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.seudominio.com
```

---

## 🔐 Autenticação e Segurança

### Implementar API Key Validation

Edite `/src/api/openai_compatible_routes.py`:

```python
# Adicione no início do arquivo
VALID_API_KEYS = {
    "sk-lobechat-xxx": "user1",
    "sk-mobile-app-yyy": "user2",
    # Adicione mais keys aqui
}

def validate_api_key(authorization: Optional[str]) -> bool:
    """Validate API key from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        return False
    
    token = authorization[7:]
    return token in VALID_API_KEYS
```

### Configurar CORS para Produção

Edite `/src/api/main.py`:

```python
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lobehub.com",
        "https://seu-lobechat.vercel.app",
        "http://localhost:3210",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoramento e Logs

### Ver Logs da API

```bash
# Seguir logs em tempo real
tail -f logs/app.log

# Filtrar requisições do LobeChat
tail -f logs/app.log | grep "/v1/"
```

### Métricas

A API automaticamente loga:
- ✅ Modelos usados
- ✅ Tokens consumidos
- ✅ Tempo de resposta
- ✅ Erros

---

## 🧪 Testar Integração

### Teste 1: Listar Modelos

```bash
curl -X GET http://localhost:8001/v1/models \
  -H "Authorization: Bearer test-key"
```

**✅ Sucesso:** Deve retornar lista de modelos

### Teste 2: Chat Simples

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini/gemini-2.0-flash-exp",
    "messages": [
      {"role": "user", "content": "Olá!"}
    ],
    "stream": false
  }'
```

**✅ Sucesso:** Deve retornar resposta do modelo

### Teste 3: Streaming

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini/gemini-2.0-flash-exp",
    "messages": [
      {"role": "user", "content": "Conte uma história curta"}
    ],
    "stream": true
  }'
```

**✅ Sucesso:** Deve ver chunks de texto aparecendo

---

## 🐛 Troubleshooting

### Problema: "Invalid or missing API key"

**Solução:** Configure o Bearer token:
- No LobeChat: `your-api-key-here`
- Na requisição: `Authorization: Bearer your-api-key-here`

### Problema: "Model not supported"

**Solução:** Use formato `provider/model-name`:
- ✅ Correto: `gemini/gemini-2.0-flash-exp`
- ❌ Errado: `gemini-2.0-flash-exp`

### Problema: CORS Error

**Solução:** Adicione a origem do LobeChat ao CORS:

```python
allow_origins=[
    "http://localhost:3210",  # LobeChat local
    "https://lobehub.com",    # LobeChat hospedado
]
```

### Problema: Connection Refused

**Soluções:**
1. Verifique se a API está rodando: `curl http://localhost:8001/health`
2. Se LobeChat está no Docker, use `host.docker.internal` em vez de `localhost`
3. Verifique firewall: `sudo ufw allow 8001`

### Problema: SSL Error (LobeChat hospedado → sua API local)

**Solução:** Use ngrok ou cloudflare tunnel para expor com HTTPS

---

## 🎉 Conclusão

Agora você tem:

✅ **API FastAPI** expondo endpoints compatíveis com OpenAI  
✅ **LiteLLM** como proxy unificado  
✅ **LobeChat** como frontend  
✅ **100+ modelos** disponíveis  

**Acesse:** `http://localhost:3210` (LobeChat)  
**API:** `http://localhost:8001/v1` (Sua API)  
**Docs:** `http://localhost:8001/docs` (Swagger)

---

## 📚 Recursos Adicionais

- [LobeChat Documentation](https://lobehub.com/docs)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

**Última atualização:** 2025-11-12

