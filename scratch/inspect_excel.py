import openpyxl

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
print('Sheet names:', wb.sheetnames)

for name in wb.sheetnames:
    ws = wb[name]
    print(f"\n================ SHEET: {name} (max_row={ws.max_row}, max_column={ws.max_column}) ================")
    # Print first 5 rows
    for r in range(1, min(10, ws.max_row + 1)):
        row_vals = [ws.cell(r, c).value for c in range(1, min(25, ws.max_column + 1))]
        if any(v is not None for v in row_vals):
            print(f"Row {r}: {row_vals}")
