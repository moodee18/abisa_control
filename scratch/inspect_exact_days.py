import openpyxl, os

lotes = {
    '240401': 'ID 3 (total 155, fechas: 08/10 y 15/10)',
    '3A045050': 'ID 7 (total 14, fechas: 08/10, 15/10 y 16/10)',
    '3A511049': 'ID 11 (total 11, fechas: 08/10 y 15/10)',
    '15-22': 'ID 16 (total 1100, fechas: 05/10, 15/10 y 16/10)',
    '279NEX3325': 'ID 21 (total 14, fechas: 06/10 y 15/10)',
    '11-24': 'ID 29 (total 258, fechas: 08/10, 12/10 y 15/10)',
    '221055': 'ID 40 (total 110, fechas: 15/10 y 16/10)',
    '04238407': 'ID 45 (total 23, fechas: 08/10 y 15/10)',
}

p = r'C:\Users\moode\OneDrive\ABISALUD\INVENTARIO SIMPLIFICADO\INVETARIO SIMPLIFICADO 16 OCT.xlsx'
wb = openpyxl.load_workbook(p, data_only=True)

daily_sheets = ['05 OCT', '06 OCT', '08 OCT', '12 OCT', '14 OCT', '15 OCT', '16 OCT']

for target_lote, desc in lotes.items():
    print(f"\n=======================================================")
    print(f"LOTE {target_lote} - {desc}")
    print(f"=======================================================")
    for sname in daily_sheets:
        if sname not in wb.sheetnames: continue
        ws = wb[sname]
        # find header cols for Apoyo Institucional & Apoyo Institucional / Fecha
        for r_idx in range(4, ws.max_row + 1):
            row_vals = [ws.cell(r_idx, c).value for c in range(1, 45)]
            row_str = ' '.join([str(v) for v in row_vals if v is not None])
            if target_lote in row_str:
                # find apoyo col
                apoyo_val = None
                fecha_val = None
                for c in range(1, 45):
                    h2 = str(ws.cell(2, c).value or '')
                    if 'APOYO INSTITUCIONAL / FECHA' in h2:
                        fecha_val = ws.cell(r_idx, c).value
                    elif 'APOYO INSTITUCIONAL' in h2:
                        apoyo_val = ws.cell(r_idx, c).value
                print(f"  Sheet {sname:7s} | Apoyo: {str(apoyo_val):5s} | Fecha: {fecha_val}")
                break

