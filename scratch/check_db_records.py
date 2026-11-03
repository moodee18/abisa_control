import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
tables = [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('Tables in abisalud.db:', tables)

for t in tables:
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({t})").fetchall()]
    conds = []
    if 'lote' in cols:
        conds.append("lote LIKE '%PP0225002%'")
    if 'clave' in cols:
        conds.append("clave LIKE '%060.231.0609%'")
    if conds:
        q = f"SELECT * FROM {t} WHERE " + " OR ".join(conds)
        rows = c.execute(q).fetchall()
        if rows:
            print(f"=== Matches in {t} ({len(rows)}) ===")
            for r in rows:
                print(r)
