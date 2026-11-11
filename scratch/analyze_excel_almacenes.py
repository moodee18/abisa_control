import openpyxl
from collections import Counter

wb = openpyxl.load_workbook('data/INV_OCTUBRE_11.xlsx', data_only=True)
ws = wb['Hoja2']

almacenes = []
rows_data = []

header = [c for c in next(ws.iter_rows(values_only=True))]
print("Headers:", header)

for r in ws.iter_rows(min_row=2, values_only=True):
    if not any(r):
        continue
    cod_barras, clave, desc, lote, almacen, cant, cad = r[:7]
    if almacen:
        almacenes.append(str(almacen).strip().upper())
        rows_data.append({
            'cod_barras': str(cod_barras).strip() if cod_barras is not None else '',
            'clave': str(clave).strip() if clave is not None else '',
            'desc': str(desc).strip() if desc is not None else '',
            'lote': str(lote).strip() if lote is not None else '',
            'almacen': str(almacen).strip().upper(),
            'cant': cant if cant is not None else 0,
            'cad': str(cad).strip() if cad is not None else ''
        })

counts = Counter(almacenes)
print(f"\nTotal rows with almacen: {len(rows_data)}")
print(f"Total unique almacenes: {len(counts)}")
print("\nAlmacenes list (sorted by name):")
for alm, cnt in sorted(counts.items()):
    print(f"  {alm}: {cnt} registros")

