# 🔧 Correção - Setup do Servidor E2

## ❌ Erro que você teve:

```
wget https://raw.githubusercontent.com/ignitor_online/orkestrai-api/main/scripts/setup_gcp_server.sh
# ERROR 404: Not Found
```

**Causa:** `ignitor_online` é seu usuário SSH, não seu usuário GitHub!

**Seu usuário GitHub:** `EliasSantiago`

---

## ✅ Solução 1: Fazer Push Primeiro

### 1. No seu computador local:

```bash
cd /home/ignitor/projects/orkestrai-api

# Verificar branch
git branch --show-current

# Se não for main, criar/mudar para main
git checkout -b main  # ou: git checkout main

# Fazer push
git add .
git commit -m "Adicionar configuração de deploy"
git push origin main
```

### 2. Agora baixar o script no servidor:

```bash
# No servidor E2
wget https://raw.githubusercontent.com/EliasSantiago/orkestrai-api/main/scripts/setup_gcp_server.sh
chmod +x setup_gcp_server.sh
sudo ./setup_gcp_server.sh
```

---

## ✅ Solução 2: Setup Manual (Sem Script) ⭐ RECOMENDADO

Execute os comandos direto no servidor E2:

```bash
# No servidor E2 (você já está conectado)

# 1. Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# 3. Adicionar seu usuário ao grupo docker
sudo usermod -aG docker $USER

# 4. Instalar Docker Compose
sudo apt-get install -y docker-compose-plugin

# 5. Verificar instalação
docker --version
docker compose version

# 6. Configurar firewall local (UFW)
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8001/tcp
sudo ufw --force enable

# 7. Criar diretórios
mkdir -p ~/orkestrai-api
mkdir -p ~/orkestrai-api/backups
mkdir -p ~/orkestrai-api/logs

# 8. IMPORTANTE: Fazer logout e login novamente
echo "✅ Setup concluído!"
echo "⚠️  IMPORTANTE: Faça logout e login novamente para aplicar grupo docker"
echo "Execute: exit"
```

### Depois do logout/login:

```bash
# Reconectar
ssh ignitor_online@34.42.168.19

# Verificar Docker
docker --version
docker ps

# Criar arquivo .env
cd ~/orkestrai-api
nano .env
```

---

## 📝 Conteúdo do .env

Cole isso e configure com suas chaves:

```bash
# Database
POSTGRES_USER=agentuser
POSTGRES_PASSWORD=SENHA_FORTE_AQUI_16_CARACTERES
POSTGRES_DB=agentsdb
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://agentuser:SENHA_FORTE_AQUI_16_CARACTERES@postgres:5432/agentsdb

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=SENHA_FORTE_AQUI_16_CARACTERES
REDIS_URL=redis://:SENHA_FORTE_AQUI_16_CARACTERES@redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8001
SECRET_KEY=CHAVE_SECRETA_32_CARACTERES
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Keys - OBRIGATÓRIO!
GOOGLE_API_KEY=sua_chave_google_gemini_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Environment
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Gerar senhas fortes:

```bash
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD:', secrets.token_urlsafe(24))"
python3 -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(24))"
```

Copie os valores gerados e cole no `.env`

**Salvar:** Ctrl+X → Y → Enter

---

## 🎯 Resumo - URLs Corretas

### Seu Usuário GitHub: `EliasSantiago`

```
Repositório: https://github.com/EliasSantiago/orkestrai-api
Script: https://raw.githubusercontent.com/EliasSantiago/orkestrai-api/main/scripts/setup_gcp_server.sh
```

### Seus Dados:

```
GCP_HOST = 34.42.168.19
GCP_USERNAME = ignitor_online
Usuário GitHub = EliasSantiago
```

---

## 🚀 Próximos Passos

1. ✅ Fazer setup manual no servidor (comandos acima)
2. ✅ Fazer logout e login no servidor
3. ✅ Criar arquivo .env
4. ✅ Configurar secrets no GitHub
5. ✅ Fazer push: `git push origin main`

---

**Recomendação:** Use a **Solução 2 (Setup Manual)** que é mais direto!

