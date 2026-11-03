import sys, os
sys.path.insert(0, os.path.abspath("."))
import openpyxl
from database import DatabaseManager

db = DatabaseManager()
stream = db.export_reporte_movimientos_excel(mes="OCTUBRE", ano=2026)

wb = openpyxl.load_workbook(stream, data_only=True)
ws4 = wb["Apoyo Institucional"]

print(f"Total rows in Apoyo Institucional: {ws4.max_row}")

print("\nAll rows in Apoyo Institucional:")
for r in range(1, ws4.max_row + 1):
    vals = [ws4.cell(r, c).value for c in range(1, 10)]
    print(f"Row {r:2d} | Folio: {str(vals[0]):20s} | Fecha: {str(vals[1]):12s} | Dia: {str(vals[2]):3s} | Clave: {str(vals[4]):14s} | Lote: {str(vals[5]):12s} | Cant: {str(vals[7]):6s}")

