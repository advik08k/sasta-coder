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
import requests, json, tempfile, base64, re, random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)  # har 10s getUpdates spam band

# ═══════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════
BOT_TOKEN    = os.environ.get("BOT_TOKEN",    "8928294457:AAFbQG-pmGO6BYME20Eh6-ZoPJdeDEKkXoM")
MY_USER_ID   = int(os.environ.get("MY_USER_ID", "7774638835"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
MEMORY_REPO  = os.environ.get("MEMORY_REPO",  "advik08k/sasta-coder")  # memory saved here
GEMINI_PORT  = 8081
CLAUDE_PORT  = 8082
HEALTH_PORT  = int(os.environ.get("PORT", 10000))
GEMINI_API   = f"http://localhost:{GEMINI_PORT}/v1/chat/completions"
CLAUDE_API   = f"http://localhost:{CLAUDE_PORT}/v1/chat/completions"
MODELS = {
    "?? Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
    "⚡ Flash 3.7 (Latest)":   "gemini-3.7-flash",
    "🔥 Flash 3.6 (Stable)":  "gemini-3.6-flash",
    "🧠 Thinking (Deep)":      "gemini-3.5-flash-thinking",
    "💨 Flash Lite (Fast)":    "gemini-flash-lite",
    "?? Pollinations AI (Free)": "pollinations-openai",
}

SYSTEM_PROMPT = """You are Sasta Coder, a powerful AI assistant similar to Antigravity CLI.
You have Agentic Capabilities.

1. PYTHON EXECUTION (Sandbox):
If you need to run PURE Python code — math, string/data processing, algorithms, local logic — wrap it EXACTLY like this:
```python
# EXECUTE
print(2 ** 10)
```
The system runs this in an ISOLATED sandbox (Judge0) with NO internet/network access and NO third-party libraries (no `requests`, no network calls — they WILL fail with ModuleNotFoundError or DNS errors). Only pure computation works here. NEVER use this for GitHub, web requests, or any network task — it will always fail.

2. GITHUB REPO CREATION:
If the user asks you to create a new GitHub repository, wrap the repo name EXACTLY like this:
```
# GITHUB_CREATE_REPO
repo_name_here
```
The system creates it via the bot's own process (which has real network access) and reports back success or the exact error.

3. GITHUB FILE UPLOAD:
For uploading/updating files in a repo, tell the user to use the /github command directly — you cannot trigger it yourself.

4. SAVE/GET SKILLS:
If the user asks you to save a code snippet as a reusable "skill" (attachment for later), wrap it EXACTLY like this:
```python
# SAVE_SKILL skill_name
<the code or text to save>
```
To fetch a saved skill back as text, wrap it like this:
```
# GET_SKILL skill_name
```
Leave the name blank to list all saved skills. To RUN a saved skill directly (real execution, full network/token access), wrap it like this:
```
# RUN_SKILL skill_name
```
Use this whenever the user's request calls for it — you decide when running a skill is appropriate. Saved skills are stored as plain files on GitHub.

6. FULL GITHUB API ACCESS:
For anything not covered by the specific tools above — branches, issues, PRs, deleting repos, listing collaborators, or any other GitHub REST API operation — you can call the API directly:
```json
# GITHUB_API
{"method": "PUT", "path": "/repos/owner/repo/contents/file.txt", "body": {"message": "...", "content": "base64..."}}
```
`method` is GET/POST/PUT/PATCH/DELETE, `path` is the API path starting with /, `body` is the JSON payload (omit for GET/DELETE with no body). This is real, unrestricted GitHub access bounded only by what the configured token is scoped to allow — use it carefully, and prefer the specific tools above when they already cover what's needed.

7. TERMINAL ACCESS (FULL SERVER ACCESS WITH INTERNET):
To run bash/shell commands on the host server (Ubuntu Linux), use:
`ash
# RUN_TERMINAL
ls -la
`
8. WEB SCRAPING:
To fetch the raw text content of a website, use:
`
# FETCH_URL
https://example.com
`

8.1 PROACTIVE / SCHEDULED MESSAGES:
If the user wants you to remind them or send a message in the future (e.g. "message me at 4 PM", "kal bhej dena"), calculate the delay in SECONDS from the CURRENT TIME (provided in your prompt), and output EXACTLY:
```
# SCHEDULE_MESSAGE <delay_in_seconds>
<Your message content here>
```
The system will automatically send this message to the user when the time comes. Do NOT write Python scripts for reminders. Use this tool.

8. WEB SCRAPING (Legacy):
To fetch the raw text content of a website, use:
`
# FETCH_URL
https://example.com
`



10. DEVELOPER & AGENT SKILLS:
You are an expert at helping the user BUILD AGENTS and WRITE CODE. Use these tools via # RUN_TERMINAL:
- python skills/tree.py . (Explore codebase directory structure)
- python skills/edit.py <filepath> write "<content>" (Create or overwrite a file. NOTE: Better to use cat << 'EOF' > file for complex code)
- cat skills/agent_guide.md (Read agent building best practices)

- python skills/db.py <db_file.sqlite> "<sql_query>" (Execute SQL queries on a local SQLite database)
- Git Automation: Run git commands directly via # RUN_TERMINAL (e.g. git status, git add ., git commit -m "msg")


To edit or create files with complex code, ALWAYS use bash heredocs via # RUN_TERMINAL:
`ash
# RUN_TERMINAL
cat << 'EOF' > my_script.py
import os
print("Hello Agent")
EOF
`
This is the most reliable way to write code on the host server.

9. GENERAL INSTRUCTIONS:
- IMPORTANT: You are provided with the full chat history. DO NOT re-answer old questions. ONLY respond to the LATEST user message at the very end of the history.

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

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
]
GEMINI_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Proxy mode mein gemini_web2api ka per-attempt timeout (default 180s). Dead/slow proxy
# 180s x 3 tak atka rehta tha (bot ka timeout pehle hit + rotation kabhi trigger nahi).
# 25s x 3 + delays ~ 79s, to fail hone par Retry lines aati hain aur proxy rotate hoti hai.
PROXY_TIMEOUT = 25

def _proxy_cfg():
    p = os.path.join(tempfile.gettempdir(), "gemini_proxy_cfg.json")
    with open(p, "w") as f:
        json.dump({"request_timeout_sec": PROXY_TIMEOUT}, f)
    return p

def get_working_proxy(exclude=()):
    """
    Random sample of proxies -> sirf wahi proxy accept jo gemini.google.com/app ka
    ASLI page (boq_assistant BL string ke saath) de. Sirf status 200 kaafi nahi hai —
    block/consent page bhi 200 deta hai. `exclude` = pehle fail ho chuki proxies.
    """
    log.info("🔍 Searching for a working proxy...")
    pool = set()
    for src_url in PROXY_SOURCES:
        try:
            r = requests.get(src_url, timeout=8)
            if r.ok:
                pool.update(p.strip() for p in r.text.splitlines() if ":" in p and "//" not in p)
        except Exception as e:
            log.warning(f"Proxy list fetch failed ({src_url}): {e}")
    pool -= {p.replace("http://", "") for p in exclude}
    if not pool:
        return None
    candidates = random.sample(sorted(pool), min(150, len(pool)))

    def test_p(p):
        px = f"http://{p}"
        try:
            r = requests.get("https://gemini.google.com/app",
                             proxies={"http": px, "https": px},
                             headers={"User-Agent": GEMINI_UA}, timeout=6)
            if r.status_code == 200 and "boq_assistant-bard-web-server" in r.text:
                return px
        except Exception:
            pass
        return None

    exe = concurrent.futures.ThreadPoolExecutor(max_workers=40)
    try:
        futs = [exe.submit(test_p, p) for p in candidates]
        for f in concurrent.futures.as_completed(futs, timeout=45):
            res = f.result()
            if res:
                log.info(f"✅ Found proxy: {res}")
                return res
    except concurrent.futures.TimeoutError:
        log.warning("Proxy search timed out")
    finally:
        exe.shutdown(wait=False, cancel_futures=True)
    return None

# gemini_web2api.py ki log lines: "Retry 1/3: HTTP Error 429..." (fail) aur
# '127.0.0.1 "POST /v1/chat/completions HTTP/1.1" 200 -' (success)
# call_gemini yahan likhta hai: Gemini ne HTTP 200 diya par content khaali/None (bekaar proxy / Google block page)
_STATE = {"empty": 0}
SKILLS_ENABLED = {"v": True}  # global kill switch for /run_skill — independent of Gemini/proxy
_FAIL_RE = re.compile(r"Retry \d+/\d+:")
_OK_RE   = re.compile(r'"POST /v1/chat/completions[^"]*" 200')

def start_gemini():
    """
    Direct start (bot turant online). Route badalne ke 2 triggers:
      1) lagataar fail (4 "Retry" lines = 2 requests, 429 / dead proxy)
      2) 2 lagataar KHAALI replies (HTTP 200 par content None) — call_gemini _STATE["empty"] badhata hai
    Pehle NAYI proxy dhundo (server chalta rehta hai), mil jaye tabhi restart — downtime kam.
    Fail hui proxy `bad` mein jaati hai, dobara use nahi hoti. Success pe counters reset.
    """
    bad = set()
    state = {"proxy": None, "switched": False}   # proxy None = direct
    lock = threading.Lock()
    backoff = 5

    def try_switch(proc, why):
        if not lock.acquire(blocking=False):      # koi aur already dhundh raha hai
            return
        try:
            if proc.poll() is not None:
                return
            log.warning(f"⚠️ {why}. Naya route dhundh raha hoon...")
            if state["proxy"]:
                bad.add(state["proxy"])
                if len(bad) > 300:
                    bad.clear()
            new_proxy = get_working_proxy(bad)
            _STATE["empty"] = 0
            if new_proxy is None and state["proxy"] is None:
                log.warning("Proxy nahi mili — direct hi chalne do, baad mein phir check hoga")
                return
            state["proxy"] = new_proxy            # None ho to wapas direct (cooldown ke baad)
            state["switched"] = True
            proc.kill()
        finally:
            lock.release()

    def watcher(proc):
        # khaali replies ke baad koi nayi log line na aaye tab bhi route badle
        while proc.poll() is None:
            time.sleep(1)
            if _STATE["empty"] >= 2:
                try_switch(proc, "2 lagataar khaali replies (200 par content None)")
                time.sleep(15)

    while True:
        proxy = state["proxy"]
        cmd = [sys.executable, "gemini_web2api.py"]
        if proxy:
            cmd += ["--proxy", proxy, "--config", _proxy_cfg()]
        log.info(f"🚀 Starting Gemini ({'proxy ' + proxy if proxy else 'direct'})...")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        state["switched"] = False
        _STATE["empty"] = 0
        threading.Thread(target=watcher, args=(proc,), daemon=True).start()

        fails, last_fail = 0, 0.0
        for line in proc.stdout:
            s = line.decode(errors="replace").strip()
            log.info(f"[gemini] {s}")

            if _OK_RE.search(s):
                fails = 0
                if _STATE["empty"] == 0:
                    backoff = 5
            elif _FAIL_RE.search(s):
                now = time.time()
                if now - last_fail > 90:      # purani failures ignore
                    fails = 0
                last_fail = now
                fails += 1
                # 1 poori failed request = 2 "Retry" lines, to 4 = 2 requests lagataar fail
                if fails >= 4:
                    fails, last_fail = 0, time.time()
                    try_switch(proc, "lagataar failures (429/proxy)")

        proc.wait()
        if state["switched"]:
            time.sleep(2)
        else:
            log.warning(f"🔄 Gemini server stopped. Restarting in {backoff}s...")
            time.sleep(backoff)
            backoff = min(backoff * 2, 120)


def wait_gemini():
    for _ in range(40):
        try:
            if requests.get(f"http://localhost:{GEMINI_PORT}/v1/models", timeout=2).ok:
                log.info("✅ Gemini server ready!")
                return True
        except: pass
        time.sleep(1)
    return False

# Gemini fail hone par error text chat mein NAHI jaata (sirf Render logs mein). True karo to wapas dikhega.
SHOW_GEMINI_ERRORS = False

def is_gemini_error(text):
    return (not isinstance(text, str)) or (not text.strip()) or text.startswith(("❌ Gemini error", "⚠️ Error"))

def hide_error(text):
    """True => ye Gemini error hai aur chat mein nahi bhejna. Log mein rakhta hai."""
    if is_gemini_error(text) and not SHOW_GEMINI_ERRORS:
        log.warning(f"Gemini failed (chat mein nahi bheja): {str(text)[:200]}")
        return True
    return False

# Bot-side wait limit. 90s se badha ke 300s (sirf backstop — asli control proxy mode ke 25s timeout se hai).
# None kar sakte ho, par sync call hai: Gemini atka to poora bot freeze ho jayega.
GEMINI_CALL_TIMEOUT = 300

def call_gemini(messages, model="gemini-3.6-flash", retries=2):
    """429/502 ya Gemini server restart ke waqt: 4s, 8s backoff ke saath retry."""
    if "pollinations" in model.lower():
        api_url = "https://text.pollinations.ai/openai"
        auth_token = "Bearer dummy"
        actual_model = "openai"
    elif "claude" in model.lower():
        api_url = CLAUDE_API
        auth_token = "Bearer sk-claude"
        actual_model = model
    else:
        api_url = GEMINI_API
        auth_token = "Bearer sk-gemini"
        actual_model = model
    last = ""
    for attempt in range(retries + 1):
        try:
            r = requests.post(api_url,
                headers={"Content-Type": "application/json", "Authorization": auth_token},
                json={"model": actual_model, "messages": messages}, timeout=GEMINI_CALL_TIMEOUT)
            d = r.json()
            if "choices" in d:
                content = d["choices"][0]["message"].get("content")
                if isinstance(content, str) and content.strip():
                    _STATE["empty"] = 0
                    return content
                _STATE["empty"] += 1
                last = "⚠️ Error: Gemini ne khaali reply diya (content None/empty)"
            else:
                last = f"⚠️ Error: {d}"
        except requests.exceptions.Timeout:
            return f"❌ Gemini error: timeout ({GEMINI_CALL_TIMEOUT}s)"
        except requests.exceptions.ConnectionError as e:
            last = f"❌ Gemini error: server restart ho raha hai ({e.__class__.__name__})"
            if attempt < retries:
                log.warning("Gemini server down/restarting — ready hone ka wait (40s tak)...")
                wait_gemini()
                continue
        except Exception as e:
            last = f"❌ Gemini error: {e}"
        if attempt < retries:
            wait = 4 * (2 ** attempt)
            log.warning(f"call_gemini failed ({last[:120]}) — retry {attempt+1}/{retries} in {wait}s")
            time.sleep(wait)
    return last

def execute_python_code(code, retries=2):
    """Executes python code via Judge0 CE (free public sandbox)"""
    url = "https://ce.judge0.com/submissions?base64_encoded=false&wait=true"
    payload = {"source_code": code, "language_id": 71}  # 71 = Python 3
    headers = {"Content-Type": "application/json"}

    for attempt in range(retries + 1):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            if r.status_code == 201:
                d = r.json()
                stdout = d.get("stdout")
                stderr = d.get("stderr")
                compile_output = d.get("compile_output")
                if stdout:
                    return stdout.strip()
                elif stderr:
                    return f"Stderr:\n{stderr.strip()}"
                elif compile_output:
                    return f"Compile Error:\n{compile_output.strip()}"
                else:
                    return "[Executed successfully with no output]"
            elif r.status_code == 429:
                time.sleep(2)
                continue
            else:
                return f"Execution Error: Status {r.status_code} - {r.text[:200]}"
        except requests.exceptions.Timeout:
            if attempt < retries:
                continue
            return "Execution timed out after retries."
        except Exception as e:
            return f"Failed to execute code: {e}"

    return "Execution failed after retries (rate limited)."

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
    gh_put_file(path, content, f"[skip render] Memory update {datetime.now().strftime('%Y-%m-%d %H:%M')}", sha)

def gh_create_repo(repo_name: str, private: bool = True) -> str:
    """Creates a new GitHub repo under the token owner's account (runs in bot process, not sandbox)"""
    if not GITHUB_TOKEN: return "❌ GITHUB_TOKEN env var set nahi hai Render pe"
    repo_name = repo_name.strip().split("/")[-1]  # strip any owner/ prefix, avoid path tricks
    if not repo_name or not re.match(r'^[A-Za-z0-9._-]+$', repo_name):
        return "❌ Invalid repo name"
    r = requests.post("https://api.github.com/user/repos",
                       headers=GH_HEADERS(),
                       json={"name": repo_name, "private": private},
                       timeout=15)
    if r.status_code == 201:
        return f"✅ Repo created: {r.json().get('html_url')}"
    if r.status_code == 422:
        return f"⚠️ Repo '{repo_name}' already exists ya naam invalid hai."
    return f"❌ Failed: {r.status_code} - {r.json().get('message', r.text[:150])}"

