"""API routes for ADK integration with conversation tracking."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt
from src.database import get_db
from src.auth import SECRET_KEY, ALGORITHM
from src.adk_conversation_middleware import get_adk_middleware

router = APIRouter(prefix="/api/adk", tags=["adk-integration"])
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


@router.post("/sessions/{session_id}/associate")
async def associate_session_with_user(
    session_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Associate an ADK session with the current user."""
    middleware = get_adk_middleware()
    success = middleware.set_user_id_for_session(session_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to associate session"
        )
    return {"status": "success", "message": "Session associated with user"}


@router.post("/sessions/{session_id}/messages")
async def save_adk_message(
    session_id: str,
    role: str,
    content: str,
    user_id: int = Depends(get_current_user_id)
):
    """Save a message from ADK conversation."""
    middleware = get_adk_middleware()
    
    if role == "user":
        success = middleware.save_user_message(
            session_id=session_id,
            content=content,
            user_id=user_id
        )
    elif role == "assistant":
        success = middleware.save_assistant_message(
            session_id=session_id,
            content=content,
            user_id=user_id
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'user' or 'assistant'"
        )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )
    
    return {"status": "success", "message": "Message saved"}

