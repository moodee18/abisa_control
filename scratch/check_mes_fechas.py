import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT mes, COUNT(*), COUNT(NULLIF(fecha_ajuste, '')) FROM entradas_movimientos GROUP BY mes")
print("Counts by month:", c.fetchall())

c.execute("SELECT mes, ano, clave, lote, fecha_ajuste, entrada_ajuste FROM entradas_movimientos WHERE entrada_ajuste > 0 LIMIT 10")
for r in c.fetchall():
    print(r)

