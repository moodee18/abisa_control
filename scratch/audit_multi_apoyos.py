import sqlite3
import glob, openpyxl, os, re

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

# Find all rows in apoyo_institucional_movimientos that have spaces in fecha and contain slashes
multi_rows = []
for row in c.execute("SELECT id, clave, lote, descripcion, cantidad, fecha, institucion FROM apoyo_institucional_movimientos").fetchall():
    f = str(row[5] or '').strip()
    dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', f)
    if len(dates) > 1:
        multi_rows.append({
            'id': row[0],
            'clave': row[1],
            'lote': row[2],
            'descripcion': row[3],
            'total_cantidad': row[4],
            'fecha_str': row[5],
            'dates': dates,
            'institucion': row[6]
        })

print(f"Found {len(multi_rows)} rows with multiple dates in apoyo_institucional_movimientos:")
for mr in multi_rows:
    print(f"ID {mr['id']} | Clave: {mr['clave']} | Lote: {mr['lote']} | Cantidad: {mr['total_cantidad']} | Fechas: {mr['fecha_str']}")

