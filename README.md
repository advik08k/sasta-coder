# 🤖 Unlimited Free Gemini Telegram Bot

Free Telegram bot powered by Gemini 3.7 Flash with NO limits, NO API key needed.

## Features
- Unlimited Gemini 3.6/3.7 Flash (free, no API key)
- Multi-turn conversation memory
- Deep thinking mode (`/think`)
- Runs 24/7 on Render.com free tier

## Deploy on Render (5 minutes)

### Step 1: Get Telegram Bot Token
1. Open Telegram → `@BotFather`
2. `/newbot` → name → username
3. Copy the token

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/TUMHARA_USERNAME/gemini-telegram-bot.git
git push -u origin main
```

### Step 3: Deploy on Render
1. [render.com](https://render.com) → Sign up (free)
2. New → Web Service → Connect GitHub repo
3. Settings:
   - **Build Command:** `pip install -r requirements.txt && curl -sL https://raw.githubusercontent.com/Sophomoresty/gemini-web2api/main/gemini_web2api.py -o gemini_web2api.py`
   - **Start Command:** `python render_main.py`
   - **Plan:** Free
4. Environment Variables → Add:
   - `BOT_TOKEN` = `123456:ABCdef...` (tumhara token)
5. Deploy!

### Step 4: Use!
Telegram pe apna bot open karo → `/start` → chat karo!

## Commands
| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/clear` | Clear chat history |
| `/think <question>` | Deep thinking mode |
| `/status` | Server status |

## Models Available (Free)
- `gemini-3.7-flash` - Latest (fastest)
- `gemini-3.6-flash` - Stable  
- `gemini-3.5-flash-thinking` - Deep reasoning

## ⚠️ Note on Render Free Tier
Render free web services sleep after 15 min of inactivity.
Since Telegram bot is always polling, it should stay awake.
If it sleeps, first message will wake it up (~30s delay).
