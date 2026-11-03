import openpyxl

p = r"C:\Users\moode\OneDrive\ABISALUD\RESPALDOS MACRO\CONCENTRADO MACROCEDIS TOTAL 08-09-2026.xlsx"
wb = openpyxl.load_workbook(p, data_only=True)
print("Sheets:", wb.sheetnames)
ws = wb.active
for r in range(1, 5):
    vals = [(c, ws.cell(r, c).value) for c in range(1, ws.max_column+1) if ws.cell(r, c).value is not None]
    print(f"R{r}:", vals[:10])
