"""Custom exceptions for API with LobeChat-compatible format."""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class LobeChatHTTPException(HTTPException):
    """
    Custom HTTPException with LobeChat-compatible error format.
    
    Format: { "detail": [ { "msg": "Mensagem de erro legível" } ], "message": "..." }
    """
    
    def __init__(
        self,
        status_code: int,
        message: str,
        **extra_fields
    ):
        detail: Dict[str, Any] = {
            "detail": [{"msg": message}],
            "message": message  # Fallback format
        }
        detail.update(extra_fields)
        
        super().__init__(status_code=status_code, detail=detail)


def create_lobechat_error(
    status_code: int,
    message: str,
    **extra_fields
) -> LobeChatHTTPException:
    """
    Create a LobeChat-compatible error exception.
    
    Args:
        status_code: HTTP status code
        message: Error message
        **extra_fields: Additional fields to include
    
    Returns:
        LobeChatHTTPException
    """
    return LobeChatHTTPException(status_code=status_code, message=message, **extra_fields)

