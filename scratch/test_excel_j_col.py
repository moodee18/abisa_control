import sys
sys.path.insert(0, '.')
import openpyxl
from database import DatabaseManager

db = DatabaseManager('sqlite:///data/abisalud.db')
out_path = 'scratch/test_export_oct.xlsx'
stream = db.export_reporte_movimientos_excel(mes='OCTUBRE', ano=2026)
with open(out_path, 'wb') as f:
    f.write(stream.getvalue())

wb = openpyxl.load_workbook(out_path)
ws = wb['Reporte Diario']
print("Sheet title:", ws.title)
print("Header J2:", ws.cell(2, 10).value)
print("Header K2:", ws.cell(2, 11).value)

filled_j = []
for row in range(4, ws.max_row):
    val_k = ws.cell(row, 11).value
    val_j = ws.cell(row, 10).value
    clave = ws.cell(row, 7).value
    lote = ws.cell(row, 8).value
    if val_k is not None:
        filled_j.append((row, clave, lote, val_j, val_k))

print(f"Total rows with entrada_ajuste: {len(filled_j)}")
print("Sample rows:")
for r in filled_j[:8]:
    print(f"Row {r[0]}: Clave={r[1]}, Lote={r[2]}, FechaAjuste={r[3]}, Ajuste={r[4]}")
