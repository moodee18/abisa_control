import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from database import (
    Base, DatabaseManager, InsumoRecord, MovimientoRecord,
    CatalogoInsumoMov, ProveedorMov, UnidadMedidaMov, EntradaMov, SalidaPdfMov, ApoyoInstitucionalMov
)
from sqlalchemy import func, or_, and_, desc
import io
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class TestMovimientosManager(DatabaseManager):
    def seed_control_movimientos_defaults(self):
        session = self.get_session()
        try:
            # 1. Unidades de Medida
            if session.query(UnidadMedidaMov).count() == 0:
                unidades = ["PZA", "CAJA", "FCO", "ENV", "AMP", "JGA", "KGO", "ML", "PQTE", "TUBO", "ROLLO", "PAR", "BOLSA", "FRASCO", "PIEZA"]
                for u in unidades:
                    session.add(UnidadMedidaMov(clave_unidad=u, descripcion=f"Unidad {u}"))
                session.commit()

            # 2. Proveedores
            if session.query(ProveedorMov).count() == 0:
                provs = session.query(InsumoRecord.proveedor).filter(
                    InsumoRecord.proveedor.isnot(None),
                    InsumoRecord.proveedor != '',
                    InsumoRecord.proveedor != 'False'
                ).distinct().all()
                for p in provs:
                    p_name = p[0].strip()
                    if p_name and not session.query(ProveedorMov).filter_by(nombre=p_name).first():
                        session.add(ProveedorMov(nombre=p_name))
                session.commit()

            # 3. Catálogo de Claves
            if session.query(CatalogoInsumoMov).count() == 0:
                cats = session.query(
                    InsumoRecord.clave,
                    func.max(InsumoRecord.descripcion).label("desc"),
                    func.max(InsumoRecord.unidad_medida).label("udm"),
                    func.max(InsumoRecord.proveedor).label("prov"),
                    func.max(InsumoRecord.no_procedimiento).label("proc")
                ).filter(InsumoRecord.clave.isnot(None), InsumoRecord.clave != '').group_by(InsumoRecord.clave).all()
                for c in cats:
                    session.add(CatalogoInsumoMov(
                        clave=c.clave,
                        descripcion=c.desc or "Sin descripción",
                        unidad_medida=c.udm or "PZA",
                        proveedor_predeterminado=c.prov or "",
                        procedimiento=c.proc or ""
                    ))
                session.commit()

            # 4. Entradas iniciales (Octubre 2026)
            if session.query(EntradaMov).count() == 0:
                ins = session.query(InsumoRecord).filter(
                    InsumoRecord.clave.isnot(None), InsumoRecord.lote.isnot(None)
                ).limit(100).all()
                for item in ins:
                    session.add(EntradaMov(
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
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"[ERROR SEED]: {e}")
        finally:
            session.close()

mgr = TestMovimientosManager()
mgr.seed_control_movimientos_defaults()
print("Seed test executed successfully!")
