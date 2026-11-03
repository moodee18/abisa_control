import openpyxl

p = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO\INVETARIO SIMPLIFICADO 15 OCT.xlsx'
wb = openpyxl.load_workbook(p, data_only=True)

for sname in ['64', '65', '66', 'Entradas']:
    ws = wb[sname]
    print(f"=== Sheet: {sname} (max_row={ws.max_row}, max_col={ws.max_column}) ===")
    for r in range(1, min(15, ws.max_row + 1)):
        vals = [ws.cell(r, c).value for c in range(1, min(15, ws.max_column + 1))]
        if any(v is not None for v in vals):
            print(f"  R{r}: {vals[:8]}")

