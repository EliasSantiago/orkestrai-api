"""LobeChat compatible API routes for tRPC compatibility.

These endpoints provide compatibility with LobeChat frontend tRPC calls:
- /trpc/lambda/message.getMessages -> /api/messages
- /trpc/lambda/session.getGroupedSessions -> /api/sessions/grouped
- /trpc/lambda/topic.getTopics -> /api/topics
- /trpc/lambda/plugin.getPlugins -> /api/plugins
- /trpc/lambda/market.getPluginList -> /api/market
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.api.dependencies import get_current_user_id
from src.hybrid_conversation_service import HybridConversationService
from src.api.schemas import Message

router = APIRouter(prefix="/api", tags=["lobechat-compat"])


@router.get("/messages", response_model=List[Message])
async def get_messages(
    session_id: Optional[str] = Query(None, description="Session ID to filter messages (obrigatório)"),
    topic_id: Optional[str] = Query(None, description="Topic ID (not used, for compatibility)"),
    limit: Optional[int] = Query(100, description="Maximum number of messages to return"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get messages (compatible with LobeChat message.getMessages).
    
    This endpoint is compatible with LobeChat's tRPC message.getMessages call.
    Requires session_id to be provided.
    
    **Query Parameters:**
    - `session_id` (obrigatório): Filter by specific session
    - `topic_id` (optional): Not used, kept for compatibility
    - `limit` (optional): Maximum messages to return (default: 100)
    
    **Response:**
    List of Message objects compatible with LobeChat format with id, createdAt, updatedAt, etc.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "session_id is required"}]
        )
    
    # Get messages from specific session
    history = HybridConversationService.get_conversation_history(
        user_id=user_id,
        session_id=session_id,
        limit=limit,
        db=db
    )
    
    # Convert to Message objects, ensuring all fields are present
    messages = []
    for msg_dict in history:
        # Ensure all required fields are present
        msg_data = {
            "id": msg_dict.get("id"),
            "role": msg_dict.get("role"),
            "content": msg_dict.get("content"),
            "timestamp": msg_dict.get("timestamp"),
            "createdAt": msg_dict.get("createdAt"),
            "updatedAt": msg_dict.get("updatedAt"),
            "metadata": msg_dict.get("metadata", {}),
            "model": msg_dict.get("model"),
            "provider": msg_dict.get("provider"),
            "parentId": msg_dict.get("parentId")
        }
        messages.append(Message(**msg_data))
    
    # Sort by timestamp (oldest first) as expected by LobeChat
    messages.sort(key=lambda m: m.createdAt or 0)
    
    return messages


# NOTE: /sessions/grouped route moved to lobechat_rest_routes.py
# This route is removed to avoid conflicts - use /api/sessions/grouped from lobechat_rest_routes instead


@router.get("/topics", response_model=List[Dict[str, Any]])
async def get_topics(
    session_id: Optional[str] = Query(None, description="Session ID (not used, for compatibility)"),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get topics (compatible with LobeChat topic.getTopics).
    
    This endpoint returns an empty list as topics are not essential functionality.
    Kept for compatibility with LobeChat frontend.
    
    **Response:**
    Empty list (topics feature not implemented).
    """
    return []


@router.get("/plugins", response_model=List[Dict[str, Any]])
async def get_plugins(
    user_id: int = Depends(get_current_user_id)
):
    """
    Get plugins (compatible with LobeChat plugin.getPlugins).
    
    This endpoint returns an empty list as local plugins are not used.
    Kept for compatibility with LobeChat frontend.
    
    **Response:**
    Empty list (local plugins not implemented).
    """
    return []


@router.get("/market", response_model=Dict[str, Any])
async def get_market_plugin_list(
    category: Optional[str] = Query(None, description="Category filter (not used)"),
    locale: Optional[str] = Query("en", description="Locale (not used)"),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get market plugin list (compatible with LobeChat market.getPluginList).
    
    This endpoint returns an empty marketplace as we use the public marketplace.
    Kept for compatibility with LobeChat frontend.
    
    **Response:**
    Empty marketplace object.
    """
    return {
        "plugins": [],
        "categories": [],
        "total": 0
    }

