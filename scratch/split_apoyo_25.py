import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

# Check row 25
r25 = c.execute("SELECT * FROM apoyo_institucional_movimientos WHERE id = 25").fetchone()
print("Current row 25:", r25)

c.execute("""
    UPDATE apoyo_institucional_movimientos
    SET fecha = '2026-10-06',
        cantidad = 100.0,
        dia = 6,
        observaciones = 'Apoyo institucional día 06/10/2026 (separado de registro múltiple)'
    WHERE id = 25
""")

existing_apo = c.execute("""
    SELECT id FROM apoyo_institucional_movimientos
    WHERE clave = '060.231.0609' AND lote = 'PP0225002' AND fecha = '2026-10-15'
""").fetchall()

if not existing_apo:
    c.execute("""
        INSERT INTO apoyo_institucional_movimientos (
            clave, lote, descripcion, cantidad, institucion, fecha, dia, mes, ano, folio_documento, observaciones, created_at
        ) VALUES (
            '060.231.0609', 'PP0225002',
            'ROPA QUIRÚRGICA. PAQUETE PARA PARTO. TELA NO TEJIDA DE POLIPROPILENO IMPERMEABLE A LA PENETRACIÓN DE LÍQUIDOS Y FLUIDOS COLOR ANTIRREFLEJANTE NO TRANSPARENTE ANTIESTÁTICA Y RESISTENTE A LA TENSIÓN EN USO NORMAL. ESTÉRIL Y DESECHABLE. CONTIENE: DOS BATAS QUIRÚRGICAS. PARA CIRUJANO PUÑOS AJUSTABLES REFUERZO EN MANGAS Y PECHO TAMAÑO GRANDE. CUATRO CAMPOS SENCILLOS DE 90 ±10 CM X 90 ±10 CM. DOS PIERNERAS DE 100 ±10 CM X 110 ±10 CM. UNA CUBIERTA PARA MESA DE RIÑÓN DE 240 ±10 CM X 150 ±10 CM. DOS TOAL',
            60.0, 'SECRETARIA DE SALUD / OTRA INSTITUCION', '2026-10-15', 15, 'OCTUBRE', 2026, '',
            'Apoyo institucional día 15/10/2026 (separado de registro múltiple)', datetime('now')
        )
    """)
    print("Inserted second apoyo row for 15/10/2026!")

conn.commit()

rows = c.execute("SELECT id, clave, lote, fecha, cantidad, dia FROM apoyo_institucional_movimientos WHERE clave = '060.231.0609' AND lote = 'PP0225002'").fetchall()
print("Updated apoyo rows:")
for r in rows:
    print(r)

