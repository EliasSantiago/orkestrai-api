# ⚡ Início Rápido - Deploy na Google Cloud E2

Guia simplificado para configurar deploy automático em 10 minutos.

## 📝 Checklist Rápido

- [ ] Máquina E2 criada no Google Cloud
- [ ] Docker instalado na máquina E2
- [ ] Chave SSH configurada
- [ ] Secrets configurados no GitHub
- [ ] Arquivo .env configurado na máquina E2

## 🚀 Passo a Passo (10 minutos)

### 1️⃣ Configurar Máquina E2 (5 min)

```bash
# 1. Conectar via SSH na sua máquina E2
ssh seu_usuario@IP_DA_MAQUINA

# 2. Baixar e executar script de setup
wget https://raw.githubusercontent.com/seu-usuario/orkestrai-api/main/scripts/setup_gcp_server.sh
chmod +x setup_gcp_server.sh
./setup_gcp_server.sh

# 3. Fazer logout e login novamente (importante!)
exit
ssh seu_usuario@IP_DA_MAQUINA

# 4. Verificar instalação
docker --version
docker compose version
```

### 2️⃣ Configurar Projeto na Máquina E2 (3 min)

```bash
# 1. Criar diretório e navegar
mkdir -p ~/orkestrai-api
cd ~/orkestrai-api

# 2. Criar arquivo .env
cat > .env << 'EOF'
# Database
POSTGRES_USER=agentuser
POSTGRES_PASSWORD=SuaSenhaPostgresForte123!@#
POSTGRES_DB=agentsdb
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://agentuser:SuaSenhaPostgresForte123!@#@postgres:5432/agentsdb

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=SuaSenhaRedisForte456!@#
REDIS_URL=redis://:SuaSenhaRedisForte456!@#@redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8001
SECRET_KEY=sua-chave-secreta-com-pelo-menos-32-caracteres-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Keys
GOOGLE_API_KEY=sua_chave_google_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Environment
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF

# 3. Editar com suas chaves reais
nano .env

# 4. Gerar senhas seguras (copie e cole no .env)
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD:', secrets.token_urlsafe(24))"
python3 -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(24))"
```

### 3️⃣ Configurar Secrets no GitHub (2 min)

No GitHub: **Settings → Secrets and variables → Actions → New repository secret**

Adicione os seguintes secrets:

```bash
# 1. GCP_HOST
# Valor: IP da sua máquina E2 (ex: 34.123.45.67)

# 2. GCP_USERNAME  
# Valor: Seu usuário SSH (ex: seu_usuario)

# 3. GCP_SSH_KEY
# Valor: Sua chave privada SSH
# Gerar chave (no seu computador local):
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/gcp_deploy_key
cat ~/.ssh/gcp_deploy_key  # Copie TODO o conteúdo

# Adicionar chave pública na máquina E2:
cat ~/.ssh/gcp_deploy_key.pub | ssh seu_usuario@IP_DA_MAQUINA "cat >> ~/.ssh/authorized_keys"

# 4. GCP_SSH_PORT (opcional)
# Valor: 22
```

**❓ Não sabe como obter esses valores?**
- **Guia Rápido:** [`GUIA_RAPIDO_SECRETS.md`](GUIA_RAPIDO_SECRETS.md)
- **Guia Completo:** [`docs/COMO_OBTER_SECRETS.md`](docs/COMO_OBTER_SECRETS.md)

## ✅ Testar Deploy

### Opção A: Deploy Manual (Teste Primeiro)

```bash
# Na máquina E2
cd ~/orkestrai-api

# Clone o repositório
git clone https://github.com/seu-usuario/orkestrai-api.git .

# Execute deploy manual
./scripts/deploy_manual.sh

# Aguarde e teste
curl http://localhost:8001/docs
```

### Opção B: Deploy Automático

```bash
# No seu computador local
git push origin main

# Acompanhe no GitHub: Actions → Deploy to Google Cloud E2
```

