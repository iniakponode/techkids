"""
Test script for Telegram dispatcher

This script tests the Telegram Bot API integration without needing the full application.

Usage:
    python -m backend.services.dispatchers.test_telegram

Before running:
1. Create a bot with @BotFather on Telegram
2. Get your bot token
3. Create a channel and add your bot as administrator
4. Set environment variables:
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export TELEGRAM_CHANNEL_ID="@your_channel"  # or numeric ID like -1001234567890
"""

import os
import sys
from backend.services.dispatchers.telegram_dispatcher import TelegramDispatcher
from backend.services.dispatchers.base import PlatformCredentials, PostContent


def test_telegram_integration():
    """Test the Telegram dispatcher with real credentials"""
    
    # Get credentials from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        print("   Get a token from @BotFather on Telegram")
        sys.exit(1)
    
    if not channel_id:
        print("❌ TELEGRAM_CHANNEL_ID environment variable not set")
        print("   Use your channel username like @your_channel")
        sys.exit(1)
    
    print(f"🤖 Testing Telegram Bot Integration")
    print(f"   Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"   Channel ID: {channel_id}")
    print()
    
    # Create credentials
    credentials = PlatformCredentials(
        platform="telegram",
        access_token=bot_token,
        metadata={"channel_id": channel_id}
    )
    
    # Create dispatcher
    dispatcher = TelegramDispatcher()
    
    # Test 1: Validate credentials
    print("📋 Test 1: Validating bot credentials...")
    is_valid = dispatcher.validate_credentials(credentials)
    if is_valid:
        print("   ✅ Bot credentials are valid!")
    else:
        print("   ❌ Bot credentials are invalid")
        sys.exit(1)
    
    print()
    
    # Test 2: Send a simple text message
    print("📋 Test 2: Sending text message...")
    content = PostContent(
        text="🤖 Test message from TechKids Social Media System!\n\nThis is a test of our automated posting system.",
        content_type="Post"
    )
    
    result = dispatcher.publish_post(content, credentials)
    if result.success:
        print(f"   ✅ Message sent successfully!")
        print(f"   Message ID: {result.platform_post_id}")
        print(f"   Diagnostics: {result.diagnostics}")
    else:
        print(f"   ❌ Message failed to send")
        print(f"   Error: {result.error_message}")
        print(f"   Diagnostics: {result.diagnostics}")
    
    print()
    
    # Test 3: Test content validation
    print("📋 Test 3: Testing content validation...")
    long_content = PostContent(
        text="A" * 5000,  # Exceeds 4096 character limit
        content_type="Post"
    )
    
    is_valid, error_msg = dispatcher.validate_content(long_content)
    if not is_valid:
        print(f"   ✅ Content validation working correctly")
        print(f"   Error caught: {error_msg}")
    else:
        print(f"   ❌ Content validation failed to catch error")
    
    print()
    
    # Test 4: Test with invalid content type
    print("📋 Test 4: Testing invalid content type...")
    invalid_content = PostContent(
        text="Test message",
        content_type="Story"  # Not supported by Telegram
    )
    
    is_valid, error_msg = dispatcher.validate_content(invalid_content)
    if not is_valid:
        print(f"   ✅ Content type validation working")
        print(f"   Error caught: {error_msg}")
    else:
        print(f"   ❌ Content type validation failed")
    
    print()
    
    # Summary
    print("=" * 60)
    print("🎉 Telegram Integration Test Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Check your Telegram channel to see the test message")
    print("2. Try posting with images or videos")
    print("3. Integrate the dispatcher into your application")
    print()


if __name__ == "__main__":
    test_telegram_integration()
