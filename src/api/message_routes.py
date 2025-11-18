"""Message-specific API routes for advanced features."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from src.database import get_db
from src.api.dependencies import get_current_user_id
from src.models_conversation import ConversationMessage, ConversationSession
from src.api.helpers import create_error_response
from src.api.schemas import Message

router = APIRouter(prefix="/api/messages", tags=["messages"])


class MessageStatsResponse(BaseModel):
    """Response for message statistics."""
    total_messages: int
    total_words: int
    messages_today: int
    words_today: int


class ModelRankItem(BaseModel):
    """Model ranking item."""
    model: str
    count: int
    rank: int


class HeatmapItem(BaseModel):
    """Heatmap data item."""
    date: str
    count: int




@router.get("/stats", response_model=MessageStatsResponse)
async def get_message_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get message statistics for the user.
    
    Returns counts and word statistics for messages.
    """
    # Get user's sessions
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if not session_ids:
        return MessageStatsResponse(
            total_messages=0,
            total_words=0,
            messages_today=0,
            words_today=0
        )
    
    # Build query
    query = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids)
    )
    
    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(ConversationMessage.created_at >= start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date) + timedelta(days=1)
            query = query.filter(ConversationMessage.created_at < end_dt)
        except:
            pass
    
    # Get all messages
    messages = query.all()
    
    # Calculate statistics
    total_messages = len(messages)
    total_words = sum(len(msg.content.split()) for msg in messages)
    
    # Today's statistics
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_messages = [msg for msg in messages if msg.created_at >= today_start]
    messages_today = len(today_messages)
    words_today = sum(len(msg.content.split()) for msg in today_messages)
    
    return MessageStatsResponse(
        total_messages=total_messages,
        total_words=total_words,
        messages_today=messages_today,
        words_today=words_today
    )


@router.get("/models/rank", response_model=List[ModelRankItem])
async def get_model_rankings(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get ranking of most used models.
    
    Returns models sorted by usage count.
    """
    # Get user's sessions
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if not session_ids:
        return []
    
    # Get all assistant messages with model metadata
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids),
        ConversationMessage.role == "assistant"
    ).all()
    
    # Count models
    model_counts: Dict[str, int] = {}
    for msg in messages:
        if msg.message_metadata and isinstance(msg.message_metadata, dict):
            model = msg.message_metadata.get("model")
            if model:
                model_counts[model] = model_counts.get(model, 0) + 1
    
    # Sort by count and create ranking
    sorted_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for rank, (model, count) in enumerate(sorted_models, start=1):
        result.append(ModelRankItem(
            model=model,
            count=count,
            rank=rank
        ))
    
    return result


@router.get("/heatmap", response_model=List[HeatmapItem])
async def get_message_heatmap(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get message activity heatmap data.
    
    Returns daily message counts for the last 30 days.
    """
    # Get user's sessions
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id,
        ConversationSession.is_active == True
    ).all()
    
    session_ids = [s.session_id for s in sessions]
    
    if not session_ids:
        return []
    
    # Get messages from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids),
        ConversationMessage.created_at >= thirty_days_ago
    ).all()
    
    # Group by date
    date_counts: Dict[str, int] = {}
    for msg in messages:
        date_key = msg.created_at.strftime("%Y-%m-%d")
        date_counts[date_key] = date_counts.get(date_key, 0) + 1
    
    # Convert to list
    result = [
        HeatmapItem(date=date, count=count)
        for date, count in sorted(date_counts.items())
    ]
    
    return result



