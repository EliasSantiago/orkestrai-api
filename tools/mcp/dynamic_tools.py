"""
Dynamic MCP Tools - Automatically expose all tools from MCP servers.

This module dynamically creates tool wrappers for all tools available
from MCP servers, allowing agents to use all available tools without manual registration.
"""

import asyncio
import logging
import inspect
from typing import Dict, Any, Optional, Callable, List
from src.mcp.user_client_manager import get_user_mcp_manager
from src.database import SessionLocal

logger = logging.getLogger(__name__)

# Cache for tool definitions to avoid repeated calls
_tools_cache: Dict[tuple, List[Dict[str, Any]]] = {}


def clear_tools_cache(user_id: Optional[int] = None, provider: Optional[str] = None):
    """
    Clear the tools cache.
    
    Args:
        user_id: If provided, only clear cache for this user
        provider: If provided, only clear cache for this provider
    """
    global _tools_cache
    if user_id is not None and provider is not None:
        cache_key = (user_id, provider)
        if cache_key in _tools_cache:
            del _tools_cache[cache_key]
            logger.info(f"Cleared cache for {provider} (user {user_id})")
    else:
        _tools_cache.clear()
        logger.info("Cleared all tools cache")


def _get_google_calendar_tools_static() -> List[Dict[str, Any]]:
    """
    Get static tool definitions for Google Calendar.
    
    This is used directly to avoid async/event loop issues.
    Returns the same list that list_tools() would return.
    """
    return [
        {
            "name": "create_event",
            "description": "Create a new event in Google Calendar",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                    "summary": {"type": "string", "description": "Event title/summary"},
                    "description": {"type": "string", "description": "Event description"},
                    "start": {"type": "object", "description": "Event start time (ISO 8601)"},
                    "end": {"type": "object", "description": "Event end time (ISO 8601)"},
                    "location": {"type": "string", "description": "Event location"},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of attendee emails"}
                },
                "required": ["summary", "start", "end"]
            }
        },
        {
            "name": "list_events",
            "description": "List events from Google Calendar",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                    "time_min": {"type": "string", "description": "Lower bound for event end time (ISO 8601)"},
                    "time_max": {"type": "string", "description": "Upper bound for event start time (ISO 8601)"},
                    "max_results": {"type": "integer", "description": "Maximum number of events"},
                    "q": {"type": "string", "description": "Free text search"}
                }
            }
        },
        {
            "name": "get_event",
            "description": "Get a specific event by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                    "event_id": {"type": "string", "description": "Event ID"}
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "update_event",
            "description": "Update an existing event",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                    "event_id": {"type": "string", "description": "Event ID"},
                    "summary": {"type": "string", "description": "Event title/summary"},
                    "description": {"type": "string", "description": "Event description"},
                    "start": {"type": "object", "description": "Event start time"},
                    "end": {"type": "object", "description": "Event end time"},
                    "location": {"type": "string", "description": "Event location"}
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "delete_event",
            "description": "Delete an event from Google Calendar",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                    "event_id": {"type": "string", "description": "Event ID"}
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "list_calendars",
            "description": "List all calendars accessible by the user",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]


def _get_mcp_client_for_user(user_id: int, provider: str):
    """Get MCP client for user and provider."""
    logger.info(f"Getting MCP client for provider '{provider}' (user {user_id})")
    db = SessionLocal()
    try:
        manager = get_user_mcp_manager()
        # Use _run_async to handle async context properly
        # Retry logic to handle event loop issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.debug(f"Attempting to get {provider} client (attempt {attempt + 1}/{max_retries})")
                client = _run_async(manager.get_client_for_user(db, user_id, provider))
                if not client:
                    logger.error(f"{provider} client is None for user {user_id}")
                    raise RuntimeError(f"{provider} not connected")
                if not client.is_connected:
                    logger.error(f"{provider} client is not connected for user {user_id}")
                    raise RuntimeError(f"{provider} connection is not active")
                logger.info(f"Successfully got {provider} client for user {user_id}")
                return client
            except RuntimeError as e:
                error_msg = str(e)
                if "Event loop is closed" in error_msg and attempt < max_retries - 1:
                    logger.warning(f"Event loop issue on attempt {attempt + 1}, retrying...")
                    import time
                    time.sleep(0.1)  # Small delay before retry
                    continue
                logger.error(f"Error getting {provider} client: {error_msg}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error getting {provider} client: {e}", exc_info=True)
                raise
    finally:
        db.close()


