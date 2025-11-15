# 🚀 Deploy Automático - Orkestrai API

Sistema completo de CI/CD configurado com GitHub Actions para deploy automático em máquina E2 do Google Cloud.

## 📁 Arquivos de Deploy Criados

```
orkestrai-api/
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Workflow de deploy automático
│       └── ci.yml              # Workflow de CI/testes
├── scripts/
│   ├── setup_gcp_server.sh     # Setup inicial do servidor E2
│   ├── deploy_manual.sh        # Deploy manual (sem GitHub Actions)
│   ├── check_server_status.sh  # Verificar status dos serviços
│   └── backup_db.sh            # Backup do banco de dados
├── Dockerfile                  # Containerização da aplicação
├── .dockerignore              # Arquivos ignorados no build
├── docker-compose.prod.yml    # Compose para produção (completo)
└── docs/
    └── DEPLOY_SETUP.md        # 📖 Guia completo de configuração
```

## 🎯 Como Usar

### Opção 1: Deploy Automático (Recomendado)

1. **Leia o guia completo**: `docs/DEPLOY_SETUP.md`
2. **Configure os secrets** no GitHub
3. **Faça push** para `main` ou `master`
4. **Pronto!** GitHub Actions faz deploy automaticamente

### Opção 2: Setup Inicial do Servidor

Na sua máquina E2 (primeira vez):

```bash
# 1. Baixar e executar script de setup
wget https://raw.githubusercontent.com/seu-usuario/orkestrai-api/main/scripts/setup_gcp_server.sh
chmod +x setup_gcp_server.sh
./setup_gcp_server.sh

# 2. Fazer logout e login novamente
exit

# 3. Clonar repositório
cd ~/orkestrai-api
git clone https://github.com/seu-usuario/orkestrai-api.git .

# 4. Configurar .env
cp .env.example .env
nano .env  # Configure suas variáveis

# 5. Deploy inicial
./scripts/deploy_manual.sh
```

### Opção 3: Deploy Manual

```bash
# Na máquina E2
cd ~/orkestrai-api
./scripts/deploy_manual.sh
```

## 📊 Monitoramento

### Verificar Status

```bash
./scripts/check_server_status.sh
```

### Ver Logs

```bash
# Logs em tempo real
docker logs -f orkestrai-api

# Últimas 100 linhas
docker logs --tail 100 orkestrai-api
```

### Backup do Banco

```bash
./scripts/backup_db.sh
```

## 🔧 Comandos Úteis

```bash
# Reiniciar aplicação
docker restart orkestrai-api

# Ver containers rodando
docker ps

# Ver uso de recursos
docker stats

# Parar tudo
docker compose down && docker stop orkestrai-api

# Iniciar tudo
docker compose up -d
docker start orkestrai-api
```

## 🌐 Acessar a API

Após deploy, acesse:

```
# Documentação Swagger
http://SEU_IP:8001/docs

# API
http://SEU_IP:8001
```

## 📚 Documentação Completa

**Leia o guia completo em:** [`docs/DEPLOY_SETUP.md`](docs/DEPLOY_SETUP.md)

O guia inclui:
- ✅ Configuração passo a passo
- ✅ Setup de secrets do GitHub
- ✅ Configuração de firewall
- ✅ Setup de HTTPS com Nginx
- ✅ Troubleshooting
- ✅ Recomendações de segurança

## 🔐 Secrets Necessários (GitHub)

Configure em **Settings > Secrets and variables > Actions**:

| Secret | Descrição | Exemplo |
|--------|-----------|---------|
| `GCP_HOST` | IP da máquina E2 | `34.123.45.67` |
| `GCP_USERNAME` | Usuário SSH | `seu_usuario` |
| `GCP_SSH_KEY` | Chave privada SSH | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `GCP_SSH_PORT` | Porta SSH (opcional) | `22` |

## 🔄 Fluxo de Deploy

```mermaid
graph TD
    A[Push to main] --> B[GitHub Actions]
    B --> C[Build Docker Image]
    C --> D[Transfer to GCP E2]
    D --> E[Stop Old App]
    E --> F[Load New Image]
    F --> G[Start Services]
    G --> H[Run Migrations]
    H --> I[Start Application]
    I --> J[Health Check]
    J --> K[Deploy Complete ✓]
```

## ⚡ Deploy Rápido (TL;DR)

```bash
# 1. No servidor E2 (primeira vez)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Fazer logout e login

# 2. Clonar e configurar
git clone <repo> ~/orkestrai-api
cd ~/orkestrai-api
cp .env.example .env
nano .env  # Configure

# 3. Deploy
./scripts/deploy_manual.sh

# 4. Configurar GitHub Secrets e fazer push
# Pronto! Deploy automático ativado
```

## 🆘 Troubleshooting

### Container não inicia
```bash
docker logs orkestrai-api
docker compose ps
```

### Deploy falha no GitHub Actions
1. Verificar secrets no GitHub
2. Testar SSH: `ssh -i chave usuario@ip`
3. Ver logs do workflow

### API não responde
```bash
docker restart orkestrai-api
./scripts/check_server_status.sh
```

## 📞 Suporte

Problemas? Consulte:
1. [`docs/DEPLOY_SETUP.md`](docs/DEPLOY_SETUP.md) - Guia completo
2. Logs: `docker logs orkestrai-api`
3. Status: `./scripts/check_server_status.sh`

---

**✨ Deploy configurado com sucesso!** Cada push para main/master faz deploy automático.

