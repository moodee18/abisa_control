import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import openpyxl
import json

# Let's verify that with INVETARIO_SIMPLIFICADO_OCT.xlsx, all 100 rows with orden are preserved
wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb.worksheets[0]

excel_ordens = []
for r in range(4, ws.max_row + 1):
    cve = str(ws.cell(r, 4).value or '').strip()
    if not cve or 'TOTAL' in cve.upper():
        continue
    orden = str(ws.cell(r, 1).value or '').strip()
    if orden and orden != '-':
        excel_ordens.append((r, orden, cve, str(ws.cell(r, 5).value or '').strip()))

print(f"Total excel data rows with orden: {len(excel_ordens)}")
print("Sample rows:")
for r, ord_val, cve, lot in excel_ordens[:10]:
    print(f"  Row {r}: {ord_val} | {cve} | {lot}")