def gh_copy_repo(source_repo: str, new_name: str, private: bool = True) -> str:
    """
    Duplicates source_repo into a brand-new repo under the token owner's account.
    Standalone, single-purpose, manual-command-only (see cmd_repo_copy) — never
    reachable via a model-generated marker, since a bulk multi-file operation
    is exactly the kind of thing that shouldn't run without an explicit owner action.
    """
    if not GITHUB_TOKEN: return "❌ GITHUB_TOKEN env var set nahi hai Render pe"
    source_repo = source_repo.strip()
    new_name = new_name.strip().split("/")[-1]
    if not new_name or not re.match(r'^[A-Za-z0-9._-]+$', new_name):
        return "❌ Invalid new repo name"

    # 1. Get source repo's default branch
    r = requests.get(f"https://api.github.com/repos/{source_repo}", headers=GH_HEADERS(), timeout=15)
    if not r.ok:
        return f"❌ Source repo access failed: {r.status_code} - {r.json().get('message', '')}"
    default_branch = r.json().get("default_branch", "main")

    # 2. Get full file tree (recursive)
    r = requests.get(f"https://api.github.com/repos/{source_repo}/git/trees/{default_branch}?recursive=1",
                      headers=GH_HEADERS(), timeout=20)
    if not r.ok:
        return f"❌ Tree fetch failed: {r.status_code} - {r.json().get('message', '')}"
    tree = [t for t in r.json().get("tree", []) if t["type"] == "blob"]
    if not tree:
        return "❌ Source repo mein koi file nahi mili"

    # 3. Create the new repo
    create_result = gh_create_repo(new_name, private)
    if not create_result.startswith("✅"):
        return create_result  # already-exists / failure — surface as-is

    # 4. Copy each file (base64 content carries over directly, no decode/re-encode needed)
    copied, failed = 0, []
    for item in tree:
        path = item["path"]
        blob = requests.get(item["url"], headers=GH_HEADERS(), timeout=15)
        if not blob.ok:
            failed.append(path)
            continue
        content_b64 = blob.json().get("content", "")
        put = requests.put(
            f"https://api.github.com/repos/{GITHUB_OWNER()}/{new_name}/contents/{path}",
            headers=GH_HEADERS(),
            json={"message": f"Copy from {source_repo}", "content": content_b64},
            timeout=15
        )
        if put.status_code in (200, 201):
            copied += 1
        else:
            failed.append(path)

    msg = f"✅ Copied {copied}/{len(tree)} files to {new_name}"
    if failed:
        msg += f"\n⚠️ Failed: {', '.join(failed[:10])}" + (" ..." if len(failed) > 10 else "")
    return msg

