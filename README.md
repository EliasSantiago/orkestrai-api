# Orkestrai API

API completa para gerenciamento de agentes de IA com suporte a múltiplos LLMs (Google Gemini, OpenAI), context management via Redis e autenticação JWT.

## 🚀 Quick Start com Docker

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+
- API Keys: Google Gemini e OpenAI

### Iniciar Aplicação

```bash
# 1. Clonar repositório
git clone https://github.com/EliasSantiago/orkestrai-api.git
cd orkestrai-api

# 2. Configurar variáveis de ambiente
cp env.template .env
# Edite .env com suas API keys

# 3. Iniciar serviços
docker-compose up -d

# 4. Acessar API
# Docs: http://localhost:8001/docs
# API: http://localhost:8001
```

## 📦 Estrutura Docker

### Serviços

- **PostgreSQL 16**: Persistência de dados
- **Redis 7**: Cache e gerenciamento de contexto
- **API FastAPI**: Aplicação principal (porta 8001)

### Arquivos Docker

```
├── Dockerfile              # Imagem da aplicação
├── docker-compose.yml      # Desenvolvimento local
├── docker-compose.prod.yml # Produção
├── docker-entrypoint.sh    # Entrypoint com migrations
└── .dockerignore          # Exclusões de build
```

### Migrações Automáticas

As tabelas do banco são **criadas automaticamente** no primeiro deploy:

```bash
# Migrations rodam automaticamente:
# 1. Durante o deploy (GitHub Actions)
# 2. Na inicialização do container
# 3. No docker-compose up

# Você não precisa criar tabelas manualmente! ✅
```

Ver: `docs/DATABASE_MIGRATIONS.md`

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# Database
POSTGRES_USER=agentuser
POSTGRES_PASSWORD=sua_senha_forte
POSTGRES_DB=agentsdb
DATABASE_URL=postgresql://agentuser:senha@postgres:5432/agentsdb

# Redis
REDIS_PASSWORD=sua_senha_forte
REDIS_URL=redis://:senha@redis:6379/0

# API
SECRET_KEY=sua_chave_secreta_32_caracteres
GOOGLE_API_KEY=sua_chave_google
OPENAI_API_KEY=sua_chave_openai

# Environment
DEBUG=False
ENVIRONMENT=production
```

Ver template completo em `env.template`

## 🔧 Comandos Docker Úteis

```bash
# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f
docker logs orkestrai-api

# Parar serviços
docker-compose down

# Rebuild após mudanças
docker-compose up -d --build

# Acessar banco
docker exec -it agents_postgres psql -U agentuser -d agentsdb

# Backup banco
docker exec agents_postgres pg_dump -U agentuser agentsdb > backup.sql
```

## 🚀 Deploy em Produção (Google Cloud E2)

### Deploy Automático com GitHub Actions

**Configurar Secrets no GitHub:**

```
Settings → Secrets and variables → Actions:
- GCP_HOST: IP da máquina E2
- GCP_USERNAME: Usuário SSH
- GCP_SSH_KEY: Chave privada SSH
```

**Deploy:**

```bash
# Opção 1: Push direto na main
git push origin main

# Opção 2: Via Pull Request (recomendado)
# 1. Criar branch: git checkout -b feature/nova-funcionalidade
# 2. Fazer commit e push da branch
# 3. Abrir Pull Request no GitHub
# 4. Merge do PR → Deploy automático!
```

Ver guia completo: `docs/DEPLOY_COM_PR.md`

### Setup Manual do Servidor

```bash
# 1. Instalar Docker no servidor E2
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 2. Criar .env no servidor
mkdir -p ~/orkestrai-api
cd ~/orkestrai-api
nano .env  # Configure variáveis

# 3. Clonar e iniciar
git clone https://github.com/EliasSantiago/orkestrai-api.git .
docker-compose up -d
```

Ver documentação completa: `docs/DEPLOY_SETUP.md`

## 📚 API Endpoints

### Autenticação

```bash
# Registrar usuário
POST /api/auth/register

# Login
POST /api/auth/login

# Obter token
POST /api/auth/token
```

### Agentes

```bash
# Criar agente
POST /api/agents

# Listar agentes
GET /api/agents

# Chat com agente
POST /api/agents/chat

# Detalhes do agente
GET /api/agents/{agent_id}
```

### Conversas

```bash
# Histórico
GET /api/conversations/{agent_id}

# Limpar contexto
DELETE /api/conversations/{agent_id}
```

Documentação completa: http://localhost:8001/docs

## 🏗️ Arquitetura

```
orkestrai-api/
├── src/
│   ├── api/              # Endpoints FastAPI
│   ├── core/             # LLM providers e factories
│   ├── domain/           # Entities e business logic
│   ├── infrastructure/   # Banco, cache, external services
│   └── services/         # Application services
├── tools/                # Ferramentas para agentes
├── scripts/              # Scripts de deploy e utilitários
├── migrations/           # Migrações SQL
└── docs/                 # Documentação detalhada
```

## 🔒 Segurança

- Autenticação JWT com senhas hasheadas (bcrypt)
- Validação de entrada com Pydantic
- Rate limiting configurável
- Secrets nunca commitados (`.gitignore`)
- HTTPS recomendado em produção

## 📊 Monitoramento

```bash
# Status dos serviços
./scripts/check_server_status.sh

# Backup automático
./scripts/backup_db.sh

# Ver logs
./scripts/monitor_logs.sh
```

## 🛠️ Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Iniciar em modo dev
uvicorn src.api.main:app --reload --port 8001
```

## 🧪 Testes

```bash
# Executar testes
pytest

# Com coverage
pytest --cov=src tests/
```

## 📖 Documentação Adicional

- **[Deploy Completo](docs/DEPLOY_SETUP.md)** - Setup em Google Cloud E2
- **[Obter Secrets](docs/COMO_OBTER_SECRETS.md)** - Como configurar SSH e secrets
- **[Deploy com PR](docs/DEPLOY_COM_PR.md)** - Deploy via Pull Request
- **[Database Migrations](docs/DATABASE_MIGRATIONS.md)** - Sistema de migrações
- **[FAQ](docs/FAQ_DEPLOY.md)** - Perguntas frequentes e troubleshooting
- **[API Reference](docs/api-reference.md)** - Documentação completa da API
- **[MCP Setup](docs/MCP_SETUP.md)** - Model Context Protocol

## 🆘 Suporte

- Issues: https://github.com/EliasSantiago/orkestrai-api/issues
- Documentação: `/docs`
- API Docs: http://localhost:8001/docs

---

**Stack:** Python 3.11 • FastAPI • PostgreSQL 16 • Redis 7 • Docker • Google Gemini • OpenAI
# Trigger deploy
