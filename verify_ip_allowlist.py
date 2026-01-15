#!/usr/bin/env python3
"""Verify IP allowlist configuration and test connection"""

import os
import time
from dotenv import load_dotenv
from atlassian import Confluence
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", "").replace("/wiki", "").rstrip("/")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME", "")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "")

print("=" * 70)
print("IP Allowlist Verification & Connection Test")
print("=" * 70)
print()

# Get current IP
try:
    current_ip = requests.get("https://api.ipify.org", timeout=5).text
    print(f"📍 Your Current IP: {current_ip}")
    print(f"   Make sure this IP is in your allowlist!")
    print()
except:
    print("⚠️  Could not determine your IP address")
    print()

print("=" * 70)
print("Testing Connection (Multiple Attempts)")
print("=" * 70)
print()

# Test with atlassian library (this gets 403, which is progress)
cloud = '.atlassian.net' in CONFLUENCE_URL or '.atlassian.com' in CONFLUENCE_URL

print("Attempt 1: Using atlassian-python-api library")
try:
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        token=CONFLUENCE_API_TOKEN,
        cloud=cloud
    )
    spaces = confluence.get_all_spaces(start=0, limit=5)
    print(f"   ✅ SUCCESS! Found {len(spaces.get('results', []))} spaces")
    for space in spaces.get('results', [])[:3]:
        print(f"      • {space.get('name')} (key: {space.get('key')})")
    print()
    print("🎉 Connection is working! IP allowlist is configured correctly.")
    exit(0)
except Exception as e:
    error_str = str(e)
    if "403" in error_str or "FORBIDDEN" in error_str:
        print(f"   ⚠️  403 FORBIDDEN: {error_str[:80]}")
        print()
        print("   This means:")
        print("   ✅ Authentication is working")
        print("   ✅ IP allowlist might be working (no 401 error)")
        print("   ❌ But account still lacks Confluence API permissions")
        print()
        print("   The 403 error suggests the IP allowlist is NOT blocking,")
        print("   but there's still a permissions issue.")
    else:
        print(f"   ❌ Error: {error_str[:80]}")

print()
print("=" * 70)
print("Recommendations")
print("=" * 70)
print()

print("Since you've confirmed:")
print("  ✅ IP is in allowlist")
print("  ✅ Allowlist is enabled")
print("  ✅ Confluence is selected")
print()
print("But still getting 403, try these:")
print()
print("1. ⏰ Wait 2-3 minutes for allowlist to propagate")
print("   → Changes can take a few minutes to take effect")
print()
print("2. 🔑 Regenerate API Token")
print("   → Go to: https://id.atlassian.com/manage-profile/security/api-tokens")
print("   → Delete old token")
print("   → Create new token")
print("   → Update .env file")
print()
print("3. 🔍 Check API Permissions")
print("   → The 403 error specifically says 'cannot access Confluence'")
print("   → This might be a different permission than web UI access")
print("   → Check: https://admin.atlassian.com")
print("   → User management → Your account → Product access")
print()
print("4. 🌐 Try Different Endpoint")
print("   → Some endpoints might work even if /space doesn't")
print("   → Try: /rest/api/content instead")
print()

# Test alternative endpoint
print("=" * 70)
print("Testing Alternative Endpoint: /rest/api/content")
print("=" * 70)
try:
    content = confluence.get_all_pages_from_space("SD", start=0, limit=1)
    print("   ✅ Alternative endpoint works!")
except Exception as e:
    print(f"   ❌ Also failed: {str(e)[:80]}")

print()
print("=" * 70)
