import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

fechas_e = set(r[0] for r in c.execute("SELECT fecha_entrada FROM entradas_movimientos WHERE fecha_entrada IS NOT NULL AND fecha_entrada != ''").fetchall())
fechas_a = set(r[0] for r in c.execute("SELECT fecha_ajuste FROM entradas_movimientos WHERE fecha_ajuste IS NOT NULL AND fecha_ajuste != ''").fetchall())

print('Distinct fecha_entrada samples:', sorted(list(fechas_e)))
print('Distinct fecha_ajuste samples:', sorted(list(fechas_a)))

