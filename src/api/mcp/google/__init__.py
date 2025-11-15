"""
Google MCP OAuth endpoints.

This module contains OAuth endpoints for Google MCP providers.
"""

from src.api.mcp.google.calendar_oauth import router as google_calendar_oauth_router, legacy_router as google_calendar_oauth_legacy_router

__all__ = ['google_calendar_oauth_router', 'google_calendar_oauth_legacy_router']

