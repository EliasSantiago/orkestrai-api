"""Use case for chatting with an agent."""

import asyncio
import base64
import logging
from typing import Optional, List, AsyncGenerator
from sqlalchemy.orm import Session
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.domain.services.validation_service import ValidationService
from src.domain.services.tool_loader_service import ToolLoaderService
from src.hybrid_conversation_service import HybridConversationService
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage, FilePart
from src.domain.exceptions import (
    AgentNotFoundError,
    InvalidModelError,
    UnsupportedModelError
)
from src.services.adk_context_hooks import set_session_context
from src.services.token_service import TokenService

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
        self.token_service = TokenService(db)
        self._last_model_used = None  # Track last model actually used (may differ from requested)
        self._last_response = None  # Track last response for token calculation
    
    async def execute(
        self,
        user_id: int,
        agent_id: int,
        message: str,
        session_id: Optional[str] = None,
        model_override: Optional[str] = None,
        files: Optional[List[FilePart]] = None
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
        # Get agent from repository
        agent = self.agent_repository.get_by_id(agent_id, user_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        
        # Determine model
        model_name = model_override or agent.model
        
        # Normalize model name (e.g., gemini-3-pro -> gemini-3-pro-preview)
        model_name = self._normalize_model_name(model_name)
        
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
            agent_id=agent.id,
            db=self.db
        )
        
        # Get conversation history
        history = HybridConversationService.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            db=self.db
        )
        
        # Build messages for LLM (include model info in instruction)
        messages = self._build_messages(agent, history, message, model_name, files=files)
        
        # Set session context for ADK (if using Gemini models)
        if model_name.startswith("gemini/") or model_name.startswith("gemini-"):
            set_session_context(session_id, user_id)
        
        # Execute chat with retry logic
        response, actual_model = await self._execute_with_retry(
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
        
        # Log successful completion
        if actual_model != model_name:
            logger.info(f"✅ Chat completed - Model usado: {actual_model} (solicitado: {model_name}), Agent: {agent.name}, User: {user_id}")
        else:
            logger.info(f"✅ Chat completed - Model: {model_name}, Agent: {agent.name}, User: {user_id}")
        
        # Store actual model used for response tracking
        self._last_model_used = actual_model
        
        return response
    
    async def execute_with_agent(
        self,
        user_id: int,
        agent: Agent,
        message: str,
        session_id: Optional[str] = None,
        model_override: Optional[str] = None,
        files: Optional[List[FilePart]] = None
    ) -> str:
        """
        Execute chat with a provided agent entity (e.g., default agent from file).
        
        Args:
            user_id: User ID
            agent: Agent entity (can be from file or database)
            message: User message
            session_id: Optional session ID for conversation continuity
            model_override: Optional model override
            files: Optional file attachments
            
        Returns:
            Assistant response
            
        Raises:
            InvalidModelError: If model is not supported
            UnsupportedModelError: If model is not supported by any provider
        """
        # Determine model
        model_name = model_override or agent.model
        
        # Normalize model name (e.g., gemini-3-pro -> gemini-3-pro-preview)
        model_name = self._normalize_model_name(model_name)
        
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
            agent_id=agent.id,
            db=self.db
        )
        
        # Get conversation history
        history = HybridConversationService.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            db=self.db
        )
        
        # Build messages for LLM (include model info in instruction)
        messages = self._build_messages(agent, history, message, model_name, files=files)
        
        # Check token availability before making LLM call
        try:
            # Estimate tokens for the request
            estimated_tokens = self.token_service.calculate_tokens_from_messages(
                messages=[{"role": m.role, "content": m.content} for m in messages],
                model=model_name
            )
            logger.info(f"📊 Estimated tokens for request: {estimated_tokens}")
            
            # Check if user has enough tokens
            self.token_service.check_token_availability(user_id, estimated_tokens)
        except Exception as e:
            logger.error(f"❌ Token check failed: {e}")
            raise
        
        # Set session context for ADK (if using Gemini models)
        if model_name.startswith("gemini/") or model_name.startswith("gemini-"):
            set_session_context(session_id, user_id)
        
        # Execute chat with retry logic
        response, actual_model = await self._execute_with_retry(
            provider=provider,
            model=model_name,
            messages=messages,
            tools=tools,
            agent=agent,
            user_id=user_id,
            session_id=session_id
        )
        
        # Record token usage after successful response
        try:
            # Calculate tokens from messages (prompt) and response (completion)
            prompt_tokens = self.token_service.calculate_tokens_from_messages(
                messages=[{"role": m.role, "content": m.content} for m in messages],
                model=actual_model
            )
            completion_tokens = self.token_service.calculate_tokens_from_messages(
                messages=[{"role": "assistant", "content": response}],
                model=actual_model
            )
            total_tokens = prompt_tokens + completion_tokens
            
            # Estimate cost (rough estimate, LiteLLM may not have exact pricing)
            try:
                import litellm
                cost_usd = litellm.completion_cost(
                    model=actual_model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens
                )
                if cost_usd is None:
                    cost_usd = 0.0
            except Exception:
                cost_usd = 0.0
            
            # Record usage
            self.token_service.record_token_usage(
                user_id=user_id,
                model=actual_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                endpoint="/chat",
                session_id=session_id,
                metadata={"agent_id": agent.id, "agent_name": agent.name}
            )
            logger.info(f"💰 Recorded token usage: {total_tokens} tokens (prompt: {prompt_tokens}, completion: {completion_tokens}), ${cost_usd:.6f}")
        except Exception as e:
            logger.error(f"⚠️  Failed to record token usage: {e}")
        
        # Save assistant response
        HybridConversationService.add_assistant_message(
            user_id=user_id,
            session_id=session_id,
            content=response,
            db=self.db
        )
        
        # Log successful completion
        if actual_model != model_name:
            logger.info(f"✅ Chat completed - Model usado: {actual_model} (solicitado: {model_name}), Agent: {agent.name}, User: {user_id}")
        else:
            logger.info(f"✅ Chat completed - Model: {model_name}, Agent: {agent.name}, User: {user_id}")
        
        # Store actual model used for response tracking
        self._last_model_used = actual_model
        
        return response
    
    async def execute_stream(
        self,
        user_id: int,
        agent_id: int,
        message: str,
        session_id: Optional[str] = None,
        model_override: Optional[str] = None,
        files: Optional[List[FilePart]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Execute chat with agent and stream the response.
        
        Args:
            user_id: User ID
            agent_id: Agent ID
            message: User message
            session_id: Optional session ID for conversation continuity
            model_override: Optional model override
            
        Yields:
            Response chunks as they are generated
            
        Raises:
            AgentNotFoundError: If agent not found
            InvalidModelError: If model is not supported
            UnsupportedModelError: If model is not supported by any provider
        """
        # Get agent from repository
        agent = self.agent_repository.get_by_id(agent_id, user_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        
        # Determine model
        model_name = model_override or agent.model
        
        # Normalize model name
        model_name = self._normalize_model_name(model_name)
        
        # Validate model
        self.validator.validate_model(model_name)
        
        # Get LLM provider
        provider = self.llm_factory.get_provider(model_name)
        if not provider:
            available_models = self.llm_factory.get_all_supported_models()
            raise UnsupportedModelError(model_name, available_models)
        
        # Load tools
        logger.info(f"🔧 Loading tools for agent {agent.id} (name: {agent.name})")
        logger.info(f"🔧 Agent tools from DB: {agent.tools}")
        tools = self.tool_loader.load_tools_for_agent(agent.tools or [], user_id)
        logger.info(f"🔧 Loaded {len(tools)} tools: {[getattr(t, '__name__', str(t)) for t in tools]}")
        
        # Save user message
        HybridConversationService.add_user_message(
            user_id=user_id,
            session_id=session_id,
            content=message,
            agent_id=agent.id,
            db=self.db
        )
        
        # Get conversation history
        history = HybridConversationService.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            db=self.db
        )
        
        # Build messages for LLM (PASSAR FILES AQUI!)
        print(f"\n🔨 execute_stream: Building messages with files={len(files) if files else 0}")
        messages = self._build_messages(agent, history, message, model_name, files=files)
        
        # Set session context for ADK
        if model_name.startswith("gemini/") or model_name.startswith("gemini-"):
            set_session_context(session_id, user_id)
        
        # Stream response chunks
        response_chunks = []
        async for chunk in self._stream_with_retry(
            provider=provider,
            model=model_name,
            messages=messages,
            tools=tools,
            agent=agent,
            user_id=user_id,
            session_id=session_id
        ):
            response_chunks.append(chunk)
            yield chunk
        
        # Save complete assistant response
        complete_response = ''.join(response_chunks)
        HybridConversationService.add_assistant_message(
            user_id=user_id,
            session_id=session_id,
            content=complete_response,
            db=self.db
        )
        
        logger.info(f"✅ Chat stream completed - Model: {model_name}, Agent: {agent.name}, User: {user_id}")
    
    async def execute_with_agent_stream(
        self,
        user_id: int,
        agent: Agent,
        message: str,
        session_id: Optional[str] = None,
        model_override: Optional[str] = None,
        files: Optional[List[FilePart]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Execute chat with a provided agent entity and stream the response.
        
        Args:
            user_id: User ID
            agent: Agent entity (can be from file or database)
            message: User message
            session_id: Optional session ID for conversation continuity
            model_override: Optional model override
            
        Yields:
            Response chunks as they are generated
            
        Raises:
            InvalidModelError: If model is not supported
            UnsupportedModelError: If model is not supported by any provider
        """
        # Determine model
        model_name = model_override or agent.model
        
        # Normalize model name
        model_name = self._normalize_model_name(model_name)
        
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
            agent_id=agent.id,
            db=self.db
        )
        
        # Get conversation history
        history = HybridConversationService.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            db=self.db
        )
        
        # Build messages for LLM (PASSAR FILES AQUI!)
        print(f"\n🔨 execute_with_agent_stream: Building messages with files={len(files) if files else 0}")
        messages = self._build_messages(agent, history, message, model_name, files=files)
        
        # Set session context for ADK
        if model_name.startswith("gemini/") or model_name.startswith("gemini-"):
            set_session_context(session_id, user_id)
        
        # Stream response chunks
        response_chunks = []
        async for chunk in self._stream_with_retry(
            provider=provider,
            model=model_name,
            messages=messages,
            tools=tools,
            agent=agent,
            user_id=user_id,
            session_id=session_id
        ):
            response_chunks.append(chunk)
            yield chunk
        
        # Save complete assistant response
        complete_response = ''.join(response_chunks)
        HybridConversationService.add_assistant_message(
            user_id=user_id,
            session_id=session_id,
            content=complete_response,
            db=self.db
        )
        
        logger.info(f"✅ Chat stream completed - Model: {model_name}, Agent: {agent.name}, User: {user_id}")
    
    def _build_messages(
        self,
        agent: Agent,
        history: List[dict],
        current_message: str,
        model: Optional[str] = None,
        files: Optional[List[FilePart]] = None
    ) -> List[LLMMessage]:
        """
        Build messages list for LLM.
        
        Args:
            agent: Agent entity
            history: Conversation history
            current_message: Current user message
            model: Optional model name to include in system instruction
            files: Optional list of file attachments
        """
        print(f"\n🔨 BUILDING MESSAGES")
        print(f"  History: {len(history)} messages")
        print(f"  Files: {len(files) if files else 0}")
        print(f"  Current message: {current_message[:100]}...")
        logger.info(f"🔨 Building messages - History: {len(history)} messages, Files: {len(files) if files else 0}")
        
        messages = []
        
        # Build system instruction with model information
        system_instruction = agent.instruction or ""
        
        # Add model information to instruction if provided
        if model:
            # Extract readable model name (remove provider prefix if present)
            readable_model = model
            provider = "Unknown"
            
            if "/" in model:
                provider_part, model_name = model.split("/", 1)
                readable_model = model_name
                
                # Map provider prefix to readable name
                provider_map = {
                    "openai": "OpenAI",
                    "gemini": "Google",
                    "anthropic": "Anthropic",
                    "ollama": "Ollama"
                }
                provider = provider_map.get(provider_part.lower(), provider_part.title())
            else:
                model_name = model
                # Try to detect provider from model name
                if model.startswith("gemini"):
                    provider = "Google"
                    readable_model = model.replace("gemini-", "Gemini ").replace("-", " ").title()
                elif model.startswith("gpt"):
                    provider = "OpenAI"
                    # Format GPT models: gpt-4o-mini -> GPT-4o Mini
                    readable_model = model.replace("gpt-", "GPT-")
                    # Capitalize after hyphens but keep lowercase for version letters (like "o" in "4o")
                    parts = readable_model.split("-")
                    formatted_parts = []
                    for i, part in enumerate(parts):
                        if i == 0:
                            formatted_parts.append(part.upper())  # GPT
                        else:
                            # Keep version letters lowercase (4o -> 4o, not 4O)
                            formatted_parts.append(part.capitalize())
                    readable_model = " ".join(formatted_parts)
                else:
                    provider = "Unknown"
            
            # Add model info to instruction
            model_info = f"\n\nIMPORTANTE: Você está sendo executado usando o modelo {readable_model} da {provider}. Quando perguntado sobre qual modelo você usa, responda corretamente informando que está usando {readable_model} da {provider}."
            
            # Only add if not already present in instruction
            if "modelo" not in system_instruction.lower() and readable_model.lower() not in system_instruction.lower():
                system_instruction = system_instruction + model_info
        
        # Add system message (agent instruction with model info)
        if system_instruction:
            messages.append(LLMMessage(role="system", content=system_instruction))
        
        # Add conversation history
        for msg in history:
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))
        
        # Add current user message with files if provided
        # IMPORTANTE: Se houver arquivos convertidos, incluir instrução na mensagem
        message_content = current_message
        if files:
            # Adicionar contexto sobre os arquivos na mensagem
            file_names = [f.file_name for f in files if f.file_name]
            if file_names:
                message_content = f"{current_message}\n\n[Nota: Arquivos anexados: {', '.join(file_names)}. O conteúdo convertido dos arquivos será incluído abaixo.]"
        
        user_message = LLMMessage(role="user", content=message_content, files=files)
        messages.append(user_message)
        
        if files:
            logger.info(f"✅ Added user message with {len(files)} files attached")
            logger.info(f"  📝 Message content: {message_content[:200]}...")
            for i, file_part in enumerate(files):
                # Tentar decodificar para mostrar preview do conteúdo
                try:
                    if file_part.type == "text" or file_part.mime_type == "text/plain":
                        decoded_text = base64.b64decode(file_part.data).decode('utf-8')
                        preview = decoded_text[:100] + "..." if len(decoded_text) > 100 else decoded_text
                        logger.info(f"  📎 File {i+1}: {file_part.file_name} ({file_part.type}, {file_part.mime_type}, {len(decoded_text)} chars text)")
                        logger.info(f"     Preview: {preview}")
                    else:
                        logger.info(f"  📎 File {i+1}: {file_part.file_name} ({file_part.type}, {file_part.mime_type}, {len(file_part.data)} chars base64)")
                except Exception as e:
                    logger.info(f"  📎 File {i+1}: {file_part.file_name} ({file_part.type}, {file_part.mime_type}, {len(file_part.data)} chars base64)")
        else:
            logger.info("✅ Added user message without files")
        
        return messages
    
    def _normalize_model_name(self, model: str) -> str:
        """Normalize model names to match official API names."""
        # Map aliases to official model names
        model_aliases = {
            "gemini/gemini-3-pro": "gemini/gemini-3-pro-preview",  # Official name is gemini-3-pro-preview
        }
        return model_aliases.get(model, model)
    
    def _get_fallback_models(self, model: str) -> List[str]:
        """Get fallback models for a given model."""
        from src.api.models_routes import MODEL_FALLBACKS
        
        # Normalize model name first
        normalized_model = self._normalize_model_name(model)
        
        # Check if model has fallbacks defined
        if normalized_model in MODEL_FALLBACKS:
            return MODEL_FALLBACKS[normalized_model]
        
        # Default fallbacks based on provider
        if model.startswith("gemini/"):
            return [
                "gemini/gemini-2.5-flash",
                "gemini/gemini-1.5-pro-latest",
                "gemini/gemini-1.5-flash",
                "gemini/gemini-1.5-pro"
            ]
        elif model.startswith("openai/"):
            return [
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "openai/gpt-4-turbo",
                "openai/gpt-3.5-turbo"
            ]
        
        return []
    
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
        """Execute chat with retry logic and automatic model fallback."""
        base_delay = 2
        
        # Normalize model name first (e.g., gemini-3-pro -> gemini-3-pro-preview)
        normalized_model = self._normalize_model_name(model)
        fallback_models = self._get_fallback_models(normalized_model)
        
        # Try normalized model first, then fallbacks
        models_to_try = [normalized_model] + fallback_models
        
        for model_to_try in models_to_try:
            current_model = model_to_try
            if model_to_try != normalized_model:
                logger.warning(f"⚠️  Tentando modelo fallback: {current_model} (solicitado: {model})")
                print(f"⚠️  Modelo '{model}' não disponível, tentando fallback: {current_model}")
            
            response_chunks = []
            
            for attempt in range(max_retries):
                try:
                    # Prepare provider kwargs
                    provider_kwargs = self._prepare_provider_kwargs(
                        agent=agent,
                        model=current_model,
                        user_id=user_id,
                        session_id=session_id
                    )
                    
                    # Call provider
                    async for chunk in provider.chat(
                        messages=messages,
                        model=current_model,
                        tools=tools if tools else None,
                        **provider_kwargs
                    ):
                        response_chunks.append(chunk)
                    
                    # Success - log completion
                    response_length = sum(len(chunk) for chunk in response_chunks) if response_chunks else 0
                    logger.info(f"✅ Resposta completa do modelo {current_model} - {response_length} caracteres gerados")
                    if current_model != normalized_model:
                        print(f"✅ Resposta gerada com modelo fallback: {current_model} (solicitado: {model})")
                    else:
                        print(f"✅ Resposta completa do modelo {current_model} - {response_length} caracteres")
                    
                    # Success - return response and actual model used
                    response_text = ''.join(response_chunks) if response_chunks else ""
                    return response_text, current_model
                    
                except Exception as error:
                    error_str = str(error).lower()
                    # Check if it's a model error (not found, quota, or Vertex AI)
                    is_model_error = (
                        "not found" in error_str or 
                        "does not exist" in error_str or
                        "invalid model" in error_str or
                        "vertex_ai" in error_str or
                        "v1beta" in error_str or
                        "não está disponível" in error_str or
                        "quota" in error_str.lower() or
                        "429" in error_str or
                        "rate limit" in error_str.lower() or
                        "resource_exhausted" in error_str.lower() or
                        "free_tier" in error_str.lower()
                    )
                    
                    # If it's a model error and we have more models to try, break inner loop to try next model
                    if is_model_error and model_to_try != models_to_try[-1]:
                        logger.warning(f"⚠️  Modelo {current_model} não disponível: {str(error)[:200]}")
                        break  # Try next fallback model
                    
                    # If it's not a model error or it's the last model, check if should retry
                    if not self._should_retry(error, attempt, max_retries):
                        # If it's the last model to try, raise the error
                        if model_to_try == models_to_try[-1]:
                            raise
                        # Otherwise, try next fallback
                        break
                    
                    # Retry with exponential backoff
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    response_chunks = []
        
        # If we get here, all models failed
        raise ValueError(
            f"Todos os modelos falharam. Modelo solicitado: {model}, "
            f"Modelo normalizado: {normalized_model}, "
            f"Fallbacks tentados: {', '.join(fallback_models[:3])}"
        )
        
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
            # Use agent ID or 0 for default agent
            agent_id_for_sanitize = agent.id if agent.id else 0
            agent_name_sanitized = sanitize_agent_name(agent.name, agent_id_for_sanitize)
            
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
    
    async def _stream_with_retry(
        self,
        provider,
        model: str,
        messages: List[LLMMessage],
        tools: List,
        agent: Agent,
        user_id: int,
        session_id: str,
        max_retries: int = 3
    ) -> AsyncGenerator[str, None]:
        """Execute chat with retry logic and automatic model fallback, streaming response."""
        base_delay = 2
        
        # Normalize model name first
        normalized_model = self._normalize_model_name(model)
        fallback_models = self._get_fallback_models(normalized_model)
        
        # Try normalized model first, then fallbacks
        models_to_try = [normalized_model] + fallback_models
        
        for model_to_try in models_to_try:
            current_model = model_to_try
            if model_to_try != normalized_model:
                logger.warning(f"⚠️  Tentando modelo fallback: {current_model} (solicitado: {model})")
            
            for attempt in range(max_retries):
                try:
                    # Prepare provider kwargs
                    provider_kwargs = self._prepare_provider_kwargs(
                        agent=agent,
                        model=current_model,
                        user_id=user_id,
                        session_id=session_id
                    )
                    
                    # Call provider and stream chunks
                    async for chunk in provider.chat(
                        messages=messages,
                        model=current_model,
                        tools=tools if tools else None,
                        **provider_kwargs
                    ):
                        yield chunk
                    
                    # Success - log completion
                    logger.info(f"✅ Stream completo do modelo {current_model}")
                    if current_model != normalized_model:
                        logger.info(f"✅ Resposta gerada com modelo fallback: {current_model} (solicitado: {model})")
                    
                    # Success - return from generator
                    return
                    
                except Exception as error:
                    error_str = str(error).lower()
                    # Check if it's a model error
                    is_model_error = (
                        "not found" in error_str or 
                        "does not exist" in error_str or
                        "invalid model" in error_str or
                        "vertex_ai" in error_str or
                        "v1beta" in error_str or
                        "não está disponível" in error_str or
                        "quota" in error_str.lower() or
                        "429" in error_str or
                        "rate limit" in error_str.lower() or
                        "resource_exhausted" in error_str.lower() or
                        "free_tier" in error_str.lower()
                    )
                    
                    # If it's a model error and we have more models to try, break inner loop
                    if is_model_error and model_to_try != models_to_try[-1]:
                        logger.warning(f"⚠️  Modelo {current_model} não disponível: {str(error)[:200]}")
                        break  # Try next fallback model
                    
                    # If it's not a model error or it's the last model, check if should retry
                    if not self._should_retry(error, attempt, max_retries):
                        # If it's the last model to try, raise the error
                        if model_to_try == models_to_try[-1]:
                            raise
                        # Otherwise, try next fallback
                        break
                    
                    # Retry with exponential backoff
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        # If we get here, all models failed
        raise ValueError(
            f"Todos os modelos falharam. Modelo solicitado: {model}, "
            f"Modelo normalizado: {normalized_model}, "
            f"Fallbacks tentados: {', '.join(fallback_models[:3])}"
        )
    
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

