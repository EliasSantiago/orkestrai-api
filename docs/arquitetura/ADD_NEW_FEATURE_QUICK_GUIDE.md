# 🚀 Guia Rápido: Adicionar Novo Recurso

Passo a passo visual para adicionar um novo endpoint/recurso na aplicação.

## 📋 Ordem de Criação

```
1. Domain (Entidade + Interface) 
   ↓
2. Infrastructure (Implementação + Migration)
   ↓
3. Application (Use Case)
   ↓
4. API (Schema + Route)
   ↓
5. Teste
```

---

## 🎯 Exemplo Prático: Adicionar "Favoritos" aos Agentes

Vamos permitir que usuários marquem agentes como favoritos.

### **📍 Passo 1: Domain Layer**

#### **1.1 - Atualizar Entidade**

📄 `src/domain/entities/agent.py`

```python
@dataclass
class Agent:
    # ... campos existentes ...
    is_favorite: bool = False  # ✅ ADICIONAR
```

#### **1.2 - Atualizar Interface do Repository**

📄 `src/domain/repositories/agent_repository.py`

```python
class AgentRepository(ABC):
    # ... métodos existentes ...
    
    @abstractmethod
    def toggle_favorite(self, agent_id: int, user_id: int) -> Agent:
        """Toggle favorite status of an agent."""
        pass
```

---

### **📍 Passo 2: Infrastructure Layer**

#### **2.1 - Atualizar Model**

📄 `src/models.py`

```python
class Agent(Base):
    __tablename__ = "agents"
    
    # ... campos existentes ...
    is_favorite = Column(Boolean, default=False)  # ✅ ADICIONAR
```

#### **2.2 - Criar Migration**

```bash
# Terminal
cd /home/vdilinux/aplicações/api-adk-google-main
source .venv/bin/activate

# Criar migration
alembic revision --autogenerate -m "add_is_favorite_to_agents"

# Aplicar migration
alembic upgrade head
```

#### **2.3 - Implementar no Repository**

📄 `src/infrastructure/database/agent_repository_impl.py`

```python
class AgentRepositoryImpl(AgentRepository):
    # ... métodos existentes ...
    
    def toggle_favorite(self, agent_id: int, user_id: int) -> Agent:
        """Toggle favorite status of an agent."""
        from src.infrastructure.database.entity_mapper import model_to_entity
        from src.models import Agent as AgentModel
        
        # Buscar agente
        db_agent = self.db.query(AgentModel).filter(
            AgentModel.id == agent_id,
            AgentModel.user_id == user_id
        ).first()
        
        if not db_agent:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        
        # Toggle
        db_agent.is_favorite = not db_agent.is_favorite
        
        # Salvar
        self.db.commit()
        self.db.refresh(db_agent)
        
        # Converter para entidade
        return model_to_entity(db_agent)
```

---

### **📍 Passo 3: Application Layer**

#### **3.1 - Criar Use Case**

📄 `src/application/use_cases/agents/toggle_favorite.py` (criar arquivo)

```python
"""Use case para marcar/desmarcar agente como favorito."""

from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.domain.exceptions.agent_exceptions import AgentNotFoundError


class ToggleFavoriteUseCase:
    """Use case para toggle favorite status."""
    
    def __init__(self, agent_repository: AgentRepository):
        """Initialize with repository."""
        self.agent_repository = agent_repository
    
    def execute(self, agent_id: int, user_id: int) -> Agent:
        """
        Toggle favorite status of an agent.
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            Agent atualizado
            
        Raises:
            AgentNotFoundError: Se agente não existir
        """
        return self.agent_repository.toggle_favorite(agent_id, user_id)
```

---

### **📍 Passo 4: API Layer**

#### **4.1 - Atualizar Schema**

📄 `src/api/schemas.py`

```python
# AgentResponse já deve ter todos os campos,
# mas certifique-se de adicionar:
class AgentResponse(BaseModel):
    # ... campos existentes ...
    is_favorite: bool  # ✅ ADICIONAR
    # ... resto ...
```

#### **4.2 - Adicionar DI**

📄 `src/api/di.py`

```python
# Adicionar no final do arquivo
def get_toggle_favorite_use_case(
    agent_repository: AgentRepository = Depends(get_agent_repository)
) -> ToggleFavoriteUseCase:
    """Get ToggleFavoriteUseCase with dependencies."""
    from src.application.use_cases.agents.toggle_favorite import ToggleFavoriteUseCase
    return ToggleFavoriteUseCase(agent_repository)
```

#### **4.3 - Adicionar Rota**

📄 `src/api/agent_routes.py`

```python
# Adicionar import no topo
from src.application.use_cases.agents.toggle_favorite import ToggleFavoriteUseCase
from src.api.di import get_toggle_favorite_use_case

# Adicionar rota no final (antes do último router)
@router.post("/{agent_id}/favorite", response_model=AgentResponse)
async def toggle_favorite(
    agent_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: ToggleFavoriteUseCase = Depends(get_toggle_favorite_use_case)
):
    """
    Toggle favorite status of an agent.
    
    - **agent_id**: ID do agente
    """
    try:
        agent_entity = use_case.execute(agent_id, user_id)
        agent = agent_entity_to_model(agent_entity)
        return agent
    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling favorite: {str(e)}"
        )
```

