#!/bin/bash
# Properly formatted curl commands for Confluence API testing
# Handles API tokens with special characters correctly

cd "$(dirname "$0")"
source venv/bin/activate

# Load credentials
export $(grep -E '^CONFLUENCE_(URL|USERNAME|API_TOKEN)=' .env | xargs)

BASE_URL=$(echo $CONFLUENCE_URL | sed 's|https://||' | sed 's|/wiki||' | sed 's|/$||')
USERNAME=$CONFLUENCE_USERNAME
TOKEN=$CONFLUENCE_API_TOKEN

echo "=========================================="
echo "Confluence API Test - Proper Format"
echo "=========================================="
echo ""

# Method 1: Using --user with proper quoting (recommended)
echo "1. Basic Auth with --user (recommended):"
echo "curl -v 'https://${BASE_URL}/wiki/rest/api/space' \\"
echo "  --user '${USERNAME}:${TOKEN}' \\"
echo "  -H 'Accept: application/json'"
echo ""

# Method 2: Using -u shorthand
echo "2. Using -u shorthand:"
echo "curl -v 'https://${BASE_URL}/wiki/rest/api/space' \\"
echo "  -u '${USERNAME}:${TOKEN}' \\"
echo "  -H 'Accept: application/json'"
echo ""

# Method 3: Manual Basic Auth header (if --user doesn't work)
echo "3. Manual Basic Auth header:"
AUTH_HEADER=$(echo -n "${USERNAME}:${TOKEN}" | base64)
echo "curl -v 'https://${BASE_URL}/wiki/rest/api/space' \\"
echo "  -H 'Authorization: Basic ${AUTH_HEADER}' \\"
echo "  -H 'Accept: application/json'"
echo ""

# Method 4: Test with Jira API first (to verify token)
echo "4. Test Jira API (verify token works):"
echo "curl -v 'https://${BASE_URL}/rest/api/3/myself' \\"
echo "  -u '${USERNAME}:${TOKEN}' \\"
echo "  -H 'Accept: application/json'"
echo ""

echo "=========================================="
echo "Quick Test (copy and run):"
echo "=========================================="
echo ""
echo "curl -v 'https://${BASE_URL}/wiki/rest/api/space' \\"
echo "  -u '${USERNAME}:${TOKEN}' \\"
echo "  -H 'Accept: application/json'"
echo ""
