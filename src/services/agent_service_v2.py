"""Service for managing agents using repositories.

This is the new version of AgentService that uses the repository pattern.
It will eventually replace the old AgentService.
"""

from typing import List, Optional
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.models import Agent as AgentModel


class AgentServiceV2:
    """Service for agent CRUD operations using repositories."""
    
    def __init__(self, agent_repository: AgentRepository):
        """Initialize service with repository."""
        self.agent_repository = agent_repository
    
    def create_agent(
        self,
        user_id: int,
        name: str,
        description: Optional[str],
        instruction: str,
        model: str = "gemini-2.0-flash-exp",
        tools: Optional[List[str]] = None,
        use_file_search: bool = False
    ) -> Agent:
        """Create a new agent for a user."""
        agent = Agent(
            name=name,
            description=description,
            instruction=instruction,
            model=model,
            tools=tools or [],
            use_file_search=use_file_search,
            user_id=user_id
        )
        return self.agent_repository.create(agent)
    
    def get_agent_by_id(self, agent_id: int, user_id: int) -> Optional[Agent]:
        """Get an agent by ID (only if owned by user)."""
        return self.agent_repository.get_by_id(agent_id, user_id)
    
    def get_user_agents(self, user_id: int) -> List[Agent]:
        """Get all active agents for a user."""
        return self.agent_repository.get_by_user(user_id)
    
    def update_agent(
        self,
        agent_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instruction: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[str]] = None,
        use_file_search: Optional[bool] = None
    ) -> Optional[Agent]:
        """Update an agent (only if owned by user)."""
        agent = self.agent_repository.get_by_id(agent_id, user_id)
        if not agent:
            return None
        
        # Update only provided fields
        if name is not None:
            agent.name = name
        if description is not None:
            agent.description = description
        if instruction is not None:
            agent.instruction = instruction
        if model is not None:
            agent.model = model
        if tools is not None:
            agent.tools = tools
        if use_file_search is not None:
            agent.use_file_search = use_file_search
        
        return self.agent_repository.update(agent)
    
    def delete_agent(self, agent_id: int, user_id: int) -> bool:
        """Soft delete an agent (only if owned by user)."""
        return self.agent_repository.delete(agent_id, user_id)
    
    def _to_model(self, entity: Agent) -> AgentModel:
        """Convert domain entity to SQLAlchemy model (for backward compatibility)."""
        return AgentModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            instruction=entity.instruction,
            model=entity.model,
            tools=entity.tools,
            use_file_search=entity.use_file_search,
            user_id=entity.user_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

