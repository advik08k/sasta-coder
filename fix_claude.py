import sys
with open('C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo/claude_web2api.py', 'r', encoding='utf-8') as f:
    c = f.read()

old_config = '''def load_config():
    global CONFIG
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(path) as f:
        CONFIG = json.load(f)
    log(f"config loaded: port={CONFIG.get('port', 8082)}")'''

new_config = '''def load_config():
    global CONFIG
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(path):
        with open(path) as f:
            CONFIG = json.load(f)
    else:
        CONFIG = {}
    log(f"config loaded: port={CONFIG.get('port', 8082)}")'''

if old_config in c:
    c = c.replace(old_config, new_config)
    with open('C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo/claude_web2api.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Fixed load_config")
else:
    print("Could not find old_config")
