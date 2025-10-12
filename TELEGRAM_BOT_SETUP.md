# Setting Up Telegram Bot for TechKids

## Step-by-Step Guide

### Step 1: Create Your Bot with BotFather

1. **Open Telegram** on your phone or desktop
2. **Search for @BotFather** in the search bar
3. **Start a chat** with BotFather by clicking "START"
4. **Send the command**: `/newbot`
5. BotFather will ask for a **name** for your bot
   - Example: "TechKids Social Manager"
   - This is the display name users will see
6. BotFather will ask for a **username** for your bot
   - Must end with "bot" (e.g., `techkids_social_bot`)
   - Must be unique across all Telegram
   - Try: `techkids_test_bot` or `your_name_techkids_bot`

### Step 2: Save Your Bot Token

After creating the bot, BotFather will give you a **bot token**. It looks like this:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

⚠️ **IMPORTANT**: 
- Keep this token secret! Anyone with it can control your bot
- Copy it to a secure location
- We'll use it in Step 5

### Step 3: Create a Test Channel

1. **In Telegram**, click the hamburger menu (☰) or "New Message"
2. Select **"New Channel"**
3. **Name your channel** (e.g., "TechKids Test Posts")
4. Set it to **Public** or **Private** (your choice)
5. If public, choose a username (e.g., `@techkids_test_channel`)
6. Click **"Create"**

### Step 4: Add Your Bot as Administrator

1. **Open your channel**
2. Click the **channel name** at the top
3. Click **"Administrators"**
4. Click **"Add Administrator"**
5. **Search for your bot** by username (e.g., `@techkids_test_bot`)
6. **Select your bot** and give it these permissions:
   - ✅ Post Messages
   - ✅ Edit Messages of Others (optional)
   - ✅ Delete Messages of Others (optional)
7. Click **"Done"**

### Step 5: Get Your Channel ID

**Option A: If your channel is public**
- Your channel ID is just: `@your_channel_username`
- Example: `@techkids_test_channel`

**Option B: If your channel is private**
- You need the numeric ID (looks like: `-1001234567890`)
- Method 1: Forward any message from the channel to @userinfobot
- Method 2: We'll help you get it programmatically in the test

### Step 6: Set Environment Variables

Once you have your bot token and channel ID, run these commands in your terminal:

```bash
# Set your bot token (replace with your actual token)
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"

# Set your channel ID (replace with your actual channel)
export TELEGRAM_CHANNEL_ID="@techkids_test_channel"
# OR if private channel:
# export TELEGRAM_CHANNEL_ID="-1001234567890"
```

### Step 7: Test the Integration

Run the test script:

```bash
cd /workspaces/techkids
python -m backend.services.dispatchers.test_telegram
```

You should see:
```
🤖 Testing Telegram Bot Integration
   Bot Token: 123456789:...67890
   Channel ID: @techkids_test_channel

📋 Test 1: Validating bot credentials...
   ✅ Bot credentials are valid!

📋 Test 2: Sending text message...
   ✅ Message sent successfully!
   Message ID: 123
   ...
```

Then check your Telegram channel - you should see the test message! 🎉

---

## Troubleshooting

### "Bot not found" error
- Make sure you added the bot as an administrator to the channel
- Check that you're using the correct bot username

### "Chat not found" error
- Verify your channel ID is correct
- For public channels, use `@channel_username`
- For private channels, use the numeric ID like `-1001234567890`

### "Unauthorized" error
- Check your bot token is correct
- Make sure you copied the entire token (no spaces)

### "Need administrator rights" error
- The bot must be an administrator in the channel
- Give it at least "Post Messages" permission

---

## Security Notes

⚠️ **Never commit your bot token to git!**

For production:
1. Store bot token in `.env` file (add `.env` to `.gitignore`)
2. Use environment variables
3. In production, use the database to store encrypted credentials

---

## What's Next?

After successful testing:
1. We'll integrate the dispatcher into the social media scheduler
2. You can post to Telegram from the admin dashboard
3. Schedule posts for future publishing
4. Track post analytics

Ready? Let's do this! 🚀
