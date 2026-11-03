import openpyxl

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb['OCT']
print(f"Total rows: {ws.max_row}, Total cols: {ws.max_column}")
print("\nHeaders mapping:")
for c in range(1, ws.max_column + 1):
    val1 = ws.cell(1, c).value
    val2 = ws.cell(2, c).value
    val3 = ws.cell(3, c).value
    print(f"Col {c} ({openpyxl.utils.get_column_letter(c)}): R1='{val1}' | R2='{val2}' | R3='{val3}'")
