import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import openpyxl

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb.worksheets[0]

tot_ini = 0.0
tot_ajuste = 0.0
tot_recibida = 0.0
tot_mensual = 0.0
tot_salidas = 0.0
tot_apoyo = 0.0
tot_surtido = 0.0
tot_disponible = 0.0
orden_count = 0

for r in range(4, ws.max_row + 1):
    cve = ws.cell(r, 4).value
    if not cve or not str(cve).strip():
        continue
    cve_str = str(cve).strip()
    if cve_str in ('-', 'TOTALES', 'TOTALES GENERALES', 'TOTAL', 'CLAVE') or 'TOTAL' in cve_str.upper():
        continue
    if 'TOTAL' in str(ws.cell(r, 1).value or '').strip().upper():
        continue

    orden = str(ws.cell(r, 1).value or '').strip()
    if orden and orden != '-':
        orden_count += 1

    ini = float(ws.cell(r, 9).value or 0.0)
    aj = float(ws.cell(r, 7).value or 0.0)
    rec = float(ws.cell(r, 8).value or 0.0)
    men = float(ws.cell(r, 10).value or (ini + aj + rec))

    sals = 0.0
    for c in range(11, 30):
        sals += float(ws.cell(r, c).value or 0.0)

    ap = float(ws.cell(r, 30).value or 0.0)
    sur = float(ws.cell(r, 31).value or (sals + ap))
    disp = float(ws.cell(r, 32).value or (men - sur))

    tot_ini += ini
    tot_ajuste += aj
    tot_recibida += rec
    tot_mensual += men
    tot_salidas += sals
    tot_apoyo += ap
    tot_surtido += sur
    tot_disponible += disp

print(f"Total data rows: {r - 3}")
print(f"Rows with orden: {orden_count}")
print(f"Total Inv Inicial: {tot_ini}")
print(f"Total Ajuste: {tot_ajuste}")
print(f"Total Recibida: {tot_recibida}")
print(f"Total Mensual: {tot_mensual}")
print(f"Total Salidas: {tot_salidas}")
print(f"Total Apoyo: {tot_apoyo}")
print(f"Total Surtido: {tot_surtido}")
print(f"Total Disponible: {tot_disponible}")
