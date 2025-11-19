"""Config API routes for LobeChat compatibility.

Provides global configuration and default agent config endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user_id

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/global")
async def get_global_config(
    user_id: int = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get global runtime configuration.
    
    Compatible with LobeChat's config.getGlobalConfig tRPC call.
    Returns server feature flags and configuration.
    
    This endpoint is called multiple times during app initialization to get
    server configuration and feature flags.
    """
    return {
        "serverConfig": {
            "aiProvider": {},
            "defaultAgent": {
                "config": {
                    "model": "gpt-4o-mini",
                    "provider": "openai",
                    "temperature": 0.7,
                }
            },
            "enableUploadFileToServer": False,
            "enabledAccessCode": False,
            "enabledOAuthSSO": False,
            "enabledPassword": True,
            "enabledRegister": True,
            "telemetry": {
                "langfuse": False,
            },
        },
        "serverFeatureFlags": {
            # Authentication flags
            "enableWebRTC": False,
            "enableOAuthSSO": False,
            "enablePassword": True,
            "enableRegister": True,
            "enableTelemetryChat": False,
            "enableAccessCode": False,
            # Feature flags for UI functionality
            "create_session": True,  # Enable agent creation
            "edit_agent": True,  # Enable agent editing
            "plugins": True,  # Enable plugins
            "dalle": True,  # Enable DALL-E
            "ai_image": True,  # Enable AI image generation
            "speech_to_text": True,  # Enable STT
            "token_counter": True,  # Enable token counter
            "welcome_suggest": True,  # Enable welcome suggestions
            "knowledge_base": True,  # Enable knowledge base
            "rag_eval": False,  # Disable RAG eval (advanced feature)
            "market": True,  # Enable market/discover
            "changelog": True,  # Enable changelog
            "check_updates": True,  # Enable update checks
            "group_chat": False,  # Disable group chat (can be enabled later)
            "pin_list": False,  # Disable pin list (can be enabled later)
            "language_model_settings": True,  # Enable LLM settings
            "provider_settings": True,  # Enable provider settings
            "openai_api_key": True,  # Enable OpenAI API key config
            "openai_proxy_url": True,  # Enable OpenAI proxy URL config
            "api_key_manage": False,  # Disable API key management (can be enabled later)
            "cloud_promotion": False,  # Disable cloud promotion
            "commercial_hide_github": False,  # Show GitHub links
            "commercial_hide_docs": False,  # Show docs links
        },
    }


@router.get("/default-agent")
async def get_default_agent_config(
    user_id: int = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get default agent configuration.
    
    Compatible with LobeChat's config.getDefaultAgentConfig tRPC call.
    Returns default agent settings.
    """
    return {
        "model": "gpt-4o-mini",
        "provider": "openai",
        "temperature": 0.7,
        "maxTokens": 2000,
        "systemRole": "You are a helpful assistant.",
    }

