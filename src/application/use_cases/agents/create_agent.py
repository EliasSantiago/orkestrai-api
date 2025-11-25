"""Use case for creating an agent."""

from typing import Optional, Dict, Any
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
        agent_type: str = "llm",
        instruction: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[list] = None,
        use_file_search: bool = False,
        workflow_config: Optional[Dict[str, Any]] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        is_favorite: bool = False,
        is_public: bool = False,
        icon: Optional[str] = None
    ) -> Agent:
        """
        Execute agent creation.
        
        Args:
            user_id: User ID (owner)
            name: Agent name
            description: Agent description
            agent_type: Type of agent (llm, sequential, loop, parallel, custom)
            instruction: Agent instruction (required for LLM agents)
            model: Model to use (required for LLM agents)
            tools: List of tool names
            use_file_search: Whether to enable file search (LLM agents only)
            workflow_config: Configuration for workflow agents
            custom_config: Configuration for custom agents
            is_favorite: Mark as favorite
            
        Returns:
            Created agent entity
            
        Raises:
            FileSearchModelMismatchError: If file search is enabled with incompatible model
            InvalidModelError: If model is not supported
        """
        # Validate based on agent type
        if agent_type == "llm":
            if not model:
                raise ValueError("LLM agents require a model")
            # Validate model
            self.validator.validate_model(model)
            # Validate file search compatibility
            self.validator.validate_file_search_model(model, use_file_search)
        
        # Create agent entity
        agent = Agent(
            name=name,
            description=description,
            agent_type=agent_type,
            instruction=instruction,
            model=model or "gemini-2.0-flash-exp",
            tools=tools or [],
            use_file_search=use_file_search,
            workflow_config=workflow_config or {},
            custom_config=custom_config or {},
            is_favorite=is_favorite,
            is_public=is_public,
            icon=icon,
            user_id=user_id
        )
        
        # Save via repository
        return self.agent_repository.create(agent)

