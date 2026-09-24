with open("render_main.py", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Models dictionary
c = c.replace('"dY\'" Flash Lite (Fast)":    "gemini-flash-lite",\n}', '"dY\'" Flash Lite (Fast)":    "gemini-flash-lite",\n    "?? Pollinations AI (Free)": "pollinations-openai",\n}')

# 2. call_gemini
old_code = """    api_url = CLAUDE_API if "claude" in model.lower() else GEMINI_API
    auth_token = "Bearer sk-claude" if "claude" in model.lower() else "Bearer sk-gemini"
"""
new_code = """    if "pollinations" in model.lower():
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
"""
c = c.replace(old_code, new_code)
c = c.replace('json={"model": model, "messages": messages}', 'json={"model": actual_model, "messages": messages}')

with open("render_main.py", "w", encoding="utf-8") as f:
    f.write(c)
