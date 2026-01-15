#!/usr/bin/env python3
"""Comprehensive Confluence API diagnostic script"""

import os
import sys
from dotenv import load_dotenv
from atlassian import Confluence
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", "").replace("/wiki", "").rstrip("/")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME", "")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "")

print("=" * 70)
print("COMPREHENSIVE CONFLUENCE API DIAGNOSTIC")
print("=" * 70)
print()

# Basic info
print("📋 Configuration:")
print(f"   URL: {CONFLUENCE_URL}")
print(f"   Username: {CONFLUENCE_USERNAME}")
print(f"   Token: {CONFLUENCE_API_TOKEN[:15]}... (length: {len(CONFLUENCE_API_TOKEN)})")
print()

# Determine cloud
cloud = '.atlassian.net' in CONFLUENCE_URL or '.atlassian.com' in CONFLUENCE_URL
print(f"🌐 Cloud Mode: {cloud}")
print()

# Test 1: Direct HTTP request
print("=" * 70)
print("TEST 1: Direct HTTP Request to Confluence API")
print("=" * 70)
try:
    # Try the base Confluence API endpoint
    api_url = f"{CONFLUENCE_URL}/wiki/rest/api/space"
    response = requests.get(
        api_url,
        auth=HTTPBasicAuth(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=10
    )
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS: Direct API access works!")
    elif response.status_code == 403:
        print("   ❌ 403 FORBIDDEN: Account lacks API access to Confluence")
        print()
        print("   🔍 This means:")
        print("      • Your credentials are VALID")
        print("      • Authentication succeeded")
        print("      • But your account doesn't have permission to use Confluence API")
        print()
        print("   💡 Possible causes:")
        print("      1. Confluence is not enabled for your Atlassian site")
        print("      2. Your account has web UI access but not API access")
        print("      3. API access needs to be explicitly granted")
        print("      4. The API token might be scoped to Jira only")
    elif response.status_code == 401:
        print("   ❌ 401 UNAUTHORIZED: Invalid credentials")
    else:
        print(f"   ⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print()

# Test 2: Using atlassian-python-api library
print("=" * 70)
print("TEST 2: Using atlassian-python-api Library")
print("=" * 70)

# Try with 'token' parameter
print("\n   Method A: Using 'token' parameter")
try:
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        token=CONFLUENCE_API_TOKEN,
        cloud=cloud
    )
    spaces = confluence.get_all_spaces(start=0, limit=5)
    print(f"   ✅ SUCCESS: Found {len(spaces.get('results', []))} spaces")
    for space in spaces.get('results', [])[:3]:
        print(f"      • {space.get('name')} (key: {space.get('key')})")
except Exception as e:
    error_str = str(e)
    print(f"   ❌ FAILED: {error_str[:100]}")
    if "403" in error_str or "FORBIDDEN" in error_str:
        print("      → Same 403 error as direct API call")

# Try with 'password' parameter (some versions use this)
print("\n   Method B: Using 'password' parameter")
try:
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        password=CONFLUENCE_API_TOKEN,
        cloud=cloud
    )
    spaces = confluence.get_all_spaces(start=0, limit=5)
    print(f"   ✅ SUCCESS: Found {len(spaces.get('results', []))} spaces")
except Exception as e:
    error_str = str(e)
    print(f"   ❌ FAILED: {error_str[:100]}")

print()

# Test 3: Check if Confluence web UI is accessible
print("=" * 70)
print("TEST 3: Confluence Web UI Accessibility")
print("=" * 70)
try:
    wiki_url = f"{CONFLUENCE_URL}/wiki"
    response = requests.get(wiki_url, timeout=10, allow_redirects=False)
    print(f"   URL: {wiki_url}")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Confluence web UI is accessible")
    elif response.status_code == 302:
        print("   ⚠️  Redirect detected (might require login)")
        print(f"   Location: {response.headers.get('Location', 'N/A')}")
    elif response.status_code == 404:
        print("   ❌ Confluence not found - may not be enabled for this site")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error checking web UI: {str(e)}")

print()

# Test 4: Check Jira API (to verify token works)
print("=" * 70)
print("TEST 4: Verify Token Works with Jira API")
print("=" * 70)
try:
    jira_url = f"{CONFLUENCE_URL}/rest/api/3/myself"
    response = requests.get(
        jira_url,
        auth=HTTPBasicAuth(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=10
    )
    if response.status_code == 200:
        user_info = response.json()
        print(f"   ✅ Token works! Authenticated as: {user_info.get('displayName', 'Unknown')}")
        print(f"      Account ID: {user_info.get('accountId', 'N/A')}")
        print(f"      Email: {user_info.get('emailAddress', 'N/A')}")
    else:
        print(f"   ⚠️  Jira API returned: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Could not verify Jira access: {str(e)}")

print()
print("=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print()
print("Based on the tests above:")
print()
print("1. ✅ If Jira API works but Confluence API doesn't:")
print("   → Your token is valid, but Confluence API access is restricted")
print("   → Solution: Enable Confluence API access in Atlassian Admin")
print()
print("2. ✅ If both return 403:")
print("   → Check if Confluence is enabled for your site")
print("   → Visit: https://admin.atlassian.com")
print()
print("3. ✅ If web UI is accessible but API isn't:")
print("   → You have web access but not API access")
print("   → Solution: Contact Atlassian admin to grant API permissions")
print()
print("4. 🔧 Next Steps:")
print("   a. Visit: https://yashbgv2002.atlassian.net/wiki")
print("      → Can you access Confluence in browser?")
print("   b. Visit: https://admin.atlassian.com")
print("      → Check if Confluence is enabled for your site")
print("   c. Check user permissions:")
print("      → Settings → User management → Your account")
print("      → Verify 'Can use' permission for Confluence")
print()
print("=" * 70)
