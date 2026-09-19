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
You have Agentic Capabilities. 

1. PYTHON EXECUTION (Sandbox):
If you need to run Python code to solve math, process data, scrape, or test an API, you MUST wrap your code EXACTLY like this:
```python
# EXECUTE
import requests
print(requests.get("https://api.github.com").status_code)
```
The system will run this code in a secure cloud sandbox (Piston API) and feed the STDOUT back to you in the next message. 

2. GENERAL INSTRUCTIONS:
- For long responses: structure with headers and bullet points.
- Be concise but complete. Respond in user's language (Hindi/English mix is fine)."""

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
import concurrent.futures

def get_working_proxy():
    """Background mein proxy dhundho — bot chal raha hoga tab bhi"""
    log.info("🔍 Searching for proxy in background...")
    try:
        r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", timeout=10)
        proxies = [p for p in r.text.splitlines() if ":" in p][:100]
    except Exception as e:
        log.warning(f"Proxy list fetch failed: {e}")
        return None

    def test_p(p):
        try:
            r = requests.get("https://gemini.google.com",
                             proxies={"http": f"http://{p}", "https": f"http://{p}"},
                             timeout=4)
            if r.status_code == 200: return p
        except: return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as exe:
        for res in exe.map(test_p, proxies):
            if res:
                log.info(f"✅ Found proxy: {res}")
                return f"http://{res}"
    return None

