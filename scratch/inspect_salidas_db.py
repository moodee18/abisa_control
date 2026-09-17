import sqlite3

conn = sqlite3.connect(r"C:\Users\moode\.gemini\antigravity-ide\scratch\abisalud_automation\data\abisalud.db")
cursor = conn.cursor()

print("--- Distinct tipo_movimiento in salidas ---")
for row in cursor.execute("SELECT tipo_movimiento, count(*) FROM movimientos_entradas_salidas WHERE tipo = 'SALIDA' GROUP BY tipo_movimiento"):
    print(row)

print("\n--- Distinct cliente in salidas ---")
for row in cursor.execute("SELECT cliente, count(*) FROM movimientos_entradas_salidas WHERE tipo = 'SALIDA' GROUP BY cliente LIMIT 20"):
    print(row)

print("\n--- Distinct dia in salidas ---")
for row in cursor.execute("SELECT dia, count(*), sum(cantidad) FROM movimientos_entradas_salidas WHERE tipo = 'SALIDA' GROUP BY dia ORDER BY dia"):
    print(row)

print("\n--- Sample salidas where dia = 15 ---")
for row in cursor.execute("SELECT clave, clave_cliente, lote, dia, cantidad, tipo_movimiento, cliente, documento FROM movimientos_entradas_salidas WHERE tipo = 'SALIDA' AND dia = 15 LIMIT 5"):
    print(row)

print("\n--- Sample salidas where tipo_movimiento is AJUSTE ---")
for row in cursor.execute("SELECT clave, clave_cliente, lote, dia, cantidad, tipo_movimiento, cliente, documento FROM movimientos_entradas_salidas WHERE tipo = 'SALIDA' AND (tipo_movimiento LIKE '%AJUSTE%' OR cliente LIKE '%AJUSTE%') LIMIT 5"):
    print(row)

conn.close()
