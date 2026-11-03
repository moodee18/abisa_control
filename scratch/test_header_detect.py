import openpyxl, re

def detect_headers(ws):
    col_map = {}
    day_cols = {}
    
    # Scan rows 1, 2, 3
    headers_by_col = {}
    for c in range(1, ws.max_column + 1):
        texts = []
        for r in range(1, 4):
            val = ws.cell(r, c).value
            if val is not None:
                texts.append(str(val).strip())
        headers_by_col[c] = " | ".join(texts)

    # First detect day columns:
    for c, combined in headers_by_col.items():
        # Look for day numbers 1..31 in row 2 or 3
        for r in [3, 2, 1]:
            val = ws.cell(r, c).value
            if val is not None:
                val_s = str(val).strip()
                if val_s.isdigit() and 1 <= int(val_s) <= 31:
                    day_cols[c] = int(val_s)
                    break

    # Now identify specific semantic columns
    for c, text in headers_by_col.items():
        if c in day_cols:
            continue
        t = text.upper()
        
        # Check specific patterns
        if "PROCEDIMIENTO" in t:
            col_map["procedimiento"] = c
        elif "CONTRATO" in t:
            col_map["contrato"] = c
        elif "REGISTRO SANITARIO" in t or "REG. SANITARIO" in t:
            col_map["registro_sanitario"] = c
        elif "ORDEN DE SUMINISTRO" in t or "ORDEN DE COMPRA" in t:
            col_map["orden"] = c
        elif "PROVEEDOR" in t:
            col_map["proveedor"] = c
        elif "DESCRIPCION" in t or "DESCRIPCIÓN" in t:
            col_map["descripcion"] = c
        elif "CLAVE" in t and "CORTA" not in t:
            col_map["clave"] = c
        elif "LOTE" in t:
            col_map["lote"] = c
        elif "UNIDAD DE MEDIDA" in t or "UDM" in t:
            col_map["udm"] = c
        elif "FECHA DE ENTRADA" in t or "F. ENTRADA" in t or "F_ENTRADA" in t:
            col_map["fecha_entrada"] = c
        elif "ENTRADA POR AJUSTE" in t or "AJUSTE" in t:
            col_map["ajuste"] = c
        elif "FECHA DE FABRICACION" in t or "RECEPCION" in t:
            col_map["fecha_fabricacion"] = c
        elif "CANTIDAD RECIBIDA" in t or "RECIBIDA" in t:
            col_map["recibida"] = c
        elif "INVENTARIO TOTAL" in t or "TOTAL MENSUAL" in t:
            col_map["total_mensual"] = c
        elif "INVENTARIO" in t and "TOTAL" not in t and "DISPONIBLE" not in t:
            col_map["inv_inicial"] = c
        elif "FECHA DE CADUCIDAD" in t or "CADUCIDAD" in t or "F_CAD" in t:
            col_map["caducidad"] = c
        elif "APOYO INSTITUCIONAL / FECHA" in t or "FECHA APOYO" in t:
            col_map["fecha_apoyo"] = c
        elif "APOYO INSTITUCIONAL" in t or "APOYO" in t:
            col_map["apoyo"] = c
        elif "TOTAL SURTIDO" in t or "SURTIDO" in t:
            col_map["total_surtido"] = c
        elif "DISPONIBLE" in t or "INVENTARIO DISPONIBLE" in t:
            col_map["disponible"] = c

    # Fallbacks based on Col 1 header
    col1_txt = headers_by_col.get(1, "").upper()
    if "PROCEDIMIENTO" in col1_txt:
        # User new layout from image media_1793214809642.png
        default_map = {
            "procedimiento": 1, "contrato": 2, "orden": 3, "registro_sanitario": 4,
            "proveedor": 5, "descripcion": 6, "clave": 7, "lote": 8, "udm": 9,
            "fecha_entrada": 10, "ajuste": 11, "fecha_fabricacion": 12, "recibida": 13,
            "inv_inicial": 14, "total_mensual": 15
        }
        for k, v in default_map.items():
            if k not in col_map:
                col_map[k] = v
    elif "ORDEN" in col1_txt:
        # Legacy layout from INVETARIO_SIMPLIFICADO_OCT.xlsx
        default_map = {
            "orden": 1, "proveedor": 2, "descripcion": 3, "clave": 4, "lote": 5,
            "udm": 6, "ajuste": 7, "recibida": 8, "inv_inicial": 9, "total_mensual": 10,
            "apoyo": 30, "total_surtido": 31, "disponible": 32, "caducidad": 33, "fecha_apoyo": 34
        }
        for k, v in default_map.items():
            if k not in col_map:
                col_map[k] = v

    return col_map, day_cols

wb = openpyxl.load_workbook('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', data_only=True)
ws = wb.active
col_map, day_cols = detect_headers(ws)
print("Detected col_map for legacy base:")
for k, v in sorted(col_map.items()):
    print(f"  {k}: col {v}")
print(f"Detected {len(day_cols)} day columns: {sorted(day_cols.values())}")
