import openpyxl
from collections import Counter

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb.worksheets[0]

excel_orden_rows = []
for r in range(4, ws.max_row + 1):
    val = ws.cell(r, 1).value
    if val and str(val).strip() and str(val).strip() != '-':
        cve = str(ws.cell(r, 4).value or '').strip()
        lote = str(ws.cell(r, 5).value or '').strip()
        excel_orden_rows.append({
            'row': r,
            'orden': str(val).strip(),
            'clave': cve,
            'lote': lote,
            'prov': str(ws.cell(r, 2).value or '').strip(),
            'inv_ini': ws.cell(r, 9).value,
            'ajuste': ws.cell(r, 7).value,
            'recibida': ws.cell(r, 8).value
        })

print(f"Excel rows with orden: {len(excel_orden_rows)}")

c = Counter((x['clave'], x['lote']) for x in excel_orden_rows)
dups = {k: v for k, v in c.items() if v > 1}
print(f"Duplicate (clave, lote) among rows with orden: {len(dups)}")
for k, v in dups.items():
    matching = [x for x in excel_orden_rows if (x['clave'], x['lote']) == k]
    print(f"Key {k} appears {v} times:")
    for m in matching:
        print(f"   Row {m['row']}: orden={m['orden']}, inv={m['inv_ini']}, aj={m['ajuste']}, rec={m['recibida']}")

# Also check: what about rows in Excel where clave is duplicate across the entire Excel?
all_excel_rows = []
for r in range(4, ws.max_row + 1):
    cve = str(ws.cell(r, 4).value or '').strip()
    lote = str(ws.cell(r, 5).value or '').strip()
    orden = str(ws.cell(r, 1).value or '').strip()
    if cve:
        all_excel_rows.append((r, cve, lote, orden))

print(f"Total data rows in Excel: {len(all_excel_rows)}")
c_all = Counter((x[1], x[2]) for x in all_excel_rows)
print(f"Unique (clave, lote) in Excel: {len(c_all)}")
