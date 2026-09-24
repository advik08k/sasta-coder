import re
with open("render_main.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('"dY\'" Flash Lite (Fast)":    "gemini-flash-lite",\n}', '"dY\'" Flash Lite (Fast)":    "gemini-flash-lite",\n    "?? Pollinations (Free)": "pollinations-openai",\n}')

new_logic = '''    if "pollinations" in model.lower():
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
        actual_model = model'''

c = re.sub(r'api_url = CLAUDE_API if "claude" in model\.lower\(\) else GEMINI_API\n\s*auth_token = "Bearer sk-claude" if "claude" in model\.lower\(\) else "Bearer sk-gemini"', new_logic, c)

c = c.replace('json={"model": model, "messages": messages}', 'json={"model": actual_model, "messages": messages}')

with open("render_main.py", "w", encoding="utf-8") as f:
    f.write(c)
