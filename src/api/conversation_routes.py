"""Conversation and session API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt
from src.database import get_db
from src.auth import SECRET_KEY, ALGORITHM
from src.conversation_service import ConversationService
from src.api.schemas import ConversationHistory, SessionInfo, MessageCreate, Message

router = APIRouter(prefix="/api/conversations", tags=["conversations"])
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


@router.get("/sessions", response_model=List[str])
async def get_user_sessions(
    user_id: int = Depends(get_current_user_id)
):
    """Get all session IDs for the current user."""
    sessions = ConversationService.get_user_sessions(user_id)
    return sessions


@router.get("/sessions/{session_id}", response_model=ConversationHistory)
async def get_session_history(
    session_id: str,
    limit: Optional[int] = None,
    user_id: int = Depends(get_current_user_id)
):
    """Get conversation history for a specific session."""
    history = ConversationService.get_conversation_history(
        user_id=user_id,
        session_id=session_id,
        limit=limit
    )
    # Convert to Message objects
    messages = [Message(**msg) for msg in history]
    return ConversationHistory(session_id=session_id, messages=messages)


@router.get("/sessions/{session_id}/info", response_model=SessionInfo)
async def get_session_info(
    session_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Get session information."""
    info = ConversationService.get_session_info(user_id, session_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return SessionInfo(**info)


@router.post("/sessions/{session_id}/messages")
async def add_message(
    session_id: str,
    message: MessageCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Add a message to the conversation."""
    success = ConversationService.add_user_message(
        user_id=user_id,
        session_id=session_id,
        content=message.content,
        metadata=message.metadata
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )
    return {"status": "success", "message": "Message saved"}


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Delete a conversation session."""
    success = ConversationService.clear_session(user_id, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(
    user_id: int = Depends(get_current_user_id)
):
    """Delete all conversation sessions for the current user."""
    from src.redis_client import get_redis_client
    redis_client = get_redis_client()
    redis_client.clear_user_sessions(user_id)

