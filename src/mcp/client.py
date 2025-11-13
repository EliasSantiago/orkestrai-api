"""
MCP Client - Base client for Model Context Protocol integration.

This module provides a base client for connecting to MCP servers and
managing MCP tool registrations.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MCPClient(ABC):
    """
    Abstract base class for MCP clients.
    
    Each MCP integration should implement this interface.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize MCP client.
        
        Args:
            name: Name of the MCP client (e.g., "provider_name")
            config: Configuration dictionary with connection details
        """
        self.name = name
        self.config = config
        self._connected = False
        self._tools: Dict[str, Callable] = {}
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the MCP server.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the MCP server."""
        pass
    
    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of tool definitions with name, description, and parameters
        """
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected
    
    def register_tool(self, name: str, tool_func: Callable):
        """Register a tool function locally."""
        self._tools[name] = tool_func
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a registered tool function."""
        return self._tools.get(name)


class MCPManager:
    """
    Manager for multiple MCP clients.
    
    This class manages connections to multiple MCP servers and provides
    a unified interface for accessing tools from all connected clients.
    """
    
    def __init__(self):
        """Initialize MCP manager."""
        self._clients: Dict[str, MCPClient] = {}
        self._initialized = False
    
    async def register_client(self, client: MCPClient) -> bool:
        """
        Register and connect an MCP client.
        
        Args:
            client: MCP client instance to register
            
        Returns:
            True if registration and connection successful
        """
        try:
            if await client.connect():
                self._clients[client.name] = client
                logger.info(f"MCP client '{client.name}' registered successfully")
                return True
            else:
                logger.error(f"Failed to connect MCP client '{client.name}'")
                return False
        except Exception as e:
            logger.error(f"Error registering MCP client '{client.name}': {e}")
            return False
    
    async def unregister_client(self, name: str):
        """
        Unregister and disconnect an MCP client.
        
        Args:
            name: Name of the client to unregister
        """
        if name in self._clients:
            client = self._clients[name]
            await client.disconnect()
            del self._clients[name]
            logger.info(f"MCP client '{name}' unregistered")
    
    async def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available tools from all registered clients.
        
        Returns:
            Dictionary mapping tool names to tool definitions
        """
        all_tools = {}
        for client_name, client in self._clients.items():
            try:
                tools = await client.list_tools()
                for tool in tools:
                    # Prefix tool name with client name to avoid conflicts
                    prefixed_name = f"{client_name}_{tool['name']}"
                    all_tools[prefixed_name] = {
                        **tool,
                        'client': client_name,
                        'original_name': tool['name']
                    }
            except Exception as e:
                logger.error(f"Error getting tools from client '{client_name}': {e}")
        return all_tools
    
    async def call_tool(self, tool_name: str, client_name: Optional[str] = None, **kwargs) -> Any:
        """
        Call a tool from an MCP client.
        
        Args:
            tool_name: Name of the tool (can be prefixed with client name)
            client_name: Optional client name (if not in tool_name)
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        # Parse tool name if prefixed
        if '_' in tool_name and not client_name:
            parts = tool_name.split('_', 1)
            potential_client = parts[0]
            if potential_client in self._clients:
                client_name = potential_client
                tool_name = parts[1]
        
        if not client_name:
            # Try to find tool in any client
            for name, client in self._clients.items():
                try:
                    tools = await client.list_tools()
                    tool_names = [t['name'] for t in tools]
                    if tool_name in tool_names:
                        client_name = name
                        break
                except Exception:
                    continue
        
        if not client_name or client_name not in self._clients:
            raise ValueError(f"Client '{client_name}' not found or tool '{tool_name}' not available")
        
        client = self._clients[client_name]
        return await client.call_tool(tool_name, **kwargs)
    
    async def shutdown(self):
        """Shutdown all registered clients."""
        for client in list(self._clients.values()):
            await client.disconnect()
        self._clients.clear()
        logger.info("All MCP clients disconnected")
    
    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get a registered client by name."""
        return self._clients.get(name)


# Global MCP manager instance
_global_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """Get the global MCP manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = MCPManager()
    return _global_manager

