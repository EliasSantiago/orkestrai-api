"""Use case for creating an agent."""

from typing import Optional
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.domain.services.validation_service import ValidationService


class CreateAgentUseCase:
    """Use case for creating a new agent."""
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        validator: ValidationService
    ):
        """Initialize use case with dependencies."""
        self.agent_repository = agent_repository
        self.validator = validator
    
    def execute(
        self,
        user_id: int,
        name: str,
        description: Optional[str],
        instruction: str,
        model: str = "gemini-2.0-flash-exp",
        tools: Optional[list] = None,
        use_file_search: bool = False
    ) -> Agent:
        """
        Execute agent creation.
        
        Args:
            user_id: User ID (owner)
            name: Agent name
            description: Agent description
            instruction: Agent instruction
            model: Model to use
            tools: List of tool names
            use_file_search: Whether to enable file search
            
        Returns:
            Created agent entity
            
        Raises:
            FileSearchModelMismatchError: If file search is enabled with incompatible model
            InvalidModelError: If model is not supported
        """
        # Validate model
        self.validator.validate_model(model)
        
        # Validate file search compatibility
        self.validator.validate_file_search_model(model, use_file_search)
        
        # Create agent entity
        agent = Agent(
            name=name,
            description=description,
            instruction=instruction,
            model=model,
            tools=tools or [],
            use_file_search=use_file_search,
            user_id=user_id
        )
        
        # Save via repository
        return self.agent_repository.create(agent)

