"""Token management service using LiteLLM for token counting and cost calculation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import litellm
from litellm import completion_cost, token_counter

from src.models import User, Plan, UserTokenBalance, TokenUsageHistory
from src.api.exceptions import HTTPException


class TokenService:
    """Service for managing user token balances and usage tracking."""
    
    OVERAGE_TOKENS = 500  # Allow 500 extra tokens to finish tasks
    
    def __init__(self, db: Session):
        """Initialize token service with database session."""
        self.db = db
    
    def get_user_with_plan(self, user_id: int) -> tuple[User, Plan, UserTokenBalance]:
        """
        Get user with their plan and token balance.
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (User, Plan, UserTokenBalance)
            
        Raises:
            HTTPException: If user not found or plan not assigned
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.plan_id:
            # Assign free plan if not assigned
            free_plan = self.db.query(Plan).filter(Plan.name == "free").first()
            if free_plan:
                user.plan_id = free_plan.id
                self.db.commit()
                self.db.refresh(user)
        
        plan = self.db.query(Plan).filter(Plan.id == user.plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found for user")
        
        # Get or create token balance for current month
        balance = self._get_or_create_balance(user_id)
        
        return user, plan, balance
    
    def _get_or_create_balance(self, user_id: int) -> UserTokenBalance:
        """Get or create token balance for current month."""
        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year
        
        balance = self.db.query(UserTokenBalance).filter(
            UserTokenBalance.user_id == user_id
        ).first()
        
        if not balance:
            # Create new balance
            balance = UserTokenBalance(
                user_id=user_id,
                tokens_used_this_month=0,
                month=current_month,
                year=current_year,
                last_reset_at=now
            )
            self.db.add(balance)
            self.db.commit()
            self.db.refresh(balance)
        elif balance.month != current_month or balance.year != current_year:
            # Reset balance for new month
            balance.tokens_used_this_month = 0
            balance.month = current_month
            balance.year = current_year
            balance.last_reset_at = now
            self.db.commit()
            self.db.refresh(balance)
        
        return balance
    
    def check_token_availability(
        self,
        user_id: int,
        estimated_tokens: int = 0
    ) -> Dict[str, Any]:
        """
        Check if user has enough tokens available.
        
        Args:
            user_id: User ID
            estimated_tokens: Estimated tokens for the request
            
        Returns:
            Dict with availability info: {
                "available": bool,
                "tokens_remaining": int,
                "tokens_used": int,
                "tokens_limit": int,
                "overage_used": int,
                "max_overage": int
            }
            
        Raises:
            HTTPException: If tokens exceeded (including overage)
        """
        user, plan, balance = self.get_user_with_plan(user_id)
        
        tokens_limit = plan.monthly_token_limit
        tokens_used = balance.tokens_used_this_month
        tokens_remaining = max(0, tokens_limit - tokens_used)
        max_overage = self.OVERAGE_TOKENS  # Fixed 500 tokens overage
        overage_used = max(0, tokens_used - tokens_limit)
        
        # Check if user exceeded limit including overage
        if tokens_used > tokens_limit + max_overage:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Token limit exceeded",
                    "message": f"Você atingiu o limite de tokens do seu plano ({plan.name}). "
                              f"Limite mensal: {tokens_limit:,} tokens. "
                              f"Usado: {tokens_used:,} tokens. "
                              f"Considere fazer upgrade para um plano superior.",
                    "tokens_used": tokens_used,
                    "tokens_limit": tokens_limit,
                    "plan": plan.name,
                    "overage_limit_reached": True
                }
            )
        
        return {
            "available": tokens_used + estimated_tokens <= tokens_limit + max_overage,
            "tokens_remaining": tokens_remaining,
            "tokens_used": tokens_used,
            "tokens_limit": tokens_limit,
            "overage_used": overage_used,
            "max_overage": max_overage,
            "plan": plan.name
        }
    
    def calculate_tokens_from_messages(
        self,
        messages: list,
        model: str
    ) -> int:
        """
        Calculate tokens from messages using LiteLLM.
        
        Args:
            messages: List of message dictionaries
            model: Model name
            
        Returns:
            Token count
        """
        try:
            return token_counter(model=model, messages=messages)
        except Exception as e:
            # Fallback: rough estimate (4 chars per token)
            total_chars = sum(len(str(msg.get("content", ""))) for msg in messages)
            return max(1, total_chars // 4)
    
    def calculate_cost_and_tokens(
        self,
        response: Any,
        model: str
    ) -> Dict[str, Any]:
        """
        Calculate cost and tokens from LLM response using LiteLLM.
        
        Args:
            response: LLM response object (OpenAI-compatible)
            model: Model name
            
        Returns:
            Dict with token and cost info: {
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int,
                "cost_usd": float
            }
        """
        try:
            # Try to get tokens from response
            if hasattr(response, "usage"):
                prompt_tokens = getattr(response.usage, "prompt_tokens", 0)
                completion_tokens = getattr(response.usage, "completion_tokens", 0)
                total_tokens = getattr(response.usage, "total_tokens", 0)
            else:
                # Fallback: calculate from response
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0
            
            # Calculate cost using LiteLLM
            try:
                cost_usd = completion_cost(completion_response=response)
                if cost_usd is None:
                    cost_usd = 0.0
            except Exception:
                cost_usd = 0.0
            
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost_usd": float(cost_usd)
            }
        except Exception as e:
            # Return zeros on error
            return {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0
            }
    
    def record_token_usage(
        self,
        user_id: int,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost_usd: float = 0.0,
        endpoint: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TokenUsageHistory:
        """
        Record token usage in history and update balance.
        
        Args:
            user_id: User ID
            model: Model name
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
            total_tokens: Total tokens
            cost_usd: Cost in USD
            endpoint: API endpoint called
            session_id: Session/conversation ID
            metadata: Additional metadata
            
        Returns:
            TokenUsageHistory record
        """
        # Create history record
        history = TokenUsageHistory(
            user_id=user_id,
            model=model,
            endpoint=endpoint,
            session_id=session_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=Decimal(str(cost_usd)) if cost_usd else None,
            request_metadata=metadata,
            created_at=datetime.utcnow()
        )
        self.db.add(history)
        
        # Update user balance
        balance = self._get_or_create_balance(user_id)
        balance.tokens_used_this_month += total_tokens
        balance.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(history)
        
        return history
    
    def get_user_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user usage statistics for current month.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with usage stats
        """
        user, plan, balance = self.get_user_with_plan(user_id)
        
        tokens_limit = plan.monthly_token_limit
        tokens_used = balance.tokens_used_this_month
        tokens_remaining = max(0, tokens_limit - tokens_used)
        max_overage = self.OVERAGE_TOKENS  # Fixed 500 tokens overage
        overage_used = max(0, tokens_used - tokens_limit)
        
        # Calculate percentage
        usage_percentage = min(100.0, (tokens_used / tokens_limit * 100) if tokens_limit > 0 else 0)
        
        # Get usage history for current month
        # Handle case where last_reset_at might be None
        if balance.last_reset_at:
            history = self.db.query(TokenUsageHistory).filter(
                TokenUsageHistory.user_id == user_id,
                TokenUsageHistory.created_at >= balance.last_reset_at
            ).all()
        else:
            # If no reset date, get all history for this user
            history = self.db.query(TokenUsageHistory).filter(
                TokenUsageHistory.user_id == user_id
            ).all()
        
        # Calculate total cost
        total_cost = sum(float(h.cost_usd or 0) for h in history)
        
        return {
            "user_id": user_id,
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "price_month": float(plan.price_month),
                "price_year": float(plan.price_year)
            },
            "tokens": {
                "limit": tokens_limit,
                "used": tokens_used,
                "remaining": tokens_remaining,
                "usage_percentage": round(usage_percentage, 2)
            },
            "overage": {
                "max_allowed": max_overage,
                "used": overage_used,
                "remaining": max(0, max_overage - overage_used)
            },
            "period": {
                "month": balance.month,
                "year": balance.year,
                "reset_date": balance.last_reset_at.isoformat() if balance.last_reset_at else None
            },
            "cost": {
                "total_usd": round(total_cost, 6),
                "requests_count": len(history)
            }
        }

