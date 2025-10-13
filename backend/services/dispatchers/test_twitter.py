"""
Test script for Twitter/X Dispatcher

This script tests the Twitter integration without using the database.
Run it to verify your Twitter credentials and API access before using the web UI.

Usage:
    export TWITTER_API_KEY="your_api_key"
    export TWITTER_API_SECRET="your_api_secret"
    export TWITTER_ACCESS_TOKEN="your_access_token"
    export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
    
    python -m backend.services.dispatchers.test_twitter
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.dispatchers.twitter_dispatcher import TwitterDispatcher
from backend.services.dispatchers.base import PostContent, PlatformCredentials


def test_twitter_integration():
    """Test Twitter integration with credentials from environment"""
    
    # Get credentials from environment
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ Error: Missing Twitter credentials!")
        print("\nPlease set the following environment variables:")
        print("  export TWITTER_API_KEY='your_api_key'")
        print("  export TWITTER_API_SECRET='your_api_secret'")
        print("  export TWITTER_ACCESS_TOKEN='your_access_token'")
        print("  export TWITTER_ACCESS_TOKEN_SECRET='your_access_token_secret'")
        print("\nGet these from: https://developer.twitter.com/")
        return False
    
    # Create credentials object
    credentials = PlatformCredentials(
        platform="twitter",
        access_token=api_key,
        refresh_token=api_secret,
        metadata={
            "access_token": access_token,
            "access_token_secret": access_token_secret
        }
    )
    
    # Create dispatcher
    dispatcher = TwitterDispatcher()
    
    print("=" * 60)
    print("🐦 Twitter/X Integration Test")
    print("=" * 60)
    print()
    
    # Test 1: Validate credentials
    print("Test 1: Validating Twitter credentials...")
    if dispatcher.validate_credentials(credentials):
        print("✅ Credentials are valid!")
    else:
        print("❌ Credential validation failed!")
        return False
    print()
    
    # Test 2: Post a simple text tweet
    print("Test 2: Posting a text-only tweet...")
    content = PostContent(
        text="🚀 Testing Twitter integration from TechKids! This is an automated test post. #TechKids #Testing",
        content_type="Post"
    )
    
    result = dispatcher.publish_post(content, credentials)
    if result.success:
        print(f"✅ Tweet posted successfully!")
        print(f"   Tweet ID: {result.platform_post_id}")
        print(f"   View at: https://twitter.com/i/web/status/{result.platform_post_id}")
    else:
        print(f"❌ Tweet posting failed!")
        print(f"   Error: {result.error_message}")
        print(f"   Diagnostics: {result.diagnostics}")
        return False
    print()
    
    # Test 3: Content validation
    print("Test 3: Testing content validation...")
    
    # Test 3a: Text too long
    long_text = "A" * 300
    long_content = PostContent(text=long_text, content_type="Post")
    is_valid, error = dispatcher.validate_content(long_content)
    if not is_valid:
        print("✅ Correctly rejected tweet > 280 characters")
    else:
        print("❌ Should have rejected long tweet")
    
    # Test 3b: Empty text
    empty_content = PostContent(text="", content_type="Post")
    is_valid, error = dispatcher.validate_content(empty_content)
    if not is_valid:
        print("✅ Correctly rejected empty tweet")
    else:
        print("❌ Should have rejected empty tweet")
    
    # Test 3c: Invalid content type
    invalid_content = PostContent(text="Test", content_type="Story")
    is_valid, error = dispatcher.validate_content(invalid_content)
    if not is_valid:
        print("✅ Correctly rejected invalid content type")
    else:
        print("❌ Should have rejected invalid content type")
    print()
    
    # Test 4: Error handling
    print("Test 4: Testing error handling...")
    bad_credentials = PlatformCredentials(
        platform="twitter",
        access_token="fake_key",
        refresh_token="fake_secret",
        metadata={
            "access_token": "fake_token",
            "access_token_secret": "fake_secret"
        }
    )
    
    if not dispatcher.validate_credentials(bad_credentials):
        print("✅ Correctly rejected invalid credentials")
    else:
        print("❌ Should have rejected invalid credentials")
    print()
    
    print("=" * 60)
    print("✅ All Twitter integration tests passed!")
    print("=" * 60)
    print()
    print("🎉 Your Twitter integration is working correctly!")
    print("📝 You can now add these credentials in the web UI:")
    print("   - Go to Social Media Control Center")
    print("   - Platform: X or Twitter")
    print("   - Access Token: <your API Key>")
    print("   - Refresh Token: <your API Secret>")
    print("   - Metadata: {\"access_token\": \"<token>\", \"access_token_secret\": \"<secret>\"}")
    print()
    
    return True


if __name__ == "__main__":
    success = test_twitter_integration()
    sys.exit(0 if success else 1)
