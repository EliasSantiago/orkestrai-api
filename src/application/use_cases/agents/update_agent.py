"""Use case for updating an agent."""

from typing import Optional, Dict, Any
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.domain.services.validation_service import ValidationService
from src.domain.exceptions import AgentNotFoundError, FileSearchModelMismatchError


class UpdateAgentUseCase:
    """Use case for updating an agent."""
    
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
        agent_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        agent_type: Optional[str] = None,
        instruction: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[list] = None,
        use_file_search: Optional[bool] = None,
        workflow_config: Optional[Dict[str, Any]] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        is_favorite: Optional[bool] = None,
        icon: Optional[str] = None
    ) -> Agent:
        """
        Execute agent update.
        
        Args:
            agent_id: Agent ID
            user_id: User ID (for ownership check)
            name: New name (optional)
            description: New description (optional)
            agent_type: New agent type (optional)
            instruction: New instruction (optional)
            model: New model (optional)
            tools: New tools list (optional)
            use_file_search: New use_file_search value (optional)
            workflow_config: New workflow configuration (optional)
            custom_config: New custom configuration (optional)
            is_favorite: Mark/unmark as favorite (optional)
            
        Returns:
            Updated agent entity
            
        Raises:
            AgentNotFoundError: If agent not found or not owned by user
            FileSearchModelMismatchError: If file search is enabled with incompatible model
        """
        # Get current agent
        agent = self.agent_repository.get_by_id(agent_id, user_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        
        # Determine final values after update
        final_model = model if model is not None else agent.model
        final_use_file_search = use_file_search if use_file_search is not None else agent.use_file_search
        final_agent_type = agent_type if agent_type is not None else agent.agent_type
        
        # Validate file search compatibility (only for LLM agents)
        if final_agent_type == "llm" and final_model:
            self.validator.validate_file_search_model(final_model, final_use_file_search)
        
        # Update only provided fields
        if name is not None:
            agent.name = name
        if description is not None:
            agent.description = description
        if agent_type is not None:
            agent.agent_type = agent_type
        if instruction is not None:
            agent.instruction = instruction
        if model is not None:
            agent.model = model
        if tools is not None:
            agent.tools = tools
        if use_file_search is not None:
            agent.use_file_search = use_file_search
        if workflow_config is not None:
            agent.workflow_config = workflow_config
        if custom_config is not None:
            agent.custom_config = custom_config
        if is_favorite is not None:
            agent.is_favorite = is_favorite
        if icon is not None:
            agent.icon = icon
        
        # Save via repository
        updated = self.agent_repository.update(agent)
        if not updated:
            raise AgentNotFoundError(agent_id)
        
        return updated

