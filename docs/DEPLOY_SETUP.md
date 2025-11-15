# 🚀 Guia de Configuração - Deploy Automático com GitHub Actions

Este guia ensina como configurar o deploy automático da aplicação Orkestrai API em uma máquina E2 do Google Cloud usando GitHub Actions.

## 📋 Pré-requisitos

1. ✅ Conta no GitHub com o repositório do projeto
2. ✅ Máquina E2 no Google Cloud Platform rodando (Ubuntu/Debian recomendado)
3. ✅ Docker e Docker Compose instalados na máquina E2
4. ✅ Acesso SSH à máquina E2

## 🔧 Passo 1: Configurar a Máquina E2 no Google Cloud

### 1.1 Instalar Docker e Docker Compose

Conecte-se à sua máquina E2 via SSH e execute:

```bash
# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar seu usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt-get install -y docker-compose-plugin

# Verificar instalação
docker --version
docker compose version

# Relogar para aplicar grupo docker
exit
# Conectar novamente via SSH
```

### 1.2 Configurar Firewall do Google Cloud

No Console do Google Cloud, configure as regras de firewall:

```bash
# Permitir tráfego na porta da API (8001)
gcloud compute firewall-rules create allow-orkestrai-api \
    --allow tcp:8001 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Orkestrai API traffic"

# Verificar regras
gcloud compute firewall-rules list
```

Ou configure pelo Console Web:
1. Navegue para **VPC Network > Firewall**
2. Crie nova regra:
   - Nome: `allow-orkestrai-api`
   - Targets: All instances in the network
   - Source IP ranges: `0.0.0.0/0` (ou restrinja conforme necessário)
   - Protocols and ports: `tcp:8001`

### 1.3 Criar Diretório de Deploy

```bash
# Criar diretório para a aplicação
mkdir -p ~/orkestrai-api
cd ~/orkestrai-api
```

## 🔐 Passo 2: Configurar Secrets no GitHub

No seu repositório do GitHub, vá em **Settings > Secrets and variables > Actions** e adicione os seguintes secrets:

### Secrets Necessários:

1. **GCP_HOST**
   - Valor: IP externo da sua máquina E2
   - Exemplo: `34.123.45.67`
   - Como encontrar: `gcloud compute instances list` ou no Console do GCP

2. **GCP_USERNAME**
   - Valor: Nome do usuário SSH da máquina E2
   - Exemplo: `seu_usuario` (geralmente é o nome do usuário do GCP)

3. **GCP_SSH_KEY**
   - Valor: Chave privada SSH para acesso à máquina
   - Como gerar:

```bash
# No seu computador local (não na máquina E2)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/gcp_deploy_key

# Exibir chave privada (copie todo o conteúdo)
cat ~/.ssh/gcp_deploy_key

# Exibir chave pública (será adicionada na máquina E2)
cat ~/.ssh/gcp_deploy_key.pub
```

4. **GCP_SSH_PORT** (Opcional)
   - Valor: `22` (porta SSH padrão)
   - Só adicione se usar porta diferente

### Adicionar Chave Pública na Máquina E2

```bash
# Na máquina E2, adicionar chave pública
echo "sua-chave-publica-aqui" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 📝 Passo 3: Configurar Variáveis de Ambiente na Máquina E2

```bash
# Na máquina E2, criar arquivo .env
cd ~/orkestrai-api
nano .env
```

Cole o conteúdo do `.env.example` e configure com seus valores:

```bash
# Valores obrigatórios
POSTGRES_PASSWORD=sua_senha_postgres_forte
REDIS_PASSWORD=sua_senha_redis_forte
SECRET_KEY=sua_chave_secreta_minimo_32_caracteres
GOOGLE_API_KEY=sua_chave_google_api
OPENAI_API_KEY=sua_chave_openai_api

# Ajustar hosts para Docker
POSTGRES_HOST=postgres
REDIS_HOST=redis
DATABASE_URL=postgresql://agentuser:sua_senha_postgres_forte@postgres:5432/agentsdb
REDIS_URL=redis://:sua_senha_redis_forte@redis:6379/0
```

Salve e saia (Ctrl+X, Y, Enter).

## 🚀 Passo 4: Testar Deploy Manual (Opcional mas Recomendado)

Antes de ativar o deploy automático, teste manualmente:

```bash
# Na máquina E2
cd ~/orkestrai-api

# Clone o repositório (primeira vez)
git clone https://github.com/seu-usuario/orkestrai-api.git .

# Ou atualize (se já clonou)
git pull

# Iniciar serviços de infraestrutura
docker compose up -d postgres redis

# Aguardar PostgreSQL estar pronto
sleep 10

# Build da aplicação
docker build -t orkestrai-api:latest .

# Iniciar aplicação
docker run -d \
  --name orkestrai-api \
  --network agents_network \
  --restart unless-stopped \
  -p 8001:8001 \
  --env-file .env \
  orkestrai-api:latest

