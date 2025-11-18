"""Global error handler middleware.

This module provides centralized error handling for the application,
converting domain exceptions to appropriate HTTP responses.
"""

import logging
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from src.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    InvalidModelError,
    FileSearchModelMismatchError,
    UnsupportedModelError
)
from src.api.exceptions import LobeChatHTTPException

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all exceptions globally.
    
    Converts domain exceptions to appropriate HTTP responses
    and logs unexpected errors.
    """
    
    # Domain exceptions - Agent related
    # Format: { "detail": [ { "msg": "Mensagem de erro legível" } ] }
    if isinstance(exc, AgentNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": [{"msg": str(exc)}],
                "message": str(exc),  # Fallback format
                "agent_id": exc.agent_id
            }
        )
    
    if isinstance(exc, InvalidModelError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": [{"msg": str(exc)}],
                "message": str(exc),  # Fallback format
                "model": exc.model,
                "available_models": exc.available_models
            }
        )
    
    if isinstance(exc, FileSearchModelMismatchError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": [{"msg": str(exc)}],
                "message": str(exc),  # Fallback format
                "model": exc.model,
                "required_model": exc.required_model
            }
        )
    
    if isinstance(exc, UnsupportedModelError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": [{"msg": str(exc)}],
                "message": str(exc),  # Fallback format
                "model": exc.model,
                "available_models": exc.available_models
            }
        )
    
    # LobeChat-compatible exceptions
    if isinstance(exc, LobeChatHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # FastAPI HTTPException - check if it has LobeChat format
    if isinstance(exc, HTTPException):
        if isinstance(exc.detail, dict) and "detail" in exc.detail:
            # Already in LobeChat format
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail
            )
        else:
            # Convert to LobeChat format
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": [{"msg": str(exc.detail)}],
                    "message": str(exc.detail)
                }
            )
    
    # Generic error - log but don't expose details
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": [{"msg": "Internal server error"}],
            "message": "Internal server error"  # Fallback format
        }
    )

