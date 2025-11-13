# 🎨 Arquitetura Visual da Aplicação

Diagramas visuais e resumos da arquitetura.

## 🏗️ Estrutura de Pastas

```
src/
├── api/                          # 🌐 CAMADA DE APRESENTAÇÃO
│   ├── main.py                   # ⚙️ Config do FastAPI
│   ├── schemas.py                # 📋 Modelos Pydantic (request/response)
│   ├── dependencies.py           # 🔗 Dependências (auth, DB)
│   ├── di.py                     # 💉 Injeção de Dependências
│   ├── agent_routes.py           # 🛣️ Rotas de Agentes
│   ├── agent_chat_routes.py     # 💬 Rotas de Chat
│   ├── auth_routes.py            # 🔐 Rotas de Autenticação
│   └── middleware/               # 🛡️ Middlewares
│
├── application/                  # 🎯 CAMADA DE APLICAÇÃO
│   └── use_cases/               # 📦 Casos de Uso
│       └── agents/
│           ├── create_agent.py  # ➕ Criar agente
│           ├── get_agent.py     # 🔍 Buscar agente
│           ├── update_agent.py  # ✏️ Atualizar agente
│           ├── delete_agent.py  # 🗑️ Deletar agente
│           └── chat_with_agent.py # 💬 Conversar
│
├── domain/                       # 🧠 CAMADA DE DOMÍNIO
│   ├── entities/
│   │   └── agent.py             # 🤖 Entidade Agent
│   ├── repositories/
│   │   └── agent_repository.py  # 📚 Interface do Repository
│   ├── services/
│   │   ├── validation_service.py # ✅ Validações
│   │   └── tool_loader_service.py # 🔧 Carregamento de tools
│   └── exceptions/
│       └── agent_exceptions.py   # ⚠️ Exceções de domínio
│
├── infrastructure/               # 🔧 CAMADA DE INFRAESTRUTURA
│   └── database/
│       ├── agent_repository_impl.py # 💾 Implementação do Repository
│       └── entity_mapper.py         # 🔄 Conversão Entity ↔ Model
│
├── core/                         # 🎛️ NÚCLEO DA APLICAÇÃO
│   ├── llm_factory.py           # 🏭 Factory de Providers
│   ├── llm_provider.py          # 🔌 Interface base
│   └── llm_providers/           # 🤖 Implementações
│       ├── onpremise_provider.py # 🏢 On-Premise
│       ├── adk_provider.py       # 🔷 Google Gemini
│       ├── openai_provider.py    # 🟢 OpenAI
│       └── ollama_provider.py    # 🦙 Ollama
│
├── models.py                     # 🗄️ Models SQLAlchemy
├── database.py                   # 🔗 Config do Banco
└── config.py                     # ⚙️ Configurações (.env)
```

---

## 🔄 Fluxo Completo de uma Requisição

### **Exemplo: Criar Agente**

