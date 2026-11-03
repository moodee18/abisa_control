import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

c.execute("""
    SELECT 
        mes,
        CASE WHEN fecha_entrada IS NOT NULL AND fecha_entrada != '' THEN 1 ELSE 0 END as has_fe,
        CASE WHEN fecha_ajuste IS NOT NULL AND fecha_ajuste != '' THEN 1 ELSE 0 END as has_fa,
        CASE WHEN inventario_inicial > 0 THEN 1 ELSE 0 END as has_ini,
        CASE WHEN entrada_ajuste > 0 THEN 1 ELSE 0 END as has_aju,
        CASE WHEN cantidad_recibida > 0 THEN 1 ELSE 0 END as has_rec,
        COUNT(*)
    FROM entradas_movimientos
    GROUP BY mes, has_fe, has_fa, has_ini, has_aju, has_rec
""")
print("mes | has_fe | has_fa | has_ini | has_aju | has_rec | COUNT")
for r in c.fetchall():
    print(f"{r[0]:<9} | {r[1]:^6} | {r[2]:^6} | {r[3]:^7} | {r[4]:^7} | {r[5]:^7} | {r[6]}")

