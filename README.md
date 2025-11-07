# Agents ADK API - Sistema Completo de Agentes de IA

Aplicação completa para criar e gerenciar agentes de IA utilizando o Google ADK, com suporte para context management via Redis, API REST completa e interface web customizável.

## 🚀 Características Principais

- **Google ADK**: Framework para desenvolvimento de agentes de IA
- **Multi-LLM**: Suporte para Google Gemini e OpenAI
- **API REST Completa**: Gerenciamento de usuários, agentes e conversas
- **Context Management**: Sistema de contexto conversacional com Redis
- **Autenticação JWT**: Sistema seguro de registro e login
- **PostgreSQL + Redis**: Persistência de dados e contexto
- **Frontend Customizável**: API REST permite criar seu próprio frontend

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Docker e Docker Compose
- API Keys:
  - Google Gemini API Key
  - OpenAI API Key

## 🛠️ Instalação Rápida

```bash
# 1. Setup inicial
./scripts/setup.sh

# 2. Configure .env com suas API keys
cp .env.example .env
# Edite .env e adicione GOOGLE_API_KEY e OPENAI_API_KEY

# 3. Inicie serviços (PostgreSQL e Redis)
./scripts/start_services.sh

# 4. Inicialize banco de dados
./scripts/init_database.sh
```

## 🎯 Iniciar Aplicação

### Opção 1: API REST + ADK Web (Recomendado)

```bash
# Terminal 1: Iniciar API REST
./scripts/start_api.sh
# API em: http://localhost:8001
# Docs em: http://localhost:8001/docs

# Terminal 2: Iniciar ADK Web
./scripts/start_adk_web.sh
# Web UI em: http://localhost:8000
```

### Opção 2: Apenas API REST (para frontend customizado)

```bash
./scripts/start_api.sh
# Use a API para chat: POST /api/agents/chat
```

## 📚 Documentação

Toda a documentação está organizada em `docs/`:

- **[Guia de Início](docs/getting-started.md)** - Setup completo e instalação
- **[Referência da API](docs/api-reference.md)** - Todos os endpoints disponíveis
- **[Guia de Agentes](docs/agent-guide.md)** - Como criar e gerenciar agentes
- **[Contexto Redis](docs/redis-conversations.md)** - Sistema de contexto conversacional
- **[Frontend Customizado](docs/frontend-guide.md)** - Como criar seu próprio frontend
- **[Arquitetura](docs/architecture.md)** - Estrutura e design da aplicação
- **[Troubleshooting](docs/troubleshooting.md)** - Solução de problemas comuns
- **[Migração](docs/migration.md)** - Notas de versões e migrações

## 🎯 Fluxo Básico de Uso

1. **Registrar/Login**: `POST /api/auth/register` ou `/api/auth/login`
2. **Criar Agente**: `POST /api/agents`
3. **Chat com Agente**: `POST /api/agents/chat`
4. **Gerenciar Contexto**: Endpoints em `/api/conversations`

## 🔧 Portas Padrão

- **API REST**: `8001` - http://localhost:8001
- **ADK Web**: `8000` - http://localhost:8000
- **PostgreSQL**: `5432`
- **Redis**: `6379`

## 📖 Documentação Interativa

Acesse `http://localhost:8001/docs` para ver a documentação completa da API com exemplos interativos (Swagger UI).

## 🏗️ Estrutura do Projeto

```
.
├── docs/               # Documentação organizada
├── scripts/            # Scripts de inicialização
├── src/                # Código fonte
│   ├── api/           # Endpoints REST
│   ├── services/      # Serviços de negócio
│   └── ...
├── tools/              # Ferramentas para agentes
└── docker-compose.yml  # PostgreSQL e Redis
```

## 📝 Scripts Disponíveis

Todos os scripts estão em `scripts/`:

- `setup.sh` - Instalação inicial
- `start_services.sh` - Iniciar PostgreSQL e Redis
- `start_api.sh` - Iniciar API REST (porta 8001)
- `start_adk_web.sh` - Iniciar ADK Web (porta 8000)
- `init_database.sh` - Inicializar banco de dados
- `migrate_database.sh` - Migrações do banco

## 🚀 Próximos Passos

1. Leia o [Guia de Início](docs/getting-started.md)
2. Crie seu primeiro agente com o [Guia de Agentes](docs/agent-guide.md)
3. Explore a [Referência da API](docs/api-reference.md)
4. Configure [Contexto Redis](docs/redis-conversations.md) para conversas persistentes

## 📄 Licença

Este projeto utiliza o Google ADK e está sujeito às licenças dos respectivos componentes.
