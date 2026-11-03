import openpyxl

p = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO\INVETARIO SIMPLIFICADO 15 OCT.xlsx'
wb = openpyxl.load_workbook(p, data_only=True)
ws = wb['64']

target_lotes = ['3A045050', '15-22', '221055', '240401', '3A511049', '279NEX3325', '11-24', '04238407']

print("=== Scanning sheet 64 for all target lotes ===")
for r in range(6, ws.max_row + 1):
    cve = ws.cell(r, 1).value
    lot = str(ws.cell(r, 3).value or '').strip()
    qty = ws.cell(r, 5).value
    for tl in target_lotes:
        if tl in lot:
            print(f"R{r:2d} | Clave: {cve} | Lote: {lot} | Cantidad: {qty}")

