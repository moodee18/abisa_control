import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]

for t in tables:
    c.execute(f"PRAGMA table_info({t})")
    cols = [col[1] for col in c.fetchall()]
    for col in cols:
        try:
            c.execute(f"SELECT count(*) FROM {t} WHERE {col} LIKE '%12-26%'")
            r = c.fetchone()
            if r and r[0] > 0:
                print(f"Found in table {t}, col {col}: {r[0]} rows")
                c.execute(f"SELECT * FROM {t} WHERE {col} LIKE '%12-26%' LIMIT 3")
                for row in c.fetchall():
                    print("  Row:", row[:6])
        except Exception as e:
            pass
conn.close()
