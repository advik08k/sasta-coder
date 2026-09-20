import os, requests
TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("MEMORY_REPO", "advik08k/sasta-coder")
H = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
r = requests.get(f"https://api.github.com/repos/{REPO}/commits", headers=H, params={"per_page": 20}, timeout=15)
target = None
for c in r.json():
    msg = c.get("commit", {}).get("message", "")
    if msg.startswith("Save skill: "):
        target = msg.replace("Save skill: ", "").strip()
        break
if not target:
    print("Koi recent skill-save commit nahi mila.")
else:
    r2 = requests.get(f"https://api.github.com/repos/{REPO}/contents/skills/{target}", headers=H, timeout=15)
    if r2.status_code == 200:
        sha = r2.json()["sha"]
        r3 = requests.delete(f"https://api.github.com/repos/{REPO}/contents/skills/{target}",
                              headers=H, json={"message": f"kill_last: remove {target}", "sha": sha}, timeout=15)
        print(f"Deleted: {target}" if r3.status_code == 200 else f"Failed: {r3.status_code}")
    else:
        print(f"Nahi mili: skills/{target}")
