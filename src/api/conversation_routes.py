"""Conversation and session API routes."""

import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from pydantic import BaseModel
from datetime import datetime
from src.database import get_db
from src.hybrid_conversation_service import HybridConversationService
from src.api.schemas import ConversationHistory, SessionInfo, MessageCreate, Message
from src.api.dependencies import get_current_user_id
from src.api.di import get_chat_with_agent_use_case, get_get_user_agents_use_case
from src.application.use_cases.agents import ChatWithAgentUseCase, GetUserAgentsUseCase
from src.models_conversation import ConversationSession, ConversationMessage
from src.api.helpers import create_error_response

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class SessionsResponse(BaseModel):
    """Response model for paginated sessions."""
    sessions: List[str]
    total: int
    limit: int
    offset: int
    has_more: bool


@router.get("/sessions", response_model=SessionsResponse)
async def get_user_sessions(
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get paginated session IDs for the current user."""
    sessions, total = HybridConversationService.get_user_sessions(
        user_id=user_id,
        db=db,
        limit=limit,
        offset=offset
    )
    # Calculate has_more: true if there are more sessions beyond current page
    has_more = (offset + len(sessions)) < total
    
    return SessionsResponse(
        sessions=sessions,
        total=total,
        limit=limit or 20,
        offset=offset,
        has_more=has_more
    )


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


# ============================================================================
# New endpoints for LobeChat compatibility
# ============================================================================

class SessionChatRequest(BaseModel):
    """Request for session chat endpoint."""
    message: str
    model: Optional[str] = None
    provider: Optional[str] = None
    files: Optional[List[str]] = None
    parent_id: Optional[str] = None
    topic_id: Optional[str] = None
    create_new_topic: Optional[bool] = False
    agent_id: Optional[int] = None  # Optional agent ID to use for this chat


class SessionChatResponse(BaseModel):
    """Response for session chat endpoint."""
    user_message_id: str
    assistant_message_id: str
    session_id: str
    topic_id: Optional[str] = None
    is_create_new_topic: bool = False
    messages: List[Message]
    topics: List[Dict[str, Any]] = []


class SessionUpdateRequest(BaseModel):
    """Request for updating session metadata."""
    title: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    pinned: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/sessions/{session_id}/chat", response_model=SessionChatResponse)
async def chat_in_session(
    session_id: str,
    request: SessionChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    chat_use_case: ChatWithAgentUseCase = Depends(get_chat_with_agent_use_case),
    get_user_agents_use_case: GetUserAgentsUseCase = Depends(get_get_user_agents_use_case)
):
    """
    Send a message in a session and get complete response with message IDs.
    
    Compatible with LobeChat's aiChat.sendMessageInServer functionality.
    Creates both user and assistant messages and returns them with IDs.
    
    If the session doesn't exist, it will be created automatically.
    This allows the frontend to use temporary session IDs that get created on first message.
    """
    # Get or create session - if it doesn't exist, create it automatically
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        # Create session automatically if it doesn't exist
        # This handles temporary session IDs from the frontend
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            message_count=0,
            is_active=True,
            session_metadata={}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Get agent ID - use from request, or first user agent, or default agent (ID 1)
    agent_id = request.agent_id
    
    if not agent_id:
        # Try to get first agent from user's agents
        agents = get_user_agents_use_case.execute(user_id)
        if agents:
            agent_id = agents[0].id
    
    # If still no agent_id, use default agent (ID 1)
    # This allows the frontend to work without explicitly creating agents
    if not agent_id:
        agent_id = 1  # Default agent ID
    
    # Verify agent exists and belongs to user (or is default agent)
    if agent_id != 1:  # Skip verification for default agent
        from src.models import Agent
        agent = db.query(Agent).filter(
            Agent.id == agent_id,
            Agent.user_id == user_id
        ).first()
        if not agent:
            # Fallback to default agent if specified agent doesn't exist
            agent_id = 1
    
    # Generate message IDs
    user_message_id = f"msg-{uuid.uuid4()}"
    assistant_message_id = f"msg-{uuid.uuid4()}"
    
    # Prepare metadata for user message
    user_metadata = {
        "files": request.files or [],
        "parent_id": request.parent_id
    }
    if request.topic_id:
        user_metadata["topic_id"] = request.topic_id
    
    # Add user message
    HybridConversationService.add_user_message(
        user_id=user_id,
        session_id=session_id,
        content=request.message,
        metadata=user_metadata,
        db=db
    )
    
    # Get model to use
    model_name = request.model or (agents[0].model if agents else "gemini-2.0-flash-exp")
    provider_name = request.provider or model_name.split("/")[0] if "/" in model_name else "openai"
    
    # Execute chat
    try:
        response_content = await chat_use_case.execute(
            user_id=user_id,
            agent_id=agent_id,
            message=request.message,
            session_id=session_id,
            model_override=request.model
        )
    except Exception as e:
        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error generating response: {str(e)}"
        )
    
    # Add assistant message with metadata
    assistant_metadata = {
        "model": model_name,
        "provider": provider_name
    }
    HybridConversationService.add_assistant_message(
        user_id=user_id,
        session_id=session_id,
        content=response_content,
        metadata=assistant_metadata,
        db=db
    )
    
    # Get updated messages
    history = HybridConversationService.get_conversation_history(
        user_id=user_id,
        session_id=session_id,
        limit=100,
        db=db
    )
    
    # Convert to Message objects
    messages = []
    for msg_dict in history[-2:]:  # Last 2 messages (user + assistant)
        msg_data = {
            "id": msg_dict.get("id") or (user_message_id if msg_dict.get("role") == "user" else assistant_message_id),
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
    
    # Handle topics (placeholder - topics not fully implemented)
    topics = []
    if request.create_new_topic and request.topic_id:
        topics.append({
            "id": request.topic_id,
            "title": request.message[:50],
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat() + "Z"
        })
    
    return SessionChatResponse(
        user_message_id=user_message_id,
        assistant_message_id=assistant_message_id,
        session_id=session_id,
        topic_id=request.topic_id if request.create_new_topic else None,
        is_create_new_topic=request.create_new_topic or False,
        messages=messages,
        topics=topics
    )


@router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update session metadata (title, description, avatar, pinned, etc.).
    
    Compatible with LobeChat session update functionality.
    """
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Session not found"
        )
    
    # Update metadata if provided
    metadata = session.session_metadata or {}
    
    if request.title is not None:
        metadata["title"] = request.title
    if request.description is not None:
        metadata["description"] = request.description
    if request.avatar is not None:
        metadata["avatar"] = request.avatar
    if request.pinned is not None:
        metadata["pinned"] = request.pinned
    if request.metadata:
        metadata.update(request.metadata)
    
    session.session_metadata = metadata
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session_id,
        "title": metadata.get("title") or f"Session {session_id[:8]}",
        "description": metadata.get("description"),
        "avatar": metadata.get("avatar"),
        "pinned": metadata.get("pinned", False),
        "updated_at": session.updated_at.isoformat() + "Z"
    }