---

### **📍 Passo 5: Testar**

#### **5.1 - Reiniciar Servidor**

```bash
# Parar servidor (Ctrl+C)
# Reiniciar
./scripts/start_backend.sh
```

#### **5.2 - Testar via cURL**

```bash
# Marcar como favorito
curl -X POST http://localhost:8001/api/agents/1/favorite \
  -H "Authorization: Bearer SEU_TOKEN"

# Verificar (buscar agente)
curl -X GET http://localhost:8001/api/agents/1 \
  -H "Authorization: Bearer SEU_TOKEN"
```

**Resposta esperada:**
```json
{
  "id": 1,
  "name": "Meu Agente",
  "is_favorite": true,  // ✅ TRUE!
  ...
}
```

#### **5.3 - Testar no Swagger**

1. Acesse: `http://localhost:8001/docs`
2. Autorize com seu token
3. Vá em `POST /api/agents/{agent_id}/favorite`
4. Clique em "Try it out"
5. Execute

---

## 📊 Resumo Visual

```
┌─────────────────────────────────────────┐
│ 1. DOMAIN                               │
│    ├─ entities/agent.py (+ is_favorite) │
│    └─ repositories/ (+ toggle_favorite) │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 2. INFRASTRUCTURE                       │
│    ├─ models.py (+ is_favorite column)  │
│    ├─ alembic migration                 │
│    └─ repository_impl (+ método)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 3. APPLICATION                          │
│    └─ use_cases/toggle_favorite.py      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 4. API                                  │
│    ├─ schemas.py (atualizar)            │
│    ├─ di.py (+ factory)                 │
│    └─ agent_routes.py (+ rota)          │
└─────────────────────────────────────────┘
```

---

## ✅ Checklist Completo

### **Domain:**
- [ ] Atualizar Entity com novo campo
- [ ] Adicionar método na interface do Repository

### **Infrastructure:**
- [ ] Atualizar Model SQLAlchemy
- [ ] Criar migration (`alembic revision`)
- [ ] Aplicar migration (`alembic upgrade head`)
- [ ] Implementar método no Repository

### **Application:**
- [ ] Criar arquivo de Use Case
- [ ] Implementar lógica do Use Case

### **API:**
- [ ] Atualizar Schema (se necessário)
- [ ] Adicionar factory DI em `di.py`
- [ ] Criar rota em `*_routes.py`
- [ ] Adicionar imports necessários

### **Teste:**
- [ ] Reiniciar servidor
- [ ] Testar via cURL
- [ ] Testar no Swagger (`/docs`)
- [ ] Verificar banco de dados

---

## 🎯 Dicas Importantes

### **1. Sempre siga a ordem:**
```
Domain → Infrastructure → Application → API
```

### **2. Migrations:**
```bash
# Sempre depois de mudar models.py:
alembic revision --autogenerate -m "descrição"
alembic upgrade head
```

### **3. Reiniciar servidor:**
Após mudanças de código, **sempre reinicie** o servidor!

### **4. Testar no Swagger:**
Melhor forma de testar: `http://localhost:8001/docs`

### **5. Exceptions:**
Sempre use exceções de domínio específicas:
```python
from src.domain.exceptions.agent_exceptions import AgentNotFoundError
```

---

## 📚 Templates Prontos

### **Use Case Template:**

```python
"""Use case para [AÇÃO]."""

from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent


class [Nome]UseCase:
    """Use case para [descrição]."""
    
    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository
    
    def execute(self, ...) -> Agent:
        """
        [Descrição da ação]
        
        Args:
            ...
            
        Returns:
            ...
        """
        # Implementação
        pass
```

### **Rota Template:**

```python
@router.[get/post/put/delete]("/caminho", response_model=Schema)
async def nome_funcao(
    # Parâmetros
    user_id: int = Depends(get_current_user_id),
    use_case: UseCase = Depends(get_use_case)
):
    """
    Descrição da rota.
    
    - **param**: Descrição
    """
    try:
        result = use_case.execute(...)
        return result
    except SpecificError as e:
        raise HTTPException(
            status_code=status.HTTP_XXX,
            detail=str(e)
        )
```

---

## 🆘 Problemas Comuns

### **Erro: "Table already has a column named X"**
```bash
# Solução: Criar nova migration
alembic revision -m "fix_column"
# Editar arquivo gerado manualmente
alembic upgrade head
```

### **Erro: "Module not found"**
```python
# Solução: Verificar imports
# Use caminhos absolutos: from src.domain...
```

### **Erro: 404 Not Found**
```python
# Solução: Verificar se router está registrado
# em src/api/main.py
app.include_router(seu_router)
```

---

**Pronto! Agora você pode adicionar qualquer recurso seguindo este guia!** 🚀

