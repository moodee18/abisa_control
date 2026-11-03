import openpyxl

p = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO\INVETARIO SIMPLIFICADO 16 OCT.xlsx'
wb = openpyxl.load_workbook(p, data_only=True)

target_lotes = ['3A045050', '15-22', '221055']

# Check sheets 15 OCT, 16 OCT, and Salidas
for sname in ['15 OCT', '16 OCT', 'Salidas']:
    if sname not in wb.sheetnames: continue
    ws = wb[sname]
    print(f"\n=== Sheet: {sname} ===")
    for r in range(1, ws.max_row + 1):
        row_vals = [ws.cell(r, c).value for c in range(1, 45)]
        row_str = ' '.join([str(v) for v in row_vals if v is not None])
        for lot in target_lotes:
            if lot in row_str:
                non_empty = [(c, ws.cell(2, c).value if ws.max_row >= 2 else '', val) for c, val in enumerate(row_vals, 1) if val is not None and str(val).strip() != '']
                print(f"  Lot {lot} (R{r}): {non_empty[:15]}")

