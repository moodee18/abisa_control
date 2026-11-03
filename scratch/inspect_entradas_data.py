import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

c.execute("SELECT mes, COUNT(*), SUM(inventario_inicial), SUM(entrada_ajuste), SUM(cantidad_recibida) FROM entradas_movimientos GROUP BY mes")
print("Entradas by mes:")
for r in c.fetchall():
    print(r)

c.execute("SELECT COUNT(*), COUNT(fecha_ajuste), COUNT(fecha_entrada) FROM entradas_movimientos")
print("Total rows, with fecha_ajuste, with fecha_entrada:", c.fetchone())

# Check rows where inventario_inicial > 0 but entrada_ajuste == 0 and cantidad_recibida == 0
c.execute("""
    SELECT COUNT(*) FROM entradas_movimientos 
    WHERE (entrada_ajuste IS NULL OR entrada_ajuste = 0)
      AND (cantidad_recibida IS NULL OR cantidad_recibida = 0)
      AND (inventario_inicial > 0)
""")
print("Rows with only inventario_inicial > 0:", c.fetchone()[0])

# Check sample rows of these
c.execute("""
    SELECT id, mes, ano, clave, lote, inventario_inicial, entrada_ajuste, fecha_ajuste, cantidad_recibida, fecha_entrada, fecha_fabricacion, fecha_caducidad
    FROM entradas_movimientos 
    WHERE (entrada_ajuste IS NULL OR entrada_ajuste = 0)
      AND (cantidad_recibida IS NULL OR cantidad_recibida = 0)
      AND (inventario_inicial > 0)
    LIMIT 10
""")
print("\nSample rows with only inventario_inicial:")
for r in c.fetchall():
    print(r)

