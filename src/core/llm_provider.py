"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Message in a conversation."""
    role: str  # "user", "assistant", "system"
    content: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Chat with the LLM.
        
        Args:
            messages: List of messages in the conversation
            model: Model name to use
            tools: Optional list of tools/functions
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Response chunks as strings
        """
        pass
    
    @abstractmethod
    def supports_model(self, model: str) -> bool:
        """Check if this provider supports the given model."""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Get list of supported model names."""
        pass

