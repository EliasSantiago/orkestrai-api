"""Use case for getting an agent."""

from typing import Optional
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.domain.exceptions import AgentNotFoundError


class GetAgentUseCase:
    """Use case for getting an agent by ID."""
    
    def __init__(self, agent_repository: AgentRepository):
        """Initialize use case with dependencies."""
        self.agent_repository = agent_repository
    
    def execute(self, agent_id: int, user_id: int) -> Agent:
        """
        Execute agent retrieval.
        
        Args:
            agent_id: Agent ID
            user_id: User ID (for ownership check)
            
        Returns:
            Agent entity
            
        Raises:
            AgentNotFoundError: If agent not found or not owned by user
        """
        agent = self.agent_repository.get_by_id(agent_id, user_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        return agent

