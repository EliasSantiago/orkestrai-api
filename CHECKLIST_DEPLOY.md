# ✅ Checklist de Deploy - Orkestrai API

Use este checklist para garantir que tudo está configurado corretamente.

## 📋 Pré-Deploy

### Servidor E2 Google Cloud

- [ ] Instância E2 criada no Google Cloud
- [ ] IP externo configurado e anotado
- [ ] Firewall permite porta 8001
- [ ] Acesso SSH funcionando
- [ ] Docker instalado (`docker --version`)
- [ ] Docker Compose instalado (`docker compose version`)

### Repositório GitHub

- [ ] Código commitado no GitHub
- [ ] Arquivos de deploy presentes (.github/workflows/, Dockerfile, etc)
- [ ] Branch main/master configurada

### Secrets do GitHub

Configurar em: **Settings → Secrets and variables → Actions**

- [ ] `GCP_HOST` - IP da máquina E2
- [ ] `GCP_USERNAME` - Usuário SSH
- [ ] `GCP_SSH_KEY` - Chave privada SSH
- [ ] `GCP_SSH_PORT` - Porta SSH (opcional, padrão 22)

### Arquivo .env no Servidor

Na máquina E2 (`~/orkestrai-api/.env`):

- [ ] `POSTGRES_PASSWORD` - Senha forte (16+ caracteres)
- [ ] `REDIS_PASSWORD` - Senha forte (16+ caracteres)
- [ ] `SECRET_KEY` - Chave secreta (32+ caracteres)
- [ ] `GOOGLE_API_KEY` - API key do Google
- [ ] `OPENAI_API_KEY` - API key da OpenAI
- [ ] `DATABASE_URL` - Configurado corretamente
- [ ] `REDIS_URL` - Configurado corretamente

## 🔧 Setup Inicial

### 1. Preparar Servidor E2

```bash
# Conectar via SSH
ssh seu_usuario@IP_DA_MAQUINA

# Executar setup
wget https://raw.githubusercontent.com/seu-usuario/orkestrai-api/main/scripts/setup_gcp_server.sh
chmod +x setup_gcp_server.sh
./setup_gcp_server.sh

# Fazer logout e login
exit
ssh seu_usuario@IP_DA_MAQUINA

# Verificar
docker --version
docker compose version
```

**Checklist:**
- [ ] Script executado sem erros
- [ ] Docker funcionando
- [ ] Docker Compose funcionando
- [ ] Diretório `~/orkestrai-api` criado

### 2. Configurar SSH para GitHub Actions

```bash
# No seu computador local
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/gcp_deploy_key

# Ver chave privada (copiar para GitHub Secret)
cat ~/.ssh/gcp_deploy_key

# Copiar chave pública para servidor
cat ~/.ssh/gcp_deploy_key.pub | ssh seu_usuario@IP "cat >> ~/.ssh/authorized_keys"

# Testar conexão
ssh -i ~/.ssh/gcp_deploy_key seu_usuario@IP "echo 'SSH OK'"
```

**Checklist:**
- [ ] Chave gerada
- [ ] Chave pública no servidor
- [ ] Chave privada no GitHub Secret
- [ ] Conexão SSH testada e funcionando

### 3. Configurar Firewall

```bash
# Via gcloud CLI
gcloud compute firewall-rules create allow-orkestrai-api \
    --allow tcp:8001 \
    --source-ranges 0.0.0.0/0

# Verificar
gcloud compute firewall-rules list | grep orkestrai
```

**Checklist:**
- [ ] Regra de firewall criada
- [ ] Porta 8001 aberta
- [ ] Regra ativa

### 4. Criar Arquivo .env no Servidor

```bash
# SSH no servidor
ssh seu_usuario@IP_DA_MAQUINA

# Criar .env
cd ~/orkestrai-api
cat > .env << 'ENVEOF'
# Cole aqui o conteúdo do env.template
# E configure com seus valores reais
ENVEOF

# Editar
nano .env

# Gerar senhas seguras
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD:', secrets.token_urlsafe(24))"
python3 -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(24))"

# Verificar (sem mostrar senhas)
cat .env | grep -v PASSWORD | grep -v SECRET
```

**Checklist:**
- [ ] Arquivo .env criado
- [ ] Todas as variáveis configuradas
- [ ] Senhas fortes geradas
- [ ] API keys adicionadas

## 🧪 Teste de Configuração

