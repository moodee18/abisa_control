import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]

for t in tables:
    c.execute(f"PRAGMA table_info({t})")
    cols = [col[1] for col in c.fetchall()]
    for col in cols:
        try:
            c.execute(f"SELECT id, {col} FROM {t} WHERE {col} LIKE '%15/10/2026%' OR {col} LIKE '%07/10/2026%'")
            res = c.fetchall()
            if res:
                print(f"Table {t}, Col {col}: {len(res)} matches")
                for r in res[:5]:
                    print("  ", r)
        except Exception:
            pass
conn.close()

