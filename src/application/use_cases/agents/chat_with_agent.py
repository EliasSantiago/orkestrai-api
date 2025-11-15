"""Use case for chatting with an agent."""

import asyncio
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.domain.services.validation_service import ValidationService
from src.domain.services.tool_loader_service import ToolLoaderService
from src.hybrid_conversation_service import HybridConversationService
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage
from src.domain.exceptions import (
    AgentNotFoundError,
    InvalidModelError,
    UnsupportedModelError
)
from src.services.adk_context_hooks import set_session_context

logger = logging.getLogger(__name__)


def sanitize_agent_name(name: str, agent_id: int) -> str:
    """
    Sanitize agent name to be a valid Python identifier for ADK.
    
    Args:
        name: Agent name
        agent_id: Agent ID
        
    Returns:
        Sanitized name
    """
    import unicodedata
    
    # Remove accents and special characters
    sanitized = unicodedata.normalize('NFD', name)
    sanitized = ''.join(c for c in sanitized if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase and replace spaces/hyphens with underscores
    sanitized = sanitized.lower().replace(" ", "_").replace("-", "_")
    
    # Keep only alphanumeric and underscores
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    
    # Ensure it starts with letter or underscore
    if not sanitized or not (sanitized[0].isalpha() or sanitized[0] == "_"):
        sanitized = f"agent_{sanitized}" if sanitized else f"agent_{agent_id}"
    
    return sanitized


class ChatWithAgentUseCase:
    """Use case for chatting with an agent."""
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        validator: ValidationService,
        tool_loader: ToolLoaderService,
        llm_factory: LLMFactory,
        db: Session
    ):
        """Initialize use case with dependencies."""
        self.agent_repository = agent_repository
        self.validator = validator
        self.tool_loader = tool_loader
        self.llm_factory = llm_factory
        self.db = db
    
    async def execute(
        self,
        user_id: int,
        agent_id: int,
        message: str,
        session_id: Optional[str] = None,
        model_override: Optional[str] = None
    ) -> str:
        """
        Execute chat with agent.
        
        Args:
            user_id: User ID
            agent_id: Agent ID
            message: User message
            session_id: Optional session ID for conversation continuity
            model_override: Optional model override
            
        Returns:
            Assistant response
            
        Raises:
            AgentNotFoundError: If agent not found
            InvalidModelError: If model is not supported
            UnsupportedModelError: If model is not supported by any provider
        """
        # Get agent
        agent = self.agent_repository.get_by_id(agent_id, user_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        
        # Determine model
        model_name = model_override or agent.model
        
        # Validate model
        self.validator.validate_model(model_name)
        
        # Get LLM provider
        provider = self.llm_factory.get_provider(model_name)
        if not provider:
            available_models = self.llm_factory.get_all_supported_models()
            raise UnsupportedModelError(model_name, available_models)
        
        # Load tools
        tools = self.tool_loader.load_tools_for_agent(agent.tools or [], user_id)
        
        # Save user message
        HybridConversationService.add_user_message(
            user_id=user_id,
            session_id=session_id,
            content=message,
            db=self.db
        )
        
        # Get conversation history
        history = HybridConversationService.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            db=self.db
        )
        
        # Build messages for LLM
        messages = self._build_messages(agent, history, message)
        
        # Set session context for ADK
        if model_name.startswith("gemini-"):
            set_session_context(session_id, user_id)
        
        # Execute chat with retry logic
        response = await self._execute_with_retry(
            provider=provider,
            model=model_name,
            messages=messages,
            tools=tools,
            agent=agent,
            user_id=user_id,
            session_id=session_id
        )
        
        # Save assistant response
        HybridConversationService.add_assistant_message(
            user_id=user_id,
            session_id=session_id,
            content=response,
            db=self.db
        )
        
        return response
    
    def _build_messages(
        self,
        agent: Agent,
        history: List[dict],
        current_message: str
    ) -> List[LLMMessage]:
        """Build messages list for LLM."""
        messages = []
        
        # Add system message (agent instruction)
        if agent.instruction:
            messages.append(LLMMessage(role="system", content=agent.instruction))
        
        # Add conversation history
        for msg in history:
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))
        
        # Add current user message
        messages.append(LLMMessage(role="user", content=current_message))
        
        return messages
    
    async def _execute_with_retry(
        self,
        provider,
        model: str,
        messages: List[LLMMessage],
        tools: List,
        agent: Agent,
        user_id: int,
        session_id: str,
        max_retries: int = 3
    ) -> str:
        """Execute chat with retry logic."""
        base_delay = 2
        response_chunks = []
        
        for attempt in range(max_retries):
            try:
                # Prepare provider kwargs
                provider_kwargs = self._prepare_provider_kwargs(
                    agent=agent,
                    model=model,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Call provider
                async for chunk in provider.chat(
                    messages=messages,
                    model=model,
                    tools=tools if tools else None,
                    **provider_kwargs
                ):
                    response_chunks.append(chunk)
                
                # Success
                break
                
            except Exception as error:
                if not self._should_retry(error, attempt, max_retries):
                    raise
                
                # Retry with exponential backoff
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                response_chunks = []
        
        # Join chunks
        response = ''.join(response_chunks) if response_chunks else None
        
        if response is None:
            response = "I received your message but couldn't generate a response."
        elif not isinstance(response, str):
            response = str(response)
        
        return response
    
    def _prepare_provider_kwargs(
        self,
        agent: Agent,
        model: str,
        user_id: int,
        session_id: str
    ) -> dict:
        """Prepare provider-specific kwargs."""
        kwargs = {
            "user_id": str(user_id),
            "session_id": session_id,
            "app_name": "agent_chat_app",
        }
        
        # For ADK provider (Gemini), add agent metadata
        if model.startswith("gemini-"):
            agent_name_sanitized = sanitize_agent_name(agent.name, agent.id)
            
            # Get File Search Stores for RAG
            file_search_stores = []
            if agent.use_file_search:
                try:
                    from src.models import FileSearchStore
                    stores = self.db.query(FileSearchStore).filter(
                        FileSearchStore.user_id == user_id,
                        FileSearchStore.is_active == True
                    ).all()
                    file_search_stores = [store.google_store_name for store in stores]
                    if file_search_stores:
                        logger.info(f"Found {len(file_search_stores)} File Search Stores for RAG")
                except Exception as e:
                    logger.warning(f"Could not load File Search Stores: {e}")
            
            kwargs.update({
                "agent_name": agent_name_sanitized,
                "agent_description": str(agent.description) if agent.description else "",
                "instruction": agent.instruction,
                "inject_context": True,
                "file_search_stores": file_search_stores if file_search_stores else None,
            })
        
        return kwargs
    
    def _should_retry(self, error: Exception, attempt: int, max_retries: int) -> bool:
        """Determine if error should be retried."""
        error_message = str(error).upper()
        error_type = type(error).__name__
        
        # Check if it's a 429 error
        is_429_error = (
            "429" in error_message or 
            "RESOURCE_EXHAUSTED" in error_message or
            "rate limit" in error_message.lower() or 
            "quota" in error_message.lower()
        )
        
        # Check if it's a connection error (don't retry)
        is_connection_error = (
            "Connection error" in error_message or
            "ConnectError" in error_type or
            "CERTIFICATE_VERIFY_FAILED" in error_message or
            "certificate verify failed" in error_message.lower() or
            "timeout" in error_message.lower() or
            "Timeout" in error_type
        )
        
        return is_429_error and attempt < max_retries - 1 and not is_connection_error

