#!/bin/bash
# Confluence API Test Commands
# Source: Load credentials from .env file

cd "$(dirname "$0")"
source venv/bin/activate

# Load credentials
export $(grep -E '^CONFLUENCE_(URL|USERNAME|API_TOKEN)=' .env | xargs)

# Clean URL
BASE_URL=$(echo $CONFLUENCE_URL | sed 's|https://||' | sed 's|/wiki||' | sed 's|/$||')
USERNAME=$CONFLUENCE_USERNAME
TOKEN=$CONFLUENCE_API_TOKEN

echo "=========================================="
echo "Confluence API Test Commands"
echo "=========================================="
echo ""
echo "Base URL: $BASE_URL"
echo "Username: $USERNAME"
echo "Token: ${TOKEN:0:15}..."
echo ""
echo "=========================================="
echo ""

# Test 1: Basic site access
echo "1. Testing basic site access:"
echo "curl -v https://$BASE_URL --user $USERNAME:$TOKEN"
echo ""

# Test 2: Confluence wiki access
echo "2. Testing Confluence wiki access:"
echo "curl -v https://$BASE_URL/wiki --user $USERNAME:$TOKEN"
echo ""

# Test 3: Confluence REST API - Spaces
echo "3. Testing Confluence REST API (Spaces):"
echo "curl -v https://$BASE_URL/wiki/rest/api/space --user $USERNAME:$TOKEN"
echo ""

# Test 4: Jira API (to verify token works)
echo "4. Testing Jira API (verify token):"
echo "curl -v https://$BASE_URL/rest/api/3/myself --user $USERNAME:$TOKEN"
echo ""

# Test 5: Confluence content API
echo "5. Testing Confluence Content API:"
echo "curl -v 'https://$BASE_URL/wiki/rest/api/content?limit=1' --user $USERNAME:$TOKEN"
echo ""

echo "=========================================="
echo "To run any command, copy and paste it above"
echo "=========================================="
