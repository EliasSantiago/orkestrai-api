"""
Google Calendar OAuth 2.0 Flow Implementation.

This module implements the OAuth 2.0 flow for Google Calendar, allowing users to
authenticate and obtain OAuth tokens that work with the Google Calendar API.
"""

import logging
import httpx
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt
from urllib.parse import urlencode
from src.database import get_db
from src.models import MCPConnection
from src.config import Config
from src.auth import SECRET_KEY
from src.api.dependencies import get_current_user_id
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Router with the correct path structure
router = APIRouter(prefix="/api/mcp/google/calendar/oauth", tags=["google-calendar-oauth"])

# Additional router for backward compatibility (matches Google Cloud Console redirect URI)
# This handles the callback from Google which uses the path: /api/mcp/google_calendar/oauth/callback
legacy_router = APIRouter(prefix="/api/mcp/google_calendar/oauth", tags=["google-calendar-oauth"])

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def create_state_token(user_id: int) -> str:
    """Create a state token for OAuth flow security."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=10)  # 10 minute expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_state_token(state: str) -> Optional[int]:
    """Verify and extract user_id from state token."""
    try:
        payload = jwt.decode(state, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except Exception:
        return None


@router.get("/authorize")
async def authorize_google_calendar(
    user_id: int = Depends(get_current_user_id),
    request: Request = None
):
    """
    Initiate Google Calendar OAuth flow.
    
    This redirects the user to Google's authorization page where they can
    grant permissions to access their Google Calendar.
    
    **Note**: When called from Swagger UI, returns the authorization URL in JSON format.
    When called from a browser, redirects automatically to Google.
    
    **Response**: 
    - Browser: Redirects to Google OAuth consent screen (HTTP 302)
    - Swagger/API: Returns JSON with authorization URL
    """
    # Check if OAuth is configured
    if not Config.GOOGLE_CALENDAR_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Calendar OAuth not configured. Please set GOOGLE_CALENDAR_CLIENT_ID and GOOGLE_CALENDAR_CLIENT_SECRET in .env"
        )
    
    # Create state token for security
    state = create_state_token(user_id)
    
    # Build authorization URL
    # Use the redirect_uri that matches what's configured in Google Cloud Console
    # This should be the legacy path: /api/mcp/google_calendar/oauth/callback
    redirect_uri = Config.GOOGLE_CALENDAR_REDIRECT_URI
    # If config has the new path, use legacy path for compatibility with Google Cloud Console
    if "/google/calendar/" in redirect_uri:
        # Replace with legacy path
        redirect_uri = redirect_uri.replace("/google/calendar/", "/google_calendar/")
    
    params = {
        "client_id": Config.GOOGLE_CALENDAR_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",  # To get refresh_token
        "prompt": "consent",  # Force consent screen to show
        "state": state
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    logger.info(f"Initiating Google Calendar OAuth flow for user {user_id}")
    
    # Check if request is from Swagger UI (has 'accept: application/json' header)
    # or from a browser (will follow redirect)
    accept_header = request.headers.get("accept", "") if request else ""
    
    if "application/json" in accept_header.lower():
        # Return JSON for Swagger UI / API clients
        return {
            "status": "redirect_required",
            "message": "Please visit the authorization URL to complete OAuth flow",
            "authorization_url": auth_url,
            "instructions": "Open this URL in your browser to authorize Google Calendar access"
        }
    else:
        # Redirect for browser requests
        return RedirectResponse(url=auth_url, status_code=302)


async def oauth_callback_handler(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from Google.
    
    This endpoint receives the authorization code from Google and exchanges
    it for an access token and refresh token.
    
    **Query Parameters**:
    - `code`: Authorization code from Google (required if successful)
    - `state`: State token for security verification (required)
    - `error`: Error code if authorization failed (optional)
    - `error_description`: Error description if authorization failed (optional)
    
    **Response**: JSON with connection status or redirects to error page.
    """
    # Handle errors from Google
    if error:
        error_msg = error_description or error
        logger.error(f"OAuth error from Google: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": error,
                "error_description": error_msg,
                "message": "OAuth authorization failed. Please try again."
            }
        )
    
    # Verify state token
    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state parameter"
        )
    
    user_id = verify_state_token(state)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token"
        )
    
    # Verify authorization code
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code"
        )
    
    # Exchange code for access token
    try:
        async with httpx.AsyncClient(verify=Config.VERIFY_SSL) as client:
            # Exchange code for token
            # Use the same redirect_uri that was used in the authorization request
            # This must match exactly what was sent to Google
            redirect_uri = Config.GOOGLE_CALENDAR_REDIRECT_URI
            if "/google/calendar/" in redirect_uri:
                redirect_uri = redirect_uri.replace("/google/calendar/", "/google_calendar/")
            
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": Config.GOOGLE_CALENDAR_CLIENT_ID,
                    "client_secret": Config.GOOGLE_CALENDAR_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Token exchange failed: {response.status_code} - {error_text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange authorization code for token: {error_text}"
                )
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token in response from Google"
                )
            
            # Store connection in database
            credentials_dict = {
                "access_token": access_token,
                "refresh_token": refresh_token or "",
                "client_id": Config.GOOGLE_CALENDAR_CLIENT_ID,
                "client_secret": Config.GOOGLE_CALENDAR_CLIENT_SECRET
            }
            
            # Check if connection already exists
            existing = db.query(MCPConnection).filter(
                MCPConnection.user_id == user_id,
                MCPConnection.provider == "google_calendar"
            ).first()
            
            if existing:
                # Update existing connection
                existing.set_credentials(credentials_dict)
                existing.is_active = True
                existing.connected_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
                # Store token expiry if provided
                if "expires_in" in token_data:
                    expires_in = token_data.get("expires_in")
                    existing.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            else:
                # Create new connection
                connection = MCPConnection(
                    user_id=user_id,
                    provider="google_calendar",
                    is_active=True
                )
                connection.set_credentials(credentials_dict)
                if "expires_in" in token_data:
                    expires_in = token_data.get("expires_in")
                    connection.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                db.add(connection)
            
            db.commit()
            
            logger.info(f"Google Calendar OAuth flow completed successfully for user {user_id}")
            
            # Return success response
            # In a real app, you might redirect to a success page
            return {
                "status": "success",
                "message": "Google Calendar connected successfully",
                "user_id": user_id,
                "provider": "google_calendar",
                "has_refresh_token": bool(refresh_token)
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during token exchange: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error communicating with Google OAuth server: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing OAuth callback: {str(e)}"
        )


# Register callback on both routers for compatibility
@router.get("/callback")
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Callback endpoint at /api/mcp/google/calendar/oauth/callback"""
    return await oauth_callback_handler(code, state, error, error_description, request, db)


@legacy_router.get("/callback")
async def oauth_callback_legacy(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Legacy callback endpoint at /api/mcp/google_calendar/oauth/callback (for Google Cloud Console compatibility)"""
    return await oauth_callback_handler(code, state, error, error_description, request, db)