```bash
# No seu computador local, no repositório
./scripts/test_deploy_config.sh
```

**Checklist:**
- [ ] Build Docker bem-sucedido
- [ ] Imports da aplicação OK
- [ ] Git configurado corretamente
- [ ] Sem erros no teste

## 🚀 Primeiro Deploy

### Opção A: Deploy Manual (Recomendado para primeira vez)

```bash
# SSH no servidor
ssh seu_usuario@IP_DA_MAQUINA

# Clone repositório
cd ~/orkestrai-api
git clone https://github.com/seu-usuario/orkestrai-api.git .

# Deploy
./scripts/deploy_manual.sh
```

**Checklist:**
- [ ] Repositório clonado
- [ ] Deploy executado sem erros
- [ ] Containers iniciados
- [ ] API respondendo

### Opção B: Deploy Automático via GitHub Actions

```bash
# No seu computador local
git add .
git commit -m "Setup deploy automático"
git push origin main

# Acompanhar no GitHub: Actions → Deploy to Google Cloud E2
```

**Checklist:**
- [ ] Push para main bem-sucedido
- [ ] Workflow iniciou no GitHub Actions
- [ ] Deploy concluído sem erros
- [ ] Health check passou

## ✅ Verificação Pós-Deploy

### Verificar Serviços

```bash
# SSH no servidor
ssh seu_usuario@IP_DA_MAQUINA
cd ~/orkestrai-api

# Status completo
./scripts/check_server_status.sh
```

**Checklist:**
- [ ] PostgreSQL rodando e saudável
- [ ] Redis rodando e saudável
- [ ] API rodando e respondendo
- [ ] Sem erros nos logs

### Testar API

```bash
# Localmente no servidor
curl http://localhost:8001/docs

# Externamente
curl http://SEU_IP:8001/docs

# Testar endpoint específico
curl http://SEU_IP:8001/
```

**Checklist:**
- [ ] API responde localmente
- [ ] API responde externamente
- [ ] Documentação Swagger acessível
- [ ] Endpoints funcionando

### Verificar Logs

```bash
# Logs da API
docker logs --tail 50 orkestrai-api

# Logs PostgreSQL
docker logs --tail 20 agents_postgres

# Logs Redis
docker logs --tail 20 agents_redis
```

**Checklist:**
- [ ] Sem erros críticos nos logs
- [ ] Aplicação iniciou corretamente
- [ ] Conexões com banco funcionando

## 🔒 Segurança Pós-Deploy

- [ ] Senhas fortes configuradas
- [ ] Firewall configurado
- [ ] Backup automático ativado
- [ ] Security scan do GitHub Actions ativado
- [ ] `.env` com permissões corretas (600)
- [ ] Considerar configurar HTTPS

## 📊 Monitoramento

### Configurar Backup Automático

**Checklist:**
- [ ] Workflow de backup ativo (.github/workflows/backup.yml)
- [ ] Testar backup manual: `./scripts/backup_db.sh`
- [ ] Verificar backups criados: `ls -lh backups/`

### Configurar Alertas (Opcional)

- [ ] Configurar notificações no GitHub (Settings → Notifications)
- [ ] Adicionar webhook para Slack/Discord (opcional)
- [ ] Configurar monitoramento externo (UptimeRobot, etc)

## 🎉 Deploy Completo!

Se todos os checkboxes acima estão marcados, seu deploy está completo e funcional!

### Próximos Passos

- [ ] Configurar HTTPS: `sudo ./scripts/setup_https.sh`
- [ ] Configurar domínio personalizado
- [ ] Implementar monitoramento avançado
- [ ] Configurar backup para Cloud Storage
- [ ] Revisar logs regularmente

### Comandos Úteis

```bash
# Ver status
./scripts/check_server_status.sh

# Ver logs em tempo real
docker logs -f orkestrai-api

# Fazer backup
./scripts/backup_db.sh

# Reiniciar aplicação
docker restart orkestrai-api

# Rollback se necessário
./scripts/rollback.sh
```

## 🆘 Problemas?

Se algo não funcionou:

1. Consulte: `docs/FAQ_DEPLOY.md`
2. Verifique logs: `docker logs orkestrai-api`
3. Execute diagnóstico: `./scripts/check_server_status.sh`
4. Veja guia completo: `docs/DEPLOY_SETUP.md`

---

**Deploy bem-sucedido! 🎉** Cada push para main/master agora faz deploy automático!
