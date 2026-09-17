import openpyxl

path = r"C:\Users\moode\OneDrive\ABISALUD\EXISTENCIA CLUES\inventario_siplificado_cluesEnMayucula_ REPORTE DIARIO CAMBIOOOOOS.xlsx"
wb = openpyxl.load_workbook(path, data_only=True)
print("Sheet names:", wb.sheetnames)

for sname in wb.sheetnames:
    ws = wb[sname]
    print(f"\n--- Sheet: {sname} (max_row={ws.max_row}, max_col={ws.max_column}) ---")
    for r in range(1, min(6, ws.max_row + 1)):
        row_vals = [ws.cell(r, c).value for c in range(1, min(15, ws.max_column + 1))]
        print(f"Row {r}: {row_vals}")

# Let's check sheet "salidas por dia" or whatever sheet has the daily matrix:
for sname in wb.sheetnames:
    ws = wb[sname]
    if "salida" in sname.lower() or "dia" in sname.lower():
        # Check last rows
        print(f"\n--- Last 5 rows of {sname}: ---")
        for r in range(max(1, ws.max_row - 5), ws.max_row + 1):
            row_vals = [ws.cell(r, c).value for c in range(1, min(15, ws.max_column + 1))]
            print(f"Row {r}: {row_vals}")
