"""MCP connection management API routes."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database import get_db
from src.models import MCPConnection, User
from src.mcp.user_client_manager import get_user_mcp_manager
from src.api.dependencies import get_current_user_id
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


class MCPConnectionRequest(BaseModel):
    """Request model for connecting to an MCP provider."""
    provider: str  # MCP provider name (e.g., "tavily", "google_calendar")
    credentials: dict  # Provider-specific credentials
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "provider": "tavily",
                    "credentials": {
                        "api_key": "tvly-xxxxxxxxxxxxxxxxxxxxxxxx"
                    }
                },
                {
                    "provider": "google_calendar",
                    "credentials": {
                        "access_token": "ya29.xxxxxxxxxxxxxxxxx",
                        "refresh_token": "1//xxxxxxxxxxxxxxxxx"
                    }
                },
                {
                    "provider": "custom_provider",
                    "credentials": {
                        "api_key": "your_api_key_here",
                        "api_secret": "your_api_secret_here"
                    }
                }
            ]
        }


class MCPConnectionResponse(BaseModel):
    """Response model for MCP connection."""
    id: int
    provider: str
    is_active: bool
    connected_at: str
    last_used_at: Optional[str] = None
    metadata: dict


@router.post("/connect", response_model=MCPConnectionResponse)
async def connect_mcp(
    request: MCPConnectionRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Connect user to an MCP provider.
    
    This endpoint connects a user to an MCP provider using provider-specific credentials.
    The credentials are encrypted and stored securely.
    """
    # Check if connection already exists
    existing = db.query(MCPConnection).filter(
        MCPConnection.user_id == user_id,
        MCPConnection.provider == request.provider
    ).first()
    
    if existing:
        # Update existing connection
        existing.set_credentials(request.credentials)
        existing.is_active = True
        existing.connected_at = datetime.utcnow()
        existing.updated_at = datetime.utcnow()
    else:
        # Create new connection
        connection = MCPConnection(
            user_id=user_id,
            provider=request.provider,
            is_active=True
        )
        connection.set_credentials(request.credentials)
        db.add(connection)
    
    db.commit()
    db.refresh(existing if existing else connection)
    
    # Test connection by creating a client
    manager = get_user_mcp_manager()
    try:
        client = await manager.get_client_for_user(db, user_id, request.provider)
        
        if not client or not client.is_connected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to {request.provider}. Please check your credentials."
            )
    except RuntimeError as e:
        # Re-raise with more specific error message
        error_msg = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to {request.provider}: {error_msg}"
        )
    except Exception as e:
        # Catch any other errors and provide helpful message
        error_msg = str(e)
        logger.error(f"Error connecting to {request.provider}: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to {request.provider}: {error_msg}"
        )
    
    conn = existing if existing else connection
    return MCPConnectionResponse(
        id=conn.id,
        provider=conn.provider,
        is_active=conn.is_active,
        connected_at=conn.connected_at.isoformat(),
        last_used_at=conn.last_used_at.isoformat() if conn.last_used_at else None,
        metadata=conn.meta_data or {}
    )


@router.delete("/disconnect/{provider}")
async def disconnect_mcp(
    provider: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Disconnect user from an MCP provider.
    
    This endpoint disconnects the user from the specified MCP provider
    and removes the stored credentials.
    """
    connection = db.query(MCPConnection).filter(
        MCPConnection.user_id == user_id,
        MCPConnection.provider == provider
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{provider} connection not found"
        )
    
    # Disconnect client
    manager = get_user_mcp_manager()
    await manager.disconnect_user_client(user_id, provider)
    
    # Deactivate connection
    connection.is_active = False
    connection.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"{provider} disconnected successfully"}


@router.get("/connections", response_model=list[MCPConnectionResponse])
async def get_connections(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all MCP connections for the current user.
    """
    connections = db.query(MCPConnection).filter(
        MCPConnection.user_id == user_id
    ).all()
    
    return [
        MCPConnectionResponse(
            id=conn.id,
            provider=conn.provider,
            is_active=conn.is_active,
            connected_at=conn.connected_at.isoformat(),
            last_used_at=conn.last_used_at.isoformat() if conn.last_used_at else None,
            metadata=conn.meta_data or {}
        )
        for conn in connections
    ]


@router.get("/status/{provider}")
async def get_mcp_status(
    provider: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Check if user's MCP connection is active and working.
    """
    connection = db.query(MCPConnection).filter(
        MCPConnection.user_id == user_id,
        MCPConnection.provider == provider,
        MCPConnection.is_active == True
    ).first()
    
    if not connection:
        return {
            "connected": False,
            "message": f"{provider} not connected"
        }
    
    # Try to get client and test connection
    manager = get_user_mcp_manager()
    client = await manager.get_client_for_user(db, user_id, provider)
    
    if client and client.is_connected:
        return {
            "connected": True,
            "message": f"{provider} connected and working",
            "connected_at": connection.connected_at.isoformat(),
            "last_used_at": connection.last_used_at.isoformat() if connection.last_used_at else None
        }
    else:
        return {
            "connected": False,
            "message": f"{provider} connection exists but is not working. Please reconnect."
        }


@router.get("/tools/{provider}")
async def get_mcp_tools(
    provider: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all available tools for an MCP provider.
    
    Returns a list of all tools available from the MCP provider,
    which can be used when creating agents.
    """
    connection = db.query(MCPConnection).filter(
        MCPConnection.user_id == user_id,
        MCPConnection.provider == provider,
        MCPConnection.is_active == True
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{provider} not connected. Please connect your {provider} account first."
        )
    
    # Get client and list tools
    manager = get_user_mcp_manager()
    client = await manager.get_client_for_user(db, user_id, provider)
    
    if not client or not client.is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{provider} connection is not working. Please reconnect."
        )
    
    try:
        tools = await client.list_tools()
        
        # Format tools for response
        formatted_tools = []
        for tool in tools:
            tool_name = tool.get("name", "")
            # Add provider prefix if not already present
            prefixed_name = f"{provider}_{tool_name}" if not tool_name.startswith(f"{provider}_") else tool_name
            
            formatted_tools.append({
                "name": prefixed_name,
                "description": tool.get("description", ""),
                "parameters": tool.get("inputSchema", {}).get("properties", {}),
                "required": tool.get("inputSchema", {}).get("required", [])
            })
        
        return {
            "tools": formatted_tools,
            "total": len(formatted_tools),
            "message": f"Found {len(formatted_tools)} tools from {provider}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing {provider} tools: {str(e)}"
        )

