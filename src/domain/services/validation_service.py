"""Centralized validation service.

This service contains all business rule validations,
keeping them separate from use cases and controllers.
"""

from src.domain.exceptions.agent_exceptions import (
    InvalidModelError,
    FileSearchModelMismatchError
)
from src.core.llm_factory import LLMFactory


class ValidationService:
    """Service for validating business rules."""
    
    def __init__(self, llm_factory: LLMFactory = None):
        """Initialize validation service."""
        self.llm_factory = llm_factory or LLMFactory()
    
    def validate_model(self, model: str) -> None:
        """
        Validate that model is supported.
        
        Args:
            model: Model name to validate
            
        Raises:
            InvalidModelError: If model is not supported
        """
        if not self.llm_factory.is_model_supported(model):
            available_models = self.llm_factory.get_all_supported_models()
            raise InvalidModelError(model, available_models)
    
    def validate_file_search_model(
        self, 
        model: str, 
        use_file_search: bool
    ) -> None:
        """
        Validate file search model compatibility.
        
        File Search (RAG) only works with gemini-2.5-flash.
        
        Args:
            model: Model name
            use_file_search: Whether file search is enabled
            
        Raises:
            FileSearchModelMismatchError: If model is incompatible with file search
        """
        if use_file_search and model != "gemini-2.5-flash":
            raise FileSearchModelMismatchError(
                model=model,
                required_model="gemini-2.5-flash"
            )

