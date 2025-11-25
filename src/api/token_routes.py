"""API routes for token management and billing."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from src.api.dependencies import get_db, get_current_user
from src.models import User, Plan, TokenUsageHistory
from src.services.token_service import TokenService


router = APIRouter(prefix="/api/tokens", tags=["Tokens & Billing"])


# Pydantic schemas
class PlanResponse(BaseModel):
    """Plan information response."""
    id: int
    name: str
    description: Optional[str]
    price_month: float
    price_year: float
    monthly_token_limit: int
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenUsageStatsResponse(BaseModel):
    """Token usage statistics response."""
    user_id: int
    plan: dict
    tokens: dict
    overage: dict
    period: dict
    cost: dict


class TokenHistoryResponse(BaseModel):
    """Token usage history response."""
    id: int
    model: str
    endpoint: Optional[str]
    session_id: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: Optional[float]
    request_metadata: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(
    db: Session = Depends(get_db)
):
    """
    List all available subscription plans.
    
    Returns:
        List of plans with pricing and token limits
    """
    plans = db.query(Plan).filter(Plan.is_active == True).order_by(Plan.price_month).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price_month": float(p.price_month),
            "price_year": float(p.price_year),
            "monthly_token_limit": p.monthly_token_limit,
            "is_active": p.is_active
        }
        for p in plans
    ]


@router.get("/usage", response_model=TokenUsageStatsResponse)
async def get_token_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's token usage statistics for the current month.
    
    Returns:
        - Plan information
        - Tokens used, remaining, and limit
        - Overage information
        - Cost information
    """
    token_service = TokenService(db)
    stats = token_service.get_user_usage_stats(current_user.id)
    return stats


@router.get("/history", response_model=List[TokenHistoryResponse])
async def get_token_history(
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's token usage history.
    
    Args:
        limit: Number of records to return (1-1000)
        offset: Number of records to skip
        session_id: Optional filter by session ID
        
    Returns:
        List of token usage records
    """
    query = db.query(TokenUsageHistory).filter(
        TokenUsageHistory.user_id == current_user.id
    )
    
    if session_id:
        query = query.filter(TokenUsageHistory.session_id == session_id)
    
    query = query.order_by(TokenUsageHistory.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    history = query.all()
    
    return [
        {
            "id": h.id,
            "model": h.model,
            "endpoint": h.endpoint,
            "session_id": h.session_id,
            "prompt_tokens": h.prompt_tokens,
            "completion_tokens": h.completion_tokens,
            "total_tokens": h.total_tokens,
            "cost_usd": float(h.cost_usd) if h.cost_usd else None,
            "request_metadata": h.request_metadata,
            "created_at": h.created_at
        }
        for h in history
    ]


@router.get("/check")
async def check_token_availability(
    estimated_tokens: int = Query(0, ge=0, description="Estimated tokens for request"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user has enough tokens available for a request.
    
    Args:
        estimated_tokens: Estimated tokens needed for the request
        
    Returns:
        Availability information including tokens remaining and overage status
        
    Raises:
        HTTPException 429: If token limit exceeded (including overage)
    """
    token_service = TokenService(db)
    availability = token_service.check_token_availability(
        current_user.id,
        estimated_tokens
    )
    return availability

