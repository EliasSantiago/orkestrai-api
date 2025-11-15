"""Global error handler middleware.

This module provides centralized error handling for the application,
converting domain exceptions to appropriate HTTP responses.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    InvalidModelError,
    FileSearchModelMismatchError,
    UnsupportedModelError
)

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all exceptions globally.
    
    Converts domain exceptions to appropriate HTTP responses
    and logs unexpected errors.
    """
    
    # Domain exceptions - Agent related
    if isinstance(exc, AgentNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc),
                "agent_id": exc.agent_id
            }
        )
    
    if isinstance(exc, InvalidModelError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "model": exc.model,
                "available_models": exc.available_models
            }
        )
    
    if isinstance(exc, FileSearchModelMismatchError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "model": exc.model,
                "required_model": exc.required_model
            }
        )
    
    if isinstance(exc, UnsupportedModelError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "model": exc.model,
                "available_models": exc.available_models
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
        content={"detail": "Internal server error"}
    )