# Verificar logs
docker logs -f orkestrai-api

# Testar API (em outro terminal)
curl http://localhost:8001/docs
```

Se tudo funcionar, o deploy automático também funcionará!

## ✅ Passo 5: Ativar Deploy Automático

Agora que tudo está configurado, o deploy automático funcionará assim:

1. **Push para branch main/master** → Dispara deploy automático
2. **Trigger manual** → Vá em Actions > Deploy to Google Cloud E2 > Run workflow

### Fluxo do Deploy:

```mermaid
graph LR
    A[Push to main] --> B[Build Docker Image]
    B --> C[Transfer to GCP E2]
    C --> D[Stop Old Containers]
    D --> E[Start Infrastructure]
    E --> F[Run Migrations]
    F --> G[Start Application]
    G --> H[Health Check]
```

## 📊 Monitoramento e Logs

### Ver Logs da Aplicação

```bash
# SSH na máquina E2
ssh seu_usuario@IP_DA_MAQUINA

# Ver logs em tempo real
docker logs -f orkestrai-api

# Ver últimas 100 linhas
docker logs --tail 100 orkestrai-api

# Ver logs dos serviços
docker compose logs -f postgres
docker compose logs -f redis
```

### Verificar Status dos Containers

```bash
# Ver containers rodando
docker ps

# Ver uso de recursos
docker stats

# Ver redes
docker network ls
```

### Acessar a API

```bash
# URL da API
http://SEU_IP_EXTERNO:8001

# Documentação Swagger
http://SEU_IP_EXTERNO:8001/docs

# Health check
curl http://SEU_IP_EXTERNO:8001/docs
```

## 🔄 Comandos Úteis

### Restart da Aplicação

```bash
docker restart orkestrai-api
```

### Rebuild e Redeploy Manual

```bash
cd ~/orkestrai-api
docker stop orkestrai-api && docker rm orkestrai-api
docker build -t orkestrai-api:latest .
docker run -d --name orkestrai-api --network agents_network --restart unless-stopped -p 8001:8001 --env-file .env orkestrai-api:latest
```

### Backup do Banco de Dados

```bash
# Criar backup
docker exec agents_postgres pg_dump -U agentuser agentsdb > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i agents_postgres psql -U agentuser agentsdb < backup_20240101.sql
```

### Limpar Docker (liberar espaço)

```bash
# Remover imagens não usadas
docker image prune -a -f

# Remover volumes não usados
docker volume prune -f

# Limpar tudo não usado
docker system prune -a -f
```

## 🔒 Segurança

### Recomendações de Segurança:

1. **Usar senhas fortes** para POSTGRES_PASSWORD e REDIS_PASSWORD
2. **Restringir IPs** nas regras de firewall (não usar 0.0.0.0/0 em produção)
3. **Usar HTTPS** com certificado SSL (configure Nginx como proxy reverso)
4. **Rotacionar secrets** regularmente
5. **Monitorar logs** para atividades suspeitas
6. **Backup regular** do banco de dados

### Configurar HTTPS com Nginx (Opcional mas Recomendado):

```bash
# Instalar Nginx e Certbot
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Configurar Nginx
sudo nano /etc/nginx/sites-available/orkestrai
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

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

```bash
# Ativar configuração
sudo ln -s /etc/nginx/sites-available/orkestrai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com
```

## 🐛 Troubleshooting

### Problema: Container não inicia

```bash
# Ver logs completos
docker logs orkestrai-api

# Verificar variáveis de ambiente
docker exec orkestrai-api env

# Verificar conectividade com banco
docker exec orkestrai-api python -c "from src.database import engine; print('✅ DB OK')"
```

### Problema: Deploy falha no GitHub Actions

1. Verificar secrets estão corretos
2. Testar SSH manualmente: `ssh -i chave_privada usuario@ip`
3. Verificar logs do workflow no GitHub Actions
4. Verificar espaço em disco na máquina E2: `df -h`

### Problema: API retorna erro 502/503

```bash
# Verificar se container está rodando
docker ps | grep orkestrai-api

# Verificar saúde do banco
docker compose ps

# Reiniciar tudo
docker compose restart
docker restart orkestrai-api
```

## 📚 Referências

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Google Cloud E2 Instances](https://cloud.google.com/compute/docs/machine-types#e2_machine_types)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## 🎉 Conclusão

Agora você tem um pipeline de CI/CD completo! Cada push para a branch main/master fará deploy automático da sua aplicação.

**Próximos passos sugeridos:**
1. Configurar HTTPS com certificado SSL
2. Implementar backup automático do banco de dados
3. Configurar monitoramento (Prometheus + Grafana)
4. Adicionar testes automatizados no workflow CI

---

Desenvolvido com ❤️ para Orkestrai API