def start_gemini():
    """
    Phase 1: Bina proxy ke turant start karo (bot immediately online)
    Phase 2: Agar 429 aaya → background mein proxy dhundo → restart with proxy
    """
    while True:
        # --- Phase 1: No proxy, instant start ---
        log.info("🚀 Starting Gemini (no proxy, instant start)...")
        proc = subprocess.Popen(
            [sys.executable, "gemini_web2api.py"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        error_429_count = 0
        for line in proc.stdout:
            line_str = line.decode().strip()
            log.info(f"[gemini] {line_str}")
            if "HTTP Error 429" in line_str:
                error_429_count += 1
                if error_429_count >= 3:
                    log.warning("⚠️ 429s hit. Finding proxy in background...")
                    proc.kill()
                    break

        proc.wait()

        # --- Phase 2: 429 hit → get proxy → restart ---
        proxy = get_working_proxy()
        if not proxy:
            log.warning("No proxy found, retrying direct in 10s...")
            time.sleep(10)
            continue

        log.info(f"🔄 Restarting with proxy: {proxy}")
        proc2 = subprocess.Popen(
            [sys.executable, "gemini_web2api.py", "--proxy", proxy],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        error_429_count = 0
        for line in proc2.stdout:
            line_str = line.decode().strip()
            log.info(f"[gemini+proxy] {line_str}")
            if "HTTP Error 429" in line_str:
                error_429_count += 1
                if error_429_count >= 3:
                    log.warning("Proxy also 429'd. Getting new proxy...")
                    proc2.kill()
                    break

        proc2.wait()
        log.warning("🔄 Gemini server stopped. Restarting in 5s...")
        time.sleep(5)


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

def execute_python_code(code):
    """Executes python code via Piston API (Free external sandbox)"""
    try:
        r = requests.post("https://emkc.org/api/v2/piston/execute", json={
            "language": "python",
            "version": "3.10.0",
            "files": [{"content": code}]
        }, timeout=15)
        d = r.json()
        if "run" in d and "output" in d["run"]:
            out = d["run"]["output"].strip()
            return out if out else "[Executed successfully with no output]"
        return f"Execution Error: {d.get('message', str(d))}"
    except Exception as e:
        return f"Failed to execute code: {e}"

def fetch_url_content(url):
    """Fetch content using Jina Reader API (renders JS, outputs clean markdown)"""
    try:
        # If raw github url, fetch directly
        if "raw.githubusercontent.com" in url:
            r = requests.get(url, timeout=10)
        else:
            # Bypass JS/React/Cloudflare using Jina headless browser API
            r = requests.get(f"https://r.jina.ai/{url}", headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        
        r.raise_for_status()
        text = r.text
        if len(text) > 30000:
            text = text[:30000] + "\n...[TRUNCATED TO 30KB]"
        return text
    except Exception as e:
        return f"[Failed to fetch {url}: {e}]"

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
def web_search(query, model="gemini-3.6-flash"):
    """Gemini ka built-in web search use karo — koi external API nahi, koi rate limit nahi"""
    try:
        r = requests.post(GEMINI_API,
            headers={"Content-Type": "application/json", "Authorization": "Bearer sk-gemini"},
            json={"model": model, "messages": [
                {"role": "system", "content": "You have internet access via Gemini's web search. Search and give latest accurate info with sources."},
                {"role": "user", "content": f"Search the web for: {query}\n\nGive key facts and latest information."}
            ]}, timeout=60)
        d = r.json()
        if "choices" in d:
            return d["choices"][0]["message"]["content"]
        return "Search failed."
    except Exception as e:
        return f"Error: {e}"

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
        
        # Text ya Photo+Caption dono allow karna hai
        text = u.message.text or u.message.caption or ""
        uid  = MY_USER_ID
        mode = c.user_data.get("mode")

        # Handle Photo / Vision
        image_b64 = None
        if u.message.photo:
            photo_file = await u.message.photo[-1].get_file()
            img_bytes = await photo_file.download_as_bytearray()
            image_b64 = base64.b64encode(img_bytes).decode('utf-8')
            text = text or "Explain this image in detail."

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
            try:
                await msg.edit_text(
                    f"🔍 *{text}*\n━━━━━━━━━━━━━━━\n{summary[:3500]}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                await msg.edit_text(f"🔍 {text}\n━━━━━━━━━━━━━━━\n{summary[:3500]}")
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
                    parse_mode=ParseMode.MARKDOWN
                )
                os.unlink(img_path)
                await msg.delete()
            else:
                await msg.edit_text("❌ Image generation failed. Dobara try karo.")
            return

        # ── Normal chat / Vision / URL Reader ────────────────────────
        await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
        
        urls = re.findall(r'(https?://[^\s]+)', text)
        url_contexts = []
        if urls:
            for url in set(urls[:3]):  # Limit to 3 unique URLs max
                content = fetch_url_content(url)
                url_contexts.append(f"--- Content from {url} ---\n{content}\n-------------------")
        
        final_text = text
        if url_contexts:
            final_text += "\n\n" + "\n\n".join(url_contexts) + "\n\n(Note for AI: The user provided these links. Use the extracted content above to answer their prompt.)"

        mem = get_mem(uid)
        model = mem.get("model", "gemini-3.6-flash")
        h = mem.setdefault("history", [])

        if image_b64:
            # Multimodal OpenAI format
            h.append({
                "role": "user", 
                "content": [
                    {"type": "text", "text": final_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]
            })
        else:
            h.append({"role": "user", "content": final_text})
            
        if len(h) > 30: mem["history"] = h[-30:]

        # Agentic Loop for Python Execution
        max_turns = 3
        current_turn = 0
        final_reply = ""

        while current_turn < max_turns:
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + mem["history"]
            reply = call_gemini(msgs, model=model)
            h.append({"role": "assistant", "content": reply})
            
            # Check if Gemini wants to execute code
            code_match = re.search(r'```python\s*# EXECUTE\s*(.*?)```', reply, re.DOTALL)
            if code_match:
                code_to_run = code_match.group(1).strip()
                status_msg = await u.message.reply_text(f"⚙️ Running code in sandbox...\n```python\n{code_to_run[:300]}...\n```", parse_mode=ParseMode.MARKDOWN)
                
                output = execute_python_code(code_to_run)
                h.append({"role": "user", "content": f"Code Output:\n```text\n{output}\n```\nAnalyze this output and answer the user."})
                await status_msg.edit_text(f"⚙️ Output received:\n```text\n{output[:500]}\n```", parse_mode=ParseMode.MARKDOWN)
                
                # Send typing action for the next turn
                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            else:
                final_reply = reply
                break

        # Save to GitHub (async - don't block response)
        threading.Thread(target=save_mem, args=(uid,), daemon=True).start()

        # Store last reply for /savefile command
        c.user_data["last_reply"] = final_reply
        reply = final_reply

        # Split + send (NO keyboard — use /menu for that)
        chunks = [reply[i:i+4000] for i in range(0, len(reply), 4000)]
        for chunk in chunks:
            try:
                await u.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                log.warning(f"Markdown parsing failed, sending as plain text. Error: {e}")
                await u.message.reply_text(chunk) # Fallback to plain text

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
            try:
                await msg.edit_text(f"🔍 *{q}*\n━━━━━━━━━━\n{summary[:3500]}", parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())
            except Exception:
                await msg.edit_text(f"🔍 {q}\n━━━━━━━━━━\n{summary[:3500]}", reply_markup=main_keyboard())
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

    async def cmd_menu(u: Update, c):
        """Show main keyboard — sirf is command pe aayega"""
        if not auth(u): return
        mem = get_mem(MY_USER_ID)
        await u.message.reply_text(
            f"🎛 *Menu* — Model: `{mem.get('model','gemini-3.6-flash')}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_keyboard()
        )

    async def cmd_savefile(u: Update, c):
        """/savefile filename.py — last bot reply ko file ke roop mein bhejo"""
        if not auth(u): return
        last = c.user_data.get("last_reply")
        if not last:
            await u.message.reply_text("❌ Koi reply nahi mili abhi tak. Pehle kuch poochho!")
            return
        filename = c.args[0] if c.args else "output.txt"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}",
                                          mode='w', encoding='utf-8')
        tmp.write(last); tmp.close()
        await u.message.reply_document(
            open(tmp.name, "rb"),
            filename=filename,
            caption=f"📁 `{filename}`",
            parse_mode=ParseMode.MARKDOWN
        )
        os.unlink(tmp.name)

    # Build app
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("menu",     cmd_menu))
    app.add_handler(CommandHandler("search",   cmd_search))
    app.add_handler(CommandHandler("image",    cmd_image))
    app.add_handler(CommandHandler("github",   cmd_github))
    app.add_handler(CommandHandler("clear",    cmd_clear))
    app.add_handler(CommandHandler("think",    cmd_think))
    app.add_handler(CommandHandler("model",    cmd_model))
    app.add_handler(CommandHandler("memory",   cmd_memory))
    app.add_handler(CommandHandler("savefile", cmd_savefile))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_msg))

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
