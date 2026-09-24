import sqlite3, sys, json
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
