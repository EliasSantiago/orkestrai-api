#!/bin/bash

# Script to update agent 5 with correct Tavily tool names

echo "🔧 Updating Agent 5 with correct Tavily tool names..."
echo ""

# Check if JWT token is provided
if [ -z "$1" ]; then
    echo "❌ Error: JWT token required"
    echo "Usage: ./update_agent_5_tools.sh YOUR_JWT_TOKEN"
    echo ""
    echo "To get a JWT token, use:"
    echo "curl -X POST 'http://localhost:8001/api/auth/login' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"username\": \"your_username\", \"password\": \"your_password\"}'"
    exit 1
fi

JWT_TOKEN="$1"
API_URL="http://localhost:8001"

# Get current agent 5 configuration
echo "📋 Getting current Agent 5 configuration..."
AGENT_RESPONSE=$(curl -s -X GET "${API_URL}/api/agents/5" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "accept: application/json")

echo "Current Agent 5:"
echo "$AGENT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$AGENT_RESPONSE"
echo ""

# Extract current tools and update them
echo "🔧 Updating tools..."

# Update agent 5 with corrected tool names
# This payload will update only the tools field
UPDATE_RESPONSE=$(curl -s -X PUT "${API_URL}/api/agents/5" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "tools": [
      "get_current_time",
      "tavily_search",
      "tavily_extract",
      "tavily_map",
      "tavily_crawl"
    ]
  }')

echo "✅ Update response:"
echo "$UPDATE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPDATE_RESPONSE"
echo ""

# Verify the update
echo "🔍 Verifying update..."
VERIFY_RESPONSE=$(curl -s -X GET "${API_URL}/api/agents/5" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "accept: application/json")

echo "Updated Agent 5:"
echo "$VERIFY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$VERIFY_RESPONSE"
echo ""

echo "✅ Done! Agent 5 has been updated with correct Tavily tool names."
echo ""
echo "Tool name changes:"
echo "  tavily_tavily-search  →  tavily_search"
echo "  tavily_tavily-extract →  tavily_extract"
echo "  tavily_tavily-map     →  tavily_map"
echo "  tavily_tavily-crawl   →  tavily_crawl"

