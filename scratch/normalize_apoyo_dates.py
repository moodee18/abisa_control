import sqlite3, re

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

rows = c.execute("SELECT id, fecha, dia FROM apoyo_institucional_movimientos").fetchall()
updated = 0
for r_id, f, dia in rows:
    f_str = str(f or '').strip()
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', f_str)
    if m:
        new_f = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        new_dia = int(m.group(1))
        c.execute("UPDATE apoyo_institucional_movimientos SET fecha = ?, dia = ? WHERE id = ?", (new_f, new_dia, r_id))
        updated += 1

conn.commit()
print(f"Normalized {updated} dates in apoyo_institucional_movimientos to YYYY-MM-DD!")

dates = set(r[0] for r in c.execute('SELECT fecha FROM apoyo_institucional_movimientos').fetchall())
print('Normalized distinct fecha values:')
for d in sorted(list(dates)):
    print(' ', d)