## 🌐 Acessar API

Após deploy bem-sucedido:

```bash
# Documentação
http://SEU_IP:8001/docs

# Health Check
curl http://SEU_IP:8001/docs
```

## 🔧 Comandos Úteis

```bash
# Ver status
cd ~/orkestrai-api
./scripts/check_server_status.sh

# Ver logs
docker logs -f orkestrai-api

# Reiniciar
docker restart orkestrai-api

# Fazer backup
./scripts/backup_db.sh
```

## 🔥 Configurar Firewall no Google Cloud

No Console do Google Cloud:

```bash
# Via CLI
gcloud compute firewall-rules create allow-orkestrai-api \
    --allow tcp:8001 \
    --source-ranges 0.0.0.0/0

# Ou via Console Web:
# VPC Network → Firewall → CREATE FIREWALL RULE
# - Name: allow-orkestrai-api
# - Targets: All instances in the network  
# - Source IP ranges: 0.0.0.0/0
# - Protocols and ports: tcp:8001
```

## 🎯 Fluxo Após Configuração

```
1. Você faz commit e push → GitHub
2. GitHub Actions detecta push na main
3. Build da imagem Docker
4. Transfer para máquina E2
5. Deploy automático
6. Health check
7. ✅ Deploy completo!
```

## 📊 Verificar Status

```bash
# SSH na máquina
ssh seu_usuario@IP_DA_MAQUINA

# Status completo
cd ~/orkestrai-api
./scripts/check_server_status.sh

# Apenas logs da API
docker logs --tail 50 orkestrai-api

# Ver uso de recursos
docker stats
```

## 🐛 Troubleshooting Rápido

### API não inicia
```bash
# Ver erro específico
docker logs orkestrai-api

# Verificar .env
cat .env | grep -v PASSWORD

# Reiniciar tudo
docker compose down
docker compose up -d
docker restart orkestrai-api
```

### Deploy falha no GitHub Actions
1. Verificar secrets estão corretos
2. Testar SSH manualmente: `ssh -i ~/.ssh/gcp_deploy_key seu_usuario@IP`
3. Ver logs no GitHub Actions

### Sem espaço em disco
```bash
# Limpar Docker
docker system prune -a -f
docker volume prune -f

# Ver espaço
df -h
```

## 🔒 Segurança Essencial

```bash
# 1. Use senhas fortes (mínimo 16 caracteres)
# 2. Configure firewall restrito (não use 0.0.0.0/0 em produção)
# 3. Configure HTTPS com certificado SSL
# 4. Faça backups regulares
# 5. Monitore logs
```

## 🎓 Próximos Passos

Depois que tudo funcionar:

1. [ ] Configurar HTTPS com Nginx + Let's Encrypt
2. [ ] Configurar backup automático
3. [ ] Configurar monitoramento
4. [ ] Revisar configurações de segurança
5. [ ] Ler documentação completa: `docs/DEPLOY_SETUP.md`

## 📚 Documentação Completa

- **Guia Detalhado:** [`docs/DEPLOY_SETUP.md`](docs/DEPLOY_SETUP.md)
- **Overview:** [`DEPLOY_README.md`](DEPLOY_README.md)
- **Scripts:** `scripts/`

## 💡 Dicas

```bash
# Gerar senhas seguras
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Ver IP da máquina E2
gcloud compute instances list

# Conectar SSH rapidamente
ssh seu_usuario@$(gcloud compute instances describe NOME_INSTANCIA --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

# Ver logs de deploy no GitHub
# Vá em: Actions → Deploy to Google Cloud E2 → Latest run
```

## ✨ Pronto!

Agora você tem deploy automático configurado! 🎉

Cada push para `main` ou `master` dispara deploy automaticamente.

---

**Precisa de ajuda?** Consulte [`docs/DEPLOY_SETUP.md`](docs/DEPLOY_SETUP.md)

