"""Entity to model mapper.

This module provides utilities to convert between domain entities
and SQLAlchemy models for backward compatibility.
"""

from src.domain.entities.agent import Agent
from src.models import Agent as AgentModel


def agent_entity_to_model(entity: Agent) -> AgentModel:
    """
    Convert Agent domain entity to SQLAlchemy model.
    
    This is used for backward compatibility with code that expects
    SQLAlchemy models instead of domain entities.
    
    Args:
        entity: Agent domain entity
        
    Returns:
        SQLAlchemy Agent model
    """
    return AgentModel(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        agent_type=entity.agent_type,
        instruction=entity.instruction,
        model=entity.model,
        tools=entity.tools,
        use_file_search=entity.use_file_search,
        workflow_config=entity.workflow_config,
        custom_config=entity.custom_config,
        user_id=entity.user_id,
        is_active=entity.is_active,
        is_favorite=entity.is_favorite,
        icon=getattr(entity, 'icon', None),
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )

