import sys, os
sys.path.insert(0, os.path.abspath("."))
import io
import openpyxl
from fastapi.testclient import TestClient
from app import app
from database import DatabaseManager

db = DatabaseManager()

print("=== 1. TEST DIRECT DATABASE EXPORT ===")
oct_bytes = db.export_reporte_movimientos_excel(mes="OCTUBRE", ano=2026)
wb_oct = openpyxl.load_workbook(oct_bytes, data_only=True)
print("Sheets in OCT export:", wb_oct.sheetnames)

ws1_oct = wb_oct["Reporte Diario"]
ws2_oct = wb_oct["Entradas"]
ws3_oct = wb_oct["Salidas PDF"]
ws4_oct = wb_oct["Apoyo Institucional"]

print(f"OCT Hoja 1: Title={ws1_oct['O1'].value}, Rows={ws1_oct.max_row}")
print(f"OCT Hoja 2: Rows={ws2_oct.max_row} (Data rows: {ws2_oct.max_row - 1})")
print(f"OCT Hoja 3: Rows={ws3_oct.max_row} (Data rows: {ws3_oct.max_row - 1})")
print(f"OCT Hoja 4: Rows={ws4_oct.max_row} (Data rows: {ws4_oct.max_row - 1})")

assert ws2_oct.max_row >= 190
assert ws3_oct.max_row > 900
assert ws4_oct.max_row >= 50

print("Export direct test passed successfully!")
