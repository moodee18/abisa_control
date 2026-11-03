import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from database import Base, DatabaseManager, InsumoRecord, MovimientoRecord
from scratch.test_db_models import (
    CatalogoInsumoMov, ProveedorMov, UnidadMedidaMov, EntradaMov, SalidaPdfMov, ApoyoInstitucionalMov
)
from sqlalchemy import func
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

db = DatabaseManager()
s = db.get_session()

# Check seeding
if s.query(UnidadMedidaMov).count() == 0:
    for u in ["PZA", "CAJA", "FCO", "ENV", "AMP", "JGA", "KGO", "ML", "PQTE", "TUBO", "ROLLO", "PAR"]:
        s.add(UnidadMedidaMov(clave_unidad=u, descripcion=f"Unidad {u}"))
    s.commit()

if s.query(ProveedorMov).count() == 0:
    provs = s.query(InsumoRecord.proveedor).filter(InsumoRecord.proveedor.isnot(None), InsumoRecord.proveedor != '', InsumoRecord.proveedor != 'False').distinct().all()
    for p in provs:
        p_name = p[0].strip()
        if p_name and not s.query(ProveedorMov).filter_by(nombre=p_name).first():
            s.add(ProveedorMov(nombre=p_name))
    s.commit()

if s.query(CatalogoInsumoMov).count() == 0:
    cats = s.query(
        InsumoRecord.clave,
        func.max(InsumoRecord.descripcion).label("desc"),
        func.max(InsumoRecord.unidad_medida).label("udm"),
        func.max(InsumoRecord.proveedor).label("prov"),
        func.max(InsumoRecord.no_procedimiento).label("proc")
    ).filter(InsumoRecord.clave.isnot(None), InsumoRecord.clave != '').group_by(InsumoRecord.clave).all()
    
    for c in cats:
        s.add(CatalogoInsumoMov(
            clave=c.clave,
            descripcion=c.desc or "Sin descripción",
            unidad_medida=c.udm or "PZA",
            proveedor_predeterminado=c.prov or "",
            procedimiento=c.proc or ""
        ))
    s.commit()
    print("Seeded catalog:", s.query(CatalogoInsumoMov).count())

if s.query(EntradaMov).count() == 0:
    # Seed top 100 distinct lotes from insumos_report for OCTUBRE 2026
    ins = s.query(InsumoRecord).filter(InsumoRecord.clave.isnot(None), InsumoRecord.lote.isnot(None)).limit(100).all()
    for item in ins:
        s.add(EntradaMov(
            folio_documento=item.folio_documento or "E-2026-001",
            procedimiento=item.no_procedimiento or "LIC-2026",
            contrato="CONTRATO-ESTATAL-2026",
            registro_sanitario="REG-SSA-001",
            almacen=item.almacen_origen or "CS ALMACEN 2022",
            proveedor=item.proveedor or "PROVEEDOR GENERAL",
            clave=item.clave,
            lote=item.lote,
            descripcion=item.descripcion or "",
            unidad_medida=item.unidad_medida or "PZA",
            fecha_entrada=item.fecha_documento or "2026-10-01",
            fecha_fabricacion="2025-10-01",
            fecha_caducidad=item.caducidad or "2027-10-01",
            inventario_inicial=float(item.cantidad or 0.0),
            entrada_ajuste=0.0,
            cantidad_recibida=0.0,
            mes="OCTUBRE",
            ano=2026
        ))
    s.commit()
    print("Seeded initial entries:", s.query(EntradaMov).count())

s.close()
print("Seed verification finished successfully!")
