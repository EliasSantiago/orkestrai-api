"""API routes for listing supported LLM models."""

from fastapi import APIRouter
from src.core.llm_factory import LLMFactory

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
async def list_supported_models():
    """
    List all supported LLM models grouped by provider.
    
    Returns a dictionary mapping provider names to lists of supported models.
    """
    return {
        "providers": LLMFactory.get_all_supported_models(),
        "message": "These are the LLM models currently supported by the application."
    }

