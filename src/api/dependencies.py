"""Shared dependencies for FastAPI routes.

This module centralizes common dependencies used across all routes,
eliminating code duplication and ensuring consistency.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.auth import SECRET_KEY, ALGORITHM
from src.database import get_db as _get_db
from src.models import User

security = HTTPBearer()


# Re-export get_db for convenience
def get_db():
    """Get database session."""
    yield from _get_db()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user.
    
    This is a shared dependency that extracts and validates the user
    from the JWT token and loads the full User object from database.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User object from database
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None and user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Try to get user by email first, then by user_id
        if email:
            user = db.query(User).filter(User.email == email).first()
        elif user_id:
            user = db.query(User).filter(User.id == user_id).first()
        else:
            user = None
            
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Get current user ID from JWT token.
    
    This is a shared dependency used across all protected routes.
    It extracts and validates the user_id from the JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If token is invalid, expired, or missing user_id
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

