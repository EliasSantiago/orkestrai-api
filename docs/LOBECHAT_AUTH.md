# 🔐 Autenticação do LobeChat com JWT

## 📋 Como Funciona

Os endpoints OpenAI-compatible (`/v1/models`, `/v1/chat/completions`) agora usam **autenticação JWT** - o mesmo sistema usado pelas outras rotas da API.

---

## 🔑 Obter Token JWT

### Passo 1: Fazer Login

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Passo 2: Usar o Token

Use o `access_token` como Bearer token:

```bash
curl -X GET http://localhost:8001/v1/models \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 🎨 Configurar no LobeChat

### Opção 1: Usando Variável de Ambiente (Recomendado)

No `docker-compose.yml`:

```yaml
version: '3.8'

services:
  lobe-chat:
    image: lobehub/lobe-chat
    container_name: lobe-chat
    restart: always
    ports:
      - '3210:3210'
    environment:
      # Use o token JWT obtido do login
      OPENAI_API_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidXNlcl9pZCI6MiwiZXhwIjoxNzY1NTQ3MDM2fQ.Kx7SEQ7tVp0F9viX-u83nfSTdoDKO4q2VEJJsjcnDqI"
      
      OPENAI_PROXY_URL: "http://host.docker.internal:8001/v1"
      ACCESS_CODE: lobe66
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

**⚠️ Nota:** Tokens JWT expiram! O token padrão expira em 30 dias. Você precisará renovar periodicamente.

---

### Opção 2: Criar Token de Longa Duração

Para evitar renovações frequentes, você pode:

#### A) Aumentar a validade do token

Edite `/src/config.py`:

```python
# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 365 * 24 * 60  # 1 ano
```

Depois reinicie a API e faça login novamente.

#### B) Criar um usuário específico para o LobeChat

```bash
# 1. Registrar usuário do LobeChat
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LobeChat User",
    "email": "lobechat@localhost",
    "password": "secure-password-123",
    "password_confirm": "secure-password-123"
  }'

# 2. Fazer login e pegar o token
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lobechat@localhost",
    "password": "secure-password-123"
  }'

# 3. Usar o access_token no docker-compose.yml
```

---

## 🔄 Renovar Token Automaticamente

### Script para Renovar Token

Crie um script que renova o token automaticamente:

```bash
#!/bin/bash
# scripts/renew_lobechat_token.sh

EMAIL="lobechat@localhost"
PASSWORD="secure-password-123"

# Fazer login
RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

# Extrair token
TOKEN=$(echo $RESPONSE | jq -r '.access_token')

echo "Novo token JWT:"
echo $TOKEN
echo ""
echo "Atualize o docker-compose.yml com este token:"
echo "OPENAI_API_KEY: \"$TOKEN\""
```

Execute periodicamente (ex: a cada 15 dias):

```bash
chmod +x scripts/renew_lobechat_token.sh
./scripts/renew_lobechat_token.sh
```

---

## 🧪 Testar Autenticação

### Teste 1: Sem Token (deve falhar)

```bash
curl -X GET http://localhost:8001/v1/models
```

**Esperado:** `401 Unauthorized`

### Teste 2: Com Token Inválido (deve falhar)

```bash
curl -X GET http://localhost:8001/v1/models \
  -H "Authorization: Bearer token-invalido"
```

**Esperado:** `401 Unauthorized`

### Teste 3: Com Token Válido (deve funcionar)

```bash
# Fazer login
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your-password"}' \
  | jq -r '.access_token')

# Usar token
curl -X GET http://localhost:8001/v1/models \
  -H "Authorization: Bearer $TOKEN"
```

**Esperado:** Lista de modelos

---

## 🔐 Segurança

### ✅ Vantagens da Autenticação JWT

1. **Rastreabilidade**: Cada requisição está vinculada a um usuário
2. **Controle de Acesso**: Pode implementar permissões por usuário
3. **Auditoria**: Logs mostram qual usuário fez qual requisição
4. **Revogação**: Pode desativar usuários sem afetar outros

### 🔒 Boas Práticas

1. **Não compartilhe tokens**: Cada usuário/aplicação deve ter seu próprio
2. **Rotacione tokens**: Configure expiração adequada
3. **Use HTTPS em produção**: Tokens não devem trafegar em texto claro
4. **Armazene tokens com segurança**: Não commite no git

---

## 🎯 Configuração Completa do LobeChat

### docker-compose.yml Final

```yaml
version: '3.8'

services:
  lobe-chat:
    image: lobehub/lobe-chat
    container_name: lobe-chat
    restart: always
    ports:
      - '3210:3210'
    environment:
      # ============================================
      # Autenticação JWT
      # ============================================
      
      # Token obtido do login (renove periodicamente)
      OPENAI_API_KEY: "SEU_JWT_TOKEN_AQUI"
      
      # ============================================
      # URL da sua API
      # ============================================
      
      OPENAI_PROXY_URL: "http://host.docker.internal:8001/v1"
      
      # ============================================
      # Segurança (opcional)
      # ============================================
      
      ACCESS_CODE: lobe66
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

---

## 📝 Fluxo Completo

```
1. Usuário faz login na API
   ↓
2. API retorna JWT token
   ↓
3. LobeChat usa JWT token como OPENAI_API_KEY
   ↓
4. Cada requisição do LobeChat inclui: Authorization: Bearer {JWT}
   ↓
5. API valida JWT e identifica o usuário
   ↓
6. API processa requisição e retorna resposta
```

---

## 🐛 Troubleshooting

### Problema: "401 Unauthorized"

**Causas possíveis:**
1. Token expirado - Faça login novamente
2. Token inválido - Verifique se copiou corretamente
3. Usuário desativado - Verifique no banco de dados

**Solução:** Obtenha um novo token:

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu-email@exemplo.com",
    "password": "sua-senha"
  }'
```

### Problema: Token expira muito rápido

**Solução:** Aumente a validade em `src/config.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 365 * 24 * 60  # 1 ano
```

### Problema: Esqueço de renovar o token

**Solução:** Use o script de renovação automática ou configure um cronjob:

```bash
# Adicione ao crontab para renovar a cada 15 dias
0 0 */15 * * /caminho/para/scripts/renew_lobechat_token.sh
```

---

## 📚 Referências

- **Endpoints de Autenticação**: `POST /api/auth/login`, `POST /api/auth/register`
- **Documentação da API**: `http://localhost:8001/docs`
- **Configuração JWT**: `src/config.py`
- **Dependências de Auth**: `src/api/dependencies.py`

---

## ✅ Resumo

**Antes:** Endpoints `/v1/*` aceitavam qualquer Bearer token

**Depois:** Endpoints `/v1/*` requerem JWT token válido obtido via login

**Como usar:**
1. Faça login: `POST /api/auth/login`
2. Copie o `access_token`
3. Use no LobeChat: `OPENAI_API_KEY: "seu-jwt-token"`
4. Renove periodicamente

**Vantagem:** Maior segurança e rastreabilidade de uso

---

**Última atualização:** 2025-11-12

