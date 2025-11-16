"""User preferences API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.api.dependencies import get_db, get_current_user
from src.api.schemas import UserPreferences, UserPreferencesUpdate
from src.models import User

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/preferences", response_model=Dict[str, Any])
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's preferences.
    
    Returns the user's preferences as a JSON object.
    If no preferences are set, returns an empty object.
    
    **Example Response:**
    ```json
    {
      "theme": "dark",
      "language": "pt-BR",
      "layout": "compact",
      "notifications": true,
      "sidebar_expanded": false,
      "message_sound": true,
      "font_size": "medium"
    }
    ```
    """
    # Return preferences or empty dict if None
    return current_user.preferences or {}


@router.put("/preferences", response_model=Dict[str, Any])
async def update_user_preferences(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences.
    
    This endpoint accepts a JSON object with any preferences.
    It will merge the new preferences with existing ones.
    
    **Common Preferences:**
    - `theme`: "light", "dark", "auto"
    - `language`: "en", "pt-BR", "es", etc
    - `layout`: "default", "compact", "comfortable"
    - `notifications`: boolean
    - `sidebar_expanded`: boolean
    - `message_sound`: boolean
    - `font_size`: "small", "medium", "large"
    
    **Example Request:**
    ```json
    {
      "theme": "dark",
      "language": "pt-BR",
      "layout": "compact"
    }
    ```
    
    **Example Response:**
    ```json
    {
      "theme": "dark",
      "language": "pt-BR",
      "layout": "compact",
      "notifications": true,
      "sidebar_expanded": false
    }
    ```
    
    Returns the updated preferences object.
    """
    # Get current preferences
    current_prefs = current_user.preferences or {}
    
    # Merge new preferences with existing ones
    updated_prefs = {**current_prefs, **preferences}
    
    # Update user preferences
    current_user.preferences = updated_prefs
    
    # Commit changes
    db.commit()
    db.refresh(current_user)
    
    return current_user.preferences


@router.delete("/preferences")
async def reset_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset user preferences to default (empty object).
    
    This will clear all user preferences.
    """
    # Reset preferences to empty dict
    current_user.preferences = {}
    
    # Commit changes
    db.commit()
    
    return {"message": "Preferences reset successfully"}


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information.
    
    Returns user details including preferences.
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "preferences": current_user.preferences or {},
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
    }

