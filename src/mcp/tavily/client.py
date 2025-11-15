"""
Tavily MCP Client - Remote MCP server integration.

This client connects to Tavily's remote MCP server (https://mcp.tavily.com/mcp)
using HTTP + SSE. The server provides search, extract, map, and crawl tools.

Note: The Tavily MCP remote server may use SSE (Server-Sent Events) for streaming.
This implementation uses HTTP POST with JSON-RPC 2.0, which should work for most cases.
"""

import logging
import httpx
import json
from typing import Dict, List, Optional, Any
from src.mcp.client import MCPClient

logger = logging.getLogger(__name__)


class TavilyMCPClient(MCPClient):
    """
    Tavily MCP client that connects to Tavily's remote MCP server.
    
    This client uses HTTP + SSE to communicate with the remote MCP server.
    The server provides:
    - tavily-search: Real-time web search
    - tavily-extract: Extract data from web pages
    - tavily-map: Create structured map of websites
    - tavily-crawl: Systematically crawl websites
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Tavily MCP client.
        
        Args:
            config: Configuration dictionary with:
                - api_key: Tavily API key (required)
                - server_url: Optional custom server URL (defaults to official remote server)
        """
        super().__init__("tavily", config)
        # Accept both 'api_key' and 'access_token' for flexibility
        self.api_key = (config.get("api_key") or config.get("access_token") or "").strip()
        
        if not self.api_key:
            raise ValueError("Tavily API key is required. Provide 'api_key' or 'access_token' in credentials.")
        
        # Use remote MCP server URL with API key
        self.server_url = config.get(
            "server_url",
            f"https://mcp.tavily.com/mcp/?tavilyApiKey={self.api_key}"
        )
        
        self._client: Optional[httpx.AsyncClient] = None
        self._is_connected = False
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
    
    async def connect(self) -> bool:
        """Connect to Tavily MCP server and verify connection."""
        try:
            # Import Config to use SSL verification setting
            from src.config import Config
            
            self._client = httpx.AsyncClient(
                timeout=30.0,
                verify=Config.VERIFY_SSL  # Use system SSL verification setting
            )
            
            logger.info(f"Attempting to connect to Tavily MCP server: {self.server_url[:50]}...")
            
            # Test connection by listing tools
            tools = await self.list_tools()
            if tools:
                self._is_connected = True
                logger.info(f"Successfully connected to Tavily MCP server. Found {len(tools)} tools.")
                return True
            else:
                logger.warning("Connected to Tavily MCP server but no tools found")
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to connect to Tavily MCP server: {error_msg}", exc_info=True)
            # Re-raise with more context for better error messages
            raise RuntimeError(f"Failed to connect to Tavily MCP server: {error_msg}")
    
    async def disconnect(self):
        """Disconnect from Tavily MCP server."""
        if self._client:
            try:
                # Close the client properly before the event loop closes
                await self._client.aclose()
            except RuntimeError as e:
                # Ignore "Event loop is closed" errors during cleanup
                # This is expected when the event loop is closed before cleanup
                if "Event loop is closed" not in str(e):
                    logger.warning(f"Error closing Tavily HTTP client: {e}")
            except Exception as e:
                logger.warning(f"Error closing Tavily HTTP client: {e}")
            finally:
                self._client = None
        self._is_connected = False
        logger.info("Disconnected from Tavily MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from Tavily MCP server.
        
        Returns:
            List of tool definitions with name, description, and parameters
        """
        if self._tools_cache:
            return self._tools_cache
        
        try:
            # MCP protocol: tools/list request
            # The remote server uses HTTP POST with JSON-RPC 2.0
            response = await self._client.post(
                self.server_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            # Log response for debugging
            logger.info(f"Tavily MCP list_tools response status: {response.status_code}")
            logger.info(f"Tavily MCP list_tools response headers: {dict(response.headers)}")
            logger.info(f"Tavily MCP list_tools response content type: {response.headers.get('content-type', 'unknown')}")
            logger.info(f"Tavily MCP list_tools response content length: {len(response.content)}")
            
            # Log raw response for debugging
            if response.content:
                try:
                    response_text = response.text
                    logger.info(f"Tavily MCP list_tools response text (first 1000 chars): {response_text[:1000]}")
                except Exception as e:
                    logger.warning(f"Could not decode response as text: {e}")
                    logger.info(f"Tavily MCP list_tools response content (first 100 bytes): {response.content[:100]}")
            else:
                logger.warning("Tavily MCP list_tools response is empty")
            
            response.raise_for_status()
            
            # Check if response is empty
            if not response.content or len(response.content) == 0:
                raise RuntimeError("Tavily MCP server returned empty response. Check if the API key is valid and the server is accessible.")
            
            # Check if response is SSE format (Tavily MCP uses SSE)
            content_type = response.headers.get('content-type', '').lower()
            if 'text/event-stream' in content_type or 'event-stream' in content_type:
                logger.info("Tavily MCP server returned SSE format - parsing Server-Sent Events")
                # Parse SSE format
                # SSE format: event: message\n data: {...}\n\n
                response_text = response.text
                if response_text:
                    # Parse SSE lines
                    lines = response_text.split('\n')
                    data = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith('data: '):
                            json_str = line[6:]  # Remove 'data: ' prefix
                            try:
                                data = json.loads(json_str)
                                logger.debug(f"Parsed SSE data: {json_str[:200]}...")
                                break
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse SSE data line: {line[:100]} - {e}")
                                continue
                    
                    if data is None:
                        raise RuntimeError("Could not parse SSE response from Tavily MCP server. No valid 'data:' lines found.")
                else:
                    raise RuntimeError("Tavily MCP server returned empty SSE response")
            else:
                # Try to parse JSON (fallback for non-SSE responses)
                try:
                    data = response.json()
                except Exception as json_error:
                    logger.error(f"Failed to parse JSON response: {json_error}")
                    logger.error(f"Response text (first 500 chars): {response.text[:500] if response.text else 'empty'}")
                    raise RuntimeError(f"Tavily MCP server returned invalid JSON: {str(json_error)}. Response may be in a different format.")
            
            # Handle JSON-RPC 2.0 response
            if "result" in data:
                tools = data["result"].get("tools", [])
                self._tools_cache = tools
                logger.info(f"Retrieved {len(tools)} tools from Tavily MCP server")
                return tools
            elif "error" in data:
                error = data["error"]
                error_msg = error.get("message", str(error))
                logger.error(f"Error listing tools from Tavily MCP: {error_msg}")
                raise RuntimeError(f"Tavily MCP error: {error_msg}")
            else:
                logger.warning(f"Unexpected response format from Tavily MCP: {data}")
                raise RuntimeError(f"Unexpected response format from Tavily MCP: {data}")
                
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if e.response else str(e)
            logger.error(f"HTTP error listing tools from Tavily MCP: {e.response.status_code} - {error_text}")
            raise RuntimeError(f"HTTP error connecting to Tavily MCP: {e.response.status_code} - {error_text}")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error listing tools from Tavily MCP: {e}")
            raise RuntimeError(f"HTTP error connecting to Tavily MCP: {str(e)}")
        except Exception as e:
            logger.error(f"Error listing tools from Tavily MCP: {e}", exc_info=True)
            raise
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call a tool on the Tavily MCP server.
        
        Args:
            tool_name: Name of the tool to call (e.g., "tavily-search", "tavily-extract")
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to Tavily MCP server")
        
        try:
            # MCP protocol: tools/call request
            # Ensure client is still connected
            if not self._client:
                raise RuntimeError("Tavily HTTP client is not initialized")
            
            response = await self._client.post(
                self.server_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": kwargs
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            response.raise_for_status()
            
            # Check if response is SSE format (Tavily MCP uses SSE)
            content_type = response.headers.get('content-type', '').lower()
            if 'text/event-stream' in content_type or 'event-stream' in content_type:
                logger.debug(f"Tavily MCP call_tool returned SSE format - parsing Server-Sent Events")
                # Parse SSE format
                response_text = response.text
                if response_text:
                    # Parse SSE lines
                    lines = response_text.split('\n')
                    data = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith('data: '):
                            json_str = line[6:]  # Remove 'data: ' prefix
                            try:
                                data = json.loads(json_str)
                                break
                            except json.JSONDecodeError:
                                continue
                    
                    if data is None:
                        raise RuntimeError("Could not parse SSE response from Tavily MCP server")
                else:
                    raise RuntimeError("Tavily MCP server returned empty SSE response")
            else:
                # Try to parse JSON (fallback)
                try:
                    data = response.json()
                except Exception as json_error:
                    logger.error(f"Failed to parse JSON response: {json_error}")
                    raise RuntimeError(f"Tavily MCP server returned invalid JSON: {str(json_error)}")
            
            # Handle JSON-RPC 2.0 response
            if "result" in data:
                result = data["result"]
                # MCP tools/call returns { "content": [...] }
                if "content" in result and result["content"]:
                    # Extract the actual result from content array
                    content = result["content"][0]
                    if "text" in content:
                        # Parse JSON text if it's a string
                        try:
                            return json.loads(content["text"])
                        except (json.JSONDecodeError, TypeError):
                            return content["text"]
                    elif "json" in content:
                        return content["json"]
                    else:
                        return content
                else:
                    return result
            elif "error" in data:
                error = data["error"]
                error_msg = error.get("message", str(error))
                logger.error(f"Error calling Tavily tool {tool_name}: {error_msg}")
                raise RuntimeError(f"Tavily MCP error: {error_msg}")
            else:
                logger.warning(f"Unexpected response format from Tavily MCP: {data}")
                return data
                
        except RuntimeError as e:
            error_msg = str(e)
            # Check if it's an event loop error - these are handled by retry mechanism
            if "Event loop is closed" in error_msg:
                logger.debug(f"Event loop closed during Tavily tool call {tool_name} (will be retried)")
                raise
            else:
                logger.error(f"Runtime error calling Tavily tool {tool_name}: {error_msg}")
                raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Tavily tool {tool_name}: {e}")
            raise RuntimeError(f"Failed to call Tavily tool {tool_name}: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            # Check if it's an event loop error
            if "Event loop is closed" in error_msg:
                logger.debug(f"Event loop closed during Tavily tool call {tool_name} (will be retried)")
                raise RuntimeError(error_msg)
            logger.error(f"Error calling Tavily tool {tool_name}: {e}", exc_info=True)
            raise
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._is_connected

