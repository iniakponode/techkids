"""
Helper script to get your Telegram channel ID

This script helps you find the numeric ID of a private Telegram channel.

Usage:
    export TELEGRAM_BOT_TOKEN="your_bot_token"
    python -m backend.services.dispatchers.get_channel_id
"""

import os
import sys
import httpx


def get_channel_id():
    """Retrieve updates to find channel IDs where the bot is active"""
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        print("   Get a token from @BotFather on Telegram")
        print("   Then run: export TELEGRAM_BOT_TOKEN='your_token'")
        sys.exit(1)
    
    print("🔍 Looking for channels where your bot is active...\n")
    
    # Get bot info first
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            data = response.json()
            
            if data.get("ok"):
                bot_info = data["result"]
                print(f"✅ Bot validated: @{bot_info['username']}")
                print(f"   Name: {bot_info['first_name']}")
                print()
            else:
                print(f"❌ Invalid bot token: {data.get('description')}")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Error validating bot: {e}")
        sys.exit(1)
    
    # Get updates (recent messages/activity)
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            data = response.json()
            
            if not data.get("ok"):
                print(f"❌ Error getting updates: {data.get('description')}")
                sys.exit(1)
            
            updates = data.get("result", [])
            
            if not updates:
                print("📭 No recent activity found.")
                print("\nTo find your channel ID:")
                print("1. Post a message in your channel")
                print("2. Or send a message to your bot")
                print("3. Run this script again")
                print("\nAlternatively:")
                print("- For public channels, use: @your_channel_username")
                print("- Forward a message from your private channel to @userinfobot")
                return
            
            print(f"📬 Found {len(updates)} recent updates:\n")
            
            chats_found = set()
            for update in updates:
                # Check different types of updates
                message = (
                    update.get("message") or 
                    update.get("channel_post") or 
                    update.get("edited_channel_post")
                )
                
                if message:
                    chat = message.get("chat")
                    if chat:
                        chat_id = chat.get("id")
                        chat_type = chat.get("type")
                        chat_title = chat.get("title") or chat.get("username") or "Private Chat"
                        
                        if chat_id and chat_id not in chats_found:
                            chats_found.add(chat_id)
                            
                            emoji = {
                                "channel": "📢",
                                "group": "👥",
                                "supergroup": "👥",
                                "private": "👤"
                            }.get(chat_type, "💬")
                            
                            print(f"{emoji} {chat_type.upper()}: {chat_title}")
                            print(f"   ID: {chat_id}")
                            
                            if chat_type == "channel":
                                print(f"   ✅ Use this ID for your channel!")
                                print(f"   Command: export TELEGRAM_CHANNEL_ID=\"{chat_id}\"")
                            
                            if chat.get("username"):
                                print(f"   Username: @{chat['username']}")
                            
                            print()
            
            if not chats_found:
                print("❌ No channels found in recent activity")
                print("\nMake sure:")
                print("1. You added the bot as administrator to your channel")
                print("2. The bot has 'Post Messages' permission")
                print("3. Try posting a message in the channel")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    get_channel_id()
