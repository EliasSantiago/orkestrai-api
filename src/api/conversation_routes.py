"""Conversation and session API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt
from src.database import get_db
from src.auth import SECRET_KEY, ALGORITHM
from src.hybrid_conversation_service import HybridConversationService
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
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all session IDs for the current user."""
    sessions = HybridConversationService.get_user_sessions(user_id, db=db)
    return sessions


@router.get("/sessions/{session_id}", response_model=ConversationHistory)
async def get_session_history(
    session_id: str,
    limit: Optional[int] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get conversation history for a specific session."""
    history = HybridConversationService.get_conversation_history(
        user_id=user_id,
        session_id=session_id,
        limit=limit,
        db=db
    )
    # Convert to Message objects
    messages = [Message(**msg) for msg in history]
    return ConversationHistory(session_id=session_id, messages=messages)


@router.get("/sessions/{session_id}/info", response_model=SessionInfo)
async def get_session_info(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get session information."""
    info = HybridConversationService.get_session_info(user_id, session_id, db=db)
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
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Add a message to the conversation."""
    success = HybridConversationService.add_user_message(
        user_id=user_id,
        session_id=session_id,
        content=message.content,
        metadata=message.metadata,
        db=db
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
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a conversation session."""
    success = HybridConversationService.clear_session(user_id, session_id, db=db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete all conversation sessions for the current user."""
    # Get all sessions
    sessions = HybridConversationService.get_user_sessions(user_id, db=db)
    
    # Clear each session
    for session_id in sessions:
        HybridConversationService.clear_session(user_id, session_id, db=db)
    
    # Also clear Redis cache
    from src.redis_client import get_redis_client
    redis_client = get_redis_client()
    if redis_client.is_connected():
        redis_client.clear_user_sessions(user_id)

