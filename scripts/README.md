# Scripts - Orkestrai API

Scripts essenciais para deploy, monitoramento e manutenção da aplicação.

## 📁 Estrutura

```
scripts/
├── README.md                   # Este arquivo
├── start_backend.sh           # Iniciar backend em modo desenvolvimento (Python local)
├── deploy_manual.sh           # Deploy manual no servidor
├── apply_migration.sh         # Aplicar migration SQL manual (produção)
├── migrate_database.sh        # Criar tabelas + migrations (dev)
├── setup_gcp_server.sh        # Setup inicial do servidor E2
├── setup_https.sh             # Configurar HTTPS/SSL
├── test_deploy_config.sh      # Testar configuração de deploy
├── rollback.sh                # Rollback para versão anterior
├── check_server_status.sh     # Status dos serviços
├── monitor_logs.sh            # Monitor interativo de logs
├── backup_db.sh              # Backup do PostgreSQL
└── clear_mcp_cache.py         # Limpar cache MCP tools
```

## 💻 Desenvolvimento Local

### Iniciar Backend em Python
```bash
./scripts/start_backend.sh
```
Inicia o servidor FastAPI em modo desenvolvimento com hot reload.
- Cria ambiente virtual automaticamente se não existir
- Instala dependências se necessário
- Verifica se PostgreSQL e Redis estão rodando (Docker)
- Inicia servidor em `http://localhost:8001`
- Documentação disponível em `http://localhost:8001/docs`

**Requisitos:**
- Python 3.11+
- PostgreSQL e Redis rodando (via Docker ou localmente)
- Arquivo `.env` configurado

## 🚀 Deploy

### Deploy Manual
```bash
./scripts/deploy_manual.sh
```
Faz deploy completo da aplicação no servidor E2 (inclui migrations).

### Migrations do Banco

```bash
# Aplicar migration SQL em produção (seguro, manual)
./scripts/apply_migration.sh migrations/sua_migration.sql

# Criar tabelas + migrations (dev/teste apenas)
./scripts/migrate_database.sh
```

**Produção:**
- Tabelas criadas automaticamente na primeira vez
- Migrations SQL são sempre **manuais** (seguro!)

**Dev/Teste:**
- Pode usar `migrate_database.sh` livremente

Ver documentação: `docs/DATABASE_MIGRATIONS.md`

### Testar Configuração
```bash
./scripts/test_deploy_config.sh
```
Verifica se tudo está configurado antes do deploy.

## ⚙️ Setup

### Setup do Servidor E2
```bash
./scripts/setup_gcp_server.sh
```
Configura Docker, firewall e ambiente no servidor E2 (executar apenas uma vez).

### Setup HTTPS
```bash
sudo ./scripts/setup_https.sh
```
Configura Nginx + Let's Encrypt para HTTPS.

## 📊 Monitoramento

### Status dos Serviços
```bash
./scripts/check_server_status.sh
```
Exibe status de API, PostgreSQL, Redis e uso de recursos.

### Monitor de Logs
```bash
./scripts/monitor_logs.sh
```
Monitor interativo com opções para ver logs de diferentes serviços.

## 💾 Backup

### Backup Manual
```bash
./scripts/backup_db.sh
```
Cria backup comprimido do PostgreSQL em `backups/`.

**Backup automático:** Configurado via GitHub Actions (diário às 3h UTC).

## 🔄 Rollback

### Reverter Deploy
```bash
./scripts/rollback.sh
```
Volta para a versão anterior da aplicação em caso de problemas.

## 🛠️ Utilitários

### Limpar Cache MCP
```bash
python scripts/clear_mcp_cache.py
```
Limpa cache de ferramentas MCP. Execute quando:
- Mudou nomes de ferramentas no código
- Ferramentas não aparecem com nomes corretos

## 📋 Uso Comum

### Primeiro Deploy
```bash
# 1. Setup do servidor (apenas primeira vez)
./scripts/setup_gcp_server.sh

# 2. Configurar .env no servidor
cd ~/orkestrai-api
nano .env

# 3. Deploy
./scripts/deploy_manual.sh

# 4. Configurar HTTPS (opcional)
sudo ./scripts/setup_https.sh
```

### Operação Diária
```bash
# Ver status
./scripts/check_server_status.sh

# Ver logs
./scripts/monitor_logs.sh

# Fazer backup
./scripts/backup_db.sh
```

### Troubleshooting
```bash
# Ver status completo
./scripts/check_server_status.sh

# Monitorar logs em tempo real
./scripts/monitor_logs.sh

# Se necessário, fazer rollback
./scripts/rollback.sh
```

## 🔒 Segurança

- ✅ Todos os scripts usam variáveis de ambiente
- ✅ Nenhuma senha hardcoded
- ✅ Executáveis apenas para o owner
- ✅ Validação de entrada quando necessário

## 📖 Mais Informações

- **Deploy Completo:** `docs/DEPLOY_SETUP.md`
- **Obter Secrets:** `docs/COMO_OBTER_SECRETS.md`
- **Deploy com PR:** `docs/DEPLOY_COM_PR.md`
- **FAQ:** `docs/FAQ_DEPLOY.md`

---

**Nota:** Deploy automático via GitHub Actions está configurado em `.github/workflows/deploy.yml`
