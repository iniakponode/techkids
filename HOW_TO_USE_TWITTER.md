# 🐦 How to Set Up X/Twitter Integration

## Complete Setup Guide

---

## Step 1: Create Twitter Developer Account

### 1.1 Apply for Developer Access
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Click "Sign up" or "Apply"
3. Login with your Twitter account
4. Fill out the application form:
   - **Account type**: Choose appropriate type (Hobbyist, Professional, etc.)
   - **Use case**: Social media management/automation
   - **Will you analyze tweets?**: No (unless you need analytics)
   - **Will you display tweets?**: No (we're just posting)
   - **How will you use the API?**: Automated posting for educational platform

5. Submit and wait for approval (usually within 24 hours, sometimes instant)

---

## Step 2: Create a Project and App

### 2.1 Create Project
1. Once approved, go to [Developer Portal Dashboard](https://developer.twitter.com/en/portal/dashboard)
2. Click "+ Create Project"
3. Fill in project details:
   - **Project name**: "TechKids Social Media"
   - **Use case**: "Making a bot"
   - **Project description**: "Automated posting for TechKids educational platform"

### 2.2 Create App
1. Within your project, click "+ Add App"
2. Choose "Production" environment
3. Name your app: "TechKids Bot"
4. You'll receive your API Keys - **SAVE THESE IMMEDIATELY!**
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)

---

## Step 3: Generate Access Tokens

### 3.1 Set Up OAuth 1.0a
1. In your app settings, go to "Keys and tokens" tab
2. Under "Authentication Tokens", click "Generate" for Access Token and Secret
3. **SAVE THESE IMMEDIATELY!**
   - Access Token
   - Access Token Secret

### 3.2 Set App Permissions
1. Go to app "Settings" tab
2. Under "User authentication settings", click "Set up"
3. Enable "OAuth 1.0a"
4. Set **App permissions** to "Read and write" (need this to post tweets!)
5. Fill in:
   - **Callback URI**: `https://techkids.ungozu.com/auth/twitter/callback` (can be placeholder)
   - **Website URL**: `https://techkids.ungozu.com`
6. Save

**⚠️ IMPORTANT**: After changing permissions, you MUST regenerate your Access Token and Secret!

---

## Step 4: Save Your Credentials

You now have 4 credentials:
```
API Key (Consumer Key):          abc123xyz...
API Secret (Consumer Secret):     def456uvw...
Access Token:                     1234567890-AbCdEf...
Access Token Secret:              ghijkl789...
```

**⚠️ Keep these SECRET!** Never commit them to git or share publicly.

---

## Step 5: Test in Terminal (Optional)

### 5.1 Set Environment Variables
```bash
export TWITTER_API_KEY="your_api_key_here"
export TWITTER_API_SECRET="your_api_secret_here"
export TWITTER_ACCESS_TOKEN="your_access_token_here"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret_here"
```

### 5.2 Run Test Script
```bash
cd /workspaces/techkids
python -m backend.services.dispatchers.test_twitter
```

**Expected output:**
```
============================================================
🐦 Twitter/X Integration Test
============================================================

Test 1: Validating Twitter credentials...
✅ Credentials are valid!

Test 2: Posting a text-only tweet...
✅ Tweet posted successfully!
   Tweet ID: 1234567890123456789
   View at: https://twitter.com/i/web/status/1234567890123456789

Test 3: Testing content validation...
✅ Correctly rejected tweet > 280 characters
✅ Correctly rejected empty tweet
✅ Correctly rejected invalid content type

Test 4: Testing error handling...
✅ Correctly rejected invalid credentials

============================================================
✅ All Twitter integration tests passed!
============================================================
```

---

## Step 6: Add Credentials in Web UI

### 6.1 Go to Social Media Control Center
1. Login to your TechKids admin dashboard
2. Navigate to **Social Media Control Center**

### 6.2 Fill in Platform Credentials Form

```
┌─────────────────────────────────────────────────────────────┐
│  Platform Credentials                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Platform:                                                   │
│  [Select: X or Twitter ▼]                                    │
│                                                              │
│  Access Token:                                               │
│  [abc123xyz...]                    ← Paste API Key here     │
│                                                              │
│  Refresh Token:                                              │
│  [def456uvw...]                    ← Paste API Secret here  │
│                                                              │
│  Metadata:                                                   │
│  ┌───────────────────────────────────────────────┐          │
│  │ {                                             │          │
│  │   "access_token": "1234567890-AbCdEf...",    │          │
│  │   "access_token_secret": "ghijkl789..."      │          │
│  │ }                                             │          │
│  └───────────────────────────────────────────────┘          │
│  💡 Enter your User Access Token and Secret in JSON format  │
│                                                              │
│  [Save Credentials]                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Fill Each Field

**Platform:**
- Select **"X"** or **"Twitter"** from dropdown

**Access Token:**
- Paste your **API Key (Consumer Key)**
- Example: `abc123xyzDEF456GHI789...`

**Refresh Token:**
- Paste your **API Secret (Consumer Secret)**
- Example: `def456uvwJKL789MNO123...`

**Metadata:**
- Enter your User Access Token and Secret in JSON format:
```json
{
  "access_token": "1234567890-AbCdEfGhIjKlMnOpQr...",
  "access_token_secret": "ghijkl789mnopqrXYZ123..."
}
```

### 6.4 Click "Save Credentials"
- You should see a success message
- Credentials are now stored securely (encrypted)

---

## Step 7: Create Your First Tweet

### 7.1 Fill in Post Form
```
Platform:       X or Twitter
Content Type:   Post
Content:        🎉 Hello Twitter! This is an automated post from TechKids!
Image:          (optional - upload an image)
Video:          (optional - upload a video)
Schedule Time:  (leave empty for immediate posting)
```

### 7.2 Click "Save Post"
- If no schedule time: Tweet posts immediately!
- If schedule time set: Tweet posts at scheduled time

### 7.3 Verify on Twitter
1. Go to your Twitter profile
2. You should see the new tweet!
3. Check the admin dashboard - post status should be "published"

---

## 📊 Twitter vs Telegram: Field Mapping

| Field | Telegram | Twitter/X |
|-------|----------|-----------|
| Access Token | Bot Token | API Key (Consumer Key) |
| Refresh Token | *(not used)* | API Secret (Consumer Secret) |
| Metadata | `{"channel_id": "@channel"}` | `{"access_token": "...", "access_token_secret": "..."}` |

---

## 🎯 Quick Reference

### Credentials Structure:
```json
{
  "access_token": "API_KEY",
  "refresh_token": "API_SECRET",
  "metadata": {
    "access_token": "USER_ACCESS_TOKEN",
    "access_token_secret": "USER_ACCESS_TOKEN_SECRET"
  }
}
```

### Character Limits:
- **Standard**: 280 characters
- **With images**: Text + up to 4 images
- **With video**: Text + 1 video

### Supported Media:
- **Images**: JPG, PNG, GIF (up to 5MB)
- **Videos**: MP4, MOV (up to 512MB)

---

## ❓ Troubleshooting

### Issue: "Invalid credentials"

**Check:**
1. Did you regenerate tokens after changing permissions to "Read and write"?
2. Are all 4 credentials correct (no typos)?
3. Is your app in "Production" environment?

**Solution:**
1. Go to Developer Portal → Your App → Keys and tokens
2. Regenerate Access Token and Secret
3. Make sure app permissions are "Read and write"
4. Update credentials in Web UI

### Issue: "403 Forbidden" when posting

**Cause:** App doesn't have write permissions

**Solution:**
1. Go to app Settings → User authentication settings
2. Set permissions to "Read and write"
3. **Regenerate** your Access Token and Secret
4. Update credentials in Web UI

### Issue: "Tweet appears as [Automated]"

**This is normal!** Twitter marks automated posts. To avoid this:
- Don't post too frequently
- Vary your content
- Engage manually occasionally

### Issue: "Rate limit exceeded"

**Twitter limits:**
- 300 tweets per 3 hours
- 50 tweets with same content in 24 hours

**Solution:**
- Space out your posts
- Vary content
- Check Twitter's rate limits documentation

---

## ✅ Success Checklist

Before posting, verify:
- ✅ Twitter Developer account approved
- ✅ App created with "Read and write" permissions
- ✅ All 4 credentials generated
- ✅ Test script passed (optional but recommended)
- ✅ Credentials saved in Web UI
- ✅ Test tweet posted successfully

---

## 🎉 You're Ready!

Once credentials are saved, you can:
- ✅ Post tweets instantly or schedule them
- ✅ Upload images and videos
- ✅ Monitor post status in dashboard
- ✅ Retry failed posts
- ✅ Delete tweets if needed

---

## 🔒 Security Notes

- ✅ Never share your API keys publicly
- ✅ Never commit credentials to git
- ✅ Credentials are encrypted in database
- ✅ Only admin users can access credentials
- ✅ Tokens are sent over HTTPS only

---

## 📚 Additional Resources

- [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [OAuth 1.0a Guide](https://developer.twitter.com/en/docs/authentication/oauth-1-0a)
- [Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
- [Media Upload](https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/overview)

---

## 🚀 Happy Tweeting!

Your Twitter integration is now fully operational! Start posting amazing content for your TechKids community! 🎓✨
