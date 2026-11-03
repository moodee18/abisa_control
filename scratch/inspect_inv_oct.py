import openpyxl

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', read_only=True)
print("Sheets in data/INVETARIO_SIMPLIFICADO_OCT.xlsx:", wb.sheetnames)
for sname in wb.sheetnames:
    ws = wb[sname]
    print(f"Sheet '{sname}': {ws.max_row} rows")
wb.close()

