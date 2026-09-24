import os

repo_dir = 'C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo'
skills_dir = os.path.join(repo_dir, 'skills')
os.makedirs(skills_dir, exist_ok=True)

# Skill 1: Web Search (using DuckDuckGo HTML)
web_search_code = '''import sys, requests, urllib.parse, re

query = " ".join(sys.argv[1:])
url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
r = requests.get(url, headers=headers)
results = re.findall(r'<a class="result__url" href="([^"]+)">(.*?)</a>', r.text)

print(f"Search Results for '{query}':")
for link, snippet in results[:5]:
    print(f"- {link}")
'''
with open(os.path.join(skills_dir, 'web_search.py'), 'w', encoding='utf-8') as f: f.write(web_search_code)

# Skill 2: Crypto Tracker
crypto_code = '''import requests, sys
symbol = sys.argv[1].upper() if len(sys.argv) > 1 else "BTCUSDT"
if not symbol.endswith("USDT"): symbol += "USDT"
try:
    r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
    print(f"Price of {symbol}: ")
except:
    print("Could not fetch price. Make sure symbol is correct (e.g. BTC, ETH)")
'''
with open(os.path.join(skills_dir, 'crypto.py'), 'w', encoding='utf-8') as f: f.write(crypto_code)

# Skill 3: Weather
weather_code = '''import requests, sys
city = sys.argv[1] if len(sys.argv) > 1 else "Delhi"
r = requests.get(f"https://wttr.in/{city}?format=3")
print(r.text.strip())
'''
with open(os.path.join(skills_dir, 'weather.py'), 'w', encoding='utf-8') as f: f.write(weather_code)

# Now let's update SYSTEM_PROMPT to tell Claude about these skills!
with open(os.path.join(repo_dir, 'render_main.py'), 'r', encoding='utf-8') as f:
    c = f.read()

new_sp_part = '''
10. PRE-BUILT SKILLS (Run these using # RUN_TERMINAL):
You have some pre-built tools on the server in the skills/ folder. Run them using # RUN_TERMINAL:
- python skills/web_search.py "your query here" (Searches the web and returns links)
- python skills/crypto.py BTC (Gets live cryptocurrency price)
- python skills/weather.py London (Gets weather for a city)

11. AGENTIC SUPERPOWERS:
- You are autonomous! If a user asks for complex data, don't just say "I can't". 
- First run python skills/web_search.py <query> to find a URL.
- Then run # FETCH_URL <url> to read it.
- Then output the final answer!
'''

if "PRE-BUILT SKILLS" not in c:
    c = c.replace("9. GENERAL INSTRUCTIONS:", new_sp_part + "\n9. GENERAL INSTRUCTIONS:")
    with open(os.path.join(repo_dir, 'render_main.py'), 'w', encoding='utf-8') as f:
        f.write(c)
    print("Skills created and prompt updated!")
else:
    print("Already updated.")

