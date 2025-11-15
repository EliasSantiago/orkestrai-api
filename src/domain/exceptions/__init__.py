"""Domain exceptions.

This module contains domain-specific exceptions that represent
business logic errors, not technical errors.
"""

from src.domain.exceptions.agent_exceptions import (
    AgentException,
    AgentNotFoundError,
    InvalidModelError,
    FileSearchModelMismatchError,
    UnsupportedModelError
)

__all__ = [
    "AgentException",
    "AgentNotFoundError",
    "InvalidModelError",
    "FileSearchModelMismatchError",
    "UnsupportedModelError",
]

