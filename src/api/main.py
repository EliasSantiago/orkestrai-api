"""Main FastAPI application."""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth_routes, agent_routes, conversation_routes, adk_integration_routes, agent_chat_routes, models_routes, mcp_routes, file_search_routes, openai_compatible_routes, user_routes, lobechat_compat_routes, message_routes, lobechat_rest_routes, config_routes, token_routes
from src.api.mcp.google import google_calendar_oauth_router, google_calendar_oauth_legacy_router
from src.api.middleware.error_handler import global_exception_handler
from src.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    init_db()
    # MCP clients are now initialized per-user, no global initialization needed
    yield
    # Shutdown
    from src.mcp.user_client_manager import get_user_mcp_manager
    manager = get_user_mcp_manager()
    await manager.shutdown()


app = FastAPI(
    title="Agents ADK API",
    description="API for managing agents and users",
    version="1.0.0",
    lifespan=lifespan
)

# Global exception handler
app.add_exception_handler(Exception, global_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)  # User preferences and profile
app.include_router(agent_routes.router)
app.include_router(agent_chat_routes.router)
app.include_router(conversation_routes.router)
app.include_router(adk_integration_routes.router)
app.include_router(models_routes.router)
app.include_router(mcp_routes.router)
app.include_router(google_calendar_oauth_router)
app.include_router(google_calendar_oauth_legacy_router)  # Legacy path for Google Cloud Console compatibility
app.include_router(file_search_routes.router)
app.include_router(openai_compatible_routes.router)  # OpenAI-compatible API for LobeChat, LibreChat, etc.
app.include_router(lobechat_rest_routes.router)  # Complete REST API routes for LobeChat frontend (must be before compat routes)
app.include_router(lobechat_compat_routes.router)  # LobeChat compatibility endpoints (legacy, deprecated)
app.include_router(message_routes.router)  # Message-specific routes (stats, rank, heatmap, CRUD)
app.include_router(config_routes.router)  # Config routes (global config, default agent config)
app.include_router(token_routes.router)  # Token management and billing routes

# Mount static files for uploaded avatars
uploads_dir = Path("uploads")
if uploads_dir.exists():
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agents ADK API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

