# 💻 Exemplos Práticos de Refatoração

Este documento contém exemplos práticos de como o código seria refatorado seguindo a nova arquitetura proposta.

---

## 1. Dependências Compartilhadas

### ❌ Antes: Duplicação em 8 arquivos

**agent_routes.py**:
```python
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(...)
        return user_id
    except Exception:
        raise HTTPException(...)
```

**agent_chat_routes.py**:
```python
# MESMA FUNÇÃO DUPLICADA
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(...)
        return user_id
    except Exception:
        raise HTTPException(...)
```

### ✅ Depois: Função única compartilhada

**src/api/dependencies.py**:
```python
"""Shared dependencies for FastAPI routes."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from src.infrastructure.config.settings import Settings, get_settings

security = HTTPBearer()

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings)
) -> int:
    """
    Get current user ID from JWT token.
    
    This is a shared dependency used across all protected routes.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

**Uso em todas as rotas**:
```python
from src.api.dependencies import get_current_user_id

@router.post("/chat")
async def chat_with_agent(
    user_id: int = Depends(get_current_user_id),
    ...
):
    ...
```

---

## 2. Repository Pattern

### ❌ Antes: Acesso direto ao banco

**agent_routes.py**:
```python
@router.get("/{agent_id}")
async def get_agent(
    agent_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == user_id,
        Agent.is_active == True
    ).first()
    if not agent:
        raise HTTPException(...)
    return agent
```

**agent_chat_routes.py**:
```python
# MESMO CÓDIGO DUPLICADO
agent_model = db.query(Agent).filter(
    Agent.id == agent_id,
    Agent.user_id == user_id,
    Agent.is_active == True
).first()
```

### ✅ Depois: Repository Pattern

**src/domain/repositories/agent_repository.py** (Interface):
```python
"""Agent repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.agent import Agent

class AgentRepository(ABC):
    """Abstract repository for Agent entities."""
    
    @abstractmethod
    def create(self, agent: Agent) -> Agent:
        """Create a new agent."""
        pass
    
    @abstractmethod
    def get_by_id(self, agent_id: int, user_id: int) -> Optional[Agent]:
        """Get agent by ID (only if owned by user)."""
        pass
    
    @abstractmethod
    def get_by_user(self, user_id: int) -> List[Agent]:
        """Get all active agents for a user."""
        pass
    
    @abstractmethod
    def update(self, agent: Agent) -> Agent:
        """Update an agent."""
        pass
    
    @abstractmethod
    def delete(self, agent_id: int, user_id: int) -> bool:
        """Soft delete an agent."""
        pass
```

**src/infrastructure/database/agent_repository_impl.py** (Implementação):
```python
"""SQLAlchemy implementation of AgentRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.infrastructure.persistence.models import AgentModel

