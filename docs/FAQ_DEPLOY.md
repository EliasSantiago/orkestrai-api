# ❓ FAQ - Deploy e Troubleshooting

Perguntas frequentes sobre deploy, configuração e solução de problemas.

## 📋 Índice

- [Setup Inicial](#setup-inicial)
- [GitHub Actions](#github-actions)
- [Docker](#docker)
- [Banco de Dados](#banco-de-dados)
- [Networking](#networking)
- [Segurança](#segurança)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

---

## Setup Inicial

### Como obter o IP da minha máquina E2?

```bash
# Via gcloud CLI
gcloud compute instances list

# Ou via SSH dentro da máquina
curl ifconfig.me
```

### Qual tipo de máquina E2 devo usar?

Para começar, recomendamos:
- **e2-small** (2 vCPUs, 2GB RAM) - Desenvolvimento/testes
- **e2-medium** (2 vCPUs, 4GB RAM) - Produção leve
- **e2-standard-2** (2 vCPUs, 8GB RAM) - Produção média

### Como gerar senhas fortes para .env?

```bash
# SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"

# REDIS_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

---

## GitHub Actions

### O deploy não está sendo acionado após push

**Verificar:**
1. Push foi para branch `main` ou `master`?
2. Workflow está na pasta `.github/workflows/`?
3. Arquivo workflow tem extensão `.yml` ou `.yaml`?
4. Verifique em Actions → All workflows

**Forçar execução manual:**
- Actions → Deploy to Google Cloud E2 → Run workflow

### Erro: "Permission denied (publickey)"

**Causa:** Chave SSH incorreta ou não configurada.

**Solução:**
```bash
# Gerar nova chave
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/gcp_deploy

# Copiar chave pública para servidor
cat ~/.ssh/gcp_deploy.pub | ssh usuario@ip "cat >> ~/.ssh/authorized_keys"

# Copiar chave privada para GitHub Secret
cat ~/.ssh/gcp_deploy  # Cole em GCP_SSH_KEY
```

### Erro: "No space left on device"

**Causa:** Disco cheio na máquina E2.

**Solução:**
```bash
# SSH no servidor
ssh usuario@ip

# Limpar Docker
docker system prune -a -f
docker volume prune -f

# Ver espaço
df -h

# Limpar logs antigos
sudo journalctl --vacuum-time=7d
```

### Como ver logs detalhados do workflow?

1. Vá em **Actions** no GitHub
2. Clique no workflow que falhou
3. Clique no job específico
4. Expanda cada step para ver detalhes

---

## Docker

### Container não inicia após deploy

**Verificar logs:**
```bash
docker logs orkestrai-api
docker logs --tail 100 orkestrai-api
```

**Causas comuns:**
1. **Variáveis de ambiente faltando**: Verificar `.env`
2. **Porta já em uso**: `lsof -i :8001`
3. **Banco não está pronto**: Aguardar PostgreSQL iniciar
4. **Falta de memória**: `docker stats`

### Como atualizar apenas a aplicação sem recriar tudo?

```bash
# Apenas aplicação
docker stop orkestrai-api
docker rm orkestrai-api
docker pull orkestrai-api:latest  # ou rebuild local
docker run -d --name orkestrai-api [...opções...] orkestrai-api:latest

# PostgreSQL e Redis continuam rodando
```

### Imagem Docker está muito grande

**Verificar tamanho:**
```bash
docker images orkestrai-api
```

**Otimizar:**
- Já está usando multi-stage build ✓
- Adicionar mais exclusões no `.dockerignore`
- Usar imagem base menor (alpine)

### Como ver logs de build do Docker?

```bash
# Build com logs detalhados
docker build -t orkestrai-api:test . --progress=plain --no-cache
```

---

## Banco de Dados

### Erro: "could not connect to server"

**Causa:** PostgreSQL não está rodando ou não está acessível.

**Solução:**
```bash
# Verificar status
docker ps | grep postgres

# Ver logs
docker logs agents_postgres

# Reiniciar
docker restart agents_postgres

# Aguardar ficar pronto
docker exec agents_postgres pg_isready
```

### Como acessar o banco de dados diretamente?

```bash
# Via Docker
docker exec -it agents_postgres psql -U agentuser -d agentsdb

# Comandos úteis psql:
# \l - listar databases
# \dt - listar tabelas
# \q - sair
```

### Como fazer backup do banco?

```bash
# Usar script
./scripts/backup_db.sh

# Manual
docker exec agents_postgres pg_dump -U agentuser agentsdb > backup.sql
gzip backup.sql
```

### Como restaurar backup?

```bash
# Descompactar
gunzip backup.sql.gz

# Restaurar
docker exec -i agents_postgres psql -U agentuser -d agentsdb < backup.sql

# Ou criar novo banco
docker exec -i agents_postgres psql -U agentuser -d postgres < backup.sql
```

### Erro: "password authentication failed"

**Causa:** Senha incorreta no `.env` ou banco não configurado.

**Solução:**
```bash
# Verificar .env
cat .env | grep POSTGRES_PASSWORD

# Recriar banco
docker-compose down -v  # CUIDADO: apaga dados!
docker-compose up -d

# Ou resetar senha
docker exec -it agents_postgres psql -U postgres
# ALTER USER agentuser WITH PASSWORD 'nova_senha';
```

---

## Networking

### API não responde externamente

**Verificar:**

1. **Container está rodando?**
```bash
docker ps | grep orkestrai-api
```

2. **Porta está exposta?**
```bash
docker port orkestrai-api
netstat -tlnp | grep 8001
```

3. **Firewall local?**
```bash
sudo ufw status
sudo ufw allow 8001/tcp
```

4. **Firewall Google Cloud?**
```bash
# Criar regra
gcloud compute firewall-rules create allow-api \
    --allow tcp:8001 \
    --source-ranges 0.0.0.0/0
```

### Erro: "Address already in use"

**Causa:** Porta 8001 já está em uso.

**Solução:**
```bash
# Ver o que está usando a porta
lsof -i :8001
sudo netstat -tlnp | grep 8001

# Parar processo
kill -9 PID

# Ou mudar porta no .env
API_PORT=8002
```

### Como configurar domínio personalizado?

1. **Configurar DNS:**
   - Adicione registro A apontando para IP da E2
   - Aguarde propagação (até 48h)

2. **Configurar HTTPS:**
```bash
sudo ./scripts/setup_https.sh
```

3. **Testar:**
```bash
curl https://seu-dominio.com/docs
```

---

## Segurança

### Como proteger o banco de dados?

1. **Não expor porta externamente** (já configurado ✓)
2. **Usar senhas fortes** (mínimo 16 caracteres)
3. **Backup regular** (`./scripts/backup_db.sh`)
4. **Limitar conexões** no `postgresql.conf`

### Como habilitar HTTPS?

```bash
# Executar script
sudo ./scripts/setup_https.sh

# Ou seguir docs/DEPLOY_SETUP.md seção HTTPS
```

### Como limitar acesso por IP?

**No Nginx:**
```nginx
# /etc/nginx/sites-available/orkestrai
location / {
    allow 203.0.113.0/24;  # Seu IP/range
    deny all;
    proxy_pass http://localhost:8001;
}
```

**No Google Cloud Firewall:**
```bash
# Restringir a IPs específicos
gcloud compute firewall-rules update allow-api \
    --source-ranges 203.0.113.0/24
```

### Como rotacionar secrets?

1. **Gerar novos valores**
2. **Atualizar `.env` no servidor**
3. **Atualizar secrets no GitHub**
4. **Reiniciar aplicação**
```bash
docker restart orkestrai-api
```

---

## Performance

### API está lenta

**Verificar:**

1. **Uso de recursos:**
```bash
docker stats
htop
```

2. **Logs de erro:**
```bash
docker logs orkestrai-api | grep -i error
```

3. **Queries lentas no banco:**
```sql
-- Queries em execução
SELECT pid, age(clock_timestamp(), query_start), usename, query 
FROM pg_stat_activity 
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%' 
ORDER BY query_start desc;
```

**Otimizar:**
- Aumentar workers do Uvicorn no `.env`
- Adicionar índices no banco
- Implementar cache com Redis
- Upgrade da máquina E2

### Como aumentar número de workers?

No `.env`:
```bash
UVICORN_WORKERS=4  # Recomendado: número de CPUs
```

Reiniciar:
```bash
docker restart orkestrai-api
```

### Banco de dados está lento

```bash
# Verificar conexões
docker exec -it agents_postgres psql -U agentuser -d agentsdb -c "SELECT count(*) FROM pg_stat_activity;"

# Ver tamanho das tabelas
docker exec -it agents_postgres psql -U agentuser -d agentsdb -c "\dt+"

# Vacuum
docker exec -it agents_postgres psql -U agentuser -d agentsdb -c "VACUUM ANALYZE;"
```

---

## Troubleshooting

### Checklist Geral de Problemas

```bash
# 1. Containers rodando?
docker ps

# 2. Logs têm erros?
docker logs orkestrai-api --tail 50

# 3. Banco acessível?
docker exec agents_postgres pg_isready

# 4. Redis acessível?
docker exec agents_redis redis-cli ping

# 5. Portas abertas?
netstat -tlnp | grep -E "8001|5432|6379"

# 6. Espaço em disco?
df -h

# 7. Memória disponível?
free -h

# 8. .env configurado?
cat .env | grep -v PASSWORD
```

### Script Diagnóstico Rápido

```bash
./scripts/check_server_status.sh
```

### Container reinicia constantemente

**Ver por que está crashando:**
```bash
docker logs orkestrai-api
docker inspect orkestrai-api
```

**Causas comuns:**
- Erro ao iniciar aplicação (import error)
- Falta variável de ambiente obrigatória
- Falta de memória
- Health check falhando

**Desabilitar restart temporariamente:**
```bash
docker update --restart=no orkestrai-api
```

### Como fazer rollback para versão anterior?

```bash
./scripts/rollback.sh
```

### Deploy foi bem-sucedido mas API retorna 502

**Causa:** Nginx/proxy configurado mas aplicação não responde.

**Verificar:**
```bash
# Aplicação está rodando?
curl http://localhost:8001/docs

# Nginx está rodando?
sudo systemctl status nginx

# Testar config Nginx
sudo nginx -t

# Ver logs Nginx
sudo tail -f /var/log/nginx/error.log
```

### Erro: "exec format error"

**Causa:** Arquitetura incompatível (ARM vs x86).

**Solução:**
Build a imagem na máquina de destino ou use buildx:
```bash
docker buildx build --platform linux/amd64 -t orkestrai-api:latest .
```

---

## 🆘 Ainda com Problemas?

### Coletar Informações para Debug

```bash
# Salvar informações do sistema
{
    echo "=== System Info ==="
    uname -a
    df -h
    free -h
    
    echo -e "\n=== Docker Info ==="
    docker --version
    docker compose version
    docker ps -a
    
    echo -e "\n=== Container Logs ==="
    docker logs --tail 100 orkestrai-api
    
    echo -e "\n=== Network ==="
    docker network ls
    netstat -tlnp | grep -E "8001|5432|6379"
    
} > debug_info.txt
```

### Comandos de Emergência

```bash
# Parar tudo
docker-compose down
docker stop orkestrai-api

# Reiniciar tudo
docker-compose up -d
./scripts/deploy_manual.sh

# Limpar completamente e recomeçar
docker-compose down -v  # CUIDADO: Apaga dados!
docker system prune -a -f
./scripts/deploy_manual.sh
```

### Recursos Adicionais

- [Documentação Completa](DEPLOY_SETUP.md)
- [Início Rápido](../QUICKSTART_DEPLOY.md)
- [Scripts de Gerenciamento](../scripts/)

---

**Não encontrou sua pergunta?** Adicione uma issue no GitHub ou consulte a documentação oficial do Docker e FastAPI.

