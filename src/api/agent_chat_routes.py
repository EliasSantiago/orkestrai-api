"""Agent execution API routes for chat/interaction."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt
from src.database import get_db
from src.auth import SECRET_KEY, ALGORITHM
from src.services.agent_service import AgentService
from src.models import Agent as AgentModel
from src.hybrid_conversation_service import HybridConversationService
from src.services.adk_context_hooks import inject_context_into_agent, set_session_context
from src.adk_conversation_middleware import get_adk_middleware
from pydantic import BaseModel

router = APIRouter(prefix="/api/agents", tags=["agents"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from token."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


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
    agent_id: int  # Required: must specify which agent to use
    session_id: Optional[str] = None  # Optional: auto-generated if not provided
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Olá, como você pode me ajudar?",
                "agent_id": 1,
                "session_id": "session_abc123"
            }
        }


class ChatResponse(BaseModel):
    """Response model for agent chat."""
    response: str
    agent_id: int
    agent_name: str
    session_id: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Chat with an agent.
    
    This endpoint allows you to send messages to a specific agent and get responses.
    It automatically handles conversation context if session_id is provided.
    If session_id is not provided, a new one is generated automatically.
    
    **Required Fields:**
    - `message`: The message to send to the agent
    - `agent_id`: The ID of the agent to chat with
    
    **Optional Fields:**
    - `session_id`: Session ID for conversation continuity (auto-generated if not provided)
    
    **Example Request Body:**
    ```json
    {
      "message": "Olá, como você pode me ajudar?",
      "agent_id": 1,
      "session_id": "session_abc123"
    }
    ```
    """
    # Generate session_id if not provided
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:12]}"
    
    # Associate session with user if not already associated
    middleware = get_adk_middleware()
    if not middleware.get_user_id_from_session(session_id):
        middleware.set_user_id_for_session(session_id, user_id)
    
    # Get agent by ID (required)
    agent_model = AgentService.get_agent_by_id(db, request.agent_id, user_id)
    if not agent_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Load ADK agent from database model
    try:
        from google.adk.agents import Agent
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        from tools import calculator, get_current_time
        
        # Get tools
        tool_map = {
            "calculator": calculator,
            "get_current_time": get_current_time,
        }
        tool_names = agent_model.tools or []
        tools = [tool_map[name] for name in tool_names if name in tool_map]
        
        # Sanitize agent name for ADK (must be valid identifier)
        agent_name_sanitized = sanitize_agent_name(agent_model.name, agent_model.id)
        
        # Create ADK agent
        adk_agent = Agent(
            model=str(agent_model.model) if agent_model.model else "gemini-2.0-flash-exp",
            name=str(agent_name_sanitized),
            description=str(agent_model.description) if agent_model.description else "",
            instruction=str(agent_model.instruction),
            tools=tools if tools else [],
        )
        
        # Save user message to Redis + PostgreSQL BEFORE injecting context
        # This ensures the current message is included in the context
        HybridConversationService.add_user_message(
            user_id=user_id,
            session_id=session_id,
            content=request.message,
            db=db
        )
        
        # Set session context for context injection
        set_session_context(session_id, user_id)
        
        # Inject conversation context into agent BEFORE creating runner
        # This modifies the agent's instruction to include conversation history
        # We do this AFTER saving the message so it's included in context
        # IMPORTANT: Must inject BEFORE creating Runner, as Runner may clone the agent
        inject_context_into_agent(adk_agent, session_id, user_id)
        
        # Create Runner - use a consistent app_name
        # The app_name should match the directory structure or be a simple identifier
        app_name = "adk_agent_app"  # Use a consistent app name
        
        runner = InMemoryRunner(
            agent=adk_agent,
            app_name=app_name
        )
        
        # Create or get session in ADK's session service
        # The session must exist before running the agent
        try:
            session = await runner.session_service.get_session(
                app_name=app_name,
                user_id=str(user_id),
                session_id=session_id
            )
            if not session:
                # Create session if it doesn't exist
                session = await runner.session_service.create_session(
                    app_name=app_name,
                    user_id=str(user_id),
                    session_id=session_id
                )
        except Exception as session_error:
            # If session creation fails, try to create it anyway
            try:
                session = await runner.session_service.create_session(
                    app_name=app_name,
                    user_id=str(user_id),
                    session_id=session_id
                )
            except Exception:
                # If session already exists, that's fine
                pass
        
        # Prepare message as Content object for ADK
        message_str = str(request.message).strip()
        if not message_str:
            raise ValueError("Message cannot be empty")
        
        # Create Content object for ADK
        user_content = types.Content(parts=[types.Part(text=message_str)], role='user')
        
        # Execute agent using Runner.run_async - this is the correct way
        response = None
        chunks = []
        try:
            async for event in runner.run_async(
                user_id=str(user_id),
                session_id=session_id,
                new_message=user_content
            ):
                # Extract text from events
                if hasattr(event, 'content') and event.content:
                    # Event.content can be a list of Content objects
                    for content in event.content if isinstance(event.content, list) else [event.content]:
                        if hasattr(content, 'parts') and content.parts:
                            for part in content.parts:
                                if hasattr(part, 'text') and part.text:
                                    chunks.append(part.text)
                                elif isinstance(part, str):
                                    chunks.append(part)
                        elif isinstance(content, str):
                            chunks.append(content)
                    # Also check if event has text directly
                    if hasattr(event, 'text') and event.text:
                        chunks.append(event.text)
            
            # Join all chunks to form the complete response
            response = ''.join(chunks) if chunks else None
        except Exception as agent_error:
            import traceback
            error_trace = traceback.format_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error executing agent: {str(agent_error)}\nTraceback: {error_trace}"
            )
        
        # Ensure response is a string
        # ADK run_live/run_async may return different types
        if response is None:
            response = "I received your message but couldn't generate a response."
        elif isinstance(response, dict):
            # If response is a dict, try to extract text/message/content
            response = response.get('text') or response.get('message') or response.get('content') or str(response)
        elif not isinstance(response, str):
            # Convert to string if it's not already
            response = str(response)
        
        # Save assistant response to Redis + PostgreSQL
        HybridConversationService.add_assistant_message(
            user_id=user_id,
            session_id=session_id,
            content=response,
            db=db
        )
        
        return ChatResponse(
            response=response,
            agent_id=agent_model.id,
            agent_name=agent_model.name,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing agent: {str(e)}"
        )