```
┌─────────────────────────────────────────────────────┐
│  👤 USUÁRIO                                         │
│  curl -X POST /api/agents                          │
│  Body: {"name": "Bot", "model": "qwen3:30b"}      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🌐 API LAYER (src/api/agent_routes.py)           │
│                                                     │
│  @router.post("")                                  │
│  async def create_agent(                           │
│      agent_data: AgentCreate,        ← Validação   │
│      user_id: int,                   ← Auth        │
│      use_case: CreateAgentUseCase    ← DI          │
│  ):                                                 │
│      return use_case.execute(...)                  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🎯 APPLICATION LAYER (use_cases/create_agent.py)  │
│                                                     │
│  class CreateAgentUseCase:                         │
│      def execute(self, ...):                       │
│          # 1. Validar modelo                       │
│          self.validator.validate_model(model)      │
│                                                     │
│          # 2. Validar file search                  │
│          self.validator.validate_file_search(...)  │
│                                                     │
│          # 3. Criar entidade                       │
│          agent = Agent(...)                        │
│                                                     │
│          # 4. Persistir                            │
│          return self.repository.create(agent)      │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────────┐    ┌─────────────────────────────┐
│  🧠 DOMAIN       │    │  🧠 DOMAIN                  │
│  (entities/)     │    │  (services/)                │
│                  │    │                             │
│  class Agent:    │    │  class ValidationService:   │
│    name: str     │    │    def validate_model(...): │
│    model: str    │    │      # Valida se modelo     │
│    tools: list   │    │      # existe               │
│    ...           │    │      pass                   │
└──────────────────┘    └─────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  🔧 INFRASTRUCTURE (database/repository_impl.py)   │
│                                                     │
│  class AgentRepositoryImpl:                        │
│      def create(self, agent: Agent) -> Agent:      │
│          # 1. Converter Entity → Model             │
│          db_agent = entity_to_model(agent)         │
│                                                     │
│          # 2. Salvar no banco                      │
│          self.db.add(db_agent)                     │
│          self.db.commit()                          │
│          self.db.refresh(db_agent)                 │
│                                                     │
│          # 3. Converter Model → Entity             │
│          return model_to_entity(db_agent)          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🗄️ DATABASE (PostgreSQL)                         │
│                                                     │
│  INSERT INTO agents (                              │
│      name, model, tools, user_id, ...              │
│  ) VALUES (                                         │
│      'Bot', 'qwen3:30b', [...], 1, ...             │
│  )                                                  │
│  RETURNING *                                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ (Resposta sobe na ordem inversa)
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  👤 USUÁRIO                                         │
│  HTTP 201 Created                                   │
│  {                                                  │
│    "id": 1,                                         │
│    "name": "Bot",                                   │
│    "model": "qwen3:30b",                            │
│    ...                                              │
│  }                                                  │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Fluxo de Chat com Agente

```
┌─────────────────────────────────────────────────────┐
│  👤 USUÁRIO                                         │
│  POST /api/agents/chat                              │
│  {"agent_id": 1, "message": "Olá!"}                │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🌐 API (agent_chat_routes.py)                     │
│  Busca agente do banco                             │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🎯 USE CASE (chat_with_agent.py)                  │
│  • Valida agente                                    │
│  • Carrega histórico do Redis                      │
│  • Determina provider pelo modelo                  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🏭 LLM FACTORY (llm_factory.py)                   │
│  get_provider("qwen3:30b")                         │
│    ↓                                                │
│  OnPremiseProvider ✅                              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🤖 ONPREMISE PROVIDER                             │
│  • Gera token OAuth                                 │
│  • Monta payload                                    │
│  • Chama API on-premise                            │
│  • Stream de resposta                              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  🌐 API ON-PREMISE                                  │
│  POST /chat                                         │
│  {                                                  │
│    "model": "qwen3:30b",                            │
│    "messages": [...],                               │
│    "stream": true                                   │
│  }                                                  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼ (Stream)
┌─────────────────────────────────────────────────────┐
│  👤 USUÁRIO                                         │
│  Olá! Como posso ajudar? [chunk 1]                 │
│  Estou aqui para... [chunk 2]                      │
│  ...                                                │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Dependências entre Camadas

```
┌──────────────────┐
│   API Layer      │  ← Depende de Application
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Application Layer│  ← Depende de Domain
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Domain Layer    │  ← Não depende de ninguém! (Núcleo)
└────────┬─────────┘
         ▲
         │
┌────────┴─────────┐
│Infrastructure    │  ← Implementa Domain
└──────────────────┘
```

**Regra de Ouro:** As setas **SEMPRE** apontam para o Domain (centro)

---

## 🔄 Entity vs Model

### **Entity (Domain)**
```python
# src/domain/entities/agent.py
@dataclass
class Agent:
    """Entidade de negócio (pura, sem dependências)"""
    id: Optional[int]
    name: str
    model: str
    tools: List[str]
    # ... lógica de negócio
```

### **Model (Infrastructure)**
```python
# src/models.py
class Agent(Base):
    """Model SQLAlchemy (acoplado ao banco)"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    model = Column(String, nullable=False)
    tools = Column(ARRAY(String), default=[])
    # ... mapeamento ORM
```

