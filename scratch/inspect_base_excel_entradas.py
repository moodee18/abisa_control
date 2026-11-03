import openpyxl
import os

files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
print("Excel files in current dir:", files)

for fname in ['INVETARIO SIMPLIFICADO OCT MAC.xlsx', 'INVETARIO SIMPLIFICADO OCT.xlsx']:
    if os.path.exists(fname):
        wb = openpyxl.load_workbook(fname, read_only=True)
        print(f"\n{fname} sheets:", wb.sheetnames)
        if 'Entradas' in wb.sheetnames:
            ws = wb['Entradas']
            print("Entradas max_row:", ws.max_row)
            rows = []
            for r in ws.iter_rows(values_only=True):
                rows.append(r)
                if len(rows) >= 10:
                    break
            print("Entradas headers:", rows[0] if rows else None)
            for r in rows[1:6]:
                print("Row:", r)
        wb.close()

