# 🚀 Próximos Passos - Deploy Automático

## ✅ O que você já fez:

- [x] Chave SSH criada e funcionando
- [x] Conexão SSH testada com sucesso
- [x] Usuário: `ignitor_online`
- [x] IP: `34.42.168.19`

---

## 🎯 O que dispara o deploy automático?

### **PUSH para a branch `main` ou `master`**

```bash
git add .
git commit -m "Sua mensagem"
git push origin main    # ← ISSO dispara o deploy!
```

**NÃO** é necessário:
- ❌ Fazer git pull no servidor
- ❌ Aprovar pull request (PR)
- ❌ Conectar SSH manualmente

**O GitHub Actions faz TUDO automaticamente:**
1. Build da imagem Docker
2. Transfer para seu servidor E2
3. Parar containers antigos
4. Iniciar nova versão
5. Health check

---

## 📋 Próximos Passos (em ordem):

### PASSO 1: Configurar Secrets no GitHub (5 min)

1. **Copie sua chave privada:**
```bash
cat ~/.ssh/gcp_deploy_key
```

Copie **TODO** o conteúdo (incluindo BEGIN e END)

2. **Vá no GitHub:**
   - https://github.com/SEU_USUARIO/orkestrai-api
   - **Settings** → **Secrets and variables** → **Actions**
   - Clique em **"New repository secret"**

3. **Adicione os 3 secrets:**

| Name | Value |
|------|-------|
| `GCP_HOST` | `34.42.168.19` |
| `GCP_USERNAME` | `ignitor_online` |
| `GCP_SSH_KEY` | [Cole a chave privada completa aqui] |

---

### PASSO 2: Configurar Servidor E2 (10 min)

**Conecte no servidor:**
```bash
ssh ignitor_online@34.42.168.19
```

**Execute o script de setup:**

⚠️ **IMPORTANTE:** Você precisa fazer push primeiro para o script estar disponível!

```bash
# OPÇÃO A: Baixar script (após fazer git push)
wget https://raw.githubusercontent.com/EliasSantiago/orkestrai-api/main/scripts/setup_gcp_server.sh
chmod +x setup_gcp_server.sh
sudo ./setup_gcp_server.sh
```

**OPÇÃO B: Setup Manual (RECOMENDADO - sem precisar de push):**

```bash
# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt-get install -y docker-compose-plugin

# Configurar firewall
sudo apt-get install -y ufw
sudo ufw allow ssh
sudo ufw allow 8001/tcp
sudo ufw --force enable

# Criar diretórios
mkdir -p ~/orkestrai-api/{backups,logs}

# Fazer logout e login novamente
exit
ssh ignitor_online@34.42.168.19

# Verificar
docker --version
docker compose version
```

**Criar diretório e arquivo .env:**
```bash
# Criar diretório
mkdir -p ~/orkestrai-api
cd ~/orkestrai-api

# Criar arquivo .env
nano .env
```

**Cole isso no .env e configure com suas chaves:**
```bash
# Database
POSTGRES_USER=agentuser
POSTGRES_PASSWORD=MUDE_PARA_SENHA_FORTE_16_CARACTERES
POSTGRES_DB=agentsdb
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://agentuser:MUDE_PARA_SENHA_FORTE_16_CARACTERES@postgres:5432/agentsdb

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=MUDE_PARA_SENHA_FORTE_16_CARACTERES
REDIS_URL=redis://:MUDE_PARA_SENHA_FORTE_16_CARACTERES@redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8001
SECRET_KEY=MUDE_PARA_CHAVE_SECRETA_32_CARACTERES
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Keys
GOOGLE_API_KEY=sua_chave_google_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Environment
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Gerar senhas fortes:**
```bash
# Gerar senhas e copiar no .env
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD:', secrets.token_urlsafe(24))"
python3 -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(24))"
```

**Salvar e sair:**
- Ctrl+X
- Y (yes)
- Enter

---

### PASSO 3: Configurar Firewall Google Cloud (2 min)

**Via Console Web:**
1. Vá em: https://console.cloud.google.com/networking/firewalls
2. Clique em **"CREATE FIREWALL RULE"**
3. Configure:
   - **Name:** `allow-orkestrai-api`
   - **Targets:** All instances in the network
   - **Source IP ranges:** `0.0.0.0/0`
   - **Protocols and ports:** TCP: `8001`
4. Clique em **CREATE**

**Ou via gcloud CLI:**
```bash
gcloud compute firewall-rules create allow-orkestrai-api \
    --allow tcp:8001 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Orkestrai API traffic"
