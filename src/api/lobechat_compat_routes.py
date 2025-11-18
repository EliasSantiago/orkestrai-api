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


@router.get("/sessions/grouped", response_model=List[Dict[str, Any]])
async def get_grouped_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get grouped sessions (compatible with LobeChat session.getGroupedSessions).
    
    Returns sessions grouped by date or other criteria.
    Compatible with LobeChat's tRPC session.getGroupedSessions call.
    
    **Response Format:**
    ```json
    [
      {
        "date": "2025-11-18",
        "sessions": [
          {
            "session_id": "sess_123",
            "title": "Session title",
            "message_count": 10,
            "last_activity": "2025-11-18T10:30:00"
          }
        ]
      }
    ]
    ```
    """
    sessions = HybridConversationService.get_user_sessions(user_id, db=db)
    
    # Group sessions by date
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    
    for session_id in sessions:
        info = HybridConversationService.get_session_info(user_id, session_id, db=db)
        if info:
            # Extract date from last_activity or use today
            date_key = "today"
            if info.get("last_activity"):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(info["last_activity"].replace("Z", "+00:00"))
                    date_key = dt.strftime("%Y-%m-%d")
                except:
                    pass
            
            if date_key not in grouped:
                grouped[date_key] = []
            
            # Get title from session metadata or generate from first message
            title = info.get("title") or f"Session {session_id[:8]}"
            if not title or title == f"Session {session_id[:8]}":
                try:
                    history = HybridConversationService.get_conversation_history(
                        user_id=user_id,
                        session_id=session_id,
                        limit=1,
                        db=db
                    )
                    if history and len(history) > 0:
                        first_msg = history[0]
                        content = first_msg.get("content", "")
                        if content:
                            # Use first 50 chars as title
                            title = content[:50] + "..." if len(content) > 50 else content
                except:
                    pass
            
            # Build meta object from session metadata
            meta = {}
            if info.get("avatar"):
                meta["avatar"] = info["avatar"]
            if info.get("description"):
                meta["description"] = info["description"]
            
            grouped[date_key].append({
                "session_id": session_id,
                "title": title,
                "message_count": info.get("message_count", 0),
                "last_activity": info.get("last_activity"),
                "ttl": info.get("ttl"),
                "meta": meta if meta else {}
            })
    
    # Convert to list format
    result = [
        {
            "date": date,
            "sessions": sorted(sessions, key=lambda s: s.get("last_activity", ""), reverse=True)
        }
        for date, sessions in sorted(grouped.items(), reverse=True)
    ]
    
    return result


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

