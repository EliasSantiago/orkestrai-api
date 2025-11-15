# 🏗️ Arquitetura da Aplicação

## 📐 Visão Geral

A aplicação está organizada em camadas claras que facilitam a evolução e manutenção:

```
┌─────────────────────────────────────────────────┐
│         Frontend (Customizado ou ADK Web)        │
│         - ADK Web: http://localhost:8000        │
│         - API REST: http://localhost:8001        │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              API REST (FastAPI)                │
│         - Autenticação (JWT)                   │
│         - Gerenciamento de Agentes              │
│         - Chat com Agentes                     │
│         - Contexto Conversacional (Redis)       │
└─────────────────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
┌─────────────────┐      ┌─────────────────┐
│   PostgreSQL    │      │      Redis      │
│   (Agentes)     │      │   (Contexto)    │
└─────────────────┘      └─────────────────┘
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              Agentes ADK                        │
│  - Carregados do banco de dados                 │
│  - Gerados dinamicamente                        │
│  - Com suporte a tools                          │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│          Ferramentas Compartilhadas            │
│  tools/                                         │
│  ├── calculator_tool.py                         │
│  └── time_tool.py                               │
└─────────────────────────────────────────────────┘
```

---

## 🗂️ Estrutura de Diretórios

### `/src` - Código Fonte Principal

```
src/
├── api/                    # Endpoints REST
│   ├── main.py            # Aplicação FastAPI
│   ├── routes/            # Rotas da API
│   └── schemas.py         # Schemas Pydantic
├── services/              # Serviços de negócio
│   ├── agent_service.py   # Lógica de agentes
│   └── conversation_service.py  # Contexto Redis
├── database.py            # Conexão PostgreSQL
├── redis_client.py        # Cliente Redis
└── adk_loader.py          # Carregador de agentes ADK
```

### `/tools` - Ferramentas Compartilhadas

Ferramentas que podem ser usadas por qualquer agente:

```
tools/
├── __init__.py           # Exporta todas as ferramentas
├── calculator_tool.py    # Calculadora matemática
└── time_tool.py          # Informações de data/hora
```

### `/agents` - Agentes (Deprecated)

⚠️ **Nota**: Esta pasta não é mais usada. Agentes agora são criados via API REST e armazenados no PostgreSQL.

### `/.agents_db` - Agentes Gerados (Automático)

Gerado automaticamente quando o ADK Web inicia:

```
.agents_db/
  agents/
    db_agents/
      agent.py      # Gerado automaticamente
      __init__.py
```

---

## 🔄 Fluxo de Dados

### 1. Criação de Agente

```
Usuário → POST /api/agents → PostgreSQL → Sincronização → ADK
```

### 2. Chat com Agente

```
Frontend → POST /api/agents/chat
    ↓
Recupera contexto do Redis
    ↓
Carrega agente do PostgreSQL
    ↓
Injeta contexto na instruction
    ↓
Executa agente ADK
    ↓
Salva mensagens no Redis
    ↓
Retorna resposta
```

### 3. Interface ADK Web

```
ADK Web → Carrega agentes do banco
    ↓
Gera arquivos Python dinamicamente
    ↓
Expõe interface web em http://localhost:8000
```

---

## 🔧 Componentes Principais

### API REST (FastAPI)

- **Porta**: 8001
- **Endpoints**: `/api/*`
- **Autenticação**: JWT
- **Documentação**: http://localhost:8001/docs

### ADK Web Server

- **Porta**: 8000
- **Interface**: Interface web do Google ADK
- **Agentes**: Carregados do banco de dados

### PostgreSQL

- **Porta**: 5432
- **Armazena**: Usuários, agentes
- **Gerenciado**: Docker Compose

### Redis

- **Porta**: 6379
- **Armazena**: Contexto conversacional
- **TTL**: Configurável via `.env`

---

## 🎯 Princípios de Design

### 1. Separação de Responsabilidades
- **API REST**: Gerenciamento e integração
- **ADK**: Execução de agentes
- **PostgreSQL**: Persistência de dados
- **Redis**: Contexto conversacional

### 2. Escalabilidade
- Agentes carregados dinamicamente
- Contexto em memória (Redis)
- API stateless (JWT)

### 3. Manutenibilidade
- Código modular e organizado
- Documentação completa
- Scripts de inicialização claros

---

## 📚 Referências

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/docs/)

