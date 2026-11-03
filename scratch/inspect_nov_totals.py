import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

c.execute("SELECT COUNT(*), SUM(inventario_inicial), SUM(entrada_ajuste), SUM(cantidad_recibida) FROM entradas_movimientos WHERE mes='NOVIEMBRE'")
print("Noviembre entradas sums:", c.fetchone())

c.execute("SELECT COUNT(*) FROM salidas_pdf_movimientos WHERE mes='NOVIEMBRE'")
print("Noviembre salidas count:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM apoyo_institucional_movimientos WHERE mes='NOVIEMBRE'")
print("Noviembre apoyos count:", c.fetchone()[0])

