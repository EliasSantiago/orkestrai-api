"""
ADK Conversation Integration - Hooks System

This module provides hooks to automatically integrate Redis conversation context
with Google ADK agents. It follows best practices for maintainability and extensibility.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from functools import wraps
import json

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adk_conversation_middleware import get_adk_middleware


class ADKConversationHooks:
    """
    Hook system for integrating conversation context with ADK agents.
    
    This class provides hooks that can be registered to intercept messages
    before and after processing, automatically handling Redis context.
    """
    
    def __init__(self):
        self.middleware = get_adk_middleware()
        self._before_message_hooks: List[Callable] = []
        self._after_message_hooks: List[Callable] = []
        self._enabled = True
    
    def enable(self):
        """Enable automatic conversation context integration."""
        self._enabled = True
    
    def disable(self):
        """Disable automatic conversation context integration."""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if hooks are enabled."""
        return self._enabled
    
    def register_before_hook(self, hook: Callable):
        """Register a hook to be called before processing a message."""
        self._before_message_hooks.append(hook)
    
    def register_after_hook(self, hook: Callable):
        """Register a hook to be called after processing a message."""
        self._after_message_hooks.append(hook)
    
    def get_session_id_from_request(self, request_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract session_id from ADK request.
        
        ADK typically sends session_id in the request body or headers.
        This method attempts to extract it from common locations.
        """
        # Try different possible locations
        if isinstance(request_data, dict):
            # Try direct session_id
            if 'session_id' in request_data:
                return request_data['session_id']
            
            # Try in session object
            if 'session' in request_data and isinstance(request_data['session'], dict):
                if 'id' in request_data['session']:
                    return request_data['session']['id']
            
            # Try in conversation object
            if 'conversation' in request_data and isinstance(request_data['conversation'], dict):
                if 'session_id' in request_data['conversation']:
                    return request_data['conversation']['session_id']
        
        return None
    
    def get_user_id_from_request(self, request_data: Dict[str, Any]) -> Optional[int]:
        """
        Extract user_id from ADK request.
        
        This can be from headers (JWT token) or request body.
        """
        # Try to get from request metadata
        if isinstance(request_data, dict):
            if 'user_id' in request_data:
                return request_data.get('user_id')
            
            # Try to get from metadata
            if 'metadata' in request_data and isinstance(request_data['metadata'], dict):
                if 'user_id' in request_data['metadata']:
                    return request_data['metadata']['user_id']
        
        return None
    
    def before_process_message(
        self,
        session_id: str,
        user_message: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Hook called before processing a message.
        
        Returns enhanced context that should be passed to the agent.
        """
        if not self._enabled:
            return {}
        
        context = {}
        
        # Get conversation history from Redis
        history = self.middleware.get_conversation_context(
            session_id=session_id,
            user_id=user_id,
            limit=None  # Get all history, LLM will handle windowing
        )
        
        if history:
            context['conversation_history'] = history
            context['has_context'] = True
        else:
            context['has_context'] = False
        
        # Execute registered hooks
        for hook in self._before_message_hooks:
            try:
                hook_result = hook(session_id, user_message, user_id, metadata, context)
                if hook_result:
                    context.update(hook_result)
            except Exception as e:
                print(f"⚠ Warning: Error in before hook: {e}")
        
        return context
    
    def after_process_message(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Hook called after processing a message.
        
        Saves both user and assistant messages to Redis.
        """
        if not self._enabled:
            return
        
        # Save user message
        try:
            self.middleware.save_user_message(
                session_id=session_id,
                content=user_message,
                user_id=user_id,
                metadata=metadata
            )
        except Exception as e:
            print(f"⚠ Warning: Error saving user message: {e}")
        
        # Save assistant message
        try:
            assistant_metadata = metadata.copy() if metadata else {}
            assistant_metadata['source'] = 'adk'
            
            self.middleware.save_assistant_message(
                session_id=session_id,
                content=assistant_message,
                user_id=user_id,
                metadata=assistant_metadata
            )
        except Exception as e:
            print(f"⚠ Warning: Error saving assistant message: {e}")
        
        # Execute registered hooks
        for hook in self._after_message_hooks:
            try:
                hook(session_id, user_message, assistant_message, user_id, metadata)
            except Exception as e:
                print(f"⚠ Warning: Error in after hook: {e}")


# Global instance
_adk_hooks: Optional[ADKConversationHooks] = None


def get_adk_hooks() -> ADKConversationHooks:
    """Get or create ADK conversation hooks instance."""
    global _adk_hooks
    if _adk_hooks is None:
        _adk_hooks = ADKConversationHooks()
    return _adk_hooks


def enable_conversation_context():
    """Enable automatic conversation context integration."""
    hooks = get_adk_hooks()
    hooks.enable()


def disable_conversation_context():
    """Disable automatic conversation context integration."""
    hooks = get_adk_hooks()
    hooks.disable()

