"""Use case for getting all user agents."""

from typing import List
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent


class GetUserAgentsUseCase:
    """Use case for getting all agents for a user."""
    
    def __init__(self, agent_repository: AgentRepository):
        """Initialize use case with dependencies."""
        self.agent_repository = agent_repository
    
    def execute(self, user_id: int) -> List[Agent]:
        """
        Execute user agents retrieval.
        
        Args:
            user_id: User ID
            
        Returns:
            List of agent entities
        """
        return self.agent_repository.get_by_user(user_id)

