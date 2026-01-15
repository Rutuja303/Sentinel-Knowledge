#!/usr/bin/env python3
"""Test script to diagnose Confluence API connection issues"""

import os
from dotenv import load_dotenv
from atlassian import Confluence

# Load environment variables
load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", "").replace("/wiki", "").rstrip("/")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME", "")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "")

print("=" * 60)
print("Confluence Connection Test")
print("=" * 60)
print(f"URL: {CONFLUENCE_URL}")
print(f"Username: {CONFLUENCE_USERNAME}")
print(f"Token (first 10 chars): {CONFLUENCE_API_TOKEN[:10]}...")
print(f"Token length: {len(CONFLUENCE_API_TOKEN)}")
print()

# Determine if cloud
cloud = '.atlassian.net' in CONFLUENCE_URL or '.atlassian.com' in CONFLUENCE_URL
print(f"Cloud mode: {cloud}")
print()

# Try different authentication methods
print("Testing authentication methods...")
print("-" * 60)

# Method 1: Using 'token' parameter
print("\n1. Testing with 'token' parameter:")
try:
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        token=CONFLUENCE_API_TOKEN,
        cloud=cloud
    )
    # Try to get current user info
    user = confluence.get_current_user()
    print(f"   ✓ Success! Current user: {user}")
except Exception as e:
    print(f"   ✗ Failed: {str(e)}")

# Method 2: Using 'password' parameter (some versions use this)
print("\n2. Testing with 'password' parameter:")
try:
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        password=CONFLUENCE_API_TOKEN,
        cloud=cloud
    )
    user = confluence.get_current_user()
    print(f"   ✓ Success! Current user: {user}")
except Exception as e:
    print(f"   ✗ Failed: {str(e)}")

# Method 3: Try to list spaces
print("\n3. Testing space listing:")
try:
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        token=CONFLUENCE_API_TOKEN,
        cloud=cloud
    )
    spaces = confluence.get_all_spaces(start=0, limit=10)
    print(f"   ✓ Success! Found {len(spaces.get('results', []))} spaces")
    for space in spaces.get('results', [])[:3]:
        print(f"      - {space.get('name')} (key: {space.get('key')})")
except Exception as e:
    print(f"   ✗ Failed: {str(e)}")
    # Try to get more details
    error_str = str(e)
    if "403" in error_str or "FORBIDDEN" in error_str:
        print("\n   ⚠️  403 Forbidden Error Detected!")
        print("   This means:")
        print("   - Your credentials are valid (authentication succeeded)")
        print("   - But your account doesn't have API access to Confluence")
        print("\n   Solutions:")
        print("   1. Check if Confluence is enabled for your Atlassian site")
        print("   2. Verify your account has 'Can use' permission for Confluence")
        print("   3. Contact your Atlassian admin to grant API access")
        print("   4. The API token might be for Jira only, not Confluence")

print("\n" + "=" * 60)
