"""
Tool wrapper for injecting user_id into MCP tools.

This module provides a wrapper function that automatically injects user_id
into MCP tool calls, ensuring each user uses their own MCP connections.
"""

from typing import Callable, Any
import functools


def inject_user_id(tool_func: Callable, user_id: int) -> Callable:
    """
    Wrap a tool function to inject user_id as a keyword argument.
    
    Args:
        tool_func: The tool function to wrap
        user_id: User ID to inject
        
    Returns:
        Wrapped function that automatically includes user_id
    """
    @functools.wraps(tool_func)
    def wrapper(**kwargs):
        # Inject user_id if not already present
        # Always inject as keyword argument to avoid signature conflicts
        if 'user_id' not in kwargs:
            kwargs['user_id'] = user_id
        return tool_func(**kwargs)
    return wrapper