```

---

### PASSO 4: Fazer Primeiro Deploy! 🎉

Agora você tem 2 opções:

#### **Opção A: Deploy Manual (Recomendado para primeira vez)**

```bash
# No servidor E2
cd ~/orkestrai-api
git clone https://github.com/SEU_USUARIO/orkestrai-api.git .
./scripts/deploy_manual.sh
```

Isso faz deploy e você pode ver se tudo funciona.

#### **Opção B: Deploy Automático via GitHub Actions**

```bash
# No seu computador local
cd /home/ignitor/projects/orkestrai-api
git add .
git commit -m "Setup deploy automático"
git push origin main   # ← ISSO dispara o deploy!
```

**Acompanhe o deploy:**
1. Vá no GitHub: https://github.com/SEU_USUARIO/orkestrai-api
2. Clique em **Actions**
3. Você verá o workflow **"Deploy to Google Cloud E2"** rodando
4. Clique nele para ver os logs em tempo real

---

## 🔄 Como Funciona o Deploy Automático?

```
┌─────────────────────────────────────────────────────────────┐
│ Seu Computador Local                                        │
│                                                              │
│ $ git add .                                                  │
│ $ git commit -m "Minhas mudanças"                           │
│ $ git push origin main      ← DISPARA O DEPLOY!            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions (Automático)                                 │
│                                                              │
│ 1. ✓ Detecta push na branch main                           │
│ 2. ✓ Faz build da imagem Docker                            │
│ 3. ✓ Conecta no servidor E2 via SSH                        │
│ 4. ✓ Para containers antigos                               │
│ 5. ✓ Carrega nova imagem                                   │
│ 6. ✓ Inicia serviços (Postgres, Redis)                     │
│ 7. ✓ Executa migrações do banco                            │
│ 8. ✓ Inicia aplicação                                      │
│ 9. ✓ Faz health check                                      │
│ 10. ✓ Deploy completo! 🎉                                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ Seu Servidor E2 (34.42.168.19)                              │
│                                                              │
│ API rodando: http://34.42.168.19:8001                       │
│ Docs: http://34.42.168.19:8001/docs                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Workflows Configurados

### 1. **Deploy Automático** (.github/workflows/deploy.yml)
- **Trigger:** Push para `main` ou `master`
- **Também:** Pode executar manualmente em Actions

### 2. **CI - Testes** (.github/workflows/ci.yml)
- **Trigger:** Pull requests
- **Faz:** Lint, testes, build Docker

### 3. **Backup Diário** (.github/workflows/backup.yml)
- **Trigger:** Diariamente às 3h UTC
- **Faz:** Backup do PostgreSQL

### 4. **Security Scan** (.github/workflows/security-scan.yml)
- **Trigger:** Semanalmente aos domingos
- **Faz:** Scan de vulnerabilidades

---

## ✅ Checklist Final

Antes do primeiro deploy:

- [ ] Secrets configurados no GitHub (GCP_HOST, GCP_USERNAME, GCP_SSH_KEY)
- [ ] Servidor E2 com Docker instalado
- [ ] Arquivo .env configurado no servidor
- [ ] Firewall GCP permite porta 8001
- [ ] Chave SSH testada e funcionando ✅ (você já fez!)

---

## 🎯 RESUMO DO QUE FAZER AGORA:

1. **Configure os 3 secrets no GitHub** (5 min)
   ```
   GCP_HOST = 34.42.168.19
   GCP_USERNAME = ignitor_online
   GCP_SSH_KEY = [cat ~/.ssh/gcp_deploy_key]
   ```

2. **Configure o servidor E2** (10 min)
   ```bash
   ssh ignitor_online@34.42.168.19
   sudo ./setup_gcp_server.sh
   cd ~/orkestrai-api
   nano .env  # Configure suas variáveis
   ```

3. **Configure firewall** (2 min)
   ```bash
   gcloud compute firewall-rules create allow-orkestrai-api --allow tcp:8001
   ```

4. **Faça deploy!** (1 min)
   ```bash
   git push origin main
   ```

---

## 🌐 Após Deploy

Acesse:
- **API:** http://34.42.168.19:8001
- **Docs:** http://34.42.168.19:8001/docs

Ver logs:
```bash
ssh ignitor_online@34.42.168.19
cd ~/orkestrai-api
./scripts/check_server_status.sh
```

---

## 🆘 Problemas?

- **FAQ:** `docs/FAQ_DEPLOY.md`
- **Checklist:** `CHECKLIST_DEPLOY.md`
- **Guia Completo:** `docs/DEPLOY_SETUP.md`

---

**Próximo passo:** Configure os secrets no GitHub! 🔑