### **Conversão (Mapper)**
```python
# src/infrastructure/database/entity_mapper.py

def model_to_entity(model: AgentModel) -> Agent:
    """Model (DB) → Entity (Domain)"""
    return Agent(
        id=model.id,
        name=model.name,
        model=model.model,
        tools=model.tools,
        # ...
    )

def entity_to_model(entity: Agent) -> AgentModel:
    """Entity (Domain) → Model (DB)"""
    return AgentModel(
        id=entity.id,
        name=entity.name,
        model=entity.model,
        tools=entity.tools,
        # ...
    )
```

---

## 🎨 Injeção de Dependências (DI)

### **Como Funciona:**

```python
# 1. Definir factory (src/api/di.py)
def get_create_agent_use_case(
    agent_repository: AgentRepository = Depends(get_agent_repository),
    validator: ValidationService = Depends(get_validation_service)
) -> CreateAgentUseCase:
    return CreateAgentUseCase(agent_repository, validator)

# 2. Usar na rota (src/api/agent_routes.py)
@router.post("")
async def create_agent(
    data: AgentCreate,
    use_case: CreateAgentUseCase = Depends(get_create_agent_use_case)
    #       ↑ FastAPI injeta automaticamente!
):
    return use_case.execute(...)
```

### **Benefícios:**
✅ Desacoplamento  
✅ Fácil testar (mock dependencies)  
✅ Código limpo  

---

## 📋 Resumo dos Arquivos-Chave

| Arquivo | O que faz | Quando modificar |
|---------|-----------|------------------|
| `src/api/main.py` | Config FastAPI | Adicionar novos routers |
| `src/api/schemas.py` | Request/Response | Novos endpoints |
| `src/api/*_routes.py` | Rotas HTTP | Novos endpoints |
| `src/api/di.py` | DI factories | Novos use cases |
| `src/application/use_cases/` | Casos de uso | Nova lógica |
| `src/domain/entities/` | Entidades | Novos campos |
| `src/domain/repositories/` | Interfaces | Novos métodos |
| `src/infrastructure/database/` | Implementações | Novos métodos |
| `src/models.py` | Models ORM | Mudanças no DB |
| `src/config.py` | Configurações | Novas env vars |

---

## 🎯 Princípios SOLID na Aplicação

### **S - Single Responsibility**
Cada classe tem **uma responsabilidade**:
- Route: Receber HTTP
- Use Case: Orquestrar
- Entity: Representar negócio
- Repository: Persistir

### **O - Open/Closed**
Aberto para extensão, fechado para modificação:
- Adicionar novo provider sem mudar existentes
- Adicionar novo use case sem mudar rotas

### **L - Liskov Substitution**
Implementações podem ser substituídas:
```python
# Pode trocar implementação sem quebrar
repository: AgentRepository = AgentRepositoryImpl()
repository: AgentRepository = AgentRepositoryMock()  # ✅ Funciona!
```

### **I - Interface Segregation**
Interfaces específicas:
- `AgentRepository` - apenas métodos de agente
- `LLMProvider` - apenas métodos de LLM

### **D - Dependency Inversion**
Dependa de abstrações, não de implementações:
```python
# ✅ BOM: Depende da interface
class CreateAgentUseCase:
    def __init__(self, repository: AgentRepository):  # Interface!
        self.repository = repository

# ❌ RUIM: Depende da implementação
class CreateAgentUseCase:
    def __init__(self, repository: AgentRepositoryImpl):  # Concreto!
        self.repository = repository
```

---

## 🚀 Exemplo Rápido: Adicionar Campo

```
1. Domain: Agent.is_active = True
   ↓
2. Infrastructure: AgentModel.is_active = Column(Boolean)
   ↓
3. Migration: alembic revision -m "add_is_active"
   ↓
4. Application: (sem mudança, já usa Entity)
   ↓
5. API: AgentResponse.is_active: bool
   ↓
6. Teste!
```

---

## 📚 Recursos

- **Guia Completo:** `ARCHITECTURE_GUIDE.md`
- **Guia Rápido:** `ADD_NEW_FEATURE_QUICK_GUIDE.md`
- **Este Resumo:** `ARCHITECTURE_VISUAL_SUMMARY.md`

---

**Agora você entende completamente a arquitetura!** 🎉

