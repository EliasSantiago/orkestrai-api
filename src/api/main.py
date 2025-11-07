"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth_routes, agent_routes, conversation_routes, adk_integration_routes, agent_chat_routes
from src.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="Agents ADK API",
    description="API for managing agents and users",
    version="1.0.0",
    lifespan=lifespan
)

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
app.include_router(agent_routes.router)
app.include_router(agent_chat_routes.router)
app.include_router(conversation_routes.router)
app.include_router(adk_integration_routes.router)


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