class SQLAlchemyAgentRepository(AgentRepository):
    """SQLAlchemy implementation of AgentRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, agent: Agent) -> Agent:
        """Create a new agent."""
        agent_model = AgentModel.from_entity(agent)
        self.db.add(agent_model)
        self.db.commit()
        self.db.refresh(agent_model)
        return agent_model.to_entity()
    
    def get_by_id(self, agent_id: int, user_id: int) -> Optional[Agent]:
        """Get agent by ID (only if owned by user)."""
        agent_model = self.db.query(AgentModel).filter(
            AgentModel.id == agent_id,
            AgentModel.user_id == user_id,
            AgentModel.is_active == True
        ).first()
        return agent_model.to_entity() if agent_model else None
    
    def get_by_user(self, user_id: int) -> List[Agent]:
        """Get all active agents for a user."""
        agent_models = self.db.query(AgentModel).filter(
            AgentModel.user_id == user_id,
            AgentModel.is_active == True
        ).order_by(AgentModel.created_at.desc()).all()
        return [model.to_entity() for model in agent_models]
    
    def update(self, agent: Agent) -> Agent:
        """Update an agent."""
        agent_model = self.db.query(AgentModel).filter(
            AgentModel.id == agent.id,
            AgentModel.user_id == agent.user_id
        ).first()
        if not agent_model:
            return None
        
        agent_model.update_from_entity(agent)
        self.db.commit()
        self.db.refresh(agent_model)
        return agent_model.to_entity()
    
    def delete(self, agent_id: int, user_id: int) -> bool:
        """Soft delete an agent."""
        agent_model = self.db.query(AgentModel).filter(
            AgentModel.id == agent_id,
            AgentModel.user_id == user_id,
            AgentModel.is_active == True
        ).first()
        if not agent_model:
            return False
        
        agent_model.is_active = False
        self.db.commit()
        return True
```

**Uso no controller**:
```python
from src.domain.repositories.agent_repository import AgentRepository
from src.api.di import get_agent_repository

@router.get("/{agent_id}")
async def get_agent(
    agent_id: int,
    user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository)
):
    agent = agent_repo.get_by_id(agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return AgentResponse.from_entity(agent)
```

---

## 3. Use Cases (Casos de Uso)

### ❌ Antes: Lógica complexa no controller (429 linhas)

**agent_chat_routes.py**:
```python
@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # 50+ linhas de validação
    if use_file_search and model != "gemini-2.5-flash":
        raise HTTPException(...)
    
    # 30+ linhas de carregamento de agent
    agent_model = AgentService.get_agent_by_id(db, request.agent_id, user_id)
    if not agent_model:
        raise HTTPException(...)
    
    # 50+ linhas de carregamento de tools
    tool_map = {...}
    for connection in mcp_connections:
        # lógica complexa...
    
    # 100+ linhas de execução de chat
    # retry logic
    # error handling
    # ...
    
    return ChatResponse(...)
```

### ✅ Depois: Use Case separado

**src/application/use_cases/agents/chat_with_agent.py**:
```python
"""Use case for chatting with an agent."""

from typing import Optional
from src.domain.entities.agent import Agent
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.repositories.conversation_repository import ConversationRepository
from src.infrastructure.llm.factory import LLMFactory
from src.domain.services.validation_service import ValidationService
from src.domain.services.tool_loader_service import ToolLoaderService
from src.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    UnsupportedModelError
)

class ChatWithAgentUseCase:
    """Use case for chatting with an agent."""
    
    def __init__(
        self,
        agent_repo: AgentRepository,
        conversation_repo: ConversationRepository,
        llm_factory: LLMFactory,
        validator: ValidationService,
        tool_loader: ToolLoaderService
    ):
        self.agent_repo = agent_repo
        self.conversation_repo = conversation_repo
        self.llm_factory = llm_factory
        self.validator = validator
        self.tool_loader = tool_loader
    
    async def execute(
        self,
        user_id: int,
        agent_id: int,
        message: str,
        session_id: Optional[str] = None,
        model_override: Optional[str] = None
    ) -> str:
        """
        Execute chat with agent.
        
        Args:
            user_id: User ID
            agent_id: Agent ID
            message: User message
            session_id: Optional session ID for conversation continuity
            model_override: Optional model override
            
        Returns:
            Assistant response
            
        Raises:
            AgentNotFoundError: If agent not found
            UnsupportedModelError: If model not supported
        """
        # 1. Get agent
        agent = self.agent_repo.get_by_id(agent_id, user_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        
        # 2. Determine model
        model = model_override or agent.model
        
        # 3. Validate model and file search compatibility
        self.validator.validate_model(model)
        self.validator.validate_file_search_model(model, agent.use_file_search)
        
        # 4. Get conversation history
        history = self.conversation_repo.get_history(
            user_id=user_id,
            session_id=session_id
        )
        
        # 5. Load tools
        tools = self.tool_loader.load_tools_for_agent(
            agent=agent,
            user_id=user_id
        )
        
        # 6. Get LLM provider
        provider = self.llm_factory.get_provider(model)
        if not provider:
            raise UnsupportedModelError(model)
        
        # 7. Save user message
        self.conversation_repo.add_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=message
        )
        
        # 8. Execute chat with retry logic
        response = await self._execute_with_retry(
            provider=provider,
            model=model,
            messages=history + [message],
            tools=tools,
            agent=agent
        )
        
        # 9. Save assistant response
        self.conversation_repo.add_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=response
        )
        
        return response
    
    async def _execute_with_retry(
        self,
        provider,
        model: str,
        messages: List,
        tools: List,
        agent: Agent,
        max_retries: int = 3
    ) -> str:
        """Execute chat with retry logic."""
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response_chunks = []
                async for chunk in provider.chat(
                    messages=messages,
                    model=model,
                    tools=tools,
                    **self._get_provider_kwargs(agent)
                ):
                    response_chunks.append(chunk)
                
                return ''.join(response_chunks)
                
            except Exception as e:
                if self._should_retry(e, attempt, max_retries):
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise
        
        raise Exception("Max retries exceeded")
    
    def _get_provider_kwargs(self, agent: Agent) -> dict:
        """Get provider-specific kwargs."""
        kwargs = {
            "user_id": str(agent.user_id),
            "session_id": agent.session_id,
            "app_name": "agent_chat_app"
        }
        
        if agent.model.startswith("gemini-"):
            kwargs.update({
                "agent_name": agent.sanitized_name,
                "agent_description": agent.description or "",
                "instruction": agent.instruction,
                "inject_context": True,
                "file_search_stores": agent.file_search_stores if agent.use_file_search else None
            })
        
        return kwargs
    
    def _should_retry(self, error: Exception, attempt: int, max_retries: int) -> bool:
        """Determine if error should be retried."""
        error_message = str(error).upper()
        is_429 = "429" in error_message or "RESOURCE_EXHAUSTED" in error_message
        is_connection_error = "CONNECTION" in error_message or "TIMEOUT" in error_message
        
        return is_429 and attempt < max_retries - 1 and not is_connection_error
```

**Controller simplificado**:
```python
"""Chat routes for agents."""

from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user_id
from src.api.schemas.agent_schemas import ChatRequest, ChatResponse
from src.application.use_cases.agents.chat_with_agent import ChatWithAgentUseCase
from src.api.di import get_chat_use_case

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: ChatWithAgentUseCase = Depends(get_chat_use_case)
):
    """Chat with an agent."""
    response = await use_case.execute(
        user_id=user_id,
        agent_id=request.agent_id,
        message=request.message,
        session_id=request.session_id,
        model_override=request.model
    )
    return ChatResponse(
        response=response,
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        session_id=request.session_id,
        model_used=request.model
    )
```

**Redução**: 429 linhas → 20 linhas no controller + 150 linhas no use case (organizado)

---

## 4. Validações Centralizadas

### ❌ Antes: Validações espalhadas

**agent_routes.py**:
```python
@router.post("")
async def create_agent(...):
    # Validação inline
    if use_file_search and model != "gemini-2.5-flash":
        raise HTTPException(...)
    ...
```

**agent_chat_routes.py**:
```python
@router.post("/chat")
async def chat_with_agent(...):
    # MESMA validação duplicada
    if use_file_search and model != "gemini-2.5-flash":
        raise HTTPException(...)
    ...
```

### ✅ Depois: Serviço de Validação

**src/domain/services/validation_service.py**:
```python
"""Centralized validation service."""

from src.domain.exceptions.agent_exceptions import (
    InvalidModelError,
    FileSearchModelMismatchError
)
from src.infrastructure.llm.factory import LLMFactory

class ValidationService:
    """Service for validating business rules."""
    
    def __init__(self, llm_factory: LLMFactory):
        self.llm_factory = llm_factory
    
    def validate_model(self, model: str) -> None:
        """
        Validate that model is supported.
        
        Raises:
            InvalidModelError: If model is not supported
        """
        if not self.llm_factory.is_model_supported(model):
            available_models = self.llm_factory.get_all_supported_models()
            raise InvalidModelError(
                model=model,
                available_models=available_models
            )
    
    def validate_file_search_model(
        self, 
        model: str, 
        use_file_search: bool
    ) -> None:
        """
        Validate file search model compatibility.
        
        File Search (RAG) only works with gemini-2.5-flash.
        
        Raises:
            FileSearchModelMismatchError: If model is incompatible with file search
        """
        if use_file_search and model != "gemini-2.5-flash":
            raise FileSearchModelMismatchError(
                model=model,
                required_model="gemini-2.5-flash"
            )
```

**Uso no use case**:
```python
# No ChatWithAgentUseCase
self.validator.validate_model(model)
self.validator.validate_file_search_model(model, agent.use_file_search)
```

---

## 5. Exceções de Domínio

### ❌ Antes: HTTPException genérico

```python
if not agent:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Agent not found"
    )
```

### ✅ Depois: Exceções de domínio

**src/domain/exceptions/agent_exceptions.py**:
```python
"""Domain exceptions for agents."""

class AgentException(Exception):
    """Base exception for agent-related errors."""
    pass

class AgentNotFoundError(AgentException):
    """Raised when agent is not found."""
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        super().__init__(f"Agent with ID {agent_id} not found")

class InvalidModelError(AgentException):
    """Raised when model is not supported."""
    def __init__(self, model: str, available_models: dict):
        self.model = model
        self.available_models = available_models
        super().__init__(
            f"Model '{model}' is not supported. "
            f"Available models: {available_models}"
        )

class FileSearchModelMismatchError(AgentException):
    """Raised when model is incompatible with file search."""
    def __init__(self, model: str, required_model: str):
        self.model = model
        self.required_model = required_model
        super().__init__(
            f"File Search (RAG) is only supported with model '{required_model}'. "
            f"Current model: '{model}'"
        )
```

**Error handler global**:
```python
"""Global error handler middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    InvalidModelError,
    FileSearchModelMismatchError
)

