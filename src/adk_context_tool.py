"""
Conversation Context Tool for ADK Agents

This tool allows agents to automatically retrieve and use conversation context
from Redis without explicit handling in the agent code.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adk_conversation_middleware import get_adk_middleware


def get_conversation_context(session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Tool function to retrieve conversation context from Redis.
    
    This function can be called by agents to get conversation history.
    
    Args:
        session_id: The session ID to get context for
        limit: Optional limit on number of messages (default: all)
    
    Returns:
        List of messages in format [{role: str, content: str}, ...]
    """
    try:
        middleware = get_adk_middleware()
        context = middleware.get_conversation_context(
            session_id=session_id,
            user_id=None,  # Will be resolved from session
            limit=limit
        )
        return context
    except Exception as e:
        print(f"⚠ Warning: Error getting conversation context: {e}")
        return []


# Export for use in agent generation
__all__ = ['get_conversation_context']

