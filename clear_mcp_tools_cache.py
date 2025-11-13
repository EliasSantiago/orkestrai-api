#!/usr/bin/env python3
"""
Clear MCP tools cache to force reloading tools with new names.
Run this after updating the dynamic_tools.py file.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.mcp.dynamic_tools import clear_tools_cache

if __name__ == "__main__":
    print("🧹 Clearing MCP tools cache...")
    clear_tools_cache()
    print("✅ Cache cleared successfully!")
    print("")
    print("The tools will be reloaded with correct names on the next agent request.")
    print("")
    print("Tool naming fix:")
    print("  tavily-search  → tavily_search")
    print("  tavily-extract → tavily_extract")
    print("  tavily-map     → tavily_map")
    print("  tavily-crawl   → tavily_crawl")

