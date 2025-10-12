# Social Media Platform Integration Guide

This document provides instructions for integrating TechKids with real social media platform APIs.

## Overview

The social media dispatcher system allows TechKids to automatically post content to multiple platforms. Each platform has its own dispatcher that handles:
- Authentication & token management
- Content posting (text, images, videos)
- Media uploads
- Analytics retrieval
- Platform-specific constraints

## Architecture

```
backend/services/dispatchers/
├── __init__.py                 # Dispatcher registry
├── base.py                     # Abstract base class
├── facebook_dispatcher.py      # Facebook Graph API
├── instagram_dispatcher.py     # Instagram Graph API
├── x_dispatcher.py             # X (Twitter) API v2
├── telegram_dispatcher.py      # Telegram Bot API
└── whatsapp_dispatcher.py      # WhatsApp Business API
```

## Platform Requirements

### 1. Facebook & Instagram (Meta Platforms)
- **API**: Graph API v18.0+
- **Authentication**: OAuth 2.0, Page Access Tokens
- **Required Permissions**: 
  - `pages_manage_posts` - Publish to Facebook Pages
  - `pages_read_engagement` - Read analytics
  - `instagram_basic` - Instagram basic access
  - `instagram_content_publish` - Publish to Instagram
- **Setup Steps**:
  1. Create a Facebook App at https://developers.facebook.com/
  2. Add Facebook Login and Instagram Graph API products
  3. Get your App ID and App Secret
  4. Generate a Page Access Token with required permissions
  5. For Instagram: Link Instagram Business Account to Facebook Page

**Documentation**: https://developers.facebook.com/docs/graph-api/

### 2. X (Twitter)
- **API**: Twitter API v2
- **Authentication**: OAuth 2.0 with PKCE or OAuth 1.0a
- **Required Scopes**: `tweet.read`, `tweet.write`, `users.read`
- **Setup Steps**:
  1. Apply for Twitter Developer Account at https://developer.twitter.com/
  2. Create a new App in the Developer Portal
  3. Get API Key, API Secret, Access Token, Access Token Secret
  4. Enable OAuth 2.0 if using user authentication

**Documentation**: https://developer.twitter.com/en/docs/twitter-api

### 3. Telegram
- **API**: Telegram Bot API
- **Authentication**: Bot Token
- **Setup Steps**:
  1. Talk to @BotFather on Telegram
  2. Create a new bot with `/newbot`
  3. Get your Bot Token
  4. Create a Channel and add your bot as administrator
  5. Get the Channel ID (use @userinfobot or API call)

**Documentation**: https://core.telegram.org/bots/api

### 4. WhatsApp Business
- **API**: WhatsApp Business Cloud API
- **Authentication**: System User Access Token
- **Setup Steps**:
  1. Create Meta Business Account
  2. Set up WhatsApp Business API at https://business.facebook.com/
  3. Get Phone Number ID
  4. Generate System User Access Token
  5. Configure webhooks for message status

**Documentation**: https://developers.facebook.com/docs/whatsapp/cloud-api

### 5. Threads (Meta)
- **API**: Threads API (currently limited beta)
- **Authentication**: OAuth 2.0
- **Status**: Limited availability, may require special access

## Environment Variables

Add these to your `.env` file:

```bash
# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token

# Instagram
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id

# X (Twitter)
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
X_BEARER_TOKEN=your_bearer_token

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel

# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# General settings
SOCIAL_MEDIA_DEBUG=true
SOCIAL_MEDIA_RETRY_ATTEMPTS=3
SOCIAL_MEDIA_RETRY_DELAY=300
```

## Implementation Priority

Recommended order based on complexity and usage:

1. **Telegram** - Simplest API, good for testing the system
2. **X (Twitter)** - Well-documented, straightforward
3. **Facebook** - Most complex but powerful
4. **Instagram** - Requires Facebook integration
5. **WhatsApp** - Business-focused, requires careful setup

## Testing Strategy

### Development Testing
1. Create test accounts on each platform
2. Use sandbox/test environments where available
3. Test with small text posts first
4. Then test with images
5. Finally test with videos
6. Verify analytics retrieval

### Production Checklist
- [ ] All credentials stored securely (encrypted at rest)
- [ ] Rate limiting implemented
- [ ] Error handling and retry logic tested
- [ ] Webhook endpoints secured (WhatsApp)
- [ ] Analytics sync running
- [ ] Logging and monitoring configured
- [ ] Platform-specific character limits validated
- [ ] Media format validation working

## Common Pitfalls

1. **Token Expiration**: Most tokens expire. Implement refresh logic!
2. **Rate Limits**: Each platform has different limits. Implement backoff.
3. **Media URLs**: Some platforms need publicly accessible URLs for media.
4. **Character Encoding**: Handle emojis and special characters properly.
5. **Timezone Handling**: Use UTC consistently, convert for display.
6. **Webhook Verification**: WhatsApp and others require webhook verification.

## Security Best Practices

1. **Never commit credentials** to git
2. **Encrypt credentials** in the database
3. **Use HTTPS** for all API calls
4. **Validate webhook signatures** 
5. **Rotate tokens** regularly
6. **Log access** to credentials
7. **Use environment-specific** credentials (dev/staging/prod)

## API Response Handling

Each dispatcher should:
1. Parse API responses consistently
2. Map platform-specific errors to our error codes
3. Extract analytics data into standard format
4. Store platform post IDs for future reference
5. Log detailed diagnostics for debugging

## Next Steps

1. Review this guide
2. Set up developer accounts for target platforms
3. Implement dispatchers one at a time
4. Test thoroughly in development
5. Deploy to staging with test credentials
6. Migrate to production credentials
7. Monitor and optimize

## Resources

- Facebook Graph API Explorer: https://developers.facebook.com/tools/explorer/
- Twitter API Postman Collection: https://www.postman.com/twitter/
- Telegram Bot API Tester: https://core.telegram.org/bots/api#making-requests
- WhatsApp Business API Documentation: https://developers.facebook.com/docs/whatsapp
