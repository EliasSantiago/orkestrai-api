# 🏗️ Guia de Arquitetura da Aplicação

Documentação completa sobre a arquitetura da aplicação e como adicionar novos recursos.

## 📋 Índice

1. [Visão Geral da Arquitetura](#visão-geral)
2. [Camadas da Aplicação](#camadas)
3. [Fluxo de uma Requisição](#fluxo)
4. [Como Adicionar um Novo Endpoint](#novo-endpoint)
5. [Exemplos Práticos](#exemplos)

---

## 🎯 Visão Geral da Arquitetura

Sua aplicação usa **Clean Architecture** (Arquitetura Limpa) com **Domain-Driven Design (DDD)**.

### **Princípios:**

✅ **Independência de Framework** - Lógica de negócio não depende do FastAPI  
✅ **Testabilidade** - Cada camada pode ser testada isoladamente  
✅ **Independência de UI** - Pode trocar FastAPI por outro framework  
✅ **Independência de Banco** - Pode trocar PostgreSQL por outro DB  
✅ **Separação de Responsabilidades** - Cada camada tem um papel específico  

### **Diagrama da Arquitetura:**

```
┌─────────────────────────────────────────────────────────┐
│                     EXTERNAL                             │
│                  (Usuários, APIs)                        │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  API LAYER                               │
│              (src/api/*.py)                              │
│  • Routes (agent_routes.py)                              │
│  • Schemas (schemas.py)                                  │
│  • Dependencies (dependencies.py, di.py)                 │
│  • Middleware (error_handler.py)                         │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│             APPLICATION LAYER                            │
│          (src/application/use_cases/)                    │
│  • Create Agent (create_agent.py)                        │
│  • Get Agent (get_agent.py)                              │
│  • Update Agent (update_agent.py)                        │
│  • Delete Agent (delete_agent.py)                        │
│  • Chat with Agent (chat_with_agent.py)                  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                DOMAIN LAYER                              │
│               (src/domain/)                              │
│  • Entities (agent.py)                                   │
│  • Repository Interfaces (agent_repository.py)           │
│  • Domain Services (validation_service.py)               │
│  • Exceptions (agent_exceptions.py)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│            INFRASTRUCTURE LAYER                          │
│            (src/infrastructure/)                         │
│  • Repository Implementations (agent_repository_impl.py) │
│  • Database (database/)                                  │
│  • External Services (external/)                         │
└──────────────────────────────────────────────────────────┘
```

---

## 📦 Camadas da Aplicação

### **1. API Layer** (`src/api/`)

**Responsabilidade:** Interface com o mundo exterior (HTTP)

**Arquivos:**
- `main.py` - Configuração principal do FastAPI
- `*_routes.py` - Definição de rotas/endpoints
- `schemas.py` - Modelos Pydantic (request/response)
- `dependencies.py` - Dependências do FastAPI
- `di.py` - Injeção de dependências
- `middleware/` - Middlewares (ex: error_handler)

**O que faz:**
- Recebe requisições HTTP
- Valida dados de entrada (Pydantic)
- Chama Use Cases
- Retorna respostas HTTP

### **2. Application Layer** (`src/application/`)

**Responsabilidade:** Casos de uso (lógica de aplicação)

**Estrutura:**
```
application/
├── use_cases/
│   └── agents/
│       ├── create_agent.py      # Criar agente
│       ├── get_agent.py         # Buscar agente
│       ├── get_user_agents.py   # Listar agentes
│       ├── update_agent.py      # Atualizar agente
│       ├── delete_agent.py      # Deletar agente
│       └── chat_with_agent.py   # Conversar com agente
└── dto/                          # Data Transfer Objects
```

**O que faz:**
- Orquestra fluxo de negócio
- Chama repositories
- Chama domain services
- Coordena transações

### **3. Domain Layer** (`src/domain/`)

**Responsabilidade:** Lógica de negócio pura (core da aplicação)

**Estrutura:**
```
domain/
├── entities/
│   └── agent.py                 # Entidade Agent
├── repositories/
│   └── agent_repository.py      # Interface do Repository
├── services/
│   ├── validation_service.py    # Validações de negócio
│   └── tool_loader_service.py   # Serviços de domínio
└── exceptions/
    └── agent_exceptions.py      # Exceções de negócio
```

**O que faz:**
- Define entidades do negócio
- Define regras de negócio
- Define interfaces (contratos)
- Define exceções de domínio

### **4. Infrastructure Layer** (`src/infrastructure/`)

**Responsabilidade:** Implementações concretas (detalhes técnicos)

**Estrutura:**
```
infrastructure/
├── database/
│   ├── agent_repository_impl.py  # Implementação do Repository
│   └── entity_mapper.py          # Mapeamento Entity ↔ Model
├── external/                      # Serviços externos
├── cache/                         # Cache (Redis)
└── persistence/                   # Persistência
```

**O que faz:**
- Implementa repositories
- Acessa banco de dados
- Integra com APIs externas
- Gerencia cache

### **5. Core Layer** (`src/core/`)

**Responsabilidade:** Lógica central compartilhada

**Estrutura:**
```
core/
├── llm_factory.py               # Factory de LLM providers
├── llm_provider.py              # Interface base
├── llm_providers/
│   ├── adk_provider.py          # Gemini (ADK)
│   ├── openai_provider.py       # OpenAI
│   ├── onpremise_provider.py    # On-Premise
│   └── ollama_provider.py       # Ollama
└── oauth_token_manager.py       # Gerenciamento OAuth
```

---

## 🔄 Fluxo de uma Requisição

### **Exemplo: Criar um Agente**

```
1. Cliente HTTP
   │
   ├─→ POST /api/agents
   │   Body: {"name": "...", "model": "..."}
   │
   ▼

2. API Layer (src/api/agent_routes.py)
   │
   ├─→ @router.post("")
   │   - Valida request (Pydantic schema)
   │   - Extrai user_id (dependência)
   │   - Injeta use case (DI)
   │
   ▼

3. Application Layer (src/application/use_cases/agents/create_agent.py)
   │
   ├─→ CreateAgentUseCase.execute()
   │   - Valida modelo (ValidationService)
   │   - Cria entidade Agent
   │   - Chama repository.create()
   │
   ▼

4. Domain Layer (src/domain/entities/agent.py)
   │
   ├─→ Agent (entidade)
   │   - Valida dados
   │   - Aplica regras de negócio
   │
   ▼

5. Infrastructure Layer (src/infrastructure/database/agent_repository_impl.py)
   │
   ├─→ AgentRepositoryImpl.create()
   │   - Converte Entity → Model (SQLAlchemy)
   │   - Salva no banco (PostgreSQL)
   │   - Converte Model → Entity
   │
   ▼

6. Resposta
   │
   └─→ HTTP 201 Created
       Body: {"id": 1, "name": "...", ...}
```

---

## 🆕 Como Adicionar um Novo Endpoint

Vamos criar um exemplo completo: **Listar Modelos Disponíveis**

### **Passo 1: Definir o Schema (API Layer)**

📄 **Arquivo:** `src/api/schemas.py`

```python
# Adicione no final do arquivo

# Schema para resposta de modelo
class ModelInfo(BaseModel):
    name: str
    provider: str
    available: bool
    
    class Config:
        from_attributes = True


class ModelsListResponse(BaseModel):
    models: List[ModelInfo]
    total: int
```

### **Passo 2: Criar o Use Case (Application Layer)**

📄 **Arquivo:** `src/application/use_cases/models/list_models.py` (criar)

```python
"""Use case para listar modelos disponíveis."""

from typing import List
from src.core.llm_factory import LLMFactory


class ListModelsUseCase:
    """Use case para listar todos os modelos disponíveis."""
    
    def execute(self) -> dict:
        """
        Lista todos os modelos disponíveis de todos os providers.
        
        Returns:
            Dict com modelos agrupados por provider
        """
        # Obtém modelos de todos os providers
        all_models = LLMFactory.get_all_supported_models()
        
        # Formata resposta
        models_list = []
        for provider_name, models in all_models.items():
            for model in models:
                models_list.append({
                    "name": model,
                    "provider": provider_name,
                    "available": True
                })
        
        return {
            "models": models_list,
            "total": len(models_list)
        }
```

### **Passo 3: Criar a Rota (API Layer)**

📄 **Arquivo:** `src/api/models_routes.py` (já existe, vamos editar)

```python
"""Rotas para gerenciamento de modelos."""

from fastapi import APIRouter, Depends
from src.api.schemas import ModelsListResponse
from src.application.use_cases.models.list_models import ListModelsUseCase
from src.api.dependencies import get_current_user_id

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=ModelsListResponse)
async def list_available_models(
    user_id: int = Depends(get_current_user_id)  # Requer autenticação
):
    """
    Lista todos os modelos disponíveis.
    
    Returns:
        Lista de modelos com provider e status
    """
    use_case = ListModelsUseCase()
    result = use_case.execute()
    return result
```

### **Passo 4: Registrar a Rota (API Layer)**

📄 **Arquivo:** `src/api/main.py`

```python
# ... imports existentes ...
from src.api import models_routes  # Já deve existir

# ... código existente ...

# Registrar routers
app.include_router(auth_routes.router)
app.include_router(agent_routes.router)
app.include_router(agent_chat_routes.router)
app.include_router(models_routes.router)  # ✅ Certifique-se que está aqui
# ... outros routers ...
```

### **Passo 5: Testar**

```bash
# Com autenticação
curl -X GET http://localhost:8001/api/models \
  -H "Authorization: Bearer SEU_TOKEN"
```

**Resposta esperada:**
```json
{
  "models": [
    {
      "name": "qwen3:30b-a3b-instruct-2507-q4_K_M",
      "provider": "OnPremise",
      "available": true
    },
    {
      "name": "gemini-2.0-flash",
      "provider": "ADK",
      "available": true
    },
    ...
  ],
  "total": 25
}
```

---

## 📝 Exemplo Completo: Criar Recurso de Tags para Agentes

Vamos criar um recurso completo: **adicionar tags aos agentes**.

### **Passo 1: Atualizar Entidade (Domain)**

📄 **Arquivo:** `src/domain/entities/agent.py`

```python
# Adicione o campo tags
@dataclass
class Agent:
    name: str
    description: Optional[str]
    instruction: str
    model: str
    tools: List[str]
    use_file_search: bool
    user_id: int
    tags: List[str] = field(default_factory=list)  # ✅ NOVO
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### **Passo 2: Atualizar Model SQLAlchemy (Infrastructure)**

📄 **Arquivo:** `src/models.py`

```python
# Na classe Agent, adicione:
class Agent(Base):
    __tablename__ = "agents"
    
    # ... campos existentes ...
    tags = Column(ARRAY(String), default=[])  # ✅ NOVO
```

### **Passo 3: Criar Migration**

```bash
# Criar migration
alembic revision --autogenerate -m "add_tags_to_agents"

# Aplicar migration
alembic upgrade head
```

### **Passo 4: Atualizar Schemas (API)**

📄 **Arquivo:** `src/api/schemas.py`

```python
# Atualizar AgentCreate
class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    instruction: str
    model: str = "gemini-2.0-flash-exp"
    tools: Optional[List[str]] = None
    use_file_search: Optional[bool] = False
    tags: Optional[List[str]] = []  # ✅ NOVO

# Atualizar AgentUpdate
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    model: Optional[str] = None
    tools: Optional[List[str]] = None
    use_file_search: Optional[bool] = None
    tags: Optional[List[str]] = None  # ✅ NOVO

# Atualizar AgentResponse
class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    instruction: str
    model: str
    tools: List[str]
    use_file_search: bool
    tags: List[str]  # ✅ NOVO
    user_id: int
    created_at: datetime
    updated_at: datetime
```

### **Passo 5: Atualizar Use Cases (Application)**

📄 **Arquivo:** `src/application/use_cases/agents/create_agent.py`

```python
def execute(
    self,
    user_id: int,
    name: str,
    description: Optional[str],
    instruction: str,
    model: str = "gemini-2.0-flash-exp",
    tools: Optional[list] = None,
    use_file_search: bool = False,
    tags: Optional[list] = None  # ✅ NOVO
) -> Agent:
    # ... validações existentes ...
    
    # Criar agente
    agent = Agent(
        name=name,
        description=description,
        instruction=instruction,
        model=model,
        tools=tools or [],
        use_file_search=use_file_search,
        tags=tags or [],  # ✅ NOVO
        user_id=user_id
    )
    
    # Salvar
    return self.agent_repository.create(agent)
```

### **Passo 6: Atualizar Rota (API)**

📄 **Arquivo:** `src/api/agent_routes.py`

```python
@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    use_case: CreateAgentUseCase = Depends(get_create_agent_use_case)
):
    """Create a new agent for the current user."""
    try:
        agent_entity = use_case.execute(
            user_id=user_id,
            name=agent_data.name,
            description=agent_data.description,
            instruction=agent_data.instruction,
            model=agent_data.model,
            tools=agent_data.tools,
            use_file_search=agent_data.use_file_search if agent_data.use_file_search is not None else False,
            tags=agent_data.tags  # ✅ NOVO
        )
        
        # ... resto do código ...
```

### **Passo 7: Criar Endpoint para Buscar por Tags**

📄 **Arquivo:** `src/application/use_cases/agents/search_by_tags.py` (criar)

```python
"""Use case para buscar agentes por tags."""

from typing import List
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent


class SearchAgentsByTagsUseCase:
    """Use case para buscar agentes por tags."""
    
    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository
    
    def execute(self, user_id: int, tags: List[str]) -> List[Agent]:
        """
        Busca agentes que contenham todas as tags especificadas.
        
        Args:
            user_id: ID do usuário
            tags: Lista de tags para buscar
            
        Returns:
            Lista de agentes que contêm as tags
        """
        # Buscar todos os agentes do usuário
        all_agents = self.agent_repository.get_by_user(user_id)
        
        # Filtrar por tags
        matching_agents = []
        for agent in all_agents:
            if all(tag in agent.tags for tag in tags):
                matching_agents.append(agent)
        
        return matching_agents
```

📄 **Arquivo:** `src/api/agent_routes.py`

```python
@router.get("/search/by-tags", response_model=List[AgentResponse])
async def search_agents_by_tags(
    tags: str,  # Comma-separated tags
    user_id: int = Depends(get_current_user_id),
    agent_repository: AgentRepository = Depends(get_agent_repository)
):
    """
    Busca agentes por tags.
    
    Args:
        tags: Tags separadas por vírgula (ex: "python,ai,chatbot")
    """
    from src.application.use_cases.agents.search_by_tags import SearchAgentsByTagsUseCase
    
    tags_list = [tag.strip() for tag in tags.split(",")]
    use_case = SearchAgentsByTagsUseCase(agent_repository)
    agents_entities = use_case.execute(user_id, tags_list)
    
    # Converter para models
    agents = [agent_entity_to_model(entity) for entity in agents_entities]
    return agents
```

### **Passo 8: Testar**

```bash
# Criar agente com tags
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Python",
    "model": "qwen3:30b",
    "instruction": "Especialista em Python",
    "tags": ["python", "programming", "ai"]
  }'

# Buscar por tags
curl -X GET "http://localhost:8001/api/agents/search/by-tags?tags=python,ai" \
  -H "Authorization: Bearer TOKEN"
```

---

## 📊 Checklist: Adicionar Novo Recurso

Ao adicionar um novo recurso, siga esta ordem:

### **1. Domain Layer** (Core do negócio)
- [ ] Criar/atualizar Entity (`src/domain/entities/`)
- [ ] Definir Repository Interface (`src/domain/repositories/`)
- [ ] Criar Exceptions se necessário (`src/domain/exceptions/`)
- [ ] Criar Domain Services se necessário (`src/domain/services/`)

### **2. Infrastructure Layer** (Implementação)
- [ ] Atualizar Model SQLAlchemy (`src/models.py`)
- [ ] Criar Migration (`alembic revision`)
- [ ] Implementar Repository (`src/infrastructure/database/`)
- [ ] Atualizar Mapper (`src/infrastructure/database/entity_mapper.py`)

### **3. Application Layer** (Casos de uso)
- [ ] Criar Use Case (`src/application/use_cases/`)
- [ ] Implementar lógica de orquestração

### **4. API Layer** (Interface HTTP)
- [ ] Criar/atualizar Schemas (`src/api/schemas.py`)
- [ ] Criar/atualizar Routes (`src/api/*_routes.py`)
- [ ] Adicionar DI se necessário (`src/api/di.py`)
- [ ] Registrar router em `main.py`

### **5. Testes**
- [ ] Testar via curl/Postman
- [ ] Verificar no Swagger (`/docs`)
- [ ] Criar testes unitários

---

## 🎯 Boas Práticas

### **1. Separação de Responsabilidades**

✅ **Correto:**
```python
# Route apenas delega
@router.post("")
async def create_agent(data: AgentCreate, use_case: CreateAgentUseCase):
    return use_case.execute(...)

# Use Case orquestra
class CreateAgentUseCase:
    def execute(self, ...):
        # Validação
        # Criação da entidade
        # Persistência
        return agent
```

❌ **Errado:**
```python
# Route faz tudo (RUIM!)
@router.post("")
async def create_agent(data: AgentCreate, db: Session):
    # Validação aqui
    # SQL direto aqui
    # Lógica de negócio aqui
    return agent
```

### **2. Injeção de Dependências**

✅ **Use DI (Dependency Injection):**
```python
@router.get("/{id}")
async def get_agent(
    id: int,
    use_case: GetAgentUseCase = Depends(get_get_agent_use_case)
):
    return use_case.execute(id)
```

### **3. Exceções de Domínio**

✅ **Crie exceções específicas:**
```python
# src/domain/exceptions/agent_exceptions.py
class AgentNotFoundError(Exception):
    pass

class InvalidModelError(Exception):
    pass
```

### **4. Validação em Camadas**

- **API Layer:** Valida formato (Pydantic)
- **Domain Layer:** Valida regras de negócio
- **Infrastructure:** Valida constraints do BD

---

## 📚 Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| `src/api/main.py` | Configuração principal do FastAPI |
| `src/api/schemas.py` | Schemas Pydantic (request/response) |
| `src/api/dependencies.py` | Dependências (auth, DB, etc) |
| `src/api/di.py` | Injeção de dependências de use cases |
| `src/config.py` | Configurações da aplicação |
| `src/database.py` | Configuração do banco de dados |
| `src/models.py` | Models SQLAlchemy |
| `alembic/` | Migrations do banco |

---

## 🎓 Recursos Adicionais

- **Clean Architecture:** [The Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- **DDD:** [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- **FastAPI:** [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Pronto! Agora você entende a arquitetura e sabe como adicionar novos recursos!** 🚀

