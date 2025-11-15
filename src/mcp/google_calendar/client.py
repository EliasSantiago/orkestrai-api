"""
Google Calendar MCP Client - Direct integration with Google Calendar API.

This client connects directly to Google Calendar API (https://www.googleapis.com/calendar/v3)
using OAuth 2.0 tokens. Each user connects their own Google account.
"""

import logging
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime, timedelta
from src.mcp.client import MCPClient

logger = logging.getLogger(__name__)


class GoogleCalendarClient(MCPClient):
    """
    Google Calendar API client that connects to Google Calendar REST API.
    
    This client uses OAuth 2.0 tokens which users obtain by connecting
    their Google account. Supports creating, reading, updating, and deleting events.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Google Calendar API client.
        
        Args:
            config: Configuration dictionary with:
                - access_token: OAuth 2.0 access token (required)
                - refresh_token: OAuth 2.0 refresh token (optional, for token refresh)
                - client_id: Google OAuth client ID (optional, for token refresh)
                - client_secret: Google OAuth client secret (optional, for token refresh)
        """
        super().__init__("google_calendar", config)
        self.access_token = config.get("access_token", "").strip()
        self.refresh_token = config.get("refresh_token", "").strip()
        self.client_id = config.get("client_id", "").strip()
        self.client_secret = config.get("client_secret", "").strip()
        
        if not self.access_token:
            raise ValueError("Google Calendar access token is required")
        
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self._client: Optional[httpx.AsyncClient] = None
        self._is_connected = False
    
    async def connect(self) -> bool:
        """Connect to Google Calendar API and verify token."""
        try:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                verify=True
            )
            
            # Test connection by fetching calendar list
            response = await self._client.get(
                "/users/me/calendarList",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                self._is_connected = True
                logger.info("Successfully connected to Google Calendar API")
                return True
            elif response.status_code == 401:
                # Token might be expired, try to refresh if refresh_token is available
                if self.refresh_token and self.client_id and self.client_secret:
                    if await self._refresh_access_token():
                        # Retry connection
                        response = await self._client.get(
                            "/users/me/calendarList",
                            headers={
                                "Authorization": f"Bearer {self.access_token}",
                                "Content-Type": "application/json"
                            }
                        )
                        if response.status_code == 200:
                            self._is_connected = True
                            logger.info("Successfully connected to Google Calendar API (after token refresh)")
                            return True
                
                error_data = response.json() if response.content else {}
                raise RuntimeError(
                    f"Authentication failed: Invalid or expired token. "
                    f"Error: {error_data.get('error', {}).get('message', 'Unauthorized')}"
                )
            else:
                error_text = response.text
                raise RuntimeError(f"Failed to connect to Google Calendar API: {response.status_code} - {error_text}")
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error connecting to Google Calendar API: {e}")
            raise RuntimeError(f"Failed to connect to Google Calendar API: {str(e)}")
        except Exception as e:
            logger.error(f"Error connecting to Google Calendar API: {e}")
            raise RuntimeError(f"Failed to connect to Google Calendar API: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from Google Calendar API."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._is_connected = False
        logger.info("Disconnected from Google Calendar API")
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._is_connected
    
    async def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token"
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data.get("access_token", "")
                    logger.info("Successfully refreshed Google Calendar access token")
                    return True
                else:
                    logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to Google Calendar API."""
        if not self._is_connected or not self._client:
            raise RuntimeError("Not connected to Google Calendar API. Call connect() first.")
        
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        response = await self._client.request(
            method,
            endpoint,
            headers=headers,
            **kwargs
        )
        
        if response.status_code == 401:
            # Try to refresh token if possible
            if self.refresh_token and self.client_id and self.client_secret:
                if await self._refresh_access_token():
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = await self._client.request(method, endpoint, headers=headers, **kwargs)
            
            if response.status_code == 401:
                error_data = response.json() if response.content else {}
                raise RuntimeError(
                    f"Authentication failed: {error_data.get('error', {}).get('message', 'Invalid token')}"
                )
        
        response.raise_for_status()
        return response.json() if response.content else {}
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools (operations) supported by this client.
        
        Returns a list of tool definitions compatible with MCP format.
        
        Note: This is async to match the MCPClient interface, but it returns
        a static list immediately without any async operations.
        """
        # Return immediately - no async operations needed
        # This is just a static list of available tools
        return [
            {
                "name": "create_event",
                "description": "Create a new event in Google Calendar",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID (default: 'primary' for primary calendar)"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Event title/summary"
                        },
                        "description": {
                            "type": "string",
                            "description": "Event description"
                        },
                        "start": {
                            "type": "object",
                            "description": "Event start time (ISO 8601 format or datetime object)"
                        },
                        "end": {
                            "type": "object",
                            "description": "Event end time (ISO 8601 format or datetime object)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Event location"
                        },
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of attendee email addresses"
                        }
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
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID (default: 'primary')"
                        },
                        "time_min": {
                            "type": "string",
                            "description": "Lower bound (exclusive) for an event's end time (ISO 8601)"
                        },
                        "time_max": {
                            "type": "string",
                            "description": "Upper bound (exclusive) for an event's start time (ISO 8601)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of events to return"
                        },
                        "q": {
                            "type": "string",
                            "description": "Free text search terms"
                        }
                    }
                }
            },
            {
                "name": "get_event",
                "description": "Get a specific event by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID (default: 'primary')"
                        },
                        "event_id": {
                            "type": "string",
                            "description": "Event ID"
                        }
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
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID (default: 'primary')"
                        },
                        "event_id": {
                            "type": "string",
                            "description": "Event ID"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Event title/summary"
                        },
                        "description": {
                            "type": "string",
                            "description": "Event description"
                        },
                        "start": {
                            "type": "object",
                            "description": "Event start time"
                        },
                        "end": {
                            "type": "object",
                            "description": "Event end time"
                        },
                        "location": {
                            "type": "string",
                            "description": "Event location"
                        }
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
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID (default: 'primary')"
                        },
                        "event_id": {
                            "type": "string",
                            "description": "Event ID"
                        }
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
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a Google Calendar API tool/operation."""
        # Normalize parameter names (handle variations from LLM)
        normalized_kwargs = kwargs.copy()
        
        # Map common variations to expected parameter names
        if "start_time" in normalized_kwargs and "start" not in normalized_kwargs:
            normalized_kwargs["start"] = normalized_kwargs.pop("start_time")
        if "end_time" in normalized_kwargs and "end" not in normalized_kwargs:
            normalized_kwargs["end"] = normalized_kwargs.pop("end_time")
        
        if tool_name == "create_event":
            return await self.create_event(**normalized_kwargs)
        elif tool_name == "list_events":
            return await self.list_events(**normalized_kwargs)
        elif tool_name == "get_event":
            return await self.get_event(**normalized_kwargs)
        elif tool_name == "update_event":
            return await self.update_event(**normalized_kwargs)
        elif tool_name == "delete_event":
            return await self.delete_event(**normalized_kwargs)
        elif tool_name == "list_calendars":
            return await self.list_calendars(**normalized_kwargs)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _format_datetime(self, dt: Any) -> Dict[str, str]:
        """
        Format datetime for Google Calendar API.
        
        Accepts:
        - ISO 8601 string (e.g., "2025-11-10T18:00:00-03:00")
        - datetime object
        - dict with dateTime key (already formatted)
        """
        # If already a dict with dateTime, return as is
        if isinstance(dt, dict):
            if "dateTime" in dt:
                return dt
            # If it's a dict but not formatted, try to extract datetime
            if "date" in dt:
                return {"date": dt["date"]}
        
        if isinstance(dt, str):
            # Try to parse ISO format
            try:
                # Handle ISO format with or without timezone
                if 'T' in dt:
                    # ISO format with time
                    dt_obj = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                    return {"dateTime": dt_obj.isoformat()}
                else:
                    # Date only
                    return {"date": dt}
            except Exception as e:
                logger.warning(f"Could not parse datetime string '{dt}': {e}, using as-is")
                # If parsing fails, assume it's already in the right format
                return {"dateTime": dt}
        
        if isinstance(dt, datetime):
            return {"dateTime": dt.isoformat()}
        
        # Fallback: convert to string
        return {"dateTime": str(dt)}
    
    async def create_event(
        self,
        summary: str,
        start: Any,
        end: Any,
        calendar_id: str = "primary",
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        **kwargs  # Accept additional parameters to avoid errors
    ) -> Dict[str, Any]:
        """
        Create a new event in Google Calendar.
        
        Args:
            summary: Event title/summary (required)
            start: Start time - can be ISO 8601 string, datetime object, or dict (required)
            end: End time - can be ISO 8601 string, datetime object, or dict (required)
            calendar_id: Calendar ID (default: "primary")
            description: Event description (optional)
            location: Event location (optional)
            attendees: List of attendee email addresses (optional)
        """
        # Ignore any extra kwargs to avoid errors
        logger.debug(f"Creating event: summary={summary}, start={start}, end={end}")
        
        event_data = {
            "summary": summary,
            "start": self._format_datetime(start),
            "end": self._format_datetime(end)
        }
        
        if description:
            event_data["description"] = description
        if location:
            event_data["location"] = location
        if attendees:
            event_data["attendees"] = [{"email": email} for email in attendees]
        
        logger.debug(f"Event data: {event_data}")
        return await self._request("POST", f"/calendars/{calendar_id}/events", json=event_data)
    
    async def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: Optional[int] = None,
        q: Optional[str] = None
    ) -> Dict[str, Any]:
        """List events from Google Calendar."""
        params = {}
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        if max_results:
            params["maxResults"] = max_results
        if q:
            params["q"] = q
        
        return await self._request("GET", f"/calendars/{calendar_id}/events", params=params)
    
    async def get_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Get a specific event by ID."""
        return await self._request("GET", f"/calendars/{calendar_id}/events/{event_id}")
    
    async def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        summary: Optional[str] = None,
        description: Optional[str] = None,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing event."""
        # First get the existing event
        existing_event = await self.get_event(event_id, calendar_id)
        
        # Update only provided fields
        if summary:
            existing_event["summary"] = summary
        if description:
            existing_event["description"] = description
        if start:
            existing_event["start"] = self._format_datetime(start)
        if end:
            existing_event["end"] = self._format_datetime(end)
        if location:
            existing_event["location"] = location
        
        return await self._request("PUT", f"/calendars/{calendar_id}/events/{event_id}", json=existing_event)
    
    async def delete_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Delete an event from Google Calendar."""
        await self._request("DELETE", f"/calendars/{calendar_id}/events/{event_id}")
        return {"status": "deleted", "event_id": event_id}
    
    async def list_calendars(self) -> Dict[str, Any]:
        """List all calendars accessible by the user."""
        return await self._request("GET", "/users/me/calendarList")

