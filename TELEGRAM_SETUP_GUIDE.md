# 📱 Telegram Bot Setup Guide - Visual Walkthrough

This guide shows you exactly where to click in Telegram to set up your bot.

## ✅ You Can Use Either:
- **Telegram Mobile App** (iPhone/Android) - ✅ Easiest
- **Telegram Desktop** (Windows/Mac/Linux)
- **Telegram Web** (web.telegram.org)

---

## 🤖 Step 1: Find BotFather

### On Mobile App:
1. Open your Telegram app
2. Tap the **search icon** (🔍) at the top
3. Type: `@BotFather`
4. Tap on **BotFather** (it has a verified checkmark ✓)
5. Tap **START** at the bottom

### On Desktop:
1. Open Telegram Desktop
2. Click the **search bar** at the top
3. Type: `@BotFather`
4. Click on **BotFather** 
5. Click **START**

**What you'll see:**
```
BotFather will send you a welcome message with a list of commands:

I can help you create and manage Telegram bots.

/newbot - create a new bot
/mybots - edit your bots
/setname - change a bot's name
...
```

---

## 🆕 Step 2: Create Your Bot

### What to do:
1. Type or tap: `/newbot`
2. BotFather will ask: **"Alright, a new bot. How are we going to call it?"**
3. Type your bot's display name (example: `TechKids Social Bot`)
4. BotFather will ask for a username
5. Type a username ending in `bot` (example: `techkids_social_bot`)

**Example conversation:**
```
You: /newbot

BotFather: Alright, a new bot. How are we going to call it? 
Please choose a name for your bot.

You: TechKids Social Bot

BotFather: Good. Now let's choose a username for your bot. 
It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.

You: techkids_social_bot

BotFather: Done! Congratulations on your new bot. 
You will find it at t.me/techkids_social_bot

Use this token to access the HTTP API:
7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw

Keep your token secure and store it safely...
```

### ⚠️ IMPORTANT:
**COPY THE TOKEN!** It looks like: `7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`

This is your `TELEGRAM_BOT_TOKEN` - you'll need it for testing!

---

## 📢 Step 3: Create a Test Channel

### On Mobile App:
1. Go back to your main Telegram screen
2. Tap the **pencil icon** (✏️) or **new message** button
3. Select **New Channel**
4. Enter channel name (example: `TechKids Test Channel`)
5. Select **Public** channel
6. Enter channel username (example: `techkids_test`)
7. Tap **Create**

### On Desktop:
1. Click the **☰ menu** (three lines) at top left
2. Select **New Channel**
3. Enter channel name and description
4. Choose **Public**
5. Enter channel link (example: `techkids_test`)
6. Click **Create**

**Your channel ID will be:** `@techkids_test` (your username with @ in front)

---

## 👤 Step 4: Add Your Bot as Admin

### On Mobile App:
1. Open your new channel
2. Tap the **channel name** at the top
3. Tap **Administrators**
4. Tap **Add Administrator**
5. Search for your bot name (example: `techkids_social_bot`)
6. Tap on your bot
7. Grant **Post Messages** permission (at minimum)
8. Tap **Done** or **Save**

### On Desktop:
1. Open your channel
2. Click the **channel name** at the top
3. Click **Administrators** → **Add Administrator**
4. Search for your bot
5. Select your bot
6. Check **Post Messages** permission
7. Click **Save**

---

## 🎯 Step 5: Get Your Credentials Ready

You now have everything you need:

```bash
TELEGRAM_BOT_TOKEN="7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"
TELEGRAM_CHANNEL_ID="@techkids_test"
```

### ⚠️ Security Notes:
- **Never share your bot token** publicly
- **Never commit it to git**
- Store it in `.env` file or environment variables
- Treat it like a password!

---

## 🧪 Step 6: Test Your Setup

### Option A: Quick Test (Manual)
1. Open your bot in Telegram (search for `@techkids_social_bot`)
2. Send it any message
3. If it doesn't respond, that's OK! Our bot doesn't have auto-reply yet

### Option B: Run Our Test Script (Recommended)

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHANNEL_ID="@your_channel"

# Run the test
cd /workspaces/techkids
python -m backend.services.dispatchers.test_telegram
```

**Expected output:**
```
🤖 Testing Telegram Bot Integration
   Bot Token: 7123456789...dsaw
   Channel ID: @techkids_test

📋 Test 1: Validating bot credentials...
   ✅ Bot credentials are valid!

📋 Test 2: Sending text message...
   ✅ Message sent successfully!
   Message ID: 123
   
🎉 Telegram Integration Test Complete!
```

---

## ❓ Troubleshooting

### "Unauthorized" Error
- ✅ Check you copied the token correctly (no spaces)
- ✅ Make sure you're using the token from BotFather's latest message

### "Chat not found" Error
- ✅ Check the channel username is correct (`@your_channel`)
- ✅ Make sure you added the bot as administrator
- ✅ Verify the bot has "Post Messages" permission

### "Bot is not a member" Error
- ✅ Go to your channel settings
- ✅ Add the bot as administrator again
- ✅ Make sure to save changes

### Can't find BotFather
- ✅ Make sure you're searching for `@BotFather` (with @)
- ✅ Look for the one with a verified checkmark ✓
- ✅ The official BotFather has username `@BotFather`

---

## 🎉 Success Checklist

- [ ] Found BotFather in Telegram
- [ ] Created a new bot
- [ ] Copied the bot token
- [ ] Created a test channel
- [ ] Added bot as channel administrator
- [ ] Noted the channel username (@your_channel)
- [ ] Ready to run the test!

---

## 📚 Next Steps

Once your bot is set up:

1. **Run the test script** to verify everything works
2. **Check your Telegram channel** to see the test message appear
3. **Integrate with TechKids** social media management system
4. **Schedule posts** through the admin dashboard

---

## 💡 Pro Tips

1. **Use a test channel** first - don't use your main channel for testing!
2. **Keep the bot token secret** - treat it like a password
3. **One bot can post to multiple channels** - just add it as admin to each
4. **Bot tokens don't expire** - but you can revoke/regenerate if compromised
5. **Telegram has no daily limits** for bot messages to channels (unlike other platforms!)

---

## 🆘 Need Help?

If you're stuck:
1. Check the [Telegram Bot API docs](https://core.telegram.org/bots/api)
2. Read the error messages carefully
3. Verify bot permissions in channel settings
4. Try revoking and generating a new token with BotFather (`/revoke`)

---

**Ready to test?** Follow Step 6 above! 🚀
