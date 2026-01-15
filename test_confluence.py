#!/usr/bin/env python3
"""
Test script for Confluence connection
"""
import sys
import os
from dotenv import load_dotenv

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_confluence_connection():
    """Test Confluence API connection"""
    print("🔍 Testing Confluence Connection...")
    print("=" * 50)
    
    # Check environment variables
    from app.utils.config import config
    
    print("\n📋 Configuration Check:")
    print(f"  CONFLUENCE_URL: {config.CONFLUENCE_URL or '❌ Not set'}")
    print(f"  CONFLUENCE_USERNAME: {config.CONFLUENCE_USERNAME or '❌ Not set'}")
    print(f"  CONFLUENCE_API_TOKEN: {'✅ Set' if config.CONFLUENCE_API_TOKEN else '❌ Not set'}")
    print(f"  CONFLUENCE_SPACE_KEY: {config.CONFLUENCE_SPACE_KEY or '(empty - will use all spaces)'}")
    
    if not config.CONFLUENCE_URL or not config.CONFLUENCE_USERNAME or not config.CONFLUENCE_API_TOKEN:
        print("\n❌ ERROR: Confluence credentials not configured!")
        print("\nPlease set in .env file:")
        print("  CONFLUENCE_URL=https://your-domain.atlassian.net")
        print("  CONFLUENCE_USERNAME=your-email@example.com")
        print("  CONFLUENCE_API_TOKEN=your-token-here")
        return False
    
    try:
        print("\n🔌 Initializing Confluence Service...")
        from app.services.confluence_ingestion import ConfluenceIngestionService
        
        # Test URL format
        test_url = config.CONFLUENCE_URL.replace("/wiki", "")
        if test_url != config.CONFLUENCE_URL:
            print(f"⚠️  Note: Removing /wiki from URL: {test_url}")
        
        confluence_service = ConfluenceIngestionService()
        print("✅ Confluence service initialized")
        
        print("\n📡 Testing API Connection...")
        try:
            spaces = confluence_service.get_all_spaces()
            print(f"✅ Connection successful! Found {len(spaces)} accessible spaces")
        except Exception as api_error:
            error_str = str(api_error)
            print(f"❌ API Error: {error_str[:200]}")
            
            if "403" in error_str or "FORBIDDEN" in error_str:
                print("\n" + "="*50)
                print("🔍 DIAGNOSIS: 403 FORBIDDEN")
                print("="*50)
                print("✅ Good news: Your token is VALID and authentication works!")
                print("❌ Issue: Your account doesn't have permission to access Confluence")
                print("\n💡 This usually means:")
                print("   1. Your account doesn't have Confluence access enabled")
                print("   2. Confluence might not be provisioned for your Atlassian site")
                print("   3. Your account needs to be added to Confluence")
                print("\n🔧 Solutions:")
                print("   1. Check if you can access Confluence in browser:")
                print(f"      {config.CONFLUENCE_URL}/wiki")
                print("   2. If you see 'Confluence not available', you need to:")
                print("      - Enable Confluence for your Atlassian site")
                print("      - Or use an account that has Confluence access")
                print("   3. Verify Confluence is active:")
                print("      - Go to: https://admin.atlassian.com")
                print("      - Check if Confluence is enabled for your site")
                print("   4. Try with a different account that has Confluence access")
            elif "401" in error_str or "Unauthorized" in error_str:
                print("\n🔧 Troubleshooting Steps:")
                print("  1. Verify your API token is valid:")
                print("     - Go to: https://id.atlassian.com/manage-profile/security/api-tokens")
                print("     - Check if token is active")
                print("     - Generate a new token if needed")
                print("\n  2. Check your Confluence URL format:")
                print("     - Should be: https://your-domain.atlassian.net")
                print("     - Should NOT include /wiki")
                print(f"     - Current: {config.CONFLUENCE_URL}")
                print("\n  3. Verify username format:")
                print("     - Use your email address")
                print(f"     - Current: {config.CONFLUENCE_USERNAME}")
            else:
                print("\n🔧 General Troubleshooting:")
                print("  1. Check network connectivity")
                print("  2. Verify Confluence URL is accessible")
                print("  3. Check if Confluence is enabled for your site")
            raise
        
        if spaces:
            print("\n📚 Available Spaces:")
            for i, space in enumerate(spaces[:10], 1):  # Show first 10
                print(f"  {i}. {space['name']} (Key: {space['key']})")
            if len(spaces) > 10:
                print(f"  ... and {len(spaces) - 10} more")
        
        # Test getting pages from first space
        if spaces:
            test_space = spaces[0]
            print(f"\n🧪 Testing page retrieval from space: {test_space['name']} ({test_space['key']})")
            pages = confluence_service.get_all_pages_from_space(test_space['key'], limit=5)
            print(f"✅ Retrieved {len(pages)} pages from {test_space['name']}")
            
            if pages:
                print("\n📄 Sample Pages:")
                for i, page in enumerate(pages[:3], 1):
                    print(f"  {i}. {page['title']}")
                    print(f"     URL: {page.get('url', 'N/A')}")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Confluence connection is working.")
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Connection Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check your CONFLUENCE_URL is correct")
        print("  2. Verify your API token is valid")
        print("  3. Ensure your username (email) is correct")
        print("  4. Check network connectivity")
        return False

if __name__ == "__main__":
    success = test_confluence_connection()
    sys.exit(0 if success else 1)
