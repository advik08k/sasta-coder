# 🤖 Sasta Coder — Free Unlimited AI Telegram Bot

> Antigravity CLI jaisa powerful AI bot, bilkul FREE!

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## ✨ Features

| Feature | Status |
|---------|--------|
| 🤖 Gemini 3.7 Flash Chat | ✅ Free, Unlimited |
| 🔍 Web Search | ✅ Free (DuckDuckGo) |
| 🎨 Image Generation | ✅ Free (Pollinations FLUX) |
| 🧠 Deep Thinking Mode | ✅ Gemini Thinking |
| 💾 GitHub Memory | ✅ Persistent chat history |
| 📁 File Send/Download | ✅ |
| ⬆️ GitHub Upload | ✅ |
| 🎛️ Inline Keyboard UI | ✅ Beautiful interface |

## 🚀 Deploy on Render (5 minutes)

### Step 1: Fork this repo

### Step 2: Render pe deploy karo
1. [render.com](https://render.com) → **New Web Service**
2. GitHub repo connect karo
3. Settings:
   - **Build:** `pip install -r requirements.txt && curl -sL https://raw.githubusercontent.com/Sophomoresty/gemini-web2api/main/gemini_web2api.py -o gemini_web2api.py`
   - **Start:** `python render_main.py`
   - **Plan:** Free

### Step 3: Environment Variables add karo
| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | Telegram bot token (@BotFather se) |
| `MY_USER_ID` | Tumhara Telegram user ID |
| `GITHUB_TOKEN` | GitHub PAT (repo permission) |
| `MEMORY_REPO` | `username/sasta-coder` |

### Step 4: Deploy!

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Home screen with buttons |
| `/search <query>` | Web search |
| `/image <prompt>` | Image generate |
| `/think <question>` | Deep thinking mode |
| `/model` | Switch AI model |
| `/github <repo> <path>` | Upload to GitHub |
| `/memory` | View chat history |
| `/clear` | Clear history |

## 🧠 GitHub Memory
Chat history automatically saves to `memory/{user_id}.json` in this repo.
Persist karta hai even after Render restarts!

## 🤖 Models Available
- `gemini-3.7-flash` — Latest, fastest
- `gemini-3.6-flash` — Stable
- `gemini-3.5-flash-thinking` — Deep reasoning
- `gemini-flash-lite` — Lightest

## ⚠️ Limitations
- Code execute nahi kar sakta (cloud security)
- Local files access nahi (cloud pe hai)
- Render free tier 15min mein so sakta hai (bot polling se mostly awake)

---
*Powered by [gemini-web2api](https://github.com/Sophomoresty/gemini-web2api) + Pollinations.ai*
