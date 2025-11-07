"""Authentication utilities."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from src.models import User
from src.config import Config

# JWT settings
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user_by_email(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def authenticate_user(db: Session, name: str, password: str) -> Optional[User]:
    """Authenticate a user by name (legacy, kept for compatibility)."""
    user = db.query(User).filter(User.name == name).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def get_user_by_name(db: Session, name: str) -> Optional[User]:
    """Get user by name."""
    return db.query(User).filter(User.name == name).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, name: str, email: str, password: str) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(password)
    db_user = User(
        name=name,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def generate_password_reset_token() -> str:
    """Generate a secure random token for password reset."""
    import secrets
    return secrets.token_urlsafe(32)


def create_password_reset_token(db: Session, user_id: int, expires_hours: int = 24) -> str:
    """
    Create a password reset token for a user.
    
    Args:
        db: Database session
        user_id: User ID
        expires_hours: Hours until token expires (default: 24)
    
    Returns:
        The generated token string
    """
    from src.models import PasswordResetToken
    
    # Generate token
    token = generate_password_reset_token()
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
    
    # Create token record
    reset_token = PasswordResetToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    
    return token


def get_password_reset_token(db: Session, token: str) -> Optional['PasswordResetToken']:
    """
    Get a password reset token if it's valid and not expired.
    
    Args:
        db: Database session
        token: Token string
    
    Returns:
        PasswordResetToken if valid, None otherwise
    """
    from src.models import PasswordResetToken
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    return reset_token


def mark_password_reset_token_as_used(db: Session, token: str) -> bool:
    """
    Mark a password reset token as used.
    
    Args:
        db: Database session
        token: Token string
    
    Returns:
        True if token was marked as used, False otherwise
    """
    from src.models import PasswordResetToken
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()
    
    if reset_token:
        reset_token.used = True
        db.commit()
        return True
    
    return False


def update_user_password(db: Session, user_id: int, new_password: str) -> bool:
    """
    Update a user's password.
    
    Args:
        db: Database session
        user_id: User ID
        new_password: New password (plain text)
    
    Returns:
        True if password was updated, False otherwise
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return True

