"""Dependency injection container.

This module provides dependency injection for repositories, services, and use cases,
allowing for easy testing and swapping of implementations.
"""

from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.domain.repositories.agent_repository import AgentRepository
from src.infrastructure.database.agent_repository_impl import SQLAlchemyAgentRepository
from src.domain.services.validation_service import ValidationService
from src.domain.services.tool_loader_service import ToolLoaderService
from src.core.llm_factory import LLMFactory
from src.application.use_cases.agents import (
    CreateAgentUseCase,
    GetAgentUseCase,
    GetUserAgentsUseCase,
    UpdateAgentUseCase,
    DeleteAgentUseCase,
    ChatWithAgentUseCase
)


def get_agent_repository(
    db: Session = Depends(get_db)
) -> AgentRepository:
    """
    Get agent repository instance.
    
    This function provides dependency injection for the AgentRepository.
    It returns a SQLAlchemy implementation by default, but can be easily
    swapped for a test implementation.
    
    Args:
        db: Database session
        
    Returns:
        AgentRepository instance
    """
    return SQLAlchemyAgentRepository(db)


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


def get_create_agent_use_case(
    agent_repo: AgentRepository = Depends(get_agent_repository),
    validator: ValidationService = Depends(get_validation_service)
) -> CreateAgentUseCase:
    """Get create agent use case instance."""
    return CreateAgentUseCase(agent_repo, validator)


def get_get_agent_use_case(
    agent_repo: AgentRepository = Depends(get_agent_repository)
) -> GetAgentUseCase:
    """Get get agent use case instance."""
    return GetAgentUseCase(agent_repo)


def get_get_user_agents_use_case(
    agent_repo: AgentRepository = Depends(get_agent_repository)
) -> GetUserAgentsUseCase:
    """Get get user agents use case instance."""
    return GetUserAgentsUseCase(agent_repo)


def get_update_agent_use_case(
    agent_repo: AgentRepository = Depends(get_agent_repository),
    validator: ValidationService = Depends(get_validation_service)
) -> UpdateAgentUseCase:
    """Get update agent use case instance."""
    return UpdateAgentUseCase(agent_repo, validator)


def get_delete_agent_use_case(
    agent_repo: AgentRepository = Depends(get_agent_repository)
) -> DeleteAgentUseCase:
    """Get delete agent use case instance."""
    return DeleteAgentUseCase(agent_repo)


def get_chat_with_agent_use_case(
    agent_repo: AgentRepository = Depends(get_agent_repository),
    validator: ValidationService = Depends(get_validation_service),
    tool_loader: ToolLoaderService = Depends(get_tool_loader_service),
    llm_factory: LLMFactory = Depends(get_llm_factory),
    db: Session = Depends(get_db)
) -> ChatWithAgentUseCase:
    """Get chat with agent use case instance."""
    return ChatWithAgentUseCase(
        agent_repo,
        validator,
        tool_loader,
        llm_factory,
        db
    )

