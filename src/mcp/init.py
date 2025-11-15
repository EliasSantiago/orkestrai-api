"""
MCP Initialization Module.

This module initializes MCP clients on application startup.

Note: MCP clients are now user-specific and managed per-user.
Global initialization is no longer needed as clients are created
on-demand when users connect their accounts.
"""

import logging

logger = logging.getLogger(__name__)


async def initialize_mcp_clients():
    """
    Initialize MCP system.
    
    Note: MCP clients are now user-specific and created on-demand.
    This function is kept for compatibility but does nothing.
    """
    logger.info("MCP system ready. Clients will be created per-user on connection.")


async def shutdown_mcp_clients():
    """
    Shutdown MCP system.
    
    Note: User-specific clients are managed by UserMCPClientManager
    and will be cleaned up automatically.
    """
    from src.mcp.user_client_manager import get_user_mcp_manager
    manager = get_user_mcp_manager()
    await manager.shutdown()
    logger.info("MCP system shut down")


def initialize_mcp_sync():
    """
    Synchronous wrapper for MCP initialization.
    Use this in non-async contexts.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(initialize_mcp_clients())


def shutdown_mcp_sync():
    """Synchronous wrapper for MCP shutdown."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(shutdown_mcp_clients())

