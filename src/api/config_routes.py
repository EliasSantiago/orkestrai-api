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
            "enableWebRTC": False,
            "enableOAuthSSO": False,
            "enablePassword": True,
            "enableRegister": True,
            "enableTelemetryChat": False,
            "enableAccessCode": False,
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

