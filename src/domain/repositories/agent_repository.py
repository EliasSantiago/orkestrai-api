"""Agent repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.agent import Agent


class AgentRepository(ABC):
    """Abstract repository for Agent entities."""
    
    @abstractmethod
    def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent: Agent entity to create
            
        Returns:
            Created agent entity with ID
        """
        pass
    
    @abstractmethod
    def get_by_id(self, agent_id: int, user_id: int) -> Optional[Agent]:
        """
        Get agent by ID (only if owned by user).
        
        Args:
            agent_id: Agent ID
            user_id: User ID (for ownership check)
            
        Returns:
            Agent entity if found and owned by user, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_user(self, user_id: int) -> List[Agent]:
        """
        Get all active agents for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active agent entities
        """
        pass
    
    @abstractmethod
    def update(self, agent: Agent) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent: Agent entity with updated data
            
        Returns:
            Updated agent entity, None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, agent_id: int, user_id: int) -> bool:
        """
        Soft delete an agent (only if owned by user).
        
        Args:
            agent_id: Agent ID
            user_id: User ID (for ownership check)
            
        Returns:
            True if deleted, False if not found
        """
        pass

