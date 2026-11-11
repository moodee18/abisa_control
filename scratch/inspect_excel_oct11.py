import openpyxl

wb = openpyxl.load_workbook('data/INV_OCTUBRE_11.xlsx', data_only=True)
print("Sheet names:", wb.sheetnames)

for sname in wb.sheetnames:
    ws = wb[sname]
    print(f"\n=== Sheet: {sname} (max_row={ws.max_row}, max_column={ws.max_column}) ===")
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        print("  Empty sheet")
        continue
    # Show first 10 rows
    for i, r in enumerate(rows[:10]):
        # filter trailing None
        non_empty = [c for c in r if c is not None]
        if non_empty:
            print(f"  Row {i+1}: {r[:10]}")

