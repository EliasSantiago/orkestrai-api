"""Helper functions for API routes."""

from typing import List, Dict, Any
from src.api.exceptions import create_lobechat_error


def create_error_response(
    status_code: int,
    message: str,
    **extra_fields
):
    """
    Create a standardized error response compatible with LobeChat frontend.
    
    Format: { "detail": [ { "msg": "Mensagem de erro legível" } ], "message": "..." }
    
    Args:
        status_code: HTTP status code
        message: Error message
        **extra_fields: Additional fields to include in the error response
    
    Returns:
        LobeChatHTTPException with standardized format
    """
    return create_lobechat_error(status_code=status_code, message=message, **extra_fields)


def format_validation_error(errors: List[Any]) -> Dict[str, Any]:
    """
    Format Pydantic validation errors to match LobeChat expected format.
    
    Args:
        errors: List of validation errors from Pydantic
    
    Returns:
        Formatted error dictionary
    """
    detail = []
    for error in errors:
        if isinstance(error, dict):
            msg = error.get("msg", str(error))
            loc = error.get("loc", [])
            detail.append({
                "msg": msg,
                "loc": loc
            })
        else:
            detail.append({"msg": str(error)})
    
    return {
        "detail": detail,
        "message": detail[0]["msg"] if detail else "Validation error"
    }

