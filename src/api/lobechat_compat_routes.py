"""LobeChat compatible API routes for tRPC compatibility.

These endpoints provide compatibility with LobeChat frontend tRPC calls:
- /trpc/lambda/message.getMessages -> /api/messages
- /trpc/lambda/session.getGroupedSessions -> /api/sessions/grouped
- /trpc/lambda/topic.getTopics -> /api/topics
- /trpc/lambda/plugin.getPlugins -> /api/plugins
- /trpc/lambda/market.getPluginList -> /api/market
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.api.dependencies import get_current_user_id
from src.hybrid_conversation_service import HybridConversationService
from src.api.schemas import Message

router = APIRouter(prefix="/api", tags=["lobechat-compat"])


@router.get("/messages", response_model=List[Message])
async def get_messages(
    session_id: Optional[str] = Query(None, description="Session ID to filter messages"),
    topic_id: Optional[str] = Query(None, description="Topic ID (not used, for compatibility)"),
    limit: Optional[int] = Query(100, description="Maximum number of messages to return"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get messages (compatible with LobeChat message.getMessages).
    
    This endpoint is compatible with LobeChat's tRPC message.getMessages call.
    If session_id is provided, returns messages for that session.
    Otherwise, returns messages from all user sessions (limited).
    
    **Query Parameters:**
    - `session_id` (optional): Filter by specific session
    - `topic_id` (optional): Not used, kept for compatibility
    - `limit` (optional): Maximum messages to return (default: 100)
    
    **Response:**
    List of Message objects compatible with LobeChat format.
    """
    if session_id:
        # Get messages from specific session
        history = HybridConversationService.get_conversation_history(
            user_id=user_id,
            session_id=session_id,
            limit=limit,
            db=db
        )
        messages = [Message(**msg) for msg in history]
        return messages
    else:
        # Get messages from all sessions (limited)
        sessions = HybridConversationService.get_user_sessions(user_id, db=db)
        all_messages = []
        
        for sess_id in sessions[:10]:  # Limit to first 10 sessions
            history = HybridConversationService.get_conversation_history(
                user_id=user_id,
                session_id=sess_id,
                limit=limit // len(sessions) if sessions else limit,
                db=db
            )
            all_messages.extend([Message(**msg) for msg in history])
        
        # Sort by timestamp if available
        all_messages.sort(key=lambda m: m.timestamp or "", reverse=True)
        
        return all_messages[:limit] if limit else all_messages


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
            
            # Generate title from first message if available
            title = f"Session {session_id[:8]}"
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
            
            grouped[date_key].append({
                "session_id": session_id,
                "title": title,
                "message_count": info.get("message_count", 0),
                "last_activity": info.get("last_activity"),
                "ttl": info.get("ttl")
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

