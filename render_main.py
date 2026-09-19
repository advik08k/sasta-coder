"""
SASTA CODER BOT - Antigravity-style Telegram AI
Features:
  ✅ Unlimited Gemini 3.6/3.7 Flash (free, no API key)
  ✅ GitHub as persistent memory (chat history saved to repo)
  ✅ Web search (DuckDuckGo)
  ✅ Image generation (Pollinations - free, unlimited)
  ✅ File upload/download
  ✅ GitHub repo upload
  ✅ Beautiful inline keyboard UI
  ✅ Code formatting + syntax highlight hints
  ✅ Multi-model switching
"""

import os, sys, threading, subprocess, time, logging
import requests, json, tempfile, base64, re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════
BOT_TOKEN    = os.environ.get("BOT_TOKEN",    "8928294457:AAFbQG-pmGO6BYME20Eh6-ZoPJdeDEKkXoM")
MY_USER_ID   = int(os.environ.get("MY_USER_ID", "7774638835"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
MEMORY_REPO  = os.environ.get("MEMORY_REPO",  "advik08k/sasta-coder")  # memory saved here
GEMINI_PORT  = 8081
HEALTH_PORT  = int(os.environ.get("PORT", 10000))
GEMINI_API   = f"http://localhost:{GEMINI_PORT}/v1/chat/completions"
MODELS = {
    "⚡ Flash 3.7 (Latest)":   "gemini-3.7-flash",
    "🔥 Flash 3.6 (Stable)":  "gemini-3.6-flash",
    "🧠 Thinking (Deep)":      "gemini-3.5-flash-thinking",
    "💨 Flash Lite (Fast)":    "gemini-flash-lite",
}

SYSTEM_PROMPT = """You are Sasta Coder, a powerful AI assistant similar to Antigravity CLI.
You help with coding, analysis, debugging, writing, math, and everything else.
For code: always use proper markdown code blocks with language tags.
For long responses: structure with headers and bullet points.
Be concise but complete. Respond in user's language (Hindi/English mix is fine)."""

# ═══════════════════════════════════════════════
# HEALTH SERVER (Render needs open port)
# ═══════════════════════════════════════════════
class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Sasta Coder Bot - OK")
    def log_message(self, *a): pass

def run_health():
    HTTPServer(("0.0.0.0", HEALTH_PORT), Health).serve_forever()

# ═══════════════════════════════════════════════
# GEMINI SERVER
# ═══════════════════════════════════════════════
def start_gemini():
    proc = subprocess.Popen([sys.executable, "gemini_web2api.py"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout:
        log.info(f"[gemini] {line.decode().strip()}")

def wait_gemini():
    for _ in range(40):
        try:
            if requests.get(f"http://localhost:{GEMINI_PORT}/v1/models", timeout=2).ok:
                log.info("✅ Gemini server ready!")
                return True
        except: pass
        time.sleep(1)
    return False

def call_gemini(messages, model="gemini-3.6-flash"):
    try:
        r = requests.post(GEMINI_API,
            headers={"Content-Type": "application/json", "Authorization": "Bearer sk-gemini"},
            json={"model": model, "messages": messages}, timeout=90)
        d = r.json()
        if "choices" in d: return d["choices"][0]["message"]["content"]
        return f"⚠️ Error: {d}"
    except Exception as e:
        return f"❌ Gemini error: {e}"

# ═══════════════════════════════════════════════
# GITHUB MEMORY
# ═══════════════════════════════════════════════
GH_HEADERS = lambda: {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def gh_get_file(path):
    """Get file content + sha from GitHub repo"""
    if not GITHUB_TOKEN: return None, None
    r = requests.get(f"https://api.github.com/repos/{MEMORY_REPO}/contents/{path}",
                     headers=GH_HEADERS(), timeout=10)
    if r.status_code == 200:
        d = r.json()
        content = base64.b64decode(d["content"]).decode("utf-8")
        return content, d["sha"]
    return None, None

def gh_put_file(path, content, message="Update memory", sha=None):
    """Create or update file in GitHub repo"""
    if not GITHUB_TOKEN: return False
    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode()
    }
    if sha: data["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/{MEMORY_REPO}/contents/{path}",
                     headers=GH_HEADERS(), json=data, timeout=15)
    return r.status_code in (200, 201)

def load_memory(uid):
    """Load user's chat history from GitHub"""
    content, _ = gh_get_file(f"memory/{uid}.json")
    if content:
        try:
            return json.loads(content)
        except: pass
    return {"history": [], "model": "gemini-3.6-flash", "created": str(datetime.now())}

def save_memory(uid, data):
    """Save user's chat history to GitHub"""
    path = f"memory/{uid}.json"
    _, sha = gh_get_file(path)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    gh_put_file(path, content, f"Memory update {datetime.now().strftime('%Y-%m-%d %H:%M')}", sha)

def gh_upload_file(repo, path, content, message="Upload via Sasta Coder"):
    """Upload arbitrary file to any GitHub repo"""
    if not GITHUB_TOKEN: return "❌ GITHUB_TOKEN env var set nahi hai Render pe"
    _, sha = gh_get_file(path) if repo == MEMORY_REPO else (None, None)
    # For other repos, check SHA separately
    if repo != MEMORY_REPO:
        r = requests.get(f"https://api.github.com/repos/{repo}/contents/{path}",
                         headers=GH_HEADERS(), timeout=10)
        sha = r.json().get("sha") if r.ok else None
    data = {"message": message, "content": base64.b64encode(content.encode()).decode()}
    if sha: data["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}",
                     headers=GH_HEADERS(), json=data, timeout=15)
    if r.status_code in (200, 201):
        return f"✅ Uploaded! [View on GitHub](https://github.com/{repo}/blob/main/{path})"
    return f"❌ Error: {r.json().get('message', r.text[:100])}"

# ═══════════════════════════════════════════════
# WEB SEARCH
# ═══════════════════════════════════════════════
def web_search(query):
    """Search with multiple fallbacks to avoid rate limits"""
    # Primary: DDG HTML (most reliable, no rate limit)
    try:
        r = requests.get("https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=12)
        import re
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', r.text, re.DOTALL)
        snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:5] if s.strip()]
        if snippets:
            return "\n\n".join([f"• {s[:250]}" for s in snippets])
    except: pass
    # Fallback: DDG Instant Answer
    try:
        r = requests.get("https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        d = r.json()
        parts = []
        if d.get("Abstract"): parts.append(f"📌 {d['Abstract']}")
        for t in d.get("RelatedTopics", [])[:4]:
            if isinstance(t, dict) and t.get("Text"):
                parts.append(f"• {t['Text'][:200]}")
        if parts: return "\n\n".join(parts)
    except: pass
    return f"(Web search unavailable — Gemini will answer from knowledge)"

# ═══════════════════════════════════════════════
# IMAGE GENERATION (Pollinations - FREE)
# ═══════════════════════════════════════════════
def generate_image(prompt, width=1024, height=1024):
    encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&model=flux&seed={int(time.time())}"
    r = requests.get(url, timeout=50)
    if r.ok and len(r.content) > 1000:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp.write(r.content); tmp.close()
        return tmp.name
    return None

# ═══════════════════════════════════════════════
# TELEGRAM BOT
# ═══════════════════════════════════════════════
def run_bot():
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (Application, CommandHandler, MessageHandler,
                               CallbackQueryHandler, filters, ContextTypes)
    from telegram.constants import ParseMode

    # In-memory cache (GitHub is source of truth)
    mem_cache = {}

    def get_mem(uid):
        if uid not in mem_cache:
            mem_cache[uid] = load_memory(uid)
        return mem_cache[uid]

    def save_mem(uid):
        save_memory(uid, mem_cache[uid])

    def auth(u): return u.effective_user.id == MY_USER_ID

    def main_keyboard():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search", callback_data="cmd_search"),
             InlineKeyboardButton("🎨 Image", callback_data="cmd_image")],
            [InlineKeyboardButton("🧠 Switch Model", callback_data="cmd_model"),
             InlineKeyboardButton("🗑 Clear History", callback_data="cmd_clear")],
            [InlineKeyboardButton("📊 Status", callback_data="cmd_status"),
             InlineKeyboardButton("📁 Send as File", callback_data="cmd_file")],
        ])

    def model_keyboard():
        buttons = []
        for label, mid in MODELS.items():
            buttons.append([InlineKeyboardButton(label, callback_data=f"model_{mid}")])
        buttons.append([InlineKeyboardButton("« Back", callback_data="cmd_back")])
        return InlineKeyboardMarkup(buttons)

    async def start(u: Update, c):
        if not auth(u): return
        mem = get_mem(MY_USER_ID)
        cur_model = mem.get("model", "gemini-3.6-flash")
        hist_len = len(mem.get("history", []))
        await u.message.reply_text(
            f"🤖 *Sasta Coder* — Free Unlimited AI\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📡 Model: `{cur_model}`\n"
            f"🧠 Memory: `{hist_len}` messages saved\n"
            f"💾 GitHub: `{MEMORY_REPO}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Bas kuch bhi type karo! 💬\n"
            f"Ya neeche buttons use karo 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_keyboard()
        )

    async def button_handler(u: Update, c):
        if not auth(u): return
        q = u.callback_query
        await q.answer()
        data = q.data

        if data == "cmd_search":
            c.user_data["mode"] = "search"
            await q.edit_message_text("🔍 Kya search karoon?\nType karo:", reply_markup=None)

        elif data == "cmd_image":
            c.user_data["mode"] = "image"
            await q.edit_message_text("🎨 Kaisi image chahiye? Describe karo:", reply_markup=None)

        elif data == "cmd_model":
            mem = get_mem(MY_USER_ID)
            cur = mem.get("model", "gemini-3.6-flash")
            await q.edit_message_text(
                f"🔧 *Model Select Karo*\nCurrent: `{cur}`",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=model_keyboard()
            )

        elif data.startswith("model_"):
            model_id = data[6:]
            mem = get_mem(MY_USER_ID)
            mem["model"] = model_id
            save_mem(MY_USER_ID)
            await q.edit_message_text(
                f"✅ Model changed to: `{model_id}`\nAb kuch bhi pucho!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_keyboard()
            )

        elif data == "cmd_clear":
            mem = get_mem(MY_USER_ID)
            mem["history"] = []
            save_mem(MY_USER_ID)
            await q.edit_message_text(
                "✅ *History cleared!*\nGitHub memory bhi update ho gayi.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_keyboard()
            )

        elif data == "cmd_status":
            try:
                r = requests.get(f"http://localhost:{GEMINI_PORT}/v1/models", timeout=5)
                models = [m["id"] for m in r.json().get("data", [])]
                mem = get_mem(MY_USER_ID)
                await q.edit_message_text(
                    f"📊 *System Status*\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"✅ Gemini: `ONLINE`\n"
                    f"🤖 Models: `{len(models)}`\n"
                    f"🧠 Memory: `{len(mem.get('history',[]))}` msgs\n"
                    f"💾 Repo: `{MEMORY_REPO}`\n"
                    f"🔑 GitHub: {'✅' if GITHUB_TOKEN else '❌ No token'}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"Available: `{', '.join(models[:3])}`",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=main_keyboard()
                )
            except:
                await q.edit_message_text("❌ Gemini server offline!", reply_markup=main_keyboard())

        elif data == "cmd_file":
            c.user_data["mode"] = "file"
            await q.edit_message_text(
                "📁 *File Mode*\n\nFilename batao (e.g. `script.py`):",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=None
            )
            c.user_data["awaiting_filename"] = True

        elif data == "cmd_back":
            await q.edit_message_text(
                "🤖 *Sasta Coder* — Ready!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_keyboard()
            )

    async def handle_msg(u: Update, c):
        if not auth(u): return
        text = u.message.text
        uid  = MY_USER_ID
        mode = c.user_data.get("mode")

        # ── File mode: get filename ─────────────────────
        if c.user_data.get("awaiting_filename"):
            c.user_data["filename"] = text.strip()
            c.user_data.pop("awaiting_filename")
            await u.message.reply_text(
                f"✅ Filename: `{text.strip()}`\nAb content bhejo:",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # ── File mode: save content as file ────────────
        if mode == "file" and "filename" in c.user_data:
            filename = c.user_data.pop("filename")
            c.user_data.pop("mode", None)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}",
                                              mode='w', encoding='utf-8')
            tmp.write(text); tmp.close()
            await u.message.reply_document(
                open(tmp.name, "rb"),
                filename=filename,
                caption=f"📁 `{filename}`",
                parse_mode=ParseMode.MARKDOWN
            )
            os.unlink(tmp.name)
            return

        # ── GitHub upload mode ──────────────────────────
        if mode == "github" and "gh_info" in c.user_data:
            info = c.user_data.pop("gh_info")
            c.user_data.pop("mode", None)
            msg = await u.message.reply_text("⬆️ Uploading to GitHub...")
            result = gh_upload_file(info["repo"], info["path"], text)
            await msg.edit_text(result, parse_mode=ParseMode.MARKDOWN)
            return

        # ── Search mode ─────────────────────────────────
        if mode == "search":
            c.user_data.pop("mode", None)
            msg = await u.message.reply_text(f"🔍 Searching: *{text}*...", parse_mode=ParseMode.MARKDOWN)
            results = web_search(text)
            mem = get_mem(uid)
            model = mem.get("model", "gemini-3.6-flash")
            summary = call_gemini([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Web search results for '{text}':\n{results}\n\nSummarize key points."}
            ], model=model)
            await msg.edit_text(
                f"🔍 *{text}*\n━━━━━━━━━━━━━━━\n{summary[:3500]}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_keyboard()
            )
            return

        # ── Image mode ──────────────────────────────────
        if mode == "image":
            c.user_data.pop("mode", None)
            msg = await u.message.reply_text(f"🎨 Generating: *{text[:50]}*...", parse_mode=ParseMode.MARKDOWN)
            img_path = generate_image(text)
            if img_path:
                await u.message.reply_photo(
                    open(img_path, "rb"),
                    caption=f"🎨 *{text[:100]}*\n_Powered by Pollinations.ai (Free)_",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=main_keyboard()
                )
                os.unlink(img_path)
                await msg.delete()
            else:
                await msg.edit_text("❌ Image generation failed. Dobara try karo.")
            return

        # ── Normal chat ─────────────────────────────────
        await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
        mem = get_mem(uid)
        model = mem.get("model", "gemini-3.6-flash")
        h = mem.setdefault("history", [])

        h.append({"role": "user", "content": text})
        if len(h) > 30: mem["history"] = h[-30:]

        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + mem["history"]
        reply = call_gemini(msgs, model=model)
        h.append({"role": "assistant", "content": reply})

        # Save to GitHub (async - don't block response)
        threading.Thread(target=save_mem, args=(uid,), daemon=True).start()

        # Split + send
        chunks = [reply[i:i+4000] for i in range(0, len(reply), 4000)]
        for i, chunk in enumerate(chunks):
            kb = main_keyboard() if i == len(chunks)-1 else None
            await u.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=kb)

    # ── COMMANDS ────────────────────────────────────────
    async def cmd_search(u: Update, c):
        if not auth(u): return
        if c.args:
            c.user_data["mode"] = "search"
            fake_update = type('obj', (object,), {'message': u.message, 'effective_user': u.effective_user})()
            c.user_data.pop("mode", None)
            msg = await u.message.reply_text(f"🔍 Searching...", parse_mode=ParseMode.MARKDOWN)
            q = " ".join(c.args)
            results = web_search(q)
            mem = get_mem(MY_USER_ID)
            summary = call_gemini([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Results for '{q}':\n{results}\n\nSummarize."}
            ], mem.get("model", "gemini-3.6-flash"))
            await msg.edit_text(f"🔍 *{q}*\n━━━━━━━━━━\n{summary[:3500]}", parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())
        else:
            c.user_data["mode"] = "search"
            await u.message.reply_text("🔍 Kya search karoon?")

    async def cmd_image(u: Update, c):
        if not auth(u): return
        if c.args:
            prompt = " ".join(c.args)
            msg = await u.message.reply_text(f"🎨 Generating...")
            img = generate_image(prompt)
            if img:
                await u.message.reply_photo(open(img, "rb"), caption=f"🎨 {prompt}", reply_markup=main_keyboard())
                os.unlink(img); await msg.delete()
            else:
                await msg.edit_text("❌ Failed")
        else:
            c.user_data["mode"] = "image"
            await u.message.reply_text("🎨 Describe the image:")

    async def cmd_github(u: Update, c):
        if not auth(u): return
        if len(c.args) >= 2:
            c.user_data["mode"] = "github"
            c.user_data["gh_info"] = {"repo": c.args[0], "path": c.args[1]}
            await u.message.reply_text(
                f"📁 Ready to upload to:\n`{c.args[0]}/{c.args[1]}`\n\nContent bhejo:",
                parse_mode=ParseMode.MARKDOWN)
        else:
            await u.message.reply_text("Usage: `/github owner/repo path/file.py`", parse_mode=ParseMode.MARKDOWN)

    async def cmd_clear(u: Update, c):
        if not auth(u): return
        mem = get_mem(MY_USER_ID); mem["history"] = []
        save_mem(MY_USER_ID)
        await u.message.reply_text("✅ History cleared + GitHub memory updated!", reply_markup=main_keyboard())

    async def cmd_think(u: Update, c):
        if not auth(u): return
        if not c.args:
            await u.message.reply_text("Usage: `/think your question`", parse_mode=ParseMode.MARKDOWN)
            return
        q = " ".join(c.args)
        msg = await u.message.reply_text("🧠 *Deep thinking...*", parse_mode=ParseMode.MARKDOWN)
        reply = call_gemini([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": q}
        ], model="gemini-3.5-flash-thinking")
        await msg.edit_text(reply[:4000], parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())

    async def cmd_model(u: Update, c):
        if not auth(u): return
        await u.message.reply_text("🔧 Model select karo:", reply_markup=model_keyboard())

    async def cmd_memory(u: Update, c):
        if not auth(u): return
        mem = get_mem(MY_USER_ID)
        h = mem.get("history", [])
        if not h:
            await u.message.reply_text("🧠 Memory empty hai abhi.")
            return
        summary = f"🧠 *Memory Summary*\n`{len(h)}` messages stored\n\nLast 3:\n"
        for msg in h[-3:]:
            role = "You" if msg["role"] == "user" else "Bot"
            summary += f"\n*{role}:* {msg['content'][:100]}..."
        await u.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())

    # Build app
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("search",  cmd_search))
    app.add_handler(CommandHandler("image",   cmd_image))
    app.add_handler(CommandHandler("github",  cmd_github))
    app.add_handler(CommandHandler("clear",   cmd_clear))
    app.add_handler(CommandHandler("think",   cmd_think))
    app.add_handler(CommandHandler("model",   cmd_model))
    app.add_handler(CommandHandler("memory",  cmd_memory))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

    log.info("✅ Sasta Coder Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    threading.Thread(target=run_health, daemon=True).start()
    threading.Thread(target=start_gemini, daemon=True).start()
    log.info("⏳ Waiting for Gemini server...")
    time.sleep(5)
    if not wait_gemini():
        log.error("❌ Gemini server failed to start!"); sys.exit(1)
    run_bot()
