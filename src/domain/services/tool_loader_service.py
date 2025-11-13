"""Service for loading tools for agents."""

import logging
from typing import List, Dict, Callable
from sqlalchemy.orm import Session
from src.models import MCPConnection

logger = logging.getLogger(__name__)


class ToolLoaderService:
    """Service for loading and preparing tools for agents."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    def load_tools_for_agent(
        self,
        agent_tools: List[str],
        user_id: int
    ) -> List[Callable]:
        """
        Load all tools requested by agent.
        
        Args:
            agent_tools: List of tool names requested by agent
            user_id: User ID for MCP tools
            
        Returns:
            List of callable tool functions
        """
        # Base tools
        tool_map = self._load_base_tools()
        
        # MCP tools
        mcp_tools = self._load_mcp_tools(user_id)
        tool_map.update(mcp_tools)
        
        # Filter to only requested tools
        tools = [tool_map[name] for name in agent_tools if name in tool_map]
        
        # Log for debugging
        missing_tools = [name for name in agent_tools if name not in tool_map]
        if missing_tools:
            logger.warning(f"Requested tools not found: {missing_tools}")
        
        logger.info(f"Loaded {len(tools)} tools out of {len(agent_tools)} requested")
        
        return tools
    
    def _load_base_tools(self) -> Dict[str, Callable]:
        """Load base tools (calculator, time, web search)."""
        try:
            from tools import calculator, get_current_time, tavily_web_search
            
            return {
                "calculator": calculator,
                "get_current_time": get_current_time,
                "tavily_web_search": tavily_web_search,
            }
        except ImportError as e:
            logger.warning(f"Could not load base tools: {e}")
            return {}
    
    def _load_mcp_tools(self, user_id: int) -> Dict[str, Callable]:
        """Load MCP tools for user."""
        try:
            from tools.mcp.tool_wrapper import inject_user_id
            from tools.mcp.dynamic_tools import get_all_mcp_tools
            
            # Get all active MCP connections for user
            mcp_connections = self.db.query(MCPConnection).filter(
                MCPConnection.user_id == user_id,
                MCPConnection.is_active == True
            ).all()
            
            logger.info(f"Found {len(mcp_connections)} active MCP connections for user {user_id}")
            
            tool_map = {}
            for connection in mcp_connections:
                try:
                    # Skip notion provider (removed)
                    if connection.provider == "notion":
                        logger.debug(f"Skipping notion provider for user {user_id}")
                        continue
                    
                    logger.info(f"Loading tools from {connection.provider} MCP for user {user_id}")
                    
                    # Load MCP tools for provider
                    provider_tools = get_all_mcp_tools(user_id, connection.provider)
                    
                    if not provider_tools:
                        logger.warning(f"No tools loaded from {connection.provider} MCP")
                        continue
                    
                    logger.info(f"Loaded {len(provider_tools)} tools from {connection.provider}: {list(provider_tools.keys())}")
                    
                    # Add tools with user_id injection
                    for tool_name, tool_func in provider_tools.items():
                        tool_map[tool_name] = inject_user_id(tool_func, user_id)
                        logger.debug(f"Added tool {tool_name} to tool_map")
                        
                except Exception as e:
                    logger.error(f"MCP tools for provider {connection.provider} not available: {e}", exc_info=True)
                    continue
            
            return tool_map
            
        except Exception as e:
            logger.error(f"MCP tools not available: {e}", exc_info=True)
            return {}

