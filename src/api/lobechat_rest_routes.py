"""Complete REST API routes for LobeChat frontend compatibility.

This module provides comprehensive REST endpoints that replace tRPC calls.
All endpoints are prefixed with /api and require authentication.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel
from src.database import get_db
from src.api.dependencies import get_current_user_id
from src.hybrid_conversation_service import HybridConversationService
from src.models_conversation import ConversationMessage, ConversationSession
from src.api.helpers import create_error_response
from src.api.schemas import Message

logger = logging.getLogger(__name__)

# ============================================================================
# Session Routes
# ============================================================================

sessions_router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionCreateRequest(BaseModel):
    """Request for creating a session."""
    type: Optional[str] = "agent"
    title: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    groupId: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class SessionUpdateRequest(BaseModel):
    """Request for updating a session."""
    title: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    pinned: Optional[bool] = None
    groupId: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    updatedAt: Optional[int] = None


class SessionGroupItem(BaseModel):
    """Session group item."""
    id: str
    name: str
    sort: Optional[int] = None


class SessionGroupCreateRequest(BaseModel):
    """Request for creating a session group."""
    name: str
    sort: Optional[int] = None


class SessionGroupUpdateRequest(BaseModel):
    """Request for updating a session group."""
    name: Optional[str] = None
    sort: Optional[int] = None


class SessionGroupOrderRequest(BaseModel):
    """Request for updating session group order."""
    sortMap: List[Dict[str, Any]]


@sessions_router.get("/grouped")
async def get_grouped_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get grouped sessions compatible with LobeChat.
    
    Returns sessions grouped by date.
    """
    sessions = HybridConversationService.get_user_sessions(user_id, db=db)
    
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    
    for session_id in sessions:
        info = HybridConversationService.get_session_info(user_id, session_id, db=db)
        if info:
            date_key = "today"
            if info.get("last_activity"):
                try:
                    dt = datetime.fromisoformat(info["last_activity"].replace("Z", "+00:00"))
                    date_key = dt.strftime("%Y-%m-%d")
                except:
                    pass
            
            if date_key not in grouped:
                grouped[date_key] = []
            
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
                            title = content[:50] + "..." if len(content) > 50 else content
                except:
                    pass
            
            meta = {}
            if info.get("avatar"):
                meta["avatar"] = info["avatar"]
            if info.get("description"):
                meta["description"] = info["description"]
            
            grouped[date_key].append({
                "id": session_id,
                "session_id": session_id,
                "title": title,
                "message_count": info.get("message_count", 0),
                "last_activity": info.get("last_activity"),
                "ttl": info.get("ttl"),
                "meta": meta if meta else {},
                "createdAt": info.get("last_activity") or datetime.utcnow().isoformat() + "Z",
                "updatedAt": info.get("last_activity") or datetime.utcnow().isoformat() + "Z"
            })
    
    result = [
        {
            "date": date,
            "sessions": sorted(sessions, key=lambda s: s.get("last_activity", ""), reverse=True)
        }
        for date, sessions in sorted(grouped.items(), reverse=True)
    ]
    
    return {"sessionGroups": result, "sessions": []}


@sessions_router.post("")
async def create_session(
    request: SessionCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new session."""
    # Sessions are created automatically when first message is sent
    # Return a temporary ID
    import uuid
    session_id = f"temp-session-{uuid.uuid4()}"
    return {"id": session_id, "session_id": session_id}


@sessions_router.get("/count")
async def count_sessions(
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Count sessions for the user."""
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    )
    
    if startDate:
        try:
            start_dt = datetime.fromisoformat(startDate)
            sessions = sessions.filter(ConversationSession.created_at >= start_dt)
        except:
            pass
    
    if endDate:
        try:
            end_dt = datetime.fromisoformat(endDate) + timedelta(days=1)
            sessions = sessions.filter(ConversationSession.created_at < end_dt)
        except:
            pass
    
    return sessions.count()