@router.get("/sessions/search")
async def search_sessions(
    keywords: str = Query(..., description="Search keywords"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Search sessions by keywords (title, description, message content).
    
    Compatible with LobeChat session search functionality.
    """
    if not keywords or len(keywords.strip()) < 2:
        return []
    
    keywords_lower = keywords.lower().strip()
    
    # Get all user sessions
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    matching_sessions = []
    
    for session in sessions:
        # Search in messages
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.session_id
        ).limit(10).all()
        
        # Check if keywords match any message content
        matches = False
        for msg in messages:
            if keywords_lower in msg.content.lower():
                matches = True
                break
        
        if matches:
            info = HybridConversationService.get_session_info(user_id, session.session_id, db=db)
            matching_sessions.append({
                "session_id": session.session_id,
                "title": f"Session {session.session_id[:8]}",
                "description": None,
                "last_activity": session.last_activity.isoformat() + "Z" if session.last_activity else None,
                "message_count": session.message_count
            })
    
    return matching_sessions


# ============================================================================
# Message CRUD endpoints
# ============================================================================

class MessageUpdateRequest(BaseModel):
    """Request for updating a message."""
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BulkDeleteRequest(BaseModel):
    """Request for bulk deleting messages."""
    message_ids: List[str]
    delete_assistant_only: Optional[bool] = False


@router.put("/sessions/{session_id}/messages/{message_id}")
async def update_message(
    session_id: str,
    message_id: str,
    request: MessageUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a message in a session.
    
    Updates content and/or metadata of a specific message.
    Compatible with LobeChat message update functionality.
    """
    # Verify session belongs to user
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Session not found"
        )
    
    # Extract message ID from format "msg-{id}" or use as-is
    msg_db_id = message_id.replace("msg-", "") if message_id.startswith("msg-") else message_id
    
    try:
        msg_db_id_int = int(msg_db_id)
    except ValueError:
        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid message ID format"
        )
    
    # Get message
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == msg_db_id_int,
        ConversationMessage.session_id == session_id
    ).first()
    
    if not message:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Message not found"
        )
    
    # Update fields
    if request.content is not None:
        message.content = request.content
    
    if request.metadata is not None:
        current_metadata = message.message_metadata or {}
        current_metadata.update(request.metadata)
        message.message_metadata = current_metadata
    
    db.commit()
    db.refresh(message)
    
    return {
        "id": f"msg-{message.id}",
        "content": message.content,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }


@router.delete("/sessions/{session_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    session_id: str,
    message_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a specific message from a session.
    
    Compatible with LobeChat message deletion functionality.
    """
    # Verify session belongs to user
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Session not found"
        )
    
    # Extract message ID
    msg_db_id = message_id.replace("msg-", "") if message_id.startswith("msg-") else message_id
    
    try:
        msg_db_id_int = int(msg_db_id)
    except ValueError:
        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid message ID format"
        )
    
    # Get and delete message
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == msg_db_id_int,
        ConversationMessage.session_id == session_id
    ).first()
    
    if not message:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Message not found"
        )
    
    db.delete(message)
    session.message_count = max(0, session.message_count - 1)
    db.commit()


@router.delete("/sessions/{session_id}/messages", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multiple_messages(
    session_id: str,
    request: BulkDeleteRequest = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete multiple messages from a session.
    
    Supports filtering by delete_assistant_only flag.
    Compatible with LobeChat bulk message deletion functionality.
    """
    # Verify session belongs to user
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id,
        ConversationSession.user_id == user_id
    ).first()
    
    if not session:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Session not found"
        )
    
    # Extract message IDs
    msg_ids = []
    for msg_id in request.message_ids:
        msg_db_id = msg_id.replace("msg-", "") if msg_id.startswith("msg-") else msg_id
        try:
            msg_ids.append(int(msg_db_id))
        except ValueError:
            continue
    
    if not msg_ids:
        return
    
    # Build query
    query = db.query(ConversationMessage).filter(
        ConversationMessage.id.in_(msg_ids),
        ConversationMessage.session_id == session_id
    )
    
    # Filter by role if delete_assistant_only
    if request.delete_assistant_only:
        query = query.filter(ConversationMessage.role == "assistant")
    
    # Delete messages
    deleted_count = query.delete(synchronize_session=False)
    
    # Update session count
    session.message_count = max(0, session.message_count - deleted_count)
    db.commit()

