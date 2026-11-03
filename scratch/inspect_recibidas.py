import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

c.execute("""
    SELECT id, mes, ano, clave, lote, cantidad_recibida, fecha_entrada, fecha_fabricacion 
    FROM entradas_movimientos 
    WHERE cantidad_recibida > 0
    LIMIT 20
""")
print("Sample rows with cantidad_recibida > 0:")
for r in c.fetchall():
    print(r)

c.execute("""
    SELECT COUNT(*) 
    FROM entradas_movimientos 
    WHERE cantidad_recibida > 0 AND (fecha_entrada IS NULL OR fecha_entrada = '')
""")
print("\nRows with cantidad_recibida > 0 but empty fecha_entrada:", c.fetchone()[0])