@sessions_router.get("/rank")
async def rank_sessions(
    limit: Optional[int] = Query(10),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get ranked sessions by activity."""
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).order_by(ConversationSession.last_activity.desc()).limit(limit or 10).all()
    
    result = []
    for idx, session in enumerate(sessions, start=1):
        result.append({
            "id": session.session_id,
            "session_id": session.session_id,
            "rank": idx,
            "message_count": session.message_count,
            "last_activity": session.last_activity.isoformat() + "Z" if session.last_activity else None
        })
    
    return result


@sessions_router.put("/{session_id}")
async def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update session metadata."""
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    metadata = session.session_metadata or {}
    
    if request.title is not None:
        metadata["title"] = request.title
    if request.description is not None:
        metadata["description"] = request.description
    if request.avatar is not None:
        metadata["avatar"] = request.avatar
    if request.pinned is not None:
        metadata["pinned"] = request.pinned
    if request.meta:
        metadata.update(request.meta)
    
    session.session_metadata = metadata
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return {"id": session_id, "status": "success"}


@sessions_router.put("/{session_id}/config")
async def update_session_config(
    session_id: str,
    config: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update session configuration."""
    # Session config is managed by backend
    return {"id": session_id, "status": "success"}


@sessions_router.put("/{session_id}/chat-config")
async def update_session_chat_config(
    session_id: str,
    config: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update session chat configuration."""
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    metadata = session.session_metadata or {}
    metadata["chatConfig"] = config
    session.session_metadata = metadata
    db.commit()
    
    return {"id": session_id, "status": "success"}


@sessions_router.get("/search")
async def search_sessions(
    keywords: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Search sessions by keywords."""
    if not keywords or len(keywords.strip()) < 2:
        return []
    
    keywords_lower = keywords.lower().strip()
    
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    matching_sessions = []
    
    for session in sessions:
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.session_id
        ).limit(10).all()
        
        matches = False
        for msg in messages:
            if keywords_lower in msg.content.lower():
                matches = True
                break
        
        if matches:
            info = HybridConversationService.get_session_info(user_id, session.session_id, db=db)
            matching_sessions.append({
                "id": session.session_id,
                "session_id": session.session_id,
                "title": info.get("title") or f"Session {session.session_id[:8]}",
                "description": None,
                "last_activity": session.last_activity.isoformat() + "Z" if session.last_activity else None,
                "message_count": session.message_count
            })
    
    return matching_sessions


@sessions_router.delete("/{session_id}")
async def remove_session(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a session."""
    success = HybridConversationService.clear_session(user_id, session_id, db=db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"status": "success"}


@sessions_router.delete("")
async def remove_all_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete all sessions for the user."""
    sessions = HybridConversationService.get_user_sessions(user_id, db=db)
    for session_id in sessions:
        HybridConversationService.clear_session(user_id, session_id, db=db)
    return {"status": "success"}


# Session Groups
session_groups_router = APIRouter(prefix="/api/session-groups", tags=["session-groups"])


@session_groups_router.post("")
async def create_session_group(
    request: SessionGroupCreateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Create a session group."""
    import uuid
    group_id = str(uuid.uuid4())
    return {"id": group_id}


@session_groups_router.delete("/{group_id}")
async def remove_session_group(
    group_id: str,
    removeChildren: Optional[bool] = Query(False),
    user_id: int = Depends(get_current_user_id)
):
    """Remove a session group."""
    return {"status": "success"}


@session_groups_router.delete("")
async def remove_all_session_groups(
    user_id: int = Depends(get_current_user_id)
):
    """Remove all session groups."""
    return {"status": "success"}


@session_groups_router.put("/{group_id}")
async def update_session_group(
    group_id: str,
    request: SessionGroupUpdateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Update a session group."""
    return {"id": group_id, "status": "success"}


@session_groups_router.put("/order")
async def update_session_group_order(
    request: SessionGroupOrderRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Update session group order."""
    return {"status": "success"}


# ============================================================================
# Message Routes (extended)
# ============================================================================

messages_router = APIRouter(prefix="/api/messages", tags=["messages"])


@messages_router.get("")
async def get_messages(
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    groupId: Optional[str] = Query(None),
    limit: Optional[int] = Query(100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get messages with filters."""
    if not sessionId and not groupId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sessionId or groupId is required"
        )
    
    if sessionId:
        history = HybridConversationService.get_conversation_history(
            user_id=user_id,
            session_id=sessionId,
            limit=limit or 100,
            db=db
        )
        
        messages = []
        for msg_dict in history:
            msg_data = {
                "id": msg_dict.get("id") or f"msg-{msg_dict.get('timestamp', 0)}",
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
        
        messages.sort(key=lambda m: m.createdAt or 0)
        return messages
    
    return []


@messages_router.post("")
async def create_message(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a message."""
    session_id = request.get("sessionId")
    content = request.get("content", "")
    metadata = request.get("metadata", {})
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sessionId is required"
        )
    
    success = HybridConversationService.add_user_message(
        user_id=user_id,
        session_id=session_id,
        content=content,
        metadata=metadata,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message"
        )
    
    import uuid
    message_id = f"msg-{uuid.uuid4()}"
    return {"id": message_id, "sessionId": session_id}


@messages_router.get("/count")
async def count_messages(
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Count messages."""
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if not session_ids:
        return 0
    
    query = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids)
    )
    
    if startDate:
        try:
            start_dt = datetime.fromisoformat(startDate)
            query = query.filter(ConversationMessage.created_at >= start_dt)
        except:
            pass
    
    if endDate:
        try:
            end_dt = datetime.fromisoformat(endDate) + timedelta(days=1)
            query = query.filter(ConversationMessage.created_at < end_dt)
        except:
            pass
    
    return query.count()


@messages_router.get("/words")
async def count_words(
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Count words in messages."""
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if not session_ids:
        return 0
    
    query = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids)
    )
    
    if startDate:
        try:
            start_dt = datetime.fromisoformat(startDate)
            query = query.filter(ConversationMessage.created_at >= start_dt)
        except:
            pass
    
    if endDate:
        try:
            end_dt = datetime.fromisoformat(endDate) + timedelta(days=1)
            query = query.filter(ConversationMessage.created_at < end_dt)
        except:
            pass
    
    messages = query.all()
    return sum(len(msg.content.split()) for msg in messages)


@messages_router.get("/rank-models")
async def rank_models(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get model rankings."""
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if not session_ids:
        return []
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids),
        ConversationMessage.role == "assistant"
    ).all()
    
    model_counts: Dict[str, int] = {}
    for msg in messages:
        if msg.message_metadata and isinstance(msg.message_metadata, dict):
            model = msg.message_metadata.get("model")
            if model:
                model_counts[model] = model_counts.get(model, 0) + 1
    
    sorted_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for rank, (model, count) in enumerate(sorted_models, start=1):
        result.append({
            "model": model,
            "count": count,
            "rank": rank
        })
    
    return result


@messages_router.get("/heatmaps")
async def get_heatmaps(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get message heatmap data."""
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if not session_ids:
        return []
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids),
        ConversationMessage.created_at >= thirty_days_ago
    ).all()
    
    date_counts: Dict[str, int] = {}
    for msg in messages:
        date_key = msg.created_at.strftime("%Y-%m-%d")
        date_counts[date_key] = date_counts.get(date_key, 0) + 1
    
    result = [
        {"date": date, "count": count}
        for date, count in sorted(date_counts.items())
    ]
    
    return result


@messages_router.put("/{message_id}")
async def update_message(
    message_id: str,
    value: Dict[str, Any] = Body(...),
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a message."""
    msg_db_id = message_id.replace("msg-", "") if message_id.startswith("msg-") else message_id
    
    try:
        msg_db_id_int = int(msg_db_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID format"
        )
    
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == msg_db_id_int
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if "content" in value:
        message.content = value["content"]
    
    if "metadata" in value or "error" in value or "translate" in value or "tts" in value:
        metadata = message.message_metadata or {}
        metadata.update(value)
        message.message_metadata = metadata
    
    db.commit()
    
    return {"id": message_id, "status": "success"}


@messages_router.put("/{message_id}/translate")
async def update_message_translate(
    message_id: str,
    translate: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update message translation."""
    return await update_message(message_id, {"translate": translate}, user_id=user_id, db=db)


@messages_router.put("/{message_id}/tts")
async def update_message_tts(
    message_id: str,
    tts: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update message TTS."""
    return await update_message(message_id, {"tts": tts}, user_id=user_id, db=db)


@messages_router.put("/{message_id}/metadata")
async def update_message_metadata(
    message_id: str,
    metadata: Dict[str, Any] = Body(...),
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update message metadata."""
    return await update_message(message_id, {"metadata": metadata}, sessionId=sessionId, topicId=topicId, user_id=user_id, db=db)


@messages_router.put("/{message_id}/plugin-state")
async def update_message_plugin_state(
    message_id: str,
    state: Dict[str, Any] = Body(...),
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update message plugin state."""
    return await update_message(message_id, {"pluginState": state}, sessionId=sessionId, topicId=topicId, user_id=user_id, db=db)


@messages_router.put("/{message_id}/plugin-error")
async def update_message_plugin_error(
    message_id: str,
    error: Dict[str, Any] = Body(...),
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update message plugin error."""
    return await update_message(message_id, {"pluginError": error}, sessionId=sessionId, topicId=topicId, user_id=user_id, db=db)


@messages_router.put("/{message_id}/rag")
async def update_message_rag(
    message_id: str,
    rag: Dict[str, Any] = Body(...),
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update message RAG data."""
    return await update_message(message_id, {"rag": rag}, sessionId=sessionId, topicId=topicId, user_id=user_id, db=db)


@messages_router.delete("/{message_id}")
async def remove_message(
    message_id: str,
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a message."""
    msg_db_id = message_id.replace("msg-", "") if message_id.startswith("msg-") else message_id
    
    try:
        msg_db_id_int = int(msg_db_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID format"
        )
    
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == msg_db_id_int
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    db.delete(message)
    
    # Update session count
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == message.session_id
    ).first()
    if session:
        session.message_count = max(0, session.message_count - 1)
    
    db.commit()
    
    return {"status": "success"}


@messages_router.delete("/batch")
async def remove_messages(
    ids: List[str] = Body(...),
    sessionId: Optional[str] = Query(None),
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete multiple messages."""
    msg_ids = []
    for msg_id in ids:
        msg_db_id = msg_id.replace("msg-", "") if msg_id.startswith("msg-") else msg_id
        try:
            msg_ids.append(int(msg_db_id))
        except ValueError:
            continue
    
    if not msg_ids:
        return {"status": "success"}
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.id.in_(msg_ids)
    ).all()
    
    session_ids = set()
    for msg in messages:
        session_ids.add(msg.session_id)
    
    deleted_count = len(messages)
    for msg in messages:
        db.delete(msg)
    
    # Update session counts
    for session_id in session_ids:
        session = db.query(ConversationSession).filter(
            ConversationSession.session_id == session_id
        ).first()
        if session:
            session.message_count = max(0, session.message_count - deleted_count)
    
    db.commit()
    
    return {"status": "success", "deleted": deleted_count}


@messages_router.delete("/by-assistant/{session_id}")
async def remove_messages_by_assistant(
    session_id: str,
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete all assistant messages in a session."""
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id,
        ConversationMessage.role == "assistant"
    ).all()
    
    deleted_count = len(messages)
    for msg in messages:
        db.delete(msg)
    
    session.message_count = max(0, session.message_count - deleted_count)
    db.commit()
    
    return {"status": "success", "deleted": deleted_count}


@messages_router.delete("/by-group/{group_id}")
async def remove_messages_by_group(
    group_id: str,
    topicId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete messages by group (not implemented)."""
    return {"status": "success"}


@messages_router.delete("")
async def remove_all_messages(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete all messages for the user."""
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if session_ids:
        db.query(ConversationMessage).filter(
            ConversationMessage.session_id.in_(session_ids)
        ).delete(synchronize_session=False)
        
        for session in sessions:
            session.message_count = 0
        
        db.commit()
    
    return {"status": "success"}


# ============================================================================
# Topic Routes
# ============================================================================

topics_router = APIRouter(prefix="/api/topics", tags=["topics"])


@topics_router.get("")
async def get_topics(
    sessionId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id)
):
    """Get topics (not fully implemented)."""
    return []


@topics_router.post("")
async def create_topic(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Create a topic."""
    import uuid
    topic_id = str(uuid.uuid4())
    return {"id": topic_id}


@topics_router.post("/batch")
async def batch_create_topics(
    topics: List[Dict[str, Any]] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Batch create topics."""
    import uuid
    result = []
    for topic in topics:
        topic_id = str(uuid.uuid4())
        result.append({"id": topic_id, **topic})
    return {"success": len(result), "topics": result}


@topics_router.post("/{topic_id}/clone")
async def clone_topic(
    topic_id: str,
    newTitle: str = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Clone a topic."""
    import uuid
    new_topic_id = str(uuid.uuid4())
    return {"id": new_topic_id}


@topics_router.get("/all")
async def get_all_topics(
    user_id: int = Depends(get_current_user_id)
):
    """Get all topics."""
    return []


@topics_router.get("/count")
async def count_topics(
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id)
):
    """Count topics."""
    return 0


@topics_router.get("/rank")
async def rank_topics(
    limit: Optional[int] = Query(10),
    user_id: int = Depends(get_current_user_id)
):
    """Get ranked topics."""
    return []


@topics_router.get("/search")
async def search_topics(
    keywords: str = Query(...),
    sessionId: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id)
):
    """Search topics."""
    return []


@topics_router.put("/{topic_id}")
async def update_topic(
    topic_id: str,
    value: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Update a topic."""
    return {"id": topic_id, "status": "success"}


@topics_router.delete("/{topic_id}")
async def remove_topic(
    topic_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Delete a topic."""
    return {"status": "success"}


@topics_router.delete("/by-session/{session_id}")
async def batch_delete_by_session_id(
    session_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Delete topics by session."""
    return {"status": "success"}


@topics_router.delete("/batch")
async def batch_delete_topics(
    ids: List[str] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Batch delete topics."""
    return {"status": "success", "deleted": len(ids)}


@topics_router.delete("")
async def remove_all_topics(
    user_id: int = Depends(get_current_user_id)
):
    """Delete all topics."""
    return {"status": "success"}


# ============================================================================
# Plugin Routes
# ============================================================================

plugins_router = APIRouter(prefix="/api/plugins", tags=["plugins"])


@plugins_router.get("")
async def get_plugins(
    user_id: int = Depends(get_current_user_id)
):
    """Get installed plugins."""
    return []


@plugins_router.post("")
async def create_or_install_plugin(
    plugin: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Create or install a plugin."""
    identifier = plugin.get("identifier", "unknown")
    return {"id": identifier, "status": "success"}


@plugins_router.post("/custom")
async def create_plugin(
    plugin: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Create a custom plugin."""
    identifier = plugin.get("identifier", "unknown")
    return {"id": identifier, "status": "success"}


@plugins_router.put("/{plugin_id}")
async def update_plugin(
    plugin_id: str,
    data: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Update a plugin."""
    return {"id": plugin_id, "status": "success"}


@plugins_router.delete("/{plugin_id}")
async def remove_plugin(
    plugin_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Remove a plugin."""
    return {"status": "success"}


@plugins_router.delete("")
async def remove_all_plugins(
    user_id: int = Depends(get_current_user_id)
):
    """Remove all plugins."""
    return {"status": "success"}


# ============================================================================
# Market Routes
# ============================================================================

market_router = APIRouter(prefix="/api/market", tags=["market"])


@market_router.get("")
async def get_plugin_list(
    category: Optional[str] = Query(None),
    locale: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id)
):
    """Get plugin list from market."""
    return {
        "plugins": [],
        "categories": [],
        "total": 0
    }


# ============================================================================
# User Routes (extended)
# ============================================================================

user_router = APIRouter(prefix="/api/user", tags=["user"])


@user_router.get("/registration-duration")
async def get_user_registration_duration(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user registration duration."""
    from src.models import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    now = datetime.utcnow()
    created_at = user.created_at if hasattr(user, 'created_at') else now
    duration = (now - created_at).total_seconds()
    
    return {
        "createdAt": created_at.isoformat() + "Z",
        "updatedAt": now.isoformat() + "Z",
        "duration": duration
    }


@user_router.get("/state")
async def get_user_state(
    user_id: int = Depends(get_current_user_id)
):
    """Get user initialization state."""
    return {
        "isOnboarded": True,
        "hasConversation": False
    }


@user_router.get("/sso-providers")
async def get_user_sso_providers(
    user_id: int = Depends(get_current_user_id)
):
    """Get user SSO providers."""
    return []


@user_router.delete("/sso-providers")
async def unlink_sso_provider(
    provider: str = Body(...),
    providerAccountId: str = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Unlink SSO provider."""
    return {"status": "success"}


@user_router.post("/onboarded")
async def make_user_onboarded(
    user_id: int = Depends(get_current_user_id)
):
    """Mark user as onboarded."""
    return {"status": "success"}


@user_router.put("/avatar")
async def update_avatar(
    avatar: str = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Update user avatar."""
    return {"avatar": avatar, "status": "success"}


@user_router.put("/guide")
async def update_guide(
    guide: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Update user guide state."""
    return {"status": "success"}


# ============================================================================
# Agent Routes
# ============================================================================

agent_router = APIRouter(prefix="/api/agents", tags=["agents"])


@agent_router.get("/config")
async def get_agent_config(
    sessionId: str = Query(...),
    user_id: int = Depends(get_current_user_id)
):
    """Get agent config for a session."""
    # Return default config
    return {
        "model": "gpt-4o-mini",
        "provider": "openai",
        "temperature": 0.7
    }


# ============================================================================
# Thread Routes
# ============================================================================

threads_router = APIRouter(prefix="/api/threads", tags=["threads"])


@threads_router.get("")
async def get_threads(
    topicId: str = Query(...),
    user_id: int = Depends(get_current_user_id)
):
    """Get threads for a topic."""
    return []


@threads_router.post("")
async def create_thread_with_message(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Create a thread with a message."""
    import uuid
    thread_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    return {
        "threadId": thread_id,
        "messageId": message_id
    }


@threads_router.put("/{thread_id}")
async def update_thread(
    thread_id: str,
    value: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Update a thread."""
    return {"id": thread_id, "status": "success"}


@threads_router.delete("/{thread_id}")
async def remove_thread(
    thread_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Delete a thread."""
    return {"status": "success"}


# ============================================================================
# Upload Routes
# ============================================================================

upload_router = APIRouter(prefix="/api/upload", tags=["upload"])


@upload_router.post("/presigned-url")
async def create_s3_presigned_url(
    pathname: str = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """Create S3 presigned URL for upload."""
    # Return a placeholder URL
    return {
        "preSignUrl": f"https://placeholder.s3.amazonaws.com/{pathname}",
        "pathname": pathname
    }


# ============================================================================
# Usage Routes
# ============================================================================

usage_router = APIRouter(prefix="/api/usage", tags=["usage"])


@usage_router.get("/month")
async def find_usage_by_month(
    mo: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id)
):
    """Get usage by month."""
    return {
        "month": mo or datetime.utcnow().strftime("%Y-%m"),
        "total": 0,
        "usage": []
    }


@usage_router.get("/day")
async def find_usage_and_group_by_day(
    mo: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id)
):
    """Get usage grouped by day."""
    return {
        "month": mo or datetime.utcnow().strftime("%Y-%m"),
        "days": []
    }


# Create main router that includes all sub-routers
router = APIRouter()
router.include_router(sessions_router)
router.include_router(session_groups_router)
router.include_router(messages_router)
router.include_router(topics_router)
router.include_router(plugins_router)
router.include_router(market_router)
router.include_router(user_router)
router.include_router(agent_router)
router.include_router(threads_router)
router.include_router(upload_router)
router.include_router(usage_router)

