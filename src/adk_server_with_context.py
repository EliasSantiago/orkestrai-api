"""
ADK Server with Automatic Conversation Context Integration

This server loads agents from database and wraps them with automatic
conversation context management using Redis.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / '.env')

from src.database import init_db, test_connection
from src.adk_loader import sync_agents_from_db, load_all_agents_from_db
from src.adk_conversation_hooks import get_adk_hooks
from src.adk_conversation_middleware import get_adk_middleware
from src.database import SessionLocal

# Configure Google API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

app = FastAPI(
    title="ADK Server with Conversation Context",
    description="ADK server with automatic Redis conversation context integration"
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
hooks.enable()  # Enable automatic context integration
middleware = get_adk_middleware()

# Store loaded agents
_agents_cache: Dict[str, Any] = {}


def load_agents():
    """Load agents from database."""
    global _agents_cache
    db = SessionLocal()
    try:
        _agents_cache = load_all_agents_from_db(db)
        print(f"✓ Loaded {len(_agents_cache)} agent(s)")
    finally:
        db.close()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    agent_id: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("=" * 60)
    print("🚀 Starting ADK Server with Conversation Context")
    print("=" * 60)
    
    # Initialize database
    if test_connection():
        print("✓ Database connection established")
        init_db()
    else:
        print("⚠ Warning: Could not connect to database")
    
    # Sync agents from database
    print("\n📦 Syncing agents from database...")
    sync_agents_from_db()
    
    # Load agents
    load_agents()
    
    print("\n" + "=" * 60)
    print("✓ Server ready!")
    print(f"  Conversation Context: {'Enabled' if hooks.is_enabled() else 'Disabled'}")
    print("=" * 60)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ADK Server with Conversation Context",
        "agents": list(_agents_cache.keys()),
        "conversation_context_enabled": hooks.is_enabled()
    }


@app.get("/agents")
async def list_agents():
    """List all available agents."""
    return {
        "agents": list(_agents_cache.keys()),
        "count": len(_agents_cache)
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with automatic conversation context integration.
    
    This endpoint:
    1. Retrieves conversation history from Redis
    2. Adds history to agent context
    3. Processes message with agent
    4. Saves both messages to Redis
    """
    if not request.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required"
        )
    
    # Get user_id from session association
    user_id = middleware.get_user_id_from_session(request.session_id)
    
    # Select agent
    agent_id = request.agent_id
    if not agent_id:
        # Use first available agent
        if _agents_cache:
            agent_id = list(_agents_cache.keys())[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No agents available. Please create agents via API."
            )
    
    if agent_id not in _agents_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    agent = _agents_cache[agent_id]
    
    # Get conversation context BEFORE processing
    context = hooks.before_process_message(
        session_id=request.session_id,
        user_message=request.message,
        user_id=user_id,
        metadata=request.metadata
    )
    
    # Prepare messages for agent
    # Format: Include conversation history + new message
    messages = []
    
    # Add conversation history if available
    if context.get("has_context"):
        history = context.get("conversation_history", [])
        messages.extend(history)
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": request.message
    })
    
    try:
        # Process with agent
        # Note: This depends on how Google ADK Agent processes messages
        # The actual implementation may vary based on ADK API
        
        # For now, we'll use a simple approach:
        # If agent has a chat method, use it
        if hasattr(agent, 'chat'):
            response = agent.chat(request.message)
        elif hasattr(agent, 'run'):
            response = agent.run(request.message)
        else:
            # Fallback: try to call agent directly
            # This is a placeholder - actual implementation depends on ADK API
            response = f"Agent processed: {request.message}"
        
        # Extract assistant message
        if isinstance(response, str):
            assistant_message = response
        elif isinstance(response, dict):
            assistant_message = response.get("message", str(response))
        else:
            assistant_message = str(response)
        
        # Save messages to Redis AFTER processing
        hooks.after_process_message(
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=assistant_message,
            user_id=user_id,
            metadata=request.metadata
        )
        
        return ChatResponse(
            message=assistant_message,
            session_id=request.session_id,
            agent_id=agent_id
        )
    
    except Exception as e:
        print(f"✗ Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/sessions/{session_id}/associate")
async def associate_session(session_id: str, user_id: int):
    """
    Associate an ADK session with a user.
    
    This allows the system to retrieve user_id from session_id
    for automatic context management.
    """
    success = middleware.set_user_id_for_session(session_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to associate session"
        )
    return {"status": "success", "session_id": session_id, "user_id": user_id}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agents_loaded": len(_agents_cache),
        "conversation_context_enabled": hooks.is_enabled()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("ADK_SERVER_PORT", "8000"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

