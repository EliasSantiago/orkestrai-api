"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.database import get_db
from src.api.schemas import (
    UserCreate, UserResponse, Token, LoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)
from src.auth import (
    authenticate_user_by_email,
    create_user,
    create_access_token,
    get_user_by_name,
    get_user_by_email,
    SECRET_KEY,
    ALGORITHM,
    create_password_reset_token,
    get_password_reset_token,
    mark_password_reset_token_as_used,
    update_user_password
)
from src.config import Config
from src.email_service import send_password_reset_email
from urllib.parse import urlencode

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Validate password confirmation
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if name already exists
    if get_user_by_name(db, user_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = create_user(
        db=db,
        name=user_data.name,
        email=user_data.email,
        password=user_data.password
    )
    
    return user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token using email and password.
    
    Accepts JSON payload with email and password.
    """
    user = authenticate_user_by_email(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    from jose import jwt
    from src.auth import SECRET_KEY, ALGORITHM
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Token contains email as 'sub' (subject)
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None and user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Try to get user by email first, then by user_id
        if email:
            user = get_user_by_email(db, email)
        elif user_id:
            from src.models import User
            user = db.query(User).filter(User.id == user_id).first()
        else:
            user = None
            
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset.
    
    Sends an email with a password reset link to the user.
    For security reasons, always returns success even if email doesn't exist.
    """
    # Find user by email
    user = get_user_by_email(db, request.email)
    
    # Always return success to prevent email enumeration attacks
    # Only proceed if user exists
    if user and user.is_active:
        # Create password reset token
        token = create_password_reset_token(
            db=db,
            user_id=user.id,
            expires_hours=Config.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        
        # Build reset URL with token and email as query parameters
        reset_params = urlencode({
            "token": token,
            "email": request.email
        })
        reset_url = f"{Config.PASSWORD_RESET_BASE_URL}/reset-password?{reset_params}"
        
        # Send email
        email_sent = send_password_reset_email(
            email=user.email,
            reset_token=token,
            reset_url=reset_url
        )
        
        if not email_sent:
            # Log warning but don't expose to user
            print(f"⚠ Failed to send password reset email to {user.email}")
    
    # Always return success message
    return {
        "message": "If the email exists, a password reset link has been sent.",
        "status": "success"
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email.
    
    Requires:
    - token: Password reset token from email
    - email: User's email address
    - new_password: New password
    - password_confirm: Confirmation of new password
    """
    # Validate token
    reset_token = get_password_reset_token(db, request.token)
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Verify email matches token's user
    user = get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if reset_token.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not match email address"
        )
    
    # Update password
    success = update_user_password(db, user.id, request.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    # Mark token as used
    mark_password_reset_token_as_used(db, request.token)
    
    return {
        "message": "Password has been reset successfully",
        "status": "success"
    }