def _run_async(coro):
    """
    Run async function synchronously.
    
    This function handles the case where we're in an async context (FastAPI)
    but need to call async code from a synchronous tool wrapper.
    
    Strategy:
    1. Always create a new event loop in a separate thread
    2. This avoids conflicts with existing loops that might be closed
    3. Use proper synchronization to avoid "Event loop is closed" errors
    """
    import asyncio
    import threading
    import concurrent.futures
    
    # Always use a new thread with a new event loop
    # This is the safest approach to avoid event loop conflicts
    result = None
    exception = None
    event = threading.Event()
    
    def run_in_thread():
        nonlocal result, exception
        new_loop = None
        try:
            # Create a completely new event loop in this thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(coro)
            except Exception as e:
                exception = e
        except Exception as e:
            exception = e
        finally:
            # Properly close the loop - but only after all work is done
            if new_loop and not new_loop.is_closed():
                try:
                    # Step 1: Wait for all pending tasks to complete
                    pending = [t for t in asyncio.all_tasks(new_loop) if not t.done()]
                    if pending:
                        # Cancel pending tasks
                        for task in pending:
                            if not task.done():
                                task.cancel()
                        # Wait for cancellation
                        if pending:
                            try:
                                new_loop.run_until_complete(
                                    asyncio.gather(*pending, return_exceptions=True)
                                )
                            except Exception:
                                pass
                    
                    # Step 2: Run a final cleanup task to allow HTTP clients to close
                    # This gives httpx.AsyncClient time to close connections properly
                    try:
                        # Run a small async task to ensure all cleanup happens
                        async def cleanup():
                            # Small delay to allow HTTP client cleanup
                            await asyncio.sleep(0.1)
                            # Force garbage collection of any remaining resources
                            import gc
                            gc.collect()
                        
                        new_loop.run_until_complete(cleanup())
                    except Exception:
                        pass
                    
                    # Step 3: Small synchronous delay to ensure cleanup completes
                    import time
                    time.sleep(0.1)
                    
                except Exception:
                    pass
                finally:
                    # Step 4: Close the loop only after all cleanup is done
                    try:
                        if not new_loop.is_closed():
                            # Shutdown default executor if it exists
                            try:
                                new_loop.shutdown_default_executor()
                            except Exception:
                                pass
                            new_loop.close()
                    except Exception:
                        pass
            event.set()  # Signal completion
    
    thread = threading.Thread(target=run_in_thread, daemon=False)
    thread.start()
    
    # Wait for completion with timeout
    # Use shorter timeout for list_tools (5s) vs tool calls (30s)
    # Increased from 2s to 5s to allow for SSE parsing
    timeout = 5 if "list_tools" in str(coro) else 30
    if not event.wait(timeout=timeout):
        raise TimeoutError(f"Tool execution timed out after {timeout}s")
    
    # Wait for thread to finish
    thread.join(timeout=1)
    
    if exception:
        raise exception
    
    return result


