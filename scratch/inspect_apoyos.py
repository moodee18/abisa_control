import openpyxl

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb['OCT']

print("=== INSPECCIÓN DE FILAS CON APOYO INSTITUCIONAL ===")
count = 0
for r in range(4, ws.max_row + 1):
    apoyo = ws.cell(r, 30).value
    try:
        f_apoyo = float(apoyo or 0.0)
    except:
        f_apoyo = 0.0
        
    if f_apoyo > 0:
        count += 1
        cve = ws.cell(r, 4).value
        lote = ws.cell(r, 5).value
        inst_col1 = ws.cell(r, 1).value
        col34 = ws.cell(r, 34).value
        col35 = ws.cell(r, 35).value
        print(f"[{count}] Row {r}: Clave={cve} | Lote={lote} | Apoyo={f_apoyo} | Col1='{inst_col1}' | Col34='{col34}' | Col35='{col35}'")
