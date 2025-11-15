"""Use case for deleting an agent."""

from src.domain.repositories.agent_repository import AgentRepository
from src.domain.exceptions import AgentNotFoundError


class DeleteAgentUseCase:
    """Use case for deleting (soft delete) an agent."""
    
    def __init__(self, agent_repository: AgentRepository):
        """Initialize use case with dependencies."""
        self.agent_repository = agent_repository
    
    def execute(self, agent_id: int, user_id: int) -> bool:
        """
        Execute agent deletion.
        
        Args:
            agent_id: Agent ID
            user_id: User ID (for ownership check)
            
        Returns:
            True if deleted successfully
            
        Raises:
            AgentNotFoundError: If agent not found or not owned by user
        """
        success = self.agent_repository.delete(agent_id, user_id)
        if not success:
            raise AgentNotFoundError(agent_id)
        return True

