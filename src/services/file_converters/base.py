"""Base classes for file converters."""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class ConversionResult(BaseModel):
    """Result of file conversion."""
    success: bool
    text: str
    error: Optional[str] = None
    metadata: Optional[dict] = None


class FileConverter(ABC):
    """Abstract base class for file converters."""
    
    @abstractmethod
    def can_convert(self, mime_type: str, file_name: str) -> bool:
        """
        Check if this converter can handle the given file type.
        
        Args:
            mime_type: MIME type of the file
            file_name: Name of the file
            
        Returns:
            True if this converter can handle the file
        """
        pass
    
    @abstractmethod
    async def convert(self, file_content: bytes, file_name: str, mime_type: str) -> ConversionResult:
        """
        Convert file content to text.
        
        Args:
            file_content: Raw file content as bytes
            file_name: Name of the file
            mime_type: MIME type of the file
            
        Returns:
            ConversionResult with converted text or error
        """
        pass

