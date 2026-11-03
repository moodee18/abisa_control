import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

# Check row 939
row = c.execute("SELECT * FROM entradas_movimientos WHERE id = 939").fetchone()
print("Current row 939:", row)

# 1. Update row 939: set fecha_ajuste = '2026-10-07', entrada_ajuste = 100.0, fecha_apoyo = '2026-10-06', apoyo_institucional = 100.0
c.execute("""
    UPDATE entradas_movimientos
    SET fecha_ajuste = '2026-10-07',
        entrada_ajuste = 100.0,
        fecha_apoyo = '2026-10-06',
        apoyo_institucional = 100.0,
        observaciones = 'Ajuste de inventario día 07/10/2026 (separado de registro múltiple)'
    WHERE id = 939
""")

# 2. Check if the second row already exists to avoid duplicates
existing = c.execute("""
    SELECT id FROM entradas_movimientos
    WHERE clave = '060.231.0609' AND lote = 'PP0225002' AND fecha_ajuste = '2026-10-15' AND mes = 'OCTUBRE'
""").fetchall()

if not existing:
    # Insert second row: fecha_ajuste = '2026-10-15', entrada_ajuste = 56.0, fecha_apoyo = '2026-10-15', apoyo_institucional = 60.0
    cols = [col[1] for col in c.execute("PRAGMA table_info(entradas_movimientos)").fetchall() if col[1] != 'id']
    
    # We copy values from row 939 but customize the adjustment values
    c.execute("""
        INSERT INTO entradas_movimientos (
            folio_documento, procedimiento, contrato, registro_sanitario, almacen, proveedor,
            clave, lote, descripcion, unidad_medida, fecha_entrada, fecha_fabricacion,
            fecha_caducidad, inventario_inicial, entrada_ajuste, cantidad_recibida, mes, ano,
            observaciones, created_at, row_index, dias_salidas, apoyo_institucional,
            fecha_apoyo, fecha_ajuste
        ) VALUES (
            '', '', '', '', 'CS ALMACEN 2022', 'SECRETARIA DE SALUD GOBIERNO DE CHIAPAS 2024-2030',
            '060.231.0609', 'PP0225002',
            'ROPA QUIRÚRGICA. PAQUETE PARA PARTO. TELA NO TEJIDA DE POLIPROPILENO IMPERMEABLE A LA PENETRACIÓN DE LÍQUIDOS Y FLUIDOS COLOR ANTIRREFLEJANTE NO TRANSPARENTE ANTIESTÁTICA Y RESISTENTE A LA TENSIÓN EN USO NORMAL. ESTÉRIL Y DESECHABLE. CONTIENE: DOS BATAS QUIRÚRGICAS. PARA CIRUJANO PUÑOS AJUSTABLES REFUERZO EN MANGAS Y PECHO TAMAÑO GRANDE. CUATRO CAMPOS SENCILLOS DE 90 ±10 CM X 90 ±10 CM. DOS PIERNERAS DE 100 ±10 CM X 110 ±10 CM. UNA CUBIERTA PARA MESA DE RIÑÓN DE 240 ±10 CM X 150 ±10 CM. DOS TOAL',
            'ENVASE', '', '', '2028-02-28',
            0.0, 56.0, 0.0, 'OCTUBRE', 2026,
            'Ajuste de inventario día 15/10/2026 (separado de registro múltiple)',
            datetime('now'), 939, '{}', 60.0, '2026-10-15', '2026-10-15'
        )
    """)
    print("Inserted second row for 15/10/2026!")
else:
    print("Second row already exists with id:", existing)

conn.commit()

# Verify both rows in entradas_movimientos
rows = c.execute("SELECT id, clave, lote, fecha_ajuste, entrada_ajuste, apoyo_institucional, fecha_apoyo FROM entradas_movimientos WHERE clave = '060.231.0609' AND lote = 'PP0225002' AND mes = 'OCTUBRE'").fetchall()
print("Updated OCTUBRE rows for PP0225002:")
for r in rows:
    print(r)

