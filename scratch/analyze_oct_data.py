import openpyxl

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb['OCT']

total_rows = 0
valid_clave_rows = 0
unique_claves = set()
unique_lotes = set()
unique_proveedores = set()
unique_udms = set()

sum_inv_ini = 0.0
sum_ajuste = 0.0
sum_recibida = 0.0
sum_tot_mensual = 0.0
sum_salidas = 0.0
sum_apoyo = 0.0
sum_tot_surtido = 0.0
sum_disponible = 0.0

salidas_count = 0
apoyos_count = 0

day_cols = {}
for c in range(11, 30):
    val_header = str(ws.cell(3, c).value or '').strip()
    if val_header:
        day_cols[c] = val_header

print(f"Detected day columns: {day_cols}")

for r in range(4, ws.max_row + 1):
    cve = ws.cell(r, 4).value
    if cve is None or not str(cve).strip():
        continue
    cve = str(cve).strip()
    lote = str(ws.cell(r, 5).value or '').strip()
    desc = str(ws.cell(r, 3).value or '').strip()
    prov = str(ws.cell(r, 2).value or '').strip()
    udm = str(ws.cell(r, 6).value or 'PZA').strip()
    
    valid_clave_rows += 1
    unique_claves.add(cve)
    if lote:
        unique_lotes.add((cve, lote))
    if prov:
        unique_proveedores.add(prov)
    if udm:
        unique_udms.add(udm)
        
    try:
        inv_ini = float(ws.cell(r, 9).value or 0.0)
    except:
        inv_ini = 0.0
    try:
        ajuste = float(ws.cell(r, 7).value or 0.0)
    except:
        ajuste = 0.0
    try:
        recibida = float(ws.cell(r, 8).value or 0.0)
    except:
        recibida = 0.0
    try:
        inv_tot = float(ws.cell(r, 10).value or 0.0)
    except:
        inv_tot = 0.0
    try:
        apoyo = float(ws.cell(r, 30).value or 0.0)
    except:
        apoyo = 0.0
    try:
        tot_surt = float(ws.cell(r, 31).value or 0.0)
    except:
        tot_surt = 0.0
    try:
        disp = float(ws.cell(r, 32).value or 0.0)
    except:
        disp = 0.0

    sum_inv_ini += inv_ini
    sum_ajuste += ajuste
    sum_recibida += recibida
    sum_tot_mensual += inv_tot
    sum_apoyo += apoyo
    sum_tot_surtido += tot_surt
    sum_disponible += disp
    if apoyo > 0:
        apoyos_count += 1

    for c, d_str in day_cols.items():
        v = ws.cell(r, c).value
        try:
            fv = float(v or 0.0)
            if fv > 0:
                sum_salidas += fv
                salidas_count += 1
        except:
            pass

print(f"\n--- ESTADÍSTICAS DEL ARCHIVO EXCEL ---")
print(f"Filas con Clave válida: {valid_clave_rows}")
print(f"Claves únicas: {len(unique_claves)}")
print(f"Pares Clave-Lote únicos: {len(unique_lotes)}")
print(f"Proveedores únicos: {len(unique_proveedores)}")
print(f"Unidades de medida únicas: {len(unique_udms)}")
print(f"Total Inventario Inicial: {sum_inv_ini:,.2f}")
print(f"Total Entradas por Ajuste: {sum_ajuste:,.2f}")
print(f"Total Cantidad Recibida: {sum_recibida:,.2f}")
print(f"Total Inventario Mensual: {sum_tot_mensual:,.2f}")
print(f"Total Salidas Diarias: {sum_salidas:,.2f} (en {salidas_count} registros diarios)")
print(f"Total Apoyo Institucional: {sum_apoyo:,.2f} (en {apoyos_count} registros)")
print(f"Total Surtido: {sum_tot_surtido:,.2f}")
print(f"Total Inventario Disponible: {sum_disponible:,.2f}")
