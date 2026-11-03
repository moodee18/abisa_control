import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

fechas_apo = set(r[0] for r in c.execute("SELECT fecha FROM apoyo_institucional_movimientos WHERE fecha IS NOT NULL AND fecha != ''").fetchall())
print('Distinct fecha in apoyo_institucional_movimientos:', sorted(list(fechas_apo)))

