"""Agent API routes."""

from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.agent_service import AgentService
from src.api.schemas import AgentCreate, AgentUpdate, AgentResponse
from src.api.dependencies import get_current_user_id
from src.api.di import (
    get_create_agent_use_case,
    get_get_agent_use_case,
    get_get_user_agents_use_case,
    get_update_agent_use_case,
    get_delete_agent_use_case
)
from src.application.use_cases.agents import (
    CreateAgentUseCase,
    GetAgentUseCase,
    GetUserAgentsUseCase,
    UpdateAgentUseCase,
    DeleteAgentUseCase
)
from src.domain.exceptions import FileSearchModelMismatchError, AgentNotFoundError
from src.infrastructure.database.entity_mapper import agent_entity_to_model

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/types", response_model=dict)
async def get_agent_types():
    """Get available agent types with descriptions.
    
    Returns information about all available agent types that can be created.
    Based on Google ADK documentation.
    """
    return {
        "types": [
            {
                "id": "llm",
                "name": "LLM Agent",
                "description": "Utiliza Large Language Models (LLMs) como motor principal para entender linguagem natural, raciocinar, planejar e gerar respostas. Ideal para tarefas flexíveis centradas em linguagem.",
                "icon": "sparkles",
                "features": ["reasoning", "generation", "tool_use"],
                "requires": ["instruction", "model"]
            },
            {
                "id": "sequential",
                "name": "Sequential Workflow",
                "description": "Controla a execução de agentes em sequência predefinida. Perfeito para processos estruturados que precisam de execução previsível passo a passo.",
                "icon": "arrow-right",
                "features": ["deterministic", "structured", "orchestration"],
                "requires": ["workflow_config.agents"]
            },
            {
                "id": "loop",
                "name": "Loop Workflow",
                "description": "Executa um agente repetidamente até que uma condição seja satisfeita ou um limite de iterações seja atingido. Útil para processos iterativos de refinamento.",
                "icon": "arrow-path",
                "features": ["iterative", "conditional", "refinement"],
                "requires": ["workflow_config.agent"]
            },
            {
                "id": "parallel",
                "name": "Parallel Workflow",
                "description": "Executa múltiplos agentes simultaneamente e combina seus resultados. Mais rápido que execução sequencial, ideal para análises multi-perspectiva.",
                "icon": "squares",
                "features": ["concurrent", "fast", "multi_perspective"],
                "requires": ["workflow_config.agents"]
            },
            {
                "id": "custom",
                "name": "Custom Agent",
                "description": "Permite implementar lógica única com código personalizado. Flexibilidade total para integrações específicas e fluxos de controle customizados.",
                "icon": "code",
                "features": ["flexible", "custom_logic", "specialized"],
                "requires": ["custom_config"]
            }
        ]
    }


def sync_agents_to_files_sync():
    """Sync agents from database to files (synchronous, runs in background)."""
    try:
        from src.adk_loader import sync_agents_from_db
        sync_agents_from_db()
    except Exception as e:
        # Don't fail the API request if sync fails
        # This is a background operation
        import traceback
        print(f"⚠ Warning: Could not sync agents to files: {e}")
        print(traceback.format_exc())


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    use_case: CreateAgentUseCase = Depends(get_create_agent_use_case)
):
    """Create a new agent for the current user.
    
    Supports multiple agent types:
    - llm: LLM agent with tools (default)
    - sequential: Workflow agent that executes agents in sequence
    - loop: Workflow agent that loops until condition is met
    - parallel: Workflow agent that executes agents in parallel
    - custom: Custom agent with user-defined logic
    """
    try:
        # Use case handles validation and creation
        agent_entity = use_case.execute(
            user_id=user_id,
            name=agent_data.name,
            description=agent_data.description,
            agent_type=agent_data.agent_type or "llm",
            instruction=agent_data.instruction,
            model=agent_data.model,
            tools=agent_data.tools,
            use_file_search=agent_data.use_file_search if agent_data.use_file_search is not None else False,
            workflow_config=agent_data.workflow_config,
            custom_config=agent_data.custom_config,
            is_favorite=agent_data.is_favorite if agent_data.is_favorite is not None else False,
            icon=agent_data.icon
        )
        
        # Convert to model for backward compatibility with schemas
        agent = agent_entity_to_model(agent_entity)
        
        # Sync agents to files after creation (non-blocking background task)
        background_tasks.add_task(sync_agents_to_files_sync)
        
        return agent
    except (FileSearchModelMismatchError, AgentNotFoundError):
        raise
    except Exception as e:
        import traceback
        print(f"✗ Error creating agent: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent: {str(e)}"
        )


@router.get("", response_model=List[AgentResponse])
async def get_agents(
    limit: int = 20,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    use_case: GetUserAgentsUseCase = Depends(get_get_user_agents_use_case)
):
    """Get agents for the current user with pagination.
    
    Args:
        limit: Maximum number of agents to return (default: 20, max: 100)
        offset: Number of agents to skip (default: 0)
        user_id: Current user ID (from auth)
    
    Returns:
        List of agents, ordered by is_favorite (favorites first), then by created_at (newest first)
    """
    # Validate limit
    if limit < 1:
        limit = 20
    if limit > 100:
        limit = 100
    
    agent_entities = use_case.execute(user_id)
    
    # Sort: favorites first, then by created_at (newest first)
    sorted_entities = sorted(
        agent_entities,
        key=lambda a: (not a.is_favorite, -(a.created_at.timestamp() if a.created_at else 0)),
        reverse=False
    )
    
    # Apply pagination
    paginated_entities = sorted_entities[offset:offset + limit]
    
    # Convert entities to models for backward compatibility
    agents = [agent_entity_to_model(entity) for entity in paginated_entities]
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: GetAgentUseCase = Depends(get_get_agent_use_case)
):
    """Get a specific agent by ID."""
    agent_entity = use_case.execute(agent_id, user_id)
    # Convert entity to model for backward compatibility
    agent = agent_entity_to_model(agent_entity)
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    use_case: UpdateAgentUseCase = Depends(get_update_agent_use_case)
):
    """Update an agent.
    
    Supports updating all agent types (llm, sequential, loop, parallel, custom).
    Only provided fields will be updated.
    """
    # Use case handles validation and update
    updated_entity = use_case.execute(
        agent_id=agent_id,
        user_id=user_id,
        name=agent_data.name,
        description=agent_data.description,
        agent_type=agent_data.agent_type,
        instruction=agent_data.instruction,
        model=agent_data.model,
        tools=agent_data.tools,
        use_file_search=agent_data.use_file_search,
        workflow_config=agent_data.workflow_config,
        custom_config=agent_data.custom_config,
        is_favorite=agent_data.is_favorite,
        icon=agent_data.icon
    )
    
    # Convert entity to model for backward compatibility
    agent = agent_entity_to_model(updated_entity)
    
    # Sync agents to files after update (non-blocking background task)
    background_tasks.add_task(sync_agents_to_files_sync)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    use_case: DeleteAgentUseCase = Depends(get_delete_agent_use_case)
):
    """Delete an agent."""
    use_case.execute(agent_id, user_id)
    # Sync agents to files after deletion (non-blocking background task)
    background_tasks.add_task(sync_agents_to_files_sync)

