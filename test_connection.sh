#!/bin/bash
# Quick Confluence Connection Test

cd "$(dirname "$0")"
source venv/bin/activate

echo "=========================================="
echo "Confluence Connection Test"
echo "=========================================="
echo ""

# Load credentials
export $(grep -E '^CONFLUENCE_(URL|USERNAME|API_TOKEN)=' .env | xargs)

echo "📋 Configuration:"
echo "   URL: $CONFLUENCE_URL"
echo "   Username: $CONFLUENCE_USERNAME"
echo "   Token: ${CONFLUENCE_API_TOKEN:0:15}..."
echo ""

echo "=========================================="
echo "Test 1: Application API Endpoint"
echo "=========================================="
RESULT=$(curl -s http://localhost:8000/confluence/spaces)
if echo "$RESULT" | grep -q "spaces"; then
    echo "✅ SUCCESS: Connection working!"
    echo "$RESULT" | python3 -m json.tool 2>/dev/null | head -10
elif echo "$RESULT" | grep -q "403"; then
    echo "⚠️  403 FORBIDDEN:"
    echo "   - Authentication: ✅ Working"
    echo "   - API Access: ❌ Blocked"
    echo "   - Issue: Account lacks Confluence API permissions"
    echo ""
    echo "   Solution: Check IP allowlist and API permissions"
elif echo "$RESULT" | grep -q "401"; then
    echo "❌ 401 UNAUTHORIZED:"
    echo "   - Authentication: ❌ Failed"
    echo "   - Issue: Invalid credentials or IP blocked"
else
    echo "Response: $RESULT"
fi

echo ""
echo "=========================================="
echo "Test 2: Direct Confluence API"
echo "=========================================="
BASE_URL=$(echo $CONFLUENCE_URL | sed 's|https://||' | sed 's|/wiki||' | sed 's|/$||')
RESULT=$(curl -s -w "\nHTTP_CODE:%{http_code}" "https://${BASE_URL}/wiki/rest/api/space" \
    -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
    -H "Accept: application/json")

HTTP_CODE=$(echo "$RESULT" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESULT" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS: API access working!"
    echo "$BODY" | python3 -m json.tool 2>/dev/null | head -10
elif [ "$HTTP_CODE" = "403" ]; then
    echo "⚠️  403 FORBIDDEN:"
    echo "   - Authentication: ✅ Working"
    echo "   - API Access: ❌ Blocked"
    echo "   - Possible causes:"
    echo "     • IP allowlist blocking access"
    echo "     • Account lacks Confluence API permissions"
    echo "     • Confluence not enabled for API access"
elif [ "$HTTP_CODE" = "401" ]; then
    echo "❌ 401 UNAUTHORIZED:"
    echo "   - Authentication: ❌ Failed"
    echo "   - Possible causes:"
    echo "     • Invalid API token"
    echo "     • IP allowlist blocking (even with valid credentials)"
    echo "     • Token expired or revoked"
else
    echo "⚠️  Unexpected response: HTTP $HTTP_CODE"
    echo "$BODY" | head -5
fi

echo ""
echo "=========================================="
echo "Test 3: Current IP Address"
echo "=========================================="
CURRENT_IP=$(curl -s https://api.ipify.org)
echo "Your IP: $CURRENT_IP"
echo ""
echo "⚠️  Make sure this IP is in your Atlassian IP allowlist!"
echo "   Go to: https://admin.atlassian.com → Security → IP allowlist"

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Connection is working!"
elif [ "$HTTP_CODE" = "403" ]; then
    echo "⚠️  Authentication works but API access is blocked"
    echo "   → Check IP allowlist configuration"
    echo "   → Verify Confluence API permissions"
elif [ "$HTTP_CODE" = "401" ]; then
    echo "❌ Authentication failed"
    echo "   → Verify API token is correct"
    echo "   → Check if IP allowlist is blocking access"
    echo "   → Try regenerating API token"
fi
echo ""
