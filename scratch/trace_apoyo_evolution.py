import glob, openpyxl, os

lotes = ['240401', '3A045050', '3A511049', '15-22', '279NEX3325', '11-24', '221055', '04238407']

files = [
    'INVETARIO SIMPLIFICADO 05 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 08 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 09 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 12 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 14 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 15 OCT.xlsx',
    'INVETARIO SIMPLIFICADO 16 OCT.xlsx',
    'INVETARIO SIMPLIFICADO OCT MAC.xlsx'
]

dir_path = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO'

for fname in files:
    fpath = os.path.join(dir_path, fname)
    if not os.path.exists(fpath): continue
    wb = openpyxl.load_workbook(fpath, data_only=True)
    # Check the last sheet or the sheet representing the day
    sheet_name = wb.sheetnames[-1]
    ws = wb[sheet_name]
    
    # Find columns for Clave, Lote, Apoyo Institucional, Apoyo Fecha
    # Let's read header row (row 2 or 1)
    header2 = [ws.cell(2, c).value for c in range(1, 45)]
    
    print(f"\n=== {fname} [{sheet_name}] ===")
    for r_idx in range(4, ws.max_row + 1):
        row_vals = [ws.cell(r_idx, c).value for c in range(1, 45)]
        row_str = ' '.join([str(v) for v in row_vals if v is not None])
        for target_lote in lotes:
            if target_lote in row_str:
                # Find clave, lote, apoyo, fecha_apoyo
                non_empty = [(c, ws.cell(2, c).value, ws.cell(3, c).value, val) for c, val in enumerate(row_vals, 1) if val is not None and str(val).strip() != '']
                # Filter to relevant columns: Col with Lote, and cols with Apoyo or Fecha
                relevant = []
                for c, h2, h3, val in non_empty:
                    h_str = f"{h2 or ''} {h3 or ''}".upper()
                    if target_lote in str(val) or 'APOYO' in h_str or 'TOTAL SURTIDO' in h_str:
                        relevant.append((c, h2, val))
                print(f"  Lote {target_lote} (Row {r_idx}): {relevant}")

