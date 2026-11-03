import sys, os
sys.path.insert(0, os.path.abspath("."))
import openpyxl
from database import DatabaseManager

db = DatabaseManager()
stream = db.export_reporte_movimientos_excel(mes="OCTUBRE", ano=2026)

wb = openpyxl.load_workbook(stream, data_only=True)
ws2 = wb["Entradas"]

print("Total rows in Entradas:", ws2.max_row)
print("\nFirst 10 rows in Entradas:")
for r in range(1, min(15, ws2.max_row + 1)):
    row_vals = [ws2.cell(r, c).value for c in range(1, 17)]
    print(f"Row {r:2d} | Clave: {str(row_vals[6]):12s} | Lote: {str(row_vals[7]):10s} | F_Aju: {str(row_vals[9]):12s} | C_Aju: {str(row_vals[10]):5s} | F_Ent: {str(row_vals[11]):12s} | C_Rec: {str(row_vals[12]):5s} | Tot: {str(row_vals[14]):5s}")

print("\nSearching for PP0225002 in Entradas:")
for r in range(2, ws2.max_row + 1):
    lote = str(ws2.cell(r, 8).value)
    if "PP0225002" in lote:
        row_vals = [ws2.cell(r, c).value for c in range(1, 17)]
        print(f"Row {r:2d} | Clave: {str(row_vals[6]):12s} | Lote: {str(row_vals[7]):10s} | F_Aju: {str(row_vals[9]):12s} | C_Aju: {str(row_vals[10]):5s} | F_Ent: {str(row_vals[11]):12s} | C_Rec: {str(row_vals[12]):5s} | Tot: {str(row_vals[14]):5s}")
