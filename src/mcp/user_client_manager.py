"""
User-specific MCP Client Manager.

This module manages MCP clients on a per-user basis, allowing each user
to have their own connections to MCP providers.
"""

import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from src.models import MCPConnection

logger = logging.getLogger(__name__)


class UserMCPClientManager:
    """
    Manager for user-specific MCP clients.
    
    This class manages MCP clients for each user separately, ensuring
    that each user's agents only access their own MCP connections.
    """
    
    def __init__(self):
        """Initialize the user MCP client manager."""
        # Store clients by (user_id, provider) tuple
        self._clients: Dict[tuple, any] = {}
    
    async def get_client_for_user(
        self,
        db: Session,
        user_id: int,
        provider: str
    ) -> Optional[any]:
        """
        Get or create an MCP client for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            provider: MCP provider name (e.g., "provider_name")
            
        Returns:
            MCP client instance or None if not connected
        """
        cache_key = (user_id, provider)
        
        # Check cache first
        if cache_key in self._clients:
            client = self._clients[cache_key]
            if client.is_connected:
                return client
            else:
                # Client disconnected, remove from cache
                del self._clients[cache_key]
        
        # Load from database
        connection = db.query(MCPConnection).filter(
            MCPConnection.user_id == user_id,
            MCPConnection.provider == provider,
            MCPConnection.is_active == True
        ).first()
        
        if not connection:
            return None
        
        try:
            # Decrypt credentials
            credentials = connection.get_credentials()
            
            # Create and connect client based on provider
            client = None
            
            if provider == "google_calendar":
                from src.mcp.google_calendar.client import GoogleCalendarClient
                if "access_token" not in credentials:
                    logger.error("Google Calendar credentials must contain 'access_token'")
                    return None
                client = GoogleCalendarClient(credentials)
            elif provider == "tavily":
                from src.mcp.tavily.client import TavilyMCPClient
                # Accept both 'api_key' and 'access_token' for flexibility
                if "api_key" not in credentials and "access_token" not in credentials:
                    logger.error("Tavily credentials must contain 'api_key' or 'access_token'")
                    return None
                client = TavilyMCPClient(credentials)
            else:
                logger.error(f"MCP provider '{provider}' not implemented. Add client implementation in src/mcp/{provider}/")
                return None
            
            # Connect client
            if await client.connect():
                # Cache the client
                self._clients[cache_key] = client
                
                # Update last_used_at
                from datetime import datetime
                connection.last_used_at = datetime.utcnow()
                db.commit()
                
                return client
            else:
                logger.error(f"Failed to connect {provider} client for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting {provider} client for user {user_id}: {e}")
            return None
    
    async def disconnect_user_client(self, user_id: int, provider: str):
        """
        Disconnect and remove a user's MCP client.
        
        Args:
            user_id: User ID
            provider: MCP provider name
        """
        cache_key = (user_id, provider)
        if cache_key in self._clients:
            client = self._clients[cache_key]
            await client.disconnect()
            del self._clients[cache_key]
            logger.info(f"Disconnected {provider} client for user {user_id}")
    
    async def disconnect_all_user_clients(self, user_id: int):
        """Disconnect all MCP clients for a user."""
        keys_to_remove = [key for key in self._clients.keys() if key[0] == user_id]
        for key in keys_to_remove:
            client = self._clients[key]
            await client.disconnect()
            del self._clients[key]
        logger.info(f"Disconnected all MCP clients for user {user_id}")
    
    async def shutdown(self):
        """Shutdown all clients."""
        for client in list(self._clients.values()):
            await client.disconnect()
        self._clients.clear()
        logger.info("All user MCP clients shut down")


# Global user MCP client manager instance
_global_user_manager: Optional[UserMCPClientManager] = None


def get_user_mcp_manager() -> UserMCPClientManager:
    """Get the global user MCP client manager instance."""
    global _global_user_manager
    if _global_user_manager is None:
        _global_user_manager = UserMCPClientManager()
    return _global_user_manager

