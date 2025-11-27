"""User preferences API routes."""

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from src.api.dependencies import get_db, get_current_user, get_current_user_id
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
    
    Returns user details including preferences and avatar.
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "avatar_url": current_user.avatar_url,
        "occupation": current_user.occupation,
        "bio": current_user.bio,
        "preferences": current_user.preferences or {},
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
    }


@router.put("/profile")
async def update_user_profile(
    profile_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    
    **Note:** Email cannot be changed through this endpoint.
    
    **Request Body:**
    ```json
    {
        "name": "João Silva",
        "occupation": "Desenvolvedor de Software",
        "bio": "Interesses, valores ou preferências a serem lembrados"
    }
    ```
    
    All fields are optional - only provided fields will be updated.
    """
    # Update name if provided
    if "name" in profile_data and profile_data["name"] is not None:
        current_user.name = profile_data["name"]
    
    # Update occupation if provided
    if "occupation" in profile_data:
        current_user.occupation = profile_data.get("occupation")
    
    # Update bio if provided
    if "bio" in profile_data:
        current_user.bio = profile_data.get("bio")
    
    # Commit changes
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "avatar_url": current_user.avatar_url,
        "occupation": current_user.occupation,
        "bio": current_user.bio,
        "preferences": current_user.preferences or {},
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
    }


@router.put("/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update user avatar by uploading an image file.
    
    **Security:** Users can only upload avatars for themselves.
    The user_id is automatically extracted from the JWT token.
    
    **Supported formats:** jpg, jpeg, png, gif, webp
    **Max file size:** 5MB
    
    **Example Request:**
    ```
    PUT /api/user/avatar
    Content-Type: multipart/form-data
    
    file: [binary image data]
    ```
    
    **Example Response:**
    ```json
    {
        "avatar_url": "/uploads/avatars/user_123_abc123.jpg",
        "status": "success"
    }
    ```
    """
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed size of 5MB"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create uploads directory if it doesn't exist
    # Use absolute path to avoid permission issues
    uploads_dir = Path("/app/uploads/avatars")
    try:
        uploads_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    except PermissionError:
        # Fallback to relative path if absolute fails
        uploads_dir = Path("uploads/avatars")
        uploads_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    
    # Generate unique filename
    unique_filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = uploads_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Delete old avatar file if it exists
    if user.avatar_url:
        old_file_path = Path(user.avatar_url.lstrip('/'))
        if old_file_path.exists() and old_file_path.is_file():
            try:
                old_file_path.unlink()
            except Exception:
                pass  # Ignore errors when deleting old file
    
    # Update user avatar_url in database
    # Store relative path from project root
    avatar_url = f"/uploads/avatars/{unique_filename}"
    user.avatar_url = avatar_url
    
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        # If database update fails, delete the uploaded file
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user avatar: {str(e)}"
        )
    
    return {
        "avatar_url": avatar_url,
        "status": "success"
    }