def GITHUB_OWNER() -> str:
    """Resolves the token owner's username via GitHub API (cached at module load isn't safe across token changes, so fetched live but cheap)."""
    r = requests.get("https://api.github.com/user", headers=GH_HEADERS(), timeout=10)
    return r.json().get("login", "") if r.ok else ""

def gh_api_call(method: str, path: str, body: dict = None) -> str:
    """
    Generic GitHub REST API executor — any endpoint, any method the token allows.
    This IS 'full GitHub control': repos, files, branches, issues, PRs, webhooks,
    collaborators, everything the REST API exposes. Its real boundary is whatever
    the GITHUB_TOKEN's own scope permits (fine-grained PAT restricts this to
    whichever repos/permissions were granted when it was created).
    """
    if not GITHUB_TOKEN: return "❌ GITHUB_TOKEN env var set nahi hai Render pe"
    method = method.strip().upper()
    if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
        return f"❌ Invalid method: {method}"
    if not path.startswith("/"):
        path = "/" + path
    url = f"https://api.github.com{path}"
    try:
        r = requests.request(method, url, headers=GH_HEADERS(), json=body, timeout=20)
        log.info(f"[gh_api_call] {method} {url} -> {r.status_code}")
        out = r.text[:2000]
        return f"Status {r.status_code}:\n{out}"
    except Exception as e:
        return f"❌ Error: {e}"

