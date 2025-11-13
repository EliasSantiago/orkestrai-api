"""
MCP (Model Context Protocol) Integration Module.

This module provides integration with MCP servers, allowing agents to use
external tools and services through the Model Context Protocol.

Structure:
- src/mcp/client.py: Base MCP client and connection manager
- src/mcp/{provider}/: Provider-specific MCP integrations (add as needed)
- tools/mcp/: Tool wrappers that expose MCP tools to agents
"""

__all__ = ['MCPClient', 'MCPManager']

