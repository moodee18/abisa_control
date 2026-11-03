import openpyxl

p = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO\INVETARIO SIMPLIFICADO 16 OCT.xlsx'
wb = openpyxl.load_workbook(p, data_only=True)
ws = wb['Salidas']

print("Total rows in Salidas:", ws.max_row)
for r in range(1, ws.max_row + 1):
    vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
    # print if not completely empty
    non_empty = [(c, v) for c, v in enumerate(vals, 1) if v is not None and str(v).strip() != '']
    if non_empty:
        # print clave, lote, cantidad, fecha, observaciones
        row_str = ' | '.join([f"C{c}: {v}" for c, v in non_empty[:12]])
        print(f"R{r:2d}: {row_str}")