async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions globally."""
    
    # Domain exceptions
    if isinstance(exc, AgentNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc), "agent_id": exc.agent_id}
        )
    
    if isinstance(exc, InvalidModelError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "model": exc.model,
                "available_models": exc.available_models
            }
        )
    
    if isinstance(exc, FileSearchModelMismatchError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "model": exc.model,
                "required_model": exc.required_model
            }
        )
    
    # Generic error (log but don't expose details)
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

---

## 6. Dependency Injection

### ❌ Antes: Dependências hardcoded

```python
@router.post("/chat")
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Dependências hardcoded
    agent_service = AgentService()
    conversation_service = HybridConversationService()
    llm_factory = LLMFactory()
    # ...
```

### ✅ Depois: Dependency Injection

**src/api/di.py**:
```python
"""Dependency injection container."""

from functools import lru_cache
from sqlalchemy.orm import Session
from fastapi import Depends
from src.infrastructure.persistence.database import get_db
from src.infrastructure.database.agent_repository_impl import SQLAlchemyAgentRepository
from src.infrastructure.database.conversation_repository_impl import SQLAlchemyConversationRepository
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.repositories.conversation_repository import ConversationRepository
from src.infrastructure.llm.factory import LLMFactory
from src.domain.services.validation_service import ValidationService
from src.domain.services.tool_loader_service import ToolLoaderService
from src.application.use_cases.agents.chat_with_agent import ChatWithAgentUseCase

def get_agent_repository(
    db: Session = Depends(get_db)
) -> AgentRepository:
    """Get agent repository instance."""
    return SQLAlchemyAgentRepository(db)

def get_conversation_repository(
    db: Session = Depends(get_db)
) -> ConversationRepository:
    """Get conversation repository instance."""
    return SQLAlchemyConversationRepository(db)

@lru_cache()
def get_llm_factory() -> LLMFactory:
    """Get LLM factory instance (singleton)."""
    return LLMFactory()

def get_validation_service(
    llm_factory: LLMFactory = Depends(get_llm_factory)
) -> ValidationService:
    """Get validation service instance."""
    return ValidationService(llm_factory)

def get_tool_loader_service(
    db: Session = Depends(get_db)
) -> ToolLoaderService:
    """Get tool loader service instance."""
    return ToolLoaderService(db)

def get_chat_use_case(
    agent_repo: AgentRepository = Depends(get_agent_repository),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
    llm_factory: LLMFactory = Depends(get_llm_factory),
    validator: ValidationService = Depends(get_validation_service),
    tool_loader: ToolLoaderService = Depends(get_tool_loader_service)
) -> ChatWithAgentUseCase:
    """Get chat use case instance."""
    return ChatWithAgentUseCase(
        agent_repo=agent_repo,
        conversation_repo=conversation_repo,
        llm_factory=llm_factory,
        validator=validator,
        tool_loader=tool_loader
    )
```

**Uso no controller**:
```python
from src.api.di import get_chat_use_case

@router.post("/chat")
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: ChatWithAgentUseCase = Depends(get_chat_use_case)
):
    response = await use_case.execute(...)
    return ChatResponse(...)
```

---

## 7. Testabilidade

### ❌ Antes: Impossível testar sem infraestrutura

```python
# Precisa de DB, Redis, API keys...
def test_chat_with_agent():
    # Não pode mockar nada
    pass
```

### ✅ Depois: Fácil de testar com mocks

**tests/unit/use_cases/test_chat_with_agent.py**:
```python
"""Unit tests for ChatWithAgentUseCase."""

import pytest
from unittest.mock import Mock, AsyncMock
from src.application.use_cases.agents.chat_with_agent import ChatWithAgentUseCase
from src.domain.exceptions.agent_exceptions import AgentNotFoundError

@pytest.fixture
def mock_agent_repo():
    """Mock agent repository."""
    return Mock()

@pytest.fixture
def mock_conversation_repo():
    """Mock conversation repository."""
    return Mock()

@pytest.fixture
def mock_llm_factory():
    """Mock LLM factory."""
    return Mock()

@pytest.fixture
def mock_validator():
    """Mock validation service."""
    return Mock()

@pytest.fixture
def mock_tool_loader():
    """Mock tool loader service."""
    return Mock()

@pytest.fixture
def use_case(
    mock_agent_repo,
    mock_conversation_repo,
    mock_llm_factory,
    mock_validator,
    mock_tool_loader
):
    """Create use case with mocked dependencies."""
    return ChatWithAgentUseCase(
        agent_repo=mock_agent_repo,
        conversation_repo=mock_conversation_repo,
        llm_factory=mock_llm_factory,
        validator=mock_validator,
        tool_loader=mock_tool_loader
    )

@pytest.mark.asyncio
async def test_chat_with_agent_success(use_case, mock_agent_repo, mock_llm_factory):
    """Test successful chat with agent."""
    # Arrange
    agent = Mock(id=1, model="gemini-2.0-flash-exp", tools=[])
    mock_agent_repo.get_by_id.return_value = agent
    
    provider = AsyncMock()
    provider.chat = AsyncMock(return_value=iter(["Hello", " World"]))
    mock_llm_factory.get_provider.return_value = provider
    
    # Act
    response = await use_case.execute(
        user_id=1,
        agent_id=1,
        message="Hello"
    )
    
    # Assert
    assert response == "Hello World"
    mock_agent_repo.get_by_id.assert_called_once_with(1, 1)
    mock_llm_factory.get_provider.assert_called_once_with("gemini-2.0-flash-exp")

@pytest.mark.asyncio
async def test_chat_with_agent_not_found(use_case, mock_agent_repo):
    """Test chat with non-existent agent."""
    # Arrange
    mock_agent_repo.get_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(AgentNotFoundError):
        await use_case.execute(
            user_id=1,
            agent_id=999,
            message="Hello"
        )
```

---

## 📊 Resumo das Melhorias

| Aspecto | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| **Duplicação** | 8 cópias de `get_current_user_id` | 1 função compartilhada | ✅ 87.5% redução |
| **Linhas no controller** | 429 linhas | 20 linhas | ✅ 95% redução |
| **Acoplamento** | Alto (direto ao DB) | Baixo (interfaces) | ✅ Desacoplado |
| **Testabilidade** | Impossível sem infra | Fácil com mocks | ✅ 100% testável |
| **Responsabilidades** | Múltiplas por classe | Uma por classe | ✅ SRP aplicado |
| **Manutenibilidade** | Difícil | Fácil | ✅ Organizado |

---

**Próximo passo**: Implementar essas refatorações fase por fase, começando pelas dependências compartilhadas e repositórios.

