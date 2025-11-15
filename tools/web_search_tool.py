"""
Web Search Tool - Shared tool for internet search.

This tool allows agents to search the internet for current information.
Uses Tavily Search API (optimized for AI agents) or Google Custom Search as fallback.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx
from src.config import Config

logger = logging.getLogger(__name__)

# API endpoints
TAVILY_API_URL = "https://api.tavily.com/search"
GOOGLE_CUSTOM_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def tavily_web_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic"
) -> dict:
    """
    Search the internet for information using Tavily Search API.
    
    This tool searches the web and returns relevant results with citations.
    It uses Tavily Search API (optimized for AI agents) by default,
    with Google Custom Search as fallback.
    
    Args:
        query: Search query (required)
        max_results: Maximum number of results to return (default: 5, max: 10)
        search_depth: Search depth - "basic" (faster) or "advanced" (more thorough, default: "basic")
        
    Returns:
        dict with:
        - status: 'success' or 'error'
        - results: List of search results with title, url, content, score
        - query: The search query used
        - total_results: Total number of results found
        
    Example:
        >>> tavily_web_search("latest news about AI")
        {
            'status': 'success',
            'results': [
                {
                    'title': 'AI News Article',
                    'url': 'https://example.com/article',
                    'content': 'Article content...',
                    'score': 0.95
                }
            ],
            'query': 'latest news about AI',
            'total_results': 5
        }
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return {
                'status': 'error',
                'error': 'Search query is required',
                'query': query
            }
        
        query = query.strip()
        max_results = min(max(1, max_results), 10)  # Clamp between 1 and 10
        
        # Try Tavily first (optimized for AI agents)
        if Config.TAVILY_API_KEY:
            return _search_with_tavily(query, max_results, search_depth)
        
        # Fallback to Google Custom Search
        if Config.GOOGLE_CUSTOM_SEARCH_API_KEY and Config.GOOGLE_CUSTOM_SEARCH_ENGINE_ID:
            return _search_with_google(query, max_results)
        
        # No API keys configured
        return {
            'status': 'error',
            'error': (
                'Web search is not configured. '
                'Please set TAVILY_API_KEY (recommended) or '
                'GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID in your .env file.'
            ),
            'query': query
        }
    
    except Exception as e:
        logger.error(f"Error in web_search: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': f'Error performing web search: {str(e)}',
            'query': query
        }


def _search_with_tavily(query: str, max_results: int, search_depth: str) -> dict:
    """
    Search using Tavily API (optimized for AI agents).
    
    Tavily provides:
    - Structured results with content snippets
    - Relevance scores
    - Source citations
    - Fast response times
    """
    try:
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "api_key": Config.TAVILY_API_KEY,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": True,  # Get AI-generated answer summary
            "include_raw_content": False,  # Don't include full page content
        }
        
        logger.debug(f"Searching with Tavily: {query}")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(TAVILY_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        # Parse Tavily response
        results = []
        for result in data.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
            })
        
        # Include AI-generated answer if available
        answer = data.get("answer", "")
        
        return {
            'status': 'success',
            'results': results,
            'query': query,
            'total_results': len(results),
            'answer': answer,  # AI-generated summary (if available)
            'provider': 'tavily'
        }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"Tavily API error: {e.response.status_code} - {e.response.text}")
        return {
            'status': 'error',
            'error': f'Tavily API error: {e.response.status_code}',
            'query': query
        }
    except Exception as e:
        logger.error(f"Error with Tavily search: {e}", exc_info=True)
        # Try fallback if available
        if Config.GOOGLE_CUSTOM_SEARCH_API_KEY and Config.GOOGLE_CUSTOM_SEARCH_ENGINE_ID:
            logger.info("Falling back to Google Custom Search")
            return _search_with_google(query, max_results)
        raise


def _search_with_google(query: str, max_results: int) -> dict:
    """
    Search using Google Custom Search API (fallback).
    
    Note: Requires Google Custom Search Engine setup.
    """
    try:
        params = {
            "key": Config.GOOGLE_CUSTOM_SEARCH_API_KEY,
            "cx": Config.GOOGLE_CUSTOM_SEARCH_ENGINE_ID,
            "q": query,
            "num": min(max_results, 10),  # Google allows max 10
        }
        
        logger.debug(f"Searching with Google Custom Search: {query}")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(GOOGLE_CUSTOM_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Parse Google response
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "content": item.get("snippet", ""),
                "score": 1.0,  # Google doesn't provide relevance scores
            })
        
        return {
            'status': 'success',
            'results': results,
            'query': query,
            'total_results': len(results),
            'provider': 'google'
        }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Custom Search API error: {e.response.status_code} - {e.response.text}")
        return {
            'status': 'error',
            'error': f'Google Custom Search API error: {e.response.status_code}',
            'query': query
        }
    except Exception as e:
        logger.error(f"Error with Google Custom Search: {e}", exc_info=True)
        raise

