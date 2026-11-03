import openpyxl, os

lotes = ['240401', '3A045050', '3A511049', '15-22', '279NEX3325', '11-24', '221055', '04238407']

files = [
    'INVETARIO SIMPLIFICADO 05 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 08 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 12 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 14 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 15 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 16 OCT.xlsx',
    'INVETARIO SIMPLIFICADO OCT MAC.xlsx'
]

dir_path = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO'

for target_lote in lotes:
    print(f"\n==========================================")
    print(f"LOTE: {target_lote}")
    print(f"==========================================")
    for fname in files:
        fpath = os.path.join(dir_path, fname)
        if not os.path.exists(fpath): continue
        wb = openpyxl.load_workbook(fpath, data_only=True)
        # Check sheet
        ws = wb[wb.sheetnames[-1]]
        for r_idx in range(4, ws.max_row + 1):
            row_vals = [ws.cell(r_idx, c).value for c in range(1, 45)]
            row_str = ' '.join([str(v) for v in row_vals if v is not None])
            if target_lote in row_str:
                # find apoyo and fecha_apoyo
                # In OCT MAC, col 37 is Apoyo, col 42 is Fecha Apoyo
                # In daily sheets, let's look for header
                apoyo_val = None
                fecha_val = None
                for c in range(1, 45):
                    h2 = str(ws.cell(2, c).value or '')
                    if 'APOYO INSTITUCIONAL / FECHA' in h2:
                        fecha_val = ws.cell(r_idx, c).value
                    elif 'APOYO INSTITUCIONAL' in h2:
                        apoyo_val = ws.cell(r_idx, c).value
                print(f"  {fname:35s} | Apoyo: {str(apoyo_val):5s} | Fecha: {fecha_val}")
                break

