import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT id, clave, lote, fecha_ajuste, entrada_ajuste, inventario_inicial, cantidad_recibida, fecha_entrada, observaciones FROM entradas_movimientos WHERE fecha_ajuste IS NOT NULL AND fecha_ajuste != ''")
rows = c.fetchall()
print(f"Total rows with fecha_ajuste: {len(rows)}")
for r in rows:
    print(r)
conn.close()

