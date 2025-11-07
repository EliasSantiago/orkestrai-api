"""
ADK Proxy Server with Automatic Conversation Context Integration

This server acts as a proxy to the ADK Web server, intercepting requests
and automatically integrating Redis conversation context.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / '.env')

from src.adk_conversation_hooks import get_adk_hooks
from src.adk_conversation_middleware import get_adk_middleware

# ADK server URL (internal)
ADK_BACKEND_URL = os.getenv("ADK_BACKEND_URL", "http://localhost:8001")
ADK_PROXY_PORT = int(os.getenv("ADK_PROXY_PORT", "8000"))

app = FastAPI(
    title="ADK Proxy with Conversation Context",
    description="Proxy server that integrates Redis conversation context with ADK agents"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize hooks
hooks = get_adk_hooks()
middleware = get_adk_middleware()


async def get_session_id_from_request(request: Request) -> Optional[str]:
    """Extract session_id from request."""
    try:
        body = await request.body()
        if body:
            data = json.loads(body)
            return hooks.get_session_id_from_request(data)
    except:
        pass
    
    # Try query params
    session_id = request.query_params.get("session_id")
    if session_id:
        return session_id
    
    # Try headers
    session_id = request.headers.get("X-Session-ID")
    if session_id:
        return session_id
    
    return None


async def get_user_id_from_request(request: Request) -> Optional[int]:
    """Extract user_id from request (JWT token or header)."""
    # Try header
    user_id_str = request.headers.get("X-User-ID")
    if user_id_str:
        try:
            return int(user_id_str)
        except:
            pass
    
    # Try to get from session association
    session_id = await get_session_id_from_request(request)
    if session_id:
        user_id = middleware.get_user_id_from_session(session_id)
        if user_id:
            return user_id
    
    return None


async def inject_conversation_context(
    request_data: Dict[str, Any],
    session_id: str,
    user_id: Optional[int]
) -> Dict[str, Any]:
    """
    Inject conversation history into request before sending to ADK.
    
    This modifies the request to include conversation history in the context.
    """
    # Get conversation history
    history = hooks.before_process_message(
        session_id=session_id,
        user_message=request_data.get("message", ""),
        user_id=user_id
    )
    
    # Add history to request metadata
    if "metadata" not in request_data:
        request_data["metadata"] = {}
    
    if history.get("has_context"):
        request_data["metadata"]["conversation_history"] = history.get("conversation_history", [])
    
    return request_data


@app.post("/chat/{session_id}")
@app.post("/chat")
async def proxy_chat(request: Request, session_id: Optional[str] = None):
    """
    Proxy chat endpoint that intercepts messages and adds conversation context.
    """
    # Get session_id from route or request
    if not session_id:
        session_id = await get_session_id_from_request(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required"
        )
    
    # Get user_id
    user_id = await get_user_id_from_request(request)
    
    # Get request body
    try:
        body = await request.body()
        request_data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        request_data = {}
    
    # Get user message
    user_message = request_data.get("message", "") or request_data.get("content", "")
    
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="message is required"
        )
    
    # Inject conversation context
    enhanced_request = await inject_conversation_context(
        request_data.copy(),
        session_id,
        user_id
    )
    
    # Forward to ADK backend
    async with httpx.AsyncClient() as client:
        try:
            # Determine ADK endpoint
            adk_endpoint = f"{ADK_BACKEND_URL}/chat"
            if session_id:
                adk_endpoint = f"{ADK_BACKEND_URL}/chat/{session_id}"
            
            # Forward request
            response = await client.post(
                adk_endpoint,
                json=enhanced_request,
                headers={
                    "Content-Type": "application/json",
                    "X-Session-ID": session_id,
                },
                timeout=60.0
            )
            
            # Get assistant response
            if response.status_code == 200:
                response_data = response.json()
                assistant_message = response_data.get("message", "") or response_data.get("content", "")
                
                # Save messages to Redis
                hooks.after_process_message(
                    session_id=session_id,
                    user_message=user_message,
                    assistant_message=assistant_message,
                    user_id=user_id,
                    metadata=enhanced_request.get("metadata")
                )
                
                return JSONResponse(content=response_data)
            else:
                return JSONResponse(
                    content={"error": "ADK backend error", "detail": response.text},
                    status_code=response.status_code
                )
        
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ADK backend unavailable: {str(e)}"
            )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "adk_backend": ADK_BACKEND_URL,
        "conversation_context_enabled": hooks.is_enabled()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ADK Proxy with Conversation Context",
        "endpoints": {
            "chat": "/chat/{session_id}",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 ADK Proxy Server with Conversation Context")
    print("=" * 60)
    print(f"  Proxy Port: {ADK_PROXY_PORT}")
    print(f"  ADK Backend: {ADK_BACKEND_URL}")
    print(f"  Context Integration: {'Enabled' if hooks.is_enabled() else 'Disabled'}")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=ADK_PROXY_PORT,
        log_level="info"
    )

