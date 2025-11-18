"""Agent execution API routes for chat/interaction."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from src.adk_conversation_middleware import get_adk_middleware
from src.api.dependencies import get_current_user_id
from src.api.di import get_chat_with_agent_use_case, get_get_agent_use_case, get_get_user_agents_use_case
from src.application.use_cases.agents import ChatWithAgentUseCase, GetAgentUseCase, GetUserAgentsUseCase
from src.domain.exceptions import AgentNotFoundError, UnsupportedModelError, InvalidModelError
from src.infrastructure.database.entity_mapper import agent_entity_to_model
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def generate_session_id() -> str:
    """
    Generate a session ID using UUID format.
    
    Format: UUID v4 (standard format)
    Example: cc9e7f12-0413-49bc-91dd-7a5f6f2500da
    
    Returns:
        Session ID string in UUID format (without prefix)
    """
    import uuid
    return str(uuid.uuid4())

router = APIRouter(prefix="/api/agents", tags=["agents"])


def sanitize_agent_name(name: str, agent_id: int) -> str:
    """
    Sanitize agent name to be a valid Python identifier for ADK.
    
    ADK requires agent names to be valid identifiers:
    - Start with letter or underscore
    - Only contain letters, digits, and underscores
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


class ChatRequest(BaseModel):
    """Request model for agent chat."""
    message: str
    agent_id: Optional[int] = None  # Optional: uses first agent if not provided
    session_id: Optional[str] = None  # Optional: auto-generated if not provided
    model: Optional[str] = None  # Optional: override agent's model (e.g., "openai/gpt-4o-mini", "gemini/gemini-2.0-flash-exp")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Faça um resumo das principais notícias sobre IA desta semana",
                    "agent_id": 1,
                    "session_id": "",
                    "model": None
                },
                {
                    "message": "Qual a previsão do tempo para São Paulo hoje?",
                    "agent_id": 2,
                    "session_id": "cc9e7f12-0413-49bc-91dd-7a5f6f2500da"
                },
                {
                    "message": "Extraia os dados principais desta página: https://exemplo.com",
                    "agent_id": 3,
                    "session_id": "",
                    "model": "openai/gpt-4o"
                },
                {
                    "message": "Olá, como você pode me ajudar?",
                    "agent_id": 1
                }
            ]
        }


class ChatResponse(BaseModel):
    """Response model for agent chat."""
    response: str
    agent_id: int
    agent_name: str
    session_id: Optional[str] = None
    model_used: Optional[str] = None  # Which model was used for this response


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_use_case: ChatWithAgentUseCase = Depends(get_chat_with_agent_use_case),
    get_agent_use_case: GetAgentUseCase = Depends(get_get_agent_use_case),
    get_user_agents_use_case: GetUserAgentsUseCase = Depends(get_get_user_agents_use_case)
):
    """
    Chat with an agent.
    
    This endpoint allows you to send messages to a specific agent and get responses.
    It automatically handles conversation context if session_id is provided.
    If session_id is not provided, a new one is generated automatically.
    If agent_id is not provided, uses the first agent of the user.
    
    **Required Fields:**
    - `message`: The message to send to the agent
    
    **Optional Fields:**
    - `agent_id`: The ID of the agent to chat with (uses first agent if not provided)
    - `session_id`: Session ID for conversation continuity (auto-generated if not provided)
    - `model`: Override the agent's default model (e.g., "gpt-4o-mini", "gemini-2.5-flash", "claude-3-5-sonnet-latest")
    
    **Example Request Body:**
    ```json
    {
      "message": "Olá, como você pode me ajudar?",
      "agent_id": 1,
      "session_id": "cc9e7f12-0413-49bc-91dd-7a5f6f2500da",
      "model": "gpt-4o-mini"
    }
    ```
    
    **Model Override:**
    If you specify a `model` in the request, it will override the agent's default model for this conversation.
    This is useful when:
    - The default model is overloaded (503 error)
    - You want to test different models with the same agent
    - You need a faster/cheaper model for simple queries
    """
    # Determine agent_id - use first agent if not provided
    agent_id = request.agent_id
    if agent_id is None:
        agents = get_user_agents_use_case.execute(user_id)
        if not agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=[{"msg": "No agents found. Please create an agent first."}],
                headers={"X-Error-Type": "no_agents"}
            )
        agent_id = agents[0].id
    
    # Generate session_id if not provided
    session_id = request.session_id or generate_session_id()
    
    # Associate session with user if not already associated
    middleware = get_adk_middleware()
    if not middleware.get_user_id_from_session(session_id):
        middleware.set_user_id_for_session(session_id, user_id)
    
    try:
        # Get agent info for response (need name and id)
        agent_entity = get_agent_use_case.execute(agent_id, user_id)
        agent_model = agent_entity_to_model(agent_entity)
        
        # Determine model name
        model_name = request.model or agent_entity.model or "gemini-2.0-flash-exp"
        
        # Execute chat use case (handles all the complex logic)
        response = await chat_use_case.execute(
            user_id=user_id,
            agent_id=agent_id,
            message=request.message,
            session_id=session_id,
            model_override=request.model
        )
        
        return ChatResponse(
            response=response,
            agent_id=agent_model.id,
            agent_name=agent_model.name,
            session_id=session_id,
            model_used=model_name
        )
        
    except (AgentNotFoundError, InvalidModelError, UnsupportedModelError):
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[{"msg": f"Error executing agent: {str(e)}"}]
        )

