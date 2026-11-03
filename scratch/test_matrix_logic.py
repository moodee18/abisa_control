import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from database import (
    Base, DatabaseManager, InsumoRecord, MovimientoRecord,
    CatalogoInsumoMov, ProveedorMov, UnidadMedidaMov, EntradaMov, SalidaPdfMov, ApoyoInstitucionalMov
)

db = DatabaseManager()
session = db.get_session()

mes = "OCTUBRE"
ano = 2026

entradas = session.query(EntradaMov).filter(EntradaMov.mes == mes, EntradaMov.ano == ano).all()
print(f"Total entradas in {mes} {ano}:", len(entradas))

# Map rows by (clave, lote)
rows_map = {}
for e in entradas:
    key = (e.clave, e.lote)
    if key not in rows_map:
        rows_map[key] = {
            "id": e.id,
            "folio_documento": e.folio_documento or "",
            "procedimiento": e.procedimiento or "",
            "contrato": e.contrato or "",
            "registro_sanitario": e.registro_sanitario or "",
            "almacen": e.almacen or "CS ALMACEN 2022",
            "proveedor": e.proveedor or "",
            "clave": e.clave,
            "lote": e.lote,
            "descripcion": e.descripcion or "",
            "unidad_medida": e.unidad_medida or "PZA",
            "fecha_caducidad": e.fecha_caducidad or "",
            "fecha_fabricacion": e.fecha_fabricacion or "",
            "inventario_inicial": float(e.inventario_inicial or 0.0),
            "entrada_ajuste": float(e.entrada_ajuste or 0.0),
            "cantidad_recibida": float(e.cantidad_recibida or 0.0),
            "dias": {str(d): 0.0 for d in range(1, 32)},
            "apoyo_institucional": 0.0
        }
    else:
        rows_map[key]["entrada_ajuste"] += float(e.entrada_ajuste or 0.0)
        rows_map[key]["cantidad_recibida"] += float(e.cantidad_recibida or 0.0)

salidas = session.query(SalidaPdfMov).filter(SalidaPdfMov.mes == mes, SalidaPdfMov.ano == ano).all()
for s_item in salidas:
    key = (s_item.clave, s_item.lote_asignado or "")
    if key in rows_map and s_item.dia:
        d_str = str(s_item.dia)
        if d_str in rows_map[key]["dias"]:
            rows_map[key]["dias"][d_str] += float(s_item.cantidad or 0.0)

apoyos = session.query(ApoyoInstitucionalMov).filter(ApoyoInstitucionalMov.mes == mes, ApoyoInstitucionalMov.ano == ano).all()
for a_item in apoyos:
    key = (a_item.clave, a_item.lote)
    if key in rows_map:
        rows_map[key]["apoyo_institucional"] += float(a_item.cantidad or 0.0)

final_rows = []
for (cve, lot), item in rows_map.items():
    inv_total_mensual = item["inventario_inicial"] + item["entrada_ajuste"] + item["cantidad_recibida"]
    salidas_sum = sum(item["dias"].values())
    total_surtido = salidas_sum + item["apoyo_institucional"]
    inv_disponible = inv_total_mensual - total_surtido
    
    item["inventario_total_mensual"] = inv_total_mensual
    item["salidas_diarias_total"] = salidas_sum
    item["total_surtido"] = total_surtido
    item["inventario_disponible"] = inv_disponible
    final_rows.append(item)

print(f"Consolidated rows: {len(final_rows)}")
if final_rows:
    print("Sample row:", final_rows[0]["clave"], final_rows[0]["lote"], "Inv. Disp:", final_rows[0]["inventario_disponible"])

session.close()