def _skill_name_safe(name: str) -> str:
    name = name.strip().split("/")[-1]
    name = re.sub(r'[^A-Za-z0-9._-]', '', name)
    return name

def gh_save_skill(name: str, content: str) -> str:
    """Saves a code snippet to skills/<name>.py in MEMORY_REPO. Does NOT execute or load it anywhere."""
    if not GITHUB_TOKEN: return "❌ GITHUB_TOKEN env var set nahi hai Render pe"
    raw_name = name
    name = _skill_name_safe(name)
    if not name: return "❌ Invalid skill name"
    if not name.endswith((".py", ".txt", ".md", ".json")):
        name += ".py"
    path = f"skills/{name}"
    url = f"https://api.github.com/repos/{MEMORY_REPO}/contents/{path}"
    log.info(f"[gh_save_skill] raw_name={raw_name!r} sanitized_name={name!r} path={path!r} url={url!r} repo={MEMORY_REPO!r}")
    _, sha = gh_get_file(path)
    data = {"message": f"[skip render] Save skill: {name}", "content": base64.b64encode(content.encode()).decode()}
    if sha: data["sha"] = sha
    r = requests.put(url, headers=GH_HEADERS(), json=data, timeout=15)
    log.info(f"[gh_save_skill] status={r.status_code} response={r.text[:300]!r}")
    if r.status_code in (200, 201):
        return f"✅ Skill saved: [{name}](https://github.com/{MEMORY_REPO}/blob/main/{path})"
    return f"❌ Failed ({r.status_code}) path=`{path}`: {r.json().get('message', r.text[:150])}"

