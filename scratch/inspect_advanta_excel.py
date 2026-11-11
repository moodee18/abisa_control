import openpyxl

wb = openpyxl.load_workbook('data/INV_OCTUBRE_11.xlsx', data_only=True)
ws = wb['Hoja2']

advanta_rows = []
for r in ws.iter_rows(min_row=2, values_only=True):
    alm = str(r[4] or '').strip().upper()
    if alm == 'ADVANTA PHARMA SAPI DE CV':
        cod, clave, desc, lote, _, cant, cad = r[:7]
        advanta_rows.append({
            'cod': str(cod).strip(),
            'clave': str(clave).strip(),
            'lote': str(lote).strip(),
            'cad': str(cad).strip()[:10],
            'cant': cant
        })

print(f"ADVANTA rows in Excel: {len(advanta_rows)}")
for i, x in enumerate(advanta_rows):
    print(f"  {i+1}: Lote={x['lote']}, Cod={x['cod']}, Cad={x['cad']}, Cant={x['cant']}")

