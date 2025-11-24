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
        
        File Search (RAG) works with Gemini models that support RAG:
        - gemini-2.5-flash
        - gemini-3-pro-preview
        - gemini-3-pro
        - gemini-2.5-pro
        
        Args:
            model: Model name (can be 'gemini-2.5-flash', 'gemini/gemini-3-pro-preview', etc.)
            use_file_search: Whether file search is enabled
            
        Raises:
            FileSearchModelMismatchError: If model is incompatible with file search
        """
        if not use_file_search:
            return
        
        # Extract model name without provider prefix (e.g., 'gemini/gemini-3-pro-preview' -> 'gemini-3-pro-preview')
        model_name = model.split('/')[-1] if '/' in model else model
        
        # Models that support RAG
        gemini_rag_models = [
            'gemini-2.5-flash',
            'gemini-3-pro',
            'gemini-3-pro-preview',
            'gemini-2.5-pro',
        ]
        
        # Check if it's a Gemini model and supports RAG
        is_gemini_model = model.startswith('gemini/') or model_name.startswith('gemini-')
        supports_rag = any(model_name.endswith(rag_model) or model_name == rag_model for rag_model in gemini_rag_models)
        
        if not (is_gemini_model and supports_rag):
            raise FileSearchModelMismatchError(
                model=model,
                required_model="gemini-2.5-flash, gemini-3-pro-preview, gemini-3-pro, or gemini-2.5-pro"
            )