def gh_load_skill(name: str) -> str:
    """Fetches a saved skill's raw content back. Does NOT execute it."""
    name = _skill_name_safe(name)
    if not name: return "❌ Invalid skill name"
    candidates = [name] if "." in name else [name + ".py", name + ".txt", name + ".md", name]
    for cand in candidates:
        content, _ = gh_get_file(f"skills/{cand}")
        if content is not None:
            return f"📄 `{cand}`:\n```\n{content[:3500]}\n```"
    return f"❌ Skill '{name}' nahi mili. `/skills` se list dekho."

def gh_delete_skill(name: str) -> str:
    """Deletes a saved skill file. Standalone — no Gemini/execution dependency, safe to call anytime."""
    if not GITHUB_TOKEN: return "❌ GITHUB_TOKEN env var set nahi hai Render pe"
    name = _skill_name_safe(name)
    if not name: return "❌ Invalid skill name"
    candidates = [name] if "." in name else [name + ".py", name + ".txt", name + ".md", name]
    for cand in candidates:
        content, sha = gh_get_file(f"skills/{cand}")
        if content is not None:
            r = requests.delete(f"https://api.github.com/repos/{MEMORY_REPO}/contents/skills/{cand}",
                                 headers=GH_HEADERS(),
                                 json={"message": f"[skip render] Delete skill: {cand}", "sha": sha}, timeout=15)
            if r.status_code == 200:
                return f"🗑️ Deleted: `{cand}`"
            return f"❌ Failed: {r.status_code} - {r.text[:150]}"
    return f"❌ Skill '{name}' nahi mili."