def create_dynamic_mcp_tool(provider: str, tool_name: str, tool_def: Dict[str, Any]) -> Callable:
    """
    Create a dynamic tool wrapper for an MCP tool.
    
    Args:
        provider: MCP provider name
        tool_name: Name of the tool
        tool_def: Tool definition from MCP server
        
    Returns:
        Tool function that can be used by agents
    """
    # Extract parameters from tool definition
    parameters = tool_def.get("inputSchema", {}).get("properties", {})
    required = tool_def.get("inputSchema", {}).get("required", [])
    
    # Create function signature dynamically
    # Note: user_id will be injected by inject_user_id, so we don't include it in the signature
    def dynamic_tool(**kwargs) -> Dict[str, Any]:
        """
        Dynamic MCP tool wrapper.
        
        This tool is automatically generated from the MCP server.
        """
        # Extract user_id from kwargs (injected by inject_user_id)
        user_id = kwargs.pop('user_id', None)
        if not user_id:
            return {'status': 'error', 'error': 'user_id is required'}
        
        try:
            client = _get_mcp_client_for_user(user_id, provider)
            
            # Call tool on MCP client
            # Retry logic to handle event loop issues
            max_retries = 2
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    result = _run_async(client.call_tool(tool_name, **kwargs))
                    return {
                        'status': 'success',
                        'data': result
                    }
                except (RuntimeError, TimeoutError) as e:
                    error_msg = str(e)
                    if "Event loop is closed" in error_msg and attempt < max_retries - 1:
                        logger.warning(f"Event loop issue on attempt {attempt + 1}, retrying...")
                        import time
                        time.sleep(0.1)  # Small delay before retry
                        last_exception = e
                        continue
                    else:
                        raise
                except Exception as e:
                    last_exception = e
                    raise
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
                
        except Exception as e:
            logger.error(f"Error calling {provider} tool {tool_name}: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    # Set function metadata
    # Handle tool naming properly - same logic as in get_all_mcp_tools
    if tool_name.startswith(f"{provider}-"):
        # Strip provider prefix with hyphen and replace remaining hyphens
        clean_name = tool_name[len(provider)+1:].replace("-", "_")
        prefixed_name = f"{provider}_{clean_name}"
    elif tool_name.startswith(f"{provider}_"):
        # Already properly prefixed with underscore
        prefixed_name = tool_name.replace("-", "_")
    else:
        # Add provider prefix
        prefixed_name = f"{provider}_{tool_name}".replace("-", "_")
    
    dynamic_tool.__name__ = prefixed_name
    dynamic_tool.__doc__ = tool_def.get("description", f"{provider} MCP tool: {tool_name}")
    
    # Create signature with parameters (without user_id - it will be injected)
    sig_params = []
    
    # Add required parameters first (no default)
    for param_name in required:
        if param_name in parameters:
            param_def = parameters[param_name]
            param_type = param_def.get("type", "string")
            
            # Map JSON schema types to Python types
            if param_type == "integer":
                annotation = int
            elif param_type == "number":
                annotation = float
            elif param_type == "boolean":
                annotation = bool
            elif param_type == "array":
                annotation = List[Any]
            elif param_type == "object":
                annotation = Dict[str, Any]
            else:
                annotation = str
            
            sig_params.append(
                inspect.Parameter(
                    param_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=inspect.Parameter.empty,
                    annotation=annotation
                )
            )
    
    # Add optional parameters after (with default=None)
    for param_name, param_def in parameters.items():
        if param_name not in required:
            param_type = param_def.get("type", "string")
            
            # Map JSON schema types to Python types
            if param_type == "integer":
                annotation = Optional[int]
            elif param_type == "number":
                annotation = Optional[float]
            elif param_type == "boolean":
                annotation = Optional[bool]
            elif param_type == "array":
                annotation = Optional[List[Any]]
            elif param_type == "object":
                annotation = Optional[Dict[str, Any]]
            else:
                annotation = Optional[str]
            
            sig_params.append(
                inspect.Parameter(
                    param_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=annotation
                )
            )
    
    dynamic_tool.__signature__ = inspect.Signature(sig_params)
    
    return dynamic_tool


def get_all_mcp_tools(user_id: int, provider: str) -> Dict[str, Callable]:
    """
    Get all available tools for an MCP provider.
    
    This function dynamically discovers all tools from the MCP provider
    and creates wrapper functions for them.
    
    Args:
        user_id: User ID
        provider: MCP provider name
        
    Returns:
        Dictionary mapping tool names to tool functions
    """
    try:
        logger.info(f"Getting MCP tools for provider '{provider}' (user {user_id})")
        
        # Check cache first
        cache_key = (user_id, provider)
        if cache_key in _tools_cache:
            logger.info(f"Using cached tools for {provider} (user {user_id})")
            tools_def = _tools_cache[cache_key]
        else:
            logger.info(f"Cache miss for {provider} (user {user_id}), loading from MCP server")
            # For Google Calendar, use static list directly to avoid async issues
            # since list_tools() returns a static list anyway
            if provider == "google_calendar":
                logger.debug(f"Using static tools for {provider} (user {user_id})")
                tools_def = _get_google_calendar_tools_static()
                if tools_def:
                    _tools_cache[cache_key] = tools_def
                    logger.info(f"Cached tools for {provider} (user {user_id})")
                else:
                    logger.error(f"Could not get tools for {provider} for user {user_id}")
                    return {}
            else:
                # For other providers, try to get tools dynamically
                try:
                    logger.debug(f"Getting tools dynamically for {provider} (user {user_id})")
                    client = _get_mcp_client_for_user(user_id, provider)
                    if not client:
                        logger.error(f"Could not get MCP client for {provider} (user {user_id})")
                        return {}
                    # Try to get tools with a short timeout (1 second for list_tools)
                    logger.debug(f"Calling list_tools() for {provider} (user {user_id})")
                    tools_def = _run_async(client.list_tools())
                    logger.debug(f"Got {len(tools_def) if tools_def else 0} tools from {provider} (user {user_id})")
                    # Cache the result
                    if tools_def:
                        _tools_cache[cache_key] = tools_def
                        logger.debug(f"Cached tools for {provider} (user {user_id})")
                    else:
                        logger.warning(f"No tools returned from {provider} for user {user_id}")
                except (TimeoutError, RuntimeError) as e:
                    error_msg = str(e)
                    logger.error(f"Timeout/Error getting tools from {provider} for user {user_id}: {error_msg}", exc_info=True)
                    # Don't return empty dict immediately - try to see if it's a transient error
                    if "Event loop is closed" in error_msg:
                        logger.warning(f"Event loop issue for {provider}, this may be transient")
                    return {}
                except Exception as e:
                    logger.error(f"Unexpected error getting tools from {provider} for user {user_id}: {e}", exc_info=True)
                    return {}
        
        tools = {}
        
        if not tools_def:
            logger.warning(f"No tools found from {provider} for user {user_id}")
            return {}
        
        logger.debug(f"Processing {len(tools_def)} tool definitions for {provider} (user {user_id})")
        
        for tool_def in tools_def:
            tool_name = tool_def.get("name", "")
            if tool_name:
                try:
                    # Create dynamic tool wrapper
                    tool_func = create_dynamic_mcp_tool(provider, tool_name, tool_def)
                    
                    # Handle tool naming properly
                    # If tool name already starts with provider name (with hyphen or underscore),
                    # strip it and normalize to use underscore separator
                    # Example: "tavily-search" -> "tavily_search" (not "tavily_tavily-search")
                    if tool_name.startswith(f"{provider}-"):
                        # Strip provider prefix with hyphen and replace remaining hyphens
                        clean_name = tool_name[len(provider)+1:].replace("-", "_")
                        prefixed_name = f"{provider}_{clean_name}"
                    elif tool_name.startswith(f"{provider}_"):
                        # Already properly prefixed with underscore
                        prefixed_name = tool_name.replace("-", "_")
                    else:
                        # Add provider prefix
                        prefixed_name = f"{provider}_{tool_name}".replace("-", "_")
                    
                    tools[prefixed_name] = tool_func
                    logger.debug(f"Created tool wrapper: {prefixed_name} (original: {tool_name})")
                except Exception as tool_error:
                    logger.error(f"Error creating tool wrapper for {tool_name}: {tool_error}", exc_info=True)
                    continue
        
        logger.info(f"Loaded {len(tools)} {provider} tools for user {user_id}: {list(tools.keys())}")
        return tools
    except Exception as e:
        logger.error(f"Error getting {provider} tools for user {user_id}: {e}")
        return {}

