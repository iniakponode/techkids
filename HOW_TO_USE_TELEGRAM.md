# 🎯 How to Use Telegram Bot in Social Media Control Center

## Two Ways to Set Up Your Telegram Bot

---

## Option 1: Quick Test (Terminal) - For Testing Only

This is just to **verify the integration works** before using it in the app.

### Step 1: Get your credentials from Telegram
- Bot Token from @BotFather
- Channel ID (your @channel_name)

### Step 2: Run test in terminal
```bash
# Replace with YOUR actual values!
export TELEGRAM_BOT_TOKEN="7845123456:AABbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq"
export TELEGRAM_CHANNEL_ID="@myawesomechannel"

# Run the test
cd /workspaces/techkids
python -m backend.services.dispatchers.test_telegram
```

**What this does:** Tests that your bot can post to your channel

**When to use:** When you first set up the bot, to make sure it works

---

## Option 2: Use the Web UI (Production) - For Real Use

This is the **normal way** to use Telegram in your application!

### Step 1: Login to Admin Dashboard
1. Go to your TechKids website
2. Login as admin
3. Navigate to **Social Media Control Center**

### Step 2: Find "Platform Credentials" Section
On the right side of the page, you'll see a card titled **"Platform Credentials"**

### Step 3: Fill in the Form

```
┌─────────────────────────────────────────────────┐
│  Platform Credentials                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  Platform:                                      │
│  [Select: Telegram ▼]                           │
│                                                 │
│  Access Token:                                  │
│  [8173820735:AAHz_zD85e...]                    │  ← Paste your bot token here
│                                                 │
│  Refresh Token (optional):                      │
│  [                                    ]         │  ← Leave empty for Telegram
│                                                 │
│  Metadata:                                      │
│  ┌───────────────────────────────────┐         │
│  │ {"channel_id": "@techkids_test"}  │         │  ← Enter your channel ID here
│  └───────────────────────────────────┘         │
│  💡 Telegram: Enter {"channel_id": "@channel"} │
│     Other platforms: Optional JSON or notes    │
│                                                 │
│  [Save Credentials]                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Step 4: Fill in each field

**Platform:** 
- Select **Telegram** from dropdown

**Access Token:** 
- Paste your bot token from BotFather
- Example: `7845123456:AABbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq`

**Refresh Token:**
- **Leave this empty** (Telegram doesn't use refresh tokens)

**Metadata:**
- Enter: `{"channel_id": "@your_channel_name"}`
- Replace `@your_channel_name` with your actual channel
- Example: `{"channel_id": "@techkids_test"}`

### Step 5: Save
- Click **"Save Credentials"** button
- You should see a success message

---

## ✅ After Saving Credentials

Now you can **create and schedule posts** to Telegram!

### How to Post to Telegram:

1. In the **"Create or Schedule a Post"** section (left side)
2. Fill in the form:
   ```
   Platform:      [Select: Telegram]
   Content Type:  [Post]
   Content:       [Your message text here...]
   Image:         [Optional - upload an image] ← Now visible!
   Video:         [Optional - upload a video] ← Now visible!
   Schedule Time: [Optional - leave empty for immediate post]
   ```
3. Click **"Save Post"**
4. The post will be sent to your Telegram channel!

**Note:** Both image and video fields are now always visible. You can upload:
- Text only (no media)
- Text + Image
- Text + Video
- Just choose which media you want to include!

---

## 🔄 Complete Example Flow

### 1. Setup (One Time)
```
Telegram App:
  @BotFather → /newbot → Get token
  Create Channel → Add bot as admin

TechKids Admin:
  Social Media Control Center → Platform Credentials
  Platform: Telegram
  Access Token: <paste token>
  Metadata: {"channel_id": "@mychannel"}
  Save Credentials ✅
```

### 2. Daily Use (Every Time You Want to Post)
```
TechKids Admin:
  Social Media Control Center → Create or Schedule a Post
  Platform: Telegram
  Content Type: Post
  Content: "Check out our new Python course! 🐍"
  Image: [Upload course image]
  Schedule Time: [2024-10-12 14:00] or leave empty
  Save Post ✅

Result:
  Post appears in your Telegram channel! 🎉
```

---

## 📊 What Each Field Means

### Terminal Method (Testing):
```bash
export TELEGRAM_BOT_TOKEN="..."     # Your bot's secret token
export TELEGRAM_CHANNEL_ID="@..."   # Where to post
```

### Web UI Method (Production):
```
Access Token = TELEGRAM_BOT_TOKEN    # Same thing, different name
Metadata     = {"channel_id": "@..."} # Channel info in JSON format
```

**They're the same information, just entered differently!**

---

## ❓ FAQ

### Q: Do I need to use the terminal method?
**A:** No! The terminal method is optional, just for testing. You can go straight to the Web UI.

### Q: What's the metadata field for?
**A:** It stores extra information. For Telegram, we use it to store which channel to post to.

### Q: Can I have multiple channels?
**A:** Yes! Just save credentials with different channel IDs. You can select which one when creating a post.

### Q: Do I need to enter credentials every time I post?
**A:** No! Save them once, then just create posts normally.

### Q: Is my bot token secure?
**A:** Yes! It's stored encrypted in the database. Never share it publicly.

---

## 🎬 Quick Start (Choose One):

### Path A: Test First, Then Use UI
1. Create bot on Telegram (5 mins)
2. Test with terminal commands (2 mins)
3. Add credentials in Web UI (1 min)
4. Start posting! (ongoing)

### Path B: Skip Testing, Go Straight to UI
1. Create bot on Telegram (5 mins)
2. Add credentials in Web UI (1 min)
3. Create your first post (1 min)
4. Start posting! (ongoing)

**Most users choose Path B!** Testing is optional.

---

## ✨ You're Ready!

Once you add credentials in the Web UI, you can:
- ✅ Create posts from the dashboard
- ✅ Schedule posts for later
- ✅ Upload images and videos
- ✅ Post to multiple channels
- ✅ Track your posts

No more terminal commands needed! 🎉