def run_skill(name: str, timeout: int = 20) -> str:
    """
    Runs a saved skill as a real subprocess (full env/network access — needed for
    skills that hit GitHub etc). ONLY reachable via the manual /run_skill command —
    the model can never trigger this itself. This is the deliberate safety gate.
    """
    if not SKILLS_ENABLED["v"]:
        return "🔒 Skill execution abhi disabled hai (/skillson se enable karo)."
    name = _skill_name_safe(name)
    candidates = [name] if "." in name else [name + ".py", name + ".txt", name + ".md", name]
    code = None
    for cand in candidates:
        content, _ = gh_get_file(f"skills/{cand}")
        if content is not None:
            code = content
            break
    if code is None:
        return f"❌ Skill '{name}' nahi mili."

    tmp_path = os.path.join(tempfile.gettempdir(), f"skill_{name}.py")
    try:
        with open(tmp_path, "w") as f:
            f.write(code)
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=timeout,
            env=os.environ.copy()  # full env — skill may legitimately need GITHUB_TOKEN etc.
        )
        out = (result.stdout or "") + (result.stderr or "")
        return out.strip()[:3500] if out.strip() else "[Executed, no output]"
    except subprocess.TimeoutExpired:
        return f"⏱️ Timed out after {timeout}s"
    except Exception as e:
        return f"❌ Error: {e}"
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

