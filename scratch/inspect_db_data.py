import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in c.fetchall()]
print('Tables in abisalud.db:', tables)

for t in tables:
    c.execute(f"PRAGMA table_info({t});")
    cols = [r[1] for r in c.fetchall()]
    for col in cols:
        if any(term in col.lower() for term in ['proc', 'contrat', 'folio', 'orden', 'fuente']):
            c.execute(f"SELECT COUNT(*) FROM {t} WHERE {col} IS NOT NULL AND {col} != ''")
            cnt = c.fetchone()[0]
            print(f"  {t}.{col}: {cnt} non-empty rows")
            if cnt > 0:
                c.execute(f"SELECT DISTINCT {col} FROM {t} WHERE {col} IS NOT NULL AND {col} != '' LIMIT 5")
                samples = [r[0] for r in c.fetchall()]
                print(f"    Samples: {samples}")

conn.close()
