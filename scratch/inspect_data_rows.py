import openpyxl

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb['OCT']

for r in range(4, 25):
    orden = ws.cell(r, 1).value
    prov = ws.cell(r, 2).value
    desc = ws.cell(r, 3).value
    cve = ws.cell(r, 4).value
    lote = ws.cell(r, 5).value
    udm = ws.cell(r, 6).value
    ajuste = ws.cell(r, 7).value
    recibida = ws.cell(r, 8).value
    inv_ini = ws.cell(r, 9).value
    inv_tot = ws.cell(r, 10).value
    cad = ws.cell(r, 33).value
    apoyo = ws.cell(r, 30).value
    tot_surt = ws.cell(r, 31).value
    disp = ws.cell(r, 32).value
    
    # Check if there are daily salidas
    salidas_dias = {}
    for c in range(11, 30):
        dia_header = ws.cell(3, c).value
        val = ws.cell(r, c).value
        if val is not None and str(val).strip() not in ['', '0', '0.0']:
            salidas_dias[dia_header] = val

    print(f"Row {r}: Clave={cve} | Lote={lote} | Cad={cad} | InvIni={inv_ini} | Ajuste={ajuste} | Recibida={recibida} | InvTot={inv_tot} | Surtido={tot_surt} | Disp={disp} | Salidas={salidas_dias}")