def gh_list_skills() -> str:
    """Lists all saved skills in the skills/ folder"""
    if not GITHUB_TOKEN: return "❌ GITHUB_TOKEN env var set nahi hai Render pe"
    r = requests.get(f"https://api.github.com/repos/{MEMORY_REPO}/contents/skills",
                      headers=GH_HEADERS(), timeout=10)
    if r.status_code == 404:
        return "📂 Koi skill saved nahi hai abhi."
    if not r.ok:
        return f"❌ Error: {r.status_code}"
    files = [f["name"] for f in r.json() if f["type"] == "file"]
    if not files:
        return "📂 Koi skill saved nahi hai abhi."
    return "📂 Saved skills:\n" + "\n".join(f"• `{f}`" for f in files)

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
    """Gemini ka built-in web search use karo — call_gemini ke retry/backoff ke saath"""
    return call_gemini([
        {"role": "system", "content": "You have internet access via Gemini's web search. Search and give latest accurate info with sources."},
        {"role": "user", "content": f"Search the web for: {query}\n\nGive key facts and latest information."}
    ], model=model)

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
                caption=f"📁 `{filename}` (Code Auto-Extracted)",
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
            if hide_error(results):
                await msg.delete(); return
            mem = get_mem(uid)
            model = mem.get("model", "gemini-3.6-flash")
            summary = call_gemini([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Web search results for '{text}':\n{results}\n\nSummarize key points."}
            ], model=model)
            if hide_error(summary):
                await msg.delete(); return
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
        
                text = u.message.text or ""
        
        # Inject current time
        import datetime
        now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %I:%M %p (IST)")
        time_context = f"[System: Current time is {now_ist}]\n"
        final_text = time_context + text

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
            
        if len(h) > 30: del h[:-30]   # in-place trim (pehle naya list ban raha tha, h purani list pe rehta tha)

        # Agentic Loop for Python Execution
        max_turns = 3
        current_turn = 0
        final_reply = ""

        while current_turn < max_turns:
            
            # Prevent Claude from answering all history at once
            hist_copy = list(mem["history"])
            if hist_copy and hist_copy[-1]["role"] == "user":
                hist_copy[-1] = {"role": "user", "content": hist_copy[-1]["content"] + "\n\n[SYSTEM NOTE: This is the latest message. DO NOT reply to previous history, only reply to this specific prompt.]"}
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + hist_copy

            reply = call_gemini(msgs, model=model)
            if is_gemini_error(reply):
                hide_error(reply)
                # error history mein save nahi hoga; fail hua user msg bhi hata do (dobara bhejne pe duplicate na ho)
                if current_turn == 0 and h and h[-1].get("role") == "user":
                    h.pop()
                final_reply = reply if SHOW_GEMINI_ERRORS else ""
                break
            h.append({"role": "assistant", "content": reply})
            
            # Check if Gemini wants to execute code, create a repo, save/get/run a skill, or call GitHub API directly
            code_match = re.search(r'```python\s*# EXECUTE\s*(.*?)```', reply, re.DOTALL)
            repo_match = re.search(r'```\s*# GITHUB_CREATE_REPO\s*(.*?)```', reply, re.DOTALL)
            save_skill_match = re.search(r'```\w*\s*# SAVE_SKILL\s+(\S+)\s*\n(.*?)```', reply, re.DOTALL)
            get_skill_match = re.search(r'```\s*# GET_SKILL\s*(\S*)\s*```', reply, re.DOTALL)
            run_skill_match = re.search(r'```\s*# RUN_SKILL\s+(\S+)\s*```', reply, re.DOTALL)
            api_match = re.search(r'```(?:json)?\s*# GITHUB_API\s*(.*?)```', reply, re.DOTALL)
            term_match = re.search(r'```(?:bash|sh|text)?\s*# RUN_TERMINAL\s*(.*?)```', reply, re.DOTALL)
            url_match = re.search(r'```\w*\s*# FETCH_URL\s+(\S+)\s*```', reply, re.DOTALL)
            schedule_match = re.search(r'```(?:bash|sh|text)?\s*# SCHEDULE_MESSAGE\s+(\d+)\n(.*?)```', reply, re.DOTALL)

            if term_match:
                cmd = term_match.group(1).strip()
                status_msg = await u.message.reply_text(f"??? Running: {cmd}...", parse_mode=ParseMode.MARKDOWN)
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=30).decode('utf-8', errors='replace')
                except subprocess.CalledProcessError as e:
                    result = e.output.decode('utf-8', errors='replace')
                except Exception as e:
                    result = str(e)
                if not result.strip(): result = "(Success with no output)"
                await status_msg.edit_text(f"```text\n{result[:3500]}\n```", parse_mode=ParseMode.MARKDOWN)
                h.append({"role": "user", "content": f"Terminal Result:\n{result}\nAnalyze this and answer the user."})
                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif url_match:
                url = url_match.group(1).strip()
                status_msg = await u.message.reply_text(f"?? Fetching: {url}...", parse_mode=ParseMode.MARKDOWN)
                try:
                    r = requests.get(url, timeout=15)
                    result = r.text[:10000] # get first 10k chars
                except Exception as e:
                    result = str(e)
                await status_msg.edit_text(f"```text\n{len(result)}\n```", parse_mode=ParseMode.MARKDOWN)
                h.append({"role": "user", "content": f"Website Content:\n{result}\nAnalyze this and answer the user."})
                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif schedule_match:
                delay = int(schedule_match.group(1))
                msg_to_send = schedule_match.group(2).strip()
                
                async def send_scheduled(context: ContextTypes.DEFAULT_TYPE):
                    try:
                        await context.bot.send_message(chat_id=context.job.chat_id, text=context.job.data)
                    except Exception as e:
                        pass
                
                c.job_queue.run_once(send_scheduled, delay, chat_id=u.effective_chat.id, data=msg_to_send)
                await u.message.reply_text(f"? Done! I have scheduled your message to be sent in {delay} seconds.")
                return
            elif api_match:
                try:
                    call = json.loads(api_match.group(1).strip())
                    method, path, body = call.get("method", "GET"), call.get("path", ""), call.get("body")
                except Exception as e:
                    result = f"❌ Invalid GITHUB_API block: {e}"
                    method = path = None
                if path:
                    status_msg = await u.message.reply_text(f"🔧 GitHub API: `{method} {path}`...", parse_mode=ParseMode.MARKDOWN)
                    result = gh_api_call(method, path, body)
                    await status_msg.edit_text(f"```text\n{result[:3500]}\n```", parse_mode=ParseMode.MARKDOWN)
                h.append({"role": "user", "content": f"GitHub API Result:\n{result}\nAnalyze this and answer the user."})

                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif run_skill_match:
                skill_name = run_skill_match.group(1).strip()
                status_msg = await u.message.reply_text(f"▶️ Running skill: `{skill_name}`...", parse_mode=ParseMode.MARKDOWN)
                result = run_skill(skill_name)
                h.append({"role": "user", "content": f"Skill Run Result:\n{result}\nAnalyze this and answer the user."})
                await status_msg.edit_text(f"```text\n{result[:3500]}\n```", parse_mode=ParseMode.MARKDOWN)

                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif save_skill_match:
                skill_name, skill_code = save_skill_match.group(1).strip(), save_skill_match.group(2)
                status_msg = await u.message.reply_text(f"💾 Saving skill: `{skill_name}`...", parse_mode=ParseMode.MARKDOWN)
                result = gh_save_skill(skill_name, skill_code)
                h.append({"role": "user", "content": f"Skill Save Result:\n{result}\nAnalyze this and answer the user."})
                await status_msg.edit_text(result, parse_mode=ParseMode.MARKDOWN)

                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif get_skill_match:
                skill_name = get_skill_match.group(1).strip()
                result = gh_list_skills() if not skill_name else gh_load_skill(skill_name)
                h.append({"role": "user", "content": f"Skill Fetch Result:\n{result}\nAnalyze this and answer the user (share the content directly, don't execute it)."})
                await u.message.reply_text(result[:4000], parse_mode=ParseMode.MARKDOWN)

                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif repo_match:
                repo_name = repo_match.group(1).strip()
                status_msg = await u.message.reply_text(f"📁 Creating repo: `{repo_name}`...", parse_mode=ParseMode.MARKDOWN)
                result = gh_create_repo(repo_name)
                h.append({"role": "user", "content": f"Repo Creation Result:\n{result}\nAnalyze this and answer the user."})
                await status_msg.edit_text(result, parse_mode=ParseMode.MARKDOWN)

                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif code_match:
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
        if final_reply:
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
            if hide_error(results):
                await msg.delete(); return
            mem = get_mem(MY_USER_ID)
            summary = call_gemini([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Results for '{q}':\n{results}\n\nSummarize."}
            ], mem.get("model", "gemini-3.6-flash"))
            if hide_error(summary):
                await msg.delete(); return
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
        if hide_error(reply):
            await msg.delete(); return
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

    async def cmd_skills(u: Update, c):
        """/skills — list all, or /skills <name> to fetch one. Never executes anything."""
        if not auth(u): return
        args = u.message.text.split(maxsplit=1)
        if len(args) < 2:
            result = gh_list_skills()
        else:
            result = gh_load_skill(args[1].strip())
        await u.message.reply_text(result[:4000], parse_mode=ParseMode.MARKDOWN)

    async def cmd_run_skill(u: Update, c):
        """/run_skill <name> — the ONLY way to actually execute a saved skill.
        Deliberately a manual command, never model-triggered — breaks any
        auto save+run injection chain. Requires explicit owner keystroke."""
        if not auth(u): return
        args = u.message.text.split(maxsplit=1)
        if len(args) < 2:
            await u.message.reply_text("Usage: `/run_skill skill_name`", parse_mode=ParseMode.MARKDOWN)
            return
        status = await u.message.reply_text(f"▶️ Running skill: `{args[1].strip()}`...", parse_mode=ParseMode.MARKDOWN)
        result = run_skill(args[1].strip())
        await status.edit_text(f"```text\n{result[:3800]}\n```", parse_mode=ParseMode.MARKDOWN)

    async def cmd_killskill(u: Update, c):
        """/killskill <name> — EMERGENCY: deletes a skill file directly via GitHub API.
        No Gemini call, no proxy, no execution sandbox involved. Works even if
        everything else (Gemini backend, proxies) is completely broken."""
        if not auth(u): return
        args = u.message.text.split(maxsplit=1)
        if len(args) < 2:
            await u.message.reply_text("Usage: `/killskill skill_name`", parse_mode=ParseMode.MARKDOWN)
            return
        await u.message.reply_text(gh_delete_skill(args[1].strip()), parse_mode=ParseMode.MARKDOWN)

    async def cmd_repo_copy(u: Update, c):
        """/repo_copy source_owner/source_repo new_name — duplicates an entire repo.
        Deliberately manual-only: a bulk multi-file operation never runs from a
        model-generated marker, only from an explicit typed command."""
        if not auth(u): return
        args = u.message.text.split(maxsplit=2)
        if len(args) < 3:
            await u.message.reply_text("Usage: `/repo_copy owner/source-repo new-repo-name`", parse_mode=ParseMode.MARKDOWN)
            return
        status = await u.message.reply_text(f"📦 Copying `{args[1]}` → `{args[2]}`... (bade repo mein time lagega)", parse_mode=ParseMode.MARKDOWN)
        result = gh_copy_repo(args[1].strip(), args[2].strip())
        await status.edit_text(result, parse_mode=ParseMode.MARKDOWN)

    async def cmd_skillsoff(u: Update, c):
        """/skillsoff — EMERGENCY kill switch: instantly blocks all /run_skill calls.
        Pure in-memory flag flip, zero dependencies. Always works."""
        if not auth(u): return
        SKILLS_ENABLED["v"] = False
        await u.message.reply_text("🔒 Skill execution disabled. /skillson se wapas on karo.")

    async def cmd_skillson(u: Update, c):
        if not auth(u): return
        SKILLS_ENABLED["v"] = True
        await u.message.reply_text("🔓 Skill execution enabled.")

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
        import re
        code_match = re.search(r'```(?:[a-zA-Z]*)\n(.*?)```', last, re.DOTALL)
        content_to_save = code_match.group(1).strip() if code_match else last.strip()
        tmp.write(content_to_save); tmp.close()
        await u.message.reply_document(
            open(tmp.name, "rb"),
            filename=filename,
            caption=f"📁 `{filename}` (Code Auto-Extracted)",
            parse_mode=ParseMode.MARKDOWN
        )
        os.unlink(tmp.name)

    # Build app
    async def _clear_webhook(app_):
        try:
            await app_.bot.delete_webhook(drop_pending_updates=False)
            log.info("✅ Webhook cleared (if any was set) — polling can proceed safely")
        except Exception as e:
            log.warning(f"delete_webhook failed (non-fatal): {e}")

    app = Application.builder().token(BOT_TOKEN).post_init(_clear_webhook).build()
    app.add_handler(CommandHandler("start",    start, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("menu",     cmd_menu, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("search",   cmd_search, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("image",    cmd_image, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("github",   cmd_github, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("clear",    cmd_clear, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("think",    cmd_think, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("model",    cmd_model, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("memory",   cmd_memory, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("skills",   cmd_skills, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("run_skill", cmd_run_skill, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("killskill", cmd_killskill, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("repo_copy", cmd_repo_copy, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("skillsoff", cmd_skillsoff, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("skillson", cmd_skillson, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CommandHandler("savefile", cmd_savefile, filters=filters.UpdateType.MESSAGE))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND & filters.UpdateType.MESSAGE, handle_msg))

    log.info("✅ Sasta Coder Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    threading.Thread(target=run_health, daemon=True).start()
    threading.Thread(target=start_gemini, daemon=True).start()
    subprocess.Popen([sys.executable, "claude_web2api.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log.info("⏳ Waiting for Gemini server...")
    time.sleep(5)
    if not wait_gemini():
        log.error("❌ Gemini server failed to start!"); sys.exit(1)
    run_bot()

