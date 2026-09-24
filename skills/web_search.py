import sys, requests, urllib.parse, re

query = " ".join(sys.argv[1:])
url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
r = requests.get(url, headers=headers)
results = re.findall(r'<a class="result__url" href="([^"]+)">(.*?)</a>', r.text)

print(f"Search Results for '{query}':")
for link, snippet in results[:5]:
    print(f"- {link}")
