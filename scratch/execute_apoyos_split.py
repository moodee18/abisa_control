import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

# Detailed split specification based on the official vales and adjustments:
splits = {
    3: [ # 060.040.0543, Lote 240401, Total 155
        {"fecha": "2026-10-08", "dia": 8, "cantidad": 10.0, "folio": "AJ_15391", "obs": "Apoyo institucional 08/10/2026 (Ajuste AJ_15391)"},
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 145.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"}
    ],
    7: [ # 060.066.0062, Lote 3A045050, Total 14
        {"fecha": "2026-10-08", "dia": 8, "cantidad": 2.0, "folio": "AJ_15391", "obs": "Apoyo institucional 08/10/2026 (Ajuste AJ_15391)"},
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 10.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"},
        {"fecha": "2026-10-16", "dia": 16, "cantidad": 2.0, "folio": "ALM/EXT/000065/2026", "obs": "Apoyo institucional 16/10/2026 (Vale 65)"}
    ],
    11: [ # 060.066.0666, Lote 3A511049, Total 11
        {"fecha": "2026-10-08", "dia": 8, "cantidad": 1.0, "folio": "AJ_15391", "obs": "Apoyo institucional 08/10/2026 (Ajuste AJ_15391)"},
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 10.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"}
    ],
    16: [ # 060.231.0104, Lote 15-22, Total 1100
        {"fecha": "2026-10-05", "dia": 5, "cantidad": 500.0, "folio": "", "obs": "Apoyo institucional 05/10/2026"},
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 300.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"},
        {"fecha": "2026-10-16", "dia": 16, "cantidad": 300.0, "folio": "ALM/EXT/000066/2026", "obs": "Apoyo institucional 16/10/2026 (Vale 66)"}
    ],
    21: [ # 060.231.0591, Lote 279NEX3325, Total 14
        {"fecha": "2026-10-06", "dia": 6, "cantidad": 13.0, "folio": "", "obs": "Apoyo institucional 06/10/2026"},
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 1.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"}
    ],
    29: [ # 060.436.0552, Lote 11-24, Total 258
        {"fecha": "2026-10-08", "dia": 8, "cantidad": 10.0, "folio": "AJ_15391", "obs": "Apoyo institucional 08/10/2026 (Ajuste AJ_15391)"},
        {"fecha": "2026-10-12", "dia": 12, "cantidad": 48.0, "folio": "AJ_15390", "obs": "Apoyo institucional 12/10/2026 (Ajuste AJ_15390)"},
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 200.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"}
    ],
    40: [ # 060.550.0453, Lote 221055, Total 110
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 100.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"},
        {"fecha": "2026-10-16", "dia": 16, "cantidad": 10.0, "folio": "ALM/EXT/000065/2026", "obs": "Apoyo institucional 16/10/2026 (Vale 65)"}
    ],
    45: [ # 060.841.0486, Lote 04238407, Total 23
        {"fecha": "2026-10-08", "dia": 8, "cantidad": 3.0, "folio": "AJ_15391", "obs": "Apoyo institucional 08/10/2026 (Ajuste AJ_15391)"},
        {"fecha": "2026-10-15", "dia": 15, "cantidad": 20.0, "folio": "ALM/EXT/000064/2026", "obs": "Apoyo institucional 15/10/2026 (Vale 64)"}
    ]
}

conn.row_factory = sqlite3.Row
c = conn.cursor()

for orig_id, parts in splits.items():
    orig_row = dict(c.execute("SELECT * FROM apoyo_institucional_movimientos WHERE id = ?", (orig_id,)).fetchone())
    print(f"\nProcessing ID {orig_id} ({orig_row['clave']} | {orig_row['lote']}):")
    
    # Update the original row with the first part
    first_part = parts[0]
    c.execute("""
        UPDATE apoyo_institucional_movimientos
        SET fecha = ?, dia = ?, cantidad = ?, folio_documento = ?, observaciones = ?
        WHERE id = ?
    """, (first_part['fecha'], first_part['dia'], first_part['cantidad'], first_part['folio'], first_part['obs'], orig_id))
    print(f"  Updated row {orig_id}: {first_part['fecha']} -> {first_part['cantidad']} pzas")
    
    # Insert remaining parts
    for extra_part in parts[1:]:
        c.execute("""
            INSERT INTO apoyo_institucional_movimientos (
                clave, lote, descripcion, cantidad, institucion, fecha, dia, mes, ano, folio_documento, observaciones, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            orig_row['clave'],
            orig_row['lote'],
            orig_row['descripcion'],
            extra_part['cantidad'],
            orig_row['institucion'],
            extra_part['fecha'],
            extra_part['dia'],
            orig_row['mes'],
            orig_row['ano'],
            extra_part['folio'],
            extra_part['obs']
        ))
        print(f"  Inserted extra row: {extra_part['fecha']} -> {extra_part['cantidad']} pzas")

conn.commit()
print("\nAll 8 multi-date apoyos successfully split in database!")

