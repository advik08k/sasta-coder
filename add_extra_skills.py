import os

repo_dir = 'C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo'
skills_dir = os.path.join(repo_dir, 'skills')

# 1. Database Query Skill
db_code = '''import sqlite3, sys, json
db_path = sys.argv[1]
query = sys.argv[2]
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(query)
    if query.strip().upper().startswith("SELECT"):
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        result = [dict(zip(cols, row)) for row in rows]
        print(json.dumps(result, indent=2))
    else:
        conn.commit()
        print(f"Executed successfully. Rows affected: {cur.rowcount}")
    conn.close()
except Exception as e:
    print(f"DB Error: {e}")
'''
with open(os.path.join(skills_dir, 'db.py'), 'w', encoding='utf-8') as f: f.write(db_code)

# Update SYSTEM_PROMPT in render_main.py
with open(os.path.join(repo_dir, 'render_main.py'), 'r', encoding='utf-8') as f:
    c = f.read()

dev_skills_extra = '''
- python skills/db.py <db_file.sqlite> "<sql_query>" (Execute SQL queries on a local SQLite database)
- Git Automation: Run git commands directly via # RUN_TERMINAL (e.g. git status, git add ., git commit -m "msg")
'''

c = c.replace("- cat skills/agent_guide.md (Read agent building best practices)", "- cat skills/agent_guide.md (Read agent building best practices)\n" + dev_skills_extra)

with open(os.path.join(repo_dir, 'render_main.py'), 'w', encoding='utf-8') as f:
    f.write(c)
print("Extra Dev Skills added!")
