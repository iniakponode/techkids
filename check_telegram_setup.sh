#!/bin/bash

# Telegram Bot Setup Helper
# This script helps you verify you have the correct credentials format

echo "🤖 Telegram Bot Setup Helper"
echo "============================"
echo ""

# Check if token is provided
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set"
    echo ""
    echo "To set it, run:"
    echo "  export TELEGRAM_BOT_TOKEN='your_token_here'"
    echo ""
    echo "Your token should look like: 7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"
    echo "Get it from @BotFather on Telegram by sending /newbot"
    echo ""
    TOKEN_OK=0
else
    echo "✅ TELEGRAM_BOT_TOKEN is set"
    echo "   Token: ${TELEGRAM_BOT_TOKEN:0:10}...${TELEGRAM_BOT_TOKEN: -5}"
    
    # Validate token format (should be numbers:letters)
    if [[ $TELEGRAM_BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        echo "   ✅ Token format looks correct"
        TOKEN_OK=1
    else
        echo "   ⚠️  Token format doesn't look right"
        echo "   Expected format: 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
        TOKEN_OK=0
    fi
    echo ""
fi

# Check if channel ID is provided
if [ -z "$TELEGRAM_CHANNEL_ID" ]; then
    echo "❌ TELEGRAM_CHANNEL_ID not set"
    echo ""
    echo "To set it, run:"
    echo "  export TELEGRAM_CHANNEL_ID='@your_channel'"
    echo ""
    echo "Your channel ID should look like: @techkids_test"
    echo "Or a numeric ID like: -1001234567890"
    echo ""
    CHANNEL_OK=0
else
    echo "✅ TELEGRAM_CHANNEL_ID is set"
    echo "   Channel: $TELEGRAM_CHANNEL_ID"
    
    # Validate channel format (should start with @ or be negative number)
    if [[ $TELEGRAM_CHANNEL_ID =~ ^@[A-Za-z0-9_]+$ ]] || [[ $TELEGRAM_CHANNEL_ID =~ ^-[0-9]+$ ]]; then
        echo "   ✅ Channel ID format looks correct"
        CHANNEL_OK=1
    else
        echo "   ⚠️  Channel ID format doesn't look right"
        echo "   Expected: @your_channel or -1001234567890"
        CHANNEL_OK=0
    fi
    echo ""
fi

# Summary
echo "============================"
if [ $TOKEN_OK -eq 1 ] && [ $CHANNEL_OK -eq 1 ]; then
    echo "🎉 All credentials look good!"
    echo ""
    echo "Ready to test? Run:"
    echo "  cd /workspaces/techkids"
    echo "  python -m backend.services.dispatchers.test_telegram"
    echo ""
elif [ $TOKEN_OK -eq 1 ] || [ $CHANNEL_OK -eq 1 ]; then
    echo "⚠️  Some credentials are set, but not all"
    echo ""
    echo "Make sure both are set before testing."
else
    echo "❌ Credentials not configured yet"
    echo ""
    echo "📖 Read TELEGRAM_SETUP_GUIDE.md for step-by-step instructions"
    echo ""
    echo "Quick start:"
    echo "  1. Open Telegram on your phone or computer"
    echo "  2. Search for: @BotFather"
    echo "  3. Send: /newbot"
    echo "  4. Follow the instructions to get your bot token"
    echo "  5. Create a channel and add your bot as admin"
    echo ""
fi

echo ""
echo "Need help? Check these files:"
echo "  📄 TELEGRAM_SETUP_GUIDE.md - Detailed walkthrough with screenshots"
echo "  📄 SOCIAL_MEDIA_INTEGRATION.md - Technical documentation"
echo ""
