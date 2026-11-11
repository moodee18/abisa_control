import openpyxl

wb = openpyxl.load_workbook('data/INV_OCTUBRE_11.xlsx', data_only=True)
ws = wb['Hoja2']

found = []
for r in ws.iter_rows(min_row=2, values_only=True):
    alm = str(r[4] or '').strip().upper()
    if 'ABASTECEDOR TERAPEUTICO' in alm:
        found.append(r[:7])

print("Found ABASTECEDOR TERAPEUTICO in Excel:", len(found))

