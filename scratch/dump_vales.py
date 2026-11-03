import openpyxl

p = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO\INVETARIO SIMPLIFICADO 15 OCT.xlsx'
wb = openpyxl.load_workbook(p, data_only=True)

for sname in ['64', '65', '66']:
    ws = wb[sname]
    print(f"\n=================== SHEET {sname} ===================")
    for r in range(4, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, 7)]
        if any(v is not None for v in vals):
            print(f"  R{r:2d}: {vals}")

