#!/usr/bin/env python3
"""
Test Confluence integration via the API endpoints
"""
import requests
import json
import sys

API_BASE = "http://localhost:8000"

def test_api_endpoints():
    """Test Confluence API endpoints"""
    print("🧪 Testing Confluence Integration via API")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            health = response.json()
            print(f"   Vector store: {health.get('vector_store', {}).get('total_documents', 0)} documents")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the API server is running:")
        print("   uvicorn app.main:app --reload")
        return False
    
    # Test 2: List Confluence spaces
    print("\n2️⃣ Testing Confluence Spaces Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/confluence/spaces", timeout=10)
        if response.status_code == 200:
            data = response.json()
            spaces = data.get('spaces', [])
            count = data.get('count', 0)
            print(f"✅ Success! Found {count} spaces")
            if spaces:
                print("\n   Available Spaces:")
                for space in spaces[:5]:
                    print(f"     - {space.get('name')} (Key: {space.get('key')})")
                if count > 5:
                    print(f"     ... and {count - 5} more")
            return True
        elif response.status_code == 503:
            error = response.json().get('detail', 'Unknown error')
            print(f"⚠️  Confluence not configured: {error}")
            print("\n   Please set in .env:")
            print("     CONFLUENCE_URL=https://your-domain.atlassian.net")
            print("     CONFLUENCE_USERNAME=your-email@example.com")
            print("     CONFLUENCE_API_TOKEN=your-token")
            return False
        elif response.status_code == 500:
            error = response.json().get('detail', 'Unknown error')
            print(f"❌ Error: {error}")
            if "401" in error or "Unauthorized" in error:
                print("\n   Authentication failed. Please check:")
                print("     1. API token is valid and not expired")
                print("     2. Username (email) is correct")
                print("     3. Token has proper permissions")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    print("\n" + "=" * 60)
    if success:
        print("✅ All API tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
