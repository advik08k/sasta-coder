import requests, sys
city = sys.argv[1] if len(sys.argv) > 1 else "Delhi"
r = requests.get(f"https://wttr.in/{city}?format=3")
print(r.text.strip())
