"""Agent API routes."""

from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt
from src.database import get_db
from src.auth import SECRET_KEY, ALGORITHM
from src.services.agent_service import AgentService
from src.api.schemas import AgentCreate, AgentUpdate, AgentResponse

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


def sync_agents_to_files_sync():
    """Sync agents from database to files (synchronous, runs in background)."""
    try:
        from src.adk_loader import sync_agents_from_db
        sync_agents_from_db()
    except Exception as e:
        # Don't fail the API request if sync fails
        # This is a background operation
        import traceback
        print(f"⚠ Warning: Could not sync agents to files: {e}")
        print(traceback.format_exc())


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new agent for the current user."""
    try:
        agent = AgentService.create_agent(
            db=db,
            user_id=user_id,
            name=agent_data.name,
            description=agent_data.description,
            instruction=agent_data.instruction,
            model=agent_data.model,
            tools=agent_data.tools
        )
        # Sync agents to files after creation (non-blocking background task)
        # BackgroundTasks ensures the response is returned before sync starts
        background_tasks.add_task(sync_agents_to_files_sync)
        
        return agent
    except Exception as e:
        import traceback
        print(f"✗ Error creating agent: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent: {str(e)}"
        )


@router.get("", response_model=List[AgentResponse])
async def get_agents(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all agents for the current user."""
    agents = AgentService.get_user_agents(db, user_id)
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get a specific agent by ID."""
    agent = AgentService.get_agent_by_id(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update an agent."""
    agent = AgentService.update_agent(
        db=db,
        agent_id=agent_id,
        user_id=user_id,
        name=agent_data.name,
        description=agent_data.description,
        instruction=agent_data.instruction,
        model=agent_data.model,
        tools=agent_data.tools
    )
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Sync agents to files after update (non-blocking background task)
    background_tasks.add_task(sync_agents_to_files_sync)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete an agent."""
    success = AgentService.delete_agent(db, agent_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Sync agents to files after deletion (non-blocking background task)
    background_tasks.add_task(sync_agents_to_files_sync)

