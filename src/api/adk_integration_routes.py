"""API routes for ADK integration with conversation tracking."""

from fastapi import APIRouter, Depends, HTTPException, status
from src.adk_conversation_middleware import get_adk_middleware
from src.api.dependencies import get_current_user_id

router = APIRouter(prefix="/api/adk", tags=["adk-integration"])


@router.post("/sessions/{session_id}/associate")
async def associate_session_with_user(
    session_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """
    Associate an ADK session with the current user.
    
    Note: This is usually done automatically when using /api/agents/chat.
    This endpoint is only needed for manual session management.
    """
    middleware = get_adk_middleware()
    success = middleware.set_user_id_for_session(session_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to associate session"
        )
    return {"status": "success", "message": "Session associated with user"}
