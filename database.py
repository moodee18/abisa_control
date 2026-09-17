import datetime
import re
from typing import List, Dict, Any, Optional
import json
import pandas as pd
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index, func, or_, desc
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import config

Base = declarative_base()

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operation = Column(String(50), nullable=False) # 'DOWNLOAD', 'IMPORT', 'CREATE', 'UPDATE', 'DELETE'
    file_name = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False)    # 'SUCCESS', 'FAILED', 'WARNING'
    records_count = Column(Integer, default=0)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "file_name": self.file_name,
            "status": self.status,
            "records_count": self.records_count,
            "details": self.details,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class InsumoRecord(Base):
    __tablename__ = "insumos_report"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_source = Column(String(150), nullable=False, default="MANUAL_ENTRY") # Nombre del archivo original o método de alta
    
    # 23 campos completos del reporte SIIA Abisalud
    clave = Column(String(100), index=True, nullable=True) # Clave principal (Clave Cliente del Sector Salud)
    clave_cliente = Column(String(100), index=True, nullable=True)
    clave_abisa = Column(String(100), index=True, nullable=True)
    codigo_barras = Column(String(100), index=True, nullable=True)
    descripcion = Column(Text, nullable=True)
    nombre_comercial = Column(String(200), nullable=True)
    lote = Column(String(100), index=True, nullable=True)
    almacen_origen = Column(String(150), nullable=True) # Almacén
    ubicacion = Column(String(100), nullable=True)
    cantidad = Column(Float, default=0.0) # Existencia Real piezas
    factor_fraccionados = Column(Float, default=0.0)
    existencia_real_cajas = Column(Float, default=0.0)
    caducidad = Column(String(50), nullable=True)
    caduca_en = Column(String(50), nullable=True)
    laboratorio = Column(String(200), nullable=True)
    presentacion = Column(String(200), nullable=True) # Presentación Venta
    localidad = Column(String(150), nullable=True)
    fecha_documento = Column(String(50), nullable=True) # Fecha Ultima Entrada
    proveedor = Column(String(200), nullable=True)
    no_procedimiento = Column(String(100), nullable=True)
    fuente_adquisicion = Column(String(150), nullable=True)
    ano = Column(String(20), nullable=True)
    precio_unitario = Column(Float, default=0.0) # Costo
    importe_total = Column(Float, default=0.0)
    observaciones = Column(Text, nullable=True)
    unidad_medida = Column(String(50), nullable=True)
    almacen_destino = Column(String(150), nullable=True)
    folio_documento = Column(String(100), index=True, nullable=True)
    
    # Todos los datos originales en JSON para no perder columnas adicionales
    raw_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "report_source": self.report_source,
            "clave": self.clave or "",
            "clave_cliente": self.clave_cliente or self.clave or "",
            "clave_abisa": self.clave_abisa or "",
            "codigo_barras": self.codigo_barras or "",
            "descripcion": self.descripcion or "",
            "nombre_comercial": self.nombre_comercial or "",
            "lote": self.lote or "",
            "almacen": self.almacen_origen or "",
            "almacen_origen": self.almacen_origen or "",
            "ubicacion": self.ubicacion or "",
            "cantidad": float(self.cantidad or 0.0),
            "existencia_real_piezas": float(self.cantidad or 0.0),
            "factor_fraccionados": float(self.factor_fraccionados or 0.0),
            "existencia_real_cajas": float(self.existencia_real_cajas or 0.0),
            "caducidad": self.caducidad or "",
            "caduca_en": self.caduca_en or "",
            "laboratorio": self.laboratorio or "",
            "presentacion": self.presentacion or "",
            "presentacion_venta": self.presentacion or "",
            "localidad": self.localidad or "",
            "fecha_documento": self.fecha_documento or "",
            "fecha_ultima_entrada": self.fecha_documento or "",
            "proveedor": self.proveedor or "",
            "no_procedimiento": self.no_procedimiento or "",
            "fuente_adquisicion": self.fuente_adquisicion or "",
            "ano": self.ano or "",
            "costo": float(self.precio_unitario or 0.0),
            "precio_unitario": float(self.precio_unitario or 0.0),
            "importe_total": float(self.importe_total or 0.0),
            "observaciones": self.observaciones or "",
            "unidad_medida": self.unidad_medida or "PZA",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class MovimientoRecord(Base):
    __tablename__ = "movimientos_entradas_salidas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(20), index=True, nullable=False) # 'ENTRADA' o 'SALIDA'
    report_source = Column(String(150), nullable=True)
    
    clave = Column(String(100), index=True, nullable=True) # Clave artículo (ej. SO-1557-09)
    clave_cliente = Column(String(100), index=True, nullable=True) # Clave Sector Salud (ej. 060.168.6652)
    codigo_barras = Column(String(100), index=True, nullable=True)
    descripcion = Column(Text, nullable=True)
    lote = Column(String(100), index=True, nullable=True)
    caducidad = Column(String(50), nullable=True)
    ubicacion = Column(String(100), nullable=True)
    cantidad = Column(Float, default=0.0)
    costo = Column(Float, default=0.0)
    fecha = Column(String(50), nullable=True) # Fecha y hora del movimiento
    dia = Column(Integer, index=True, nullable=True) # Día del mes (ej. 14)
    mes = Column(String(20), default="SEPTIEMBRE", nullable=True)
    tipo_movimiento = Column(String(100), nullable=True) # 'DIRECTA', 'PEDIDO', etc.
    referencia = Column(String(255), nullable=True)
    referencia_salida = Column(String(255), nullable=True)
    documento = Column(String(100), index=True, nullable=True) # Folio / Pedido (ej. N-197105, 197069)
    folio_salida = Column(String(100), nullable=True) # Folio salida WS / Folio salida
    proveedor = Column(String(200), nullable=True)
    almacen = Column(String(150), nullable=True)
    usuario = Column(String(150), nullable=True)
    cliente = Column(String(200), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "report_source": self.report_source or "",
            "clave": self.clave or "",
            "clave_cliente": self.clave_cliente or self.clave or "",
            "codigo_barras": self.codigo_barras or "",
            "descripcion": self.descripcion or "",
            "lote": self.lote or "",
            "caducidad": self.caducidad or "",
            "ubicacion": self.ubicacion or "",
            "cantidad": float(self.cantidad or 0.0),
            "costo": float(self.costo or 0.0),
            "fecha": self.fecha or "",
            "dia": int(self.dia or 0),
            "mes": self.mes or "SEPTIEMBRE",
            "tipo_movimiento": self.tipo_movimiento or "",
            "referencia": self.referencia or "",
            "referencia_salida": self.referencia_salida or "",
            "documento": self.documento or "",
            "folio_salida": self.folio_salida or "",
            "proveedor": self.proveedor or "",
            "almacen": self.almacen or "",
            "usuario": self.usuario or "",
            "cliente": self.cliente or "",
            "observaciones": self.observaciones or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class DatabaseManager:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or config.DATABASE_URL
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.init_db()

    def init_db(self):
        """Crea todas las tablas si no existen y aplica migraciones ligeras."""
        Base.metadata.create_all(self.engine)
        new_cols = [
            ("clave_cliente", "VARCHAR(100)"),
            ("clave_abisa", "VARCHAR(100)"),
            ("codigo_barras", "VARCHAR(100)"),
            ("nombre_comercial", "VARCHAR(200)"),
            ("ubicacion", "VARCHAR(100)"),
            ("factor_fraccionados", "FLOAT"),
            ("existencia_real_cajas", "FLOAT"),
            ("caduca_en", "VARCHAR(50)"),
            ("laboratorio", "VARCHAR(200)"),
            ("localidad", "VARCHAR(150)"),
            ("no_procedimiento", "VARCHAR(100)"),
            ("fuente_adquisicion", "VARCHAR(150)"),
            ("ano", "VARCHAR(20)"),
            ("observaciones", "TEXT")
        ]
        try:
            with self.engine.begin() as conn:
                for col, col_type in new_cols:
                    try:
                        conn.exec_driver_sql(f"ALTER TABLE insumos_report ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass
        except Exception:
            pass

    def get_session(self) -> Session:
        return self.SessionLocal()

    def log_execution(self, operation: str, status: str, file_name: Optional[str] = None, 
                      records_count: int = 0, details: Optional[str] = None):
        session = self.get_session()
        try:
            log = ExecutionLog(
                operation=operation,
                file_name=file_name,
                status=status,
                records_count=records_count,
                details=details
            )
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[DB ERROR] No se pudo guardar el log: {e}")
        finally:
            session.close()

    def insert_dataframe(self, df: pd.DataFrame, source_filename: str) -> int:
        """
        Inserta un DataFrame normalizado en la tabla insumos_report mapeando los 23 campos de SIIA.
        Devuelve el número de registros insertados.
        """
        if df.empty:
            return 0

        session = self.get_session()
        records_inserted = 0

        try:
            records = []
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                
                # Helper seguro para extraer flotantes eliminando comas o valores nulos
                def parse_float(val, default=0.0):
                    if pd.isna(val) or val is None:
                        return default
                    try:
                        v_str = str(val).replace(",", "").strip()
                        return float(v_str) if v_str else default
                    except (ValueError, TypeError):
                        return default

                def parse_str(val, default=""):
                    if pd.isna(val) or val is None or str(val).lower() == "nan":
                        return default
                    return str(val).strip()

                clave_cli = parse_str(row_dict.get("clave_cliente"))
                clave_abi = parse_str(row_dict.get("clave_abisa"))
                codigo_bar = parse_str(row_dict.get("codigo_barras") or row_dict.get("codigo"))

                # Clave oficial preferida: Clave Cliente del Sector Salud (ej. 060.088.0785 o 010.000...)
                clave = clave_cli or clave_abi or parse_str(row_dict.get("clave") or row_dict.get("cve_articulo"))

                desc = parse_str(row_dict.get("descripcion") or row_dict.get("concepto") or row_dict.get("articulo"))
                nombre_comercial = parse_str(row_dict.get("nombre_comercial"))
                lote = parse_str(row_dict.get("lote") or row_dict.get("no_lote"))
                almacen = parse_str(row_dict.get("almacen") or row_dict.get("almacen_origen"))
                ubicacion = parse_str(row_dict.get("ubicacion"))
                
                cantidad = parse_float(
                    row_dict.get("existencia_real_piezas") or 
                    row_dict.get("cantidad") or 
                    row_dict.get("existencia") or 
                    row_dict.get("cant")
                )
                factor_fraccionados = parse_float(row_dict.get("factor_fraccionados"))
                existencia_real_cajas = parse_float(row_dict.get("existencia_real_cajas"))

                caducidad = parse_str(row_dict.get("caducidad") or row_dict.get("fecha_caducidad"))
                caduca_en = parse_str(row_dict.get("caduca_en"))
                laboratorio = parse_str(row_dict.get("laboratorio"))
                presentacion = parse_str(row_dict.get("presentacion_venta") or row_dict.get("presentacion"))
                localidad = parse_str(row_dict.get("localidad"))
                fecha_entrada = parse_str(row_dict.get("fecha_ultima_entrada") or row_dict.get("fecha"))
                proveedor = parse_str(row_dict.get("proveedor"))
                no_proc = parse_str(row_dict.get("no_de_procedimiento") or row_dict.get("no_procedimiento"))
                fuente_adq = parse_str(row_dict.get("fuente_de_adquisicion") or row_dict.get("fuente_adquisicion"))
                ano = parse_str(row_dict.get("ano") or row_dict.get("año"))
                
                costo = parse_float(row_dict.get("costo") or row_dict.get("precio") or row_dict.get("precio_unitario"))
                importe_val = row_dict.get("importe") or row_dict.get("total")
                importe = parse_float(importe_val, default=round(cantidad * costo, 2))
                observaciones = parse_str(row_dict.get("observaciones"))

                unidad_val = parse_str(row_dict.get("unidad_de_medida") or row_dict.get("unidad_medida") or row_dict.get("unidad"), default="PZA")
                if not unidad_val:
                    unidad_val = "PZA"

                record = InsumoRecord(
                    report_source=source_filename,
                    clave=clave if clave else None,
                    clave_cliente=clave_cli if clave_cli else (clave if clave else None),
                    clave_abisa=clave_abi if clave_abi else None,
                    codigo_barras=codigo_bar if codigo_bar else None,
                    descripcion=desc if desc else None,
                    nombre_comercial=nombre_comercial if nombre_comercial else None,
                    lote=lote if lote else None,
                    almacen_origen=almacen if almacen else None,
                    ubicacion=ubicacion if ubicacion else None,
                    cantidad=cantidad,
                    factor_fraccionados=factor_fraccionados,
                    existencia_real_cajas=existencia_real_cajas,
                    caducidad=caducidad if caducidad else None,
                    caduca_en=caduca_en if caduca_en else None,
                    laboratorio=laboratorio if laboratorio else None,
                    presentacion=presentacion if presentacion else None,
                    localidad=localidad if localidad else None,
                    fecha_documento=fecha_entrada if fecha_entrada else None,
                    proveedor=proveedor if proveedor else None,
                    no_procedimiento=no_proc if no_proc else None,
                    fuente_adquisicion=fuente_adq if fuente_adq else None,
                    ano=ano if ano else None,
                    precio_unitario=costo,
                    importe_total=importe,
                    observaciones=observaciones if observaciones else None,
                    unidad_medida=unidad_val,
                    almacen_destino=parse_str(row_dict.get("destino")),
                    folio_documento=parse_str(row_dict.get("folio")),
                    raw_json=json.dumps(row_dict, default=str, ensure_ascii=False)
                )
                records.append(record)

            session.bulk_save_objects(records)
            session.commit()
            records_inserted = len(records)
            self.log_execution(
                operation="IMPORT",
                status="SUCCESS",
                file_name=source_filename,
                records_count=records_inserted,
                details=f"Se insertaron exitosamente {records_inserted} registros con todos los campos."
            )
        except Exception as e:
            session.rollback()
            self.log_execution(
                operation="IMPORT",
                status="FAILED",
                file_name=source_filename,
                records_count=0,
                details=str(e)
            )
            raise e
        finally:
            session.close()

        return records_inserted

    # ==========================================
    # MÉTODOS CRUD Y GESTIÓN DE INVENTARIO
    # ==========================================

    def get_inventory_kpis(self) -> Dict[str, Any]:
        """Obtiene indicadores clave de rendimiento (KPIs) del inventario."""
        session = self.get_session()
        try:
            total_records = session.query(InsumoRecord).count()
            
            # Claves únicas activas
            total_claves = session.query(InsumoRecord.clave)\
                .filter(InsumoRecord.clave.isnot(None), InsumoRecord.clave != "")\
                .distinct().count()
            
            # Suma de existencias y valor
            total_piezas = session.query(func.sum(InsumoRecord.cantidad)).scalar() or 0.0
            total_valor = session.query(func.sum(InsumoRecord.importe_total)).scalar() or 0.0
            
            # Lotes únicos
            total_lotes = session.query(InsumoRecord.lote)\
                .filter(InsumoRecord.lote.isnot(None), InsumoRecord.lote != "")\
                .distinct().count()

            # Almacenes registrados
            total_almacenes = session.query(InsumoRecord.almacen_origen)\
                .filter(InsumoRecord.almacen_origen.isnot(None), InsumoRecord.almacen_origen != "")\
                .distinct().count()

            return {
                "total_records": total_records,
                "total_claves": total_claves,
                "total_piezas": round(total_piezas, 2),
                "total_valor": round(total_valor, 2),
                "total_lotes": total_lotes,
                "total_almacenes": total_almacenes
            }
        finally:
            session.close()

    def get_catalog_by_clave(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Devuelve el catálogo consolidado agrupado por Clave única con stock acumulado.
        """
        session = self.get_session()
        try:
            query = session.query(
                InsumoRecord.clave,
                func.max(InsumoRecord.clave_abisa).label("clave_abisa"),
                func.max(InsumoRecord.codigo_barras).label("codigo_barras"),
                func.max(InsumoRecord.descripcion).label("descripcion"),
                func.max(InsumoRecord.presentacion).label("presentacion"),
                func.max(InsumoRecord.unidad_medida).label("unidad_medida"),
                func.sum(InsumoRecord.cantidad).label("total_existencia"),
                func.sum(InsumoRecord.importe_total).label("total_valor"),
                func.avg(InsumoRecord.precio_unitario).label("precio_promedio"),
                func.count(InsumoRecord.id).label("total_lotes_registrados")
            ).filter(InsumoRecord.clave.isnot(None), InsumoRecord.clave != "")

            if search:
                term = f"%{search.strip().lower()}%"
                query = query.filter(
                    or_(
                        func.lower(InsumoRecord.clave).like(term),
                        func.lower(InsumoRecord.clave_abisa).like(term),
                        func.lower(InsumoRecord.codigo_barras).like(term),
                        func.lower(InsumoRecord.descripcion).like(term),
                        func.lower(InsumoRecord.presentacion).like(term),
                        func.lower(InsumoRecord.lote).like(term)
                    )
                )

            query = query.group_by(InsumoRecord.clave).order_by(InsumoRecord.clave.asc())
            results = query.all()

            catalog = []
            for r in results:
                um = r.unidad_medida or "PZA"
                if um.lower() == "nan":
                    um = "PZA"
                catalog.append({
                    "clave": r.clave,
                    "clave_abisa": r.clave_abisa or "",
                    "codigo_barras": r.codigo_barras or "",
                    "descripcion": r.descripcion or "Sin descripción",
                    "presentacion": r.presentacion or "",
                    "unidad_medida": um,
                    "total_existencia": round(float(r.total_existencia or 0.0), 2),
                    "total_valor": round(float(r.total_valor or 0.0), 2),
                    "precio_promedio": round(float(r.precio_promedio or 0.0), 2),
                    "total_lotes_registrados": int(r.total_lotes_registrados or 0)
                })
            return catalog
        finally:
            session.close()

    def get_records(self, clave: Optional[str] = None, search: Optional[str] = None, 
                    lote: Optional[str] = None, almacen: Optional[str] = None, 
                    limit: int = 200, offset: int = 0) -> Dict[str, Any]:
        """
        Retorna registros detallados con soporte para filtros y paginación.
        """
        session = self.get_session()
        try:
            query = session.query(InsumoRecord)

            if clave:
                query = query.filter(or_(
                    InsumoRecord.clave == clave.strip(),
                    InsumoRecord.clave_abisa == clave.strip(),
                    InsumoRecord.codigo_barras == clave.strip()
                ))

            if lote:
                query = query.filter(InsumoRecord.lote == lote.strip())

            if almacen:
                query = query.filter(or_(
                    InsumoRecord.almacen_origen == almacen.strip(),
                    InsumoRecord.almacen_destino == almacen.strip()
                ))

            if search:
                term = f"%{search.strip().lower()}%"
                query = query.filter(
                    or_(
                        func.lower(InsumoRecord.clave).like(term),
                        func.lower(InsumoRecord.clave_abisa).like(term),
                        func.lower(InsumoRecord.codigo_barras).like(term),
                        func.lower(InsumoRecord.descripcion).like(term),
                        func.lower(InsumoRecord.lote).like(term),
                        func.lower(InsumoRecord.almacen_origen).like(term),
                        func.lower(InsumoRecord.ubicacion).like(term),
                        func.lower(InsumoRecord.proveedor).like(term)
                    )
                )

            total_filtered = query.count()
            records = query.order_by(InsumoRecord.id.desc()).offset(offset).limit(limit).all()

            return {
                "total": total_filtered,
                "limit": limit,
                "offset": offset,
                "records": [r.to_dict() for r in records]
            }
        finally:
            session.close()

    def get_record_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un registro por su ID primario."""
        session = self.get_session()
        try:
            record = session.query(InsumoRecord).filter(InsumoRecord.id == record_id).first()
            return record.to_dict() if record else None
        finally:
            session.close()

    def create_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserta manualmente un nuevo registro de insumo/inventario.
        """
        session = self.get_session()
        try:
            cantidad = float(data.get("cantidad") or 0.0)
            precio = float(data.get("precio_unitario") or 0.0)
            importe = float(data.get("importe_total") or (cantidad * precio))

            record = InsumoRecord(
                report_source=data.get("report_source", "MANUAL_ENTRY"),
                clave=str(data.get("clave", "")).strip() or None,
                descripcion=str(data.get("descripcion", "")).strip() or None,
                presentacion=str(data.get("presentacion", "")).strip() or None,
                lote=str(data.get("lote", "")).strip() or None,
                caducidad=str(data.get("caducidad", "")).strip() or None,
                cantidad=cantidad,
                unidad_medida=str(data.get("unidad_medida", "PZA")).strip(),
                precio_unitario=precio,
                importe_total=importe,
                almacen_origen=str(data.get("almacen_origen", "")).strip() or None,
                almacen_destino=str(data.get("almacen_destino", "")).strip() or None,
                proveedor=str(data.get("proveedor", "")).strip() or None,
                folio_documento=str(data.get("folio_documento", "")).strip() or None,
                fecha_documento=str(data.get("fecha_documento", datetime.date.today().strftime("%Y-%m-%d"))).strip(),
                raw_json=json.dumps(data, default=str, ensure_ascii=False)
            )
            session.add(record)
            session.commit()
            session.refresh(record)

            result = record.to_dict()
            self.log_execution(
                operation="CREATE",
                status="SUCCESS",
                file_name="MANUAL",
                records_count=1,
                details=f"Insumo creado: Clave '{result['clave']}', Cantidad: {cantidad}"
            )
            return result
        except Exception as e:
            session.rollback()
            self.log_execution(
                operation="CREATE",
                status="FAILED",
                file_name="MANUAL",
                records_count=0,
                details=str(e)
            )
            raise e
        finally:
            session.close()

    def update_record(self, record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza un registro existente y recalcula importes si es necesario.
        """
        session = self.get_session()
        try:
            record = session.query(InsumoRecord).filter(InsumoRecord.id == record_id).first()
            if not record:
                return None

            if "clave" in data:
                record.clave = str(data["clave"]).strip() or None
            if "descripcion" in data:
                record.descripcion = str(data["descripcion"]).strip() or None
            if "presentacion" in data:
                record.presentacion = str(data["presentacion"]).strip() or None
            if "lote" in data:
                record.lote = str(data["lote"]).strip() or None
            if "caducidad" in data:
                record.caducidad = str(data["caducidad"]).strip() or None
            if "unidad_medida" in data:
                record.unidad_medida = str(data["unidad_medida"]).strip() or "PZA"
            if "almacen_origen" in data:
                record.almacen_origen = str(data["almacen_origen"]).strip() or None
            if "almacen_destino" in data:
                record.almacen_destino = str(data["almacen_destino"]).strip() or None
            if "proveedor" in data:
                record.proveedor = str(data["proveedor"]).strip() or None
            if "folio_documento" in data:
                record.folio_documento = str(data["folio_documento"]).strip() or None
            if "fecha_documento" in data:
                record.fecha_documento = str(data["fecha_documento"]).strip() or None

            if "cantidad" in data or "precio_unitario" in data or "importe_total" in data:
                if "cantidad" in data:
                    record.cantidad = float(data["cantidad"] or 0.0)
                if "precio_unitario" in data:
                    record.precio_unitario = float(data["precio_unitario"] or 0.0)
                
                if "importe_total" in data and data["importe_total"] is not None:
                    record.importe_total = float(data["importe_total"])
                else:
                    record.importe_total = round(record.cantidad * record.precio_unitario, 2)

            session.commit()
            session.refresh(record)
            result = record.to_dict()

            self.log_execution(
                operation="UPDATE",
                status="SUCCESS",
                file_name="MANUAL",
                records_count=1,
                details=f"Insumo ID {record_id} actualizado: Clave '{result['clave']}', Cantidad: {result['cantidad']}"
            )
            return result
        except Exception as e:
            session.rollback()
            self.log_execution(
                operation="UPDATE",
                status="FAILED",
                file_name="MANUAL",
                records_count=0,
                details=str(e)
            )
            raise e
        finally:
            session.close()

    def delete_record(self, record_id: int) -> bool:
        """Elimina un registro por ID."""
        session = self.get_session()
        try:
            record = session.query(InsumoRecord).filter(InsumoRecord.id == record_id).first()
            if not record:
                return False

            clave = record.clave
            session.delete(record)
            session.commit()

            self.log_execution(
                operation="DELETE",
                status="SUCCESS",
                file_name="MANUAL",
                records_count=1,
                details=f"Insumo ID {record_id} eliminado (Clave: '{clave}')"
            )
            return True
        except Exception as e:
            session.rollback()
            self.log_execution(
                operation="DELETE",
                status="FAILED",
                file_name="MANUAL",
                records_count=0,
                details=str(e)
            )
            raise e
        finally:
            session.close()

    def clear_all_records(self) -> int:
        """Elimina todos los registros de inventario de la base de datos para cargar datos nuevos."""
        session = self.get_session()
        try:
            count = session.query(InsumoRecord).delete()
            session.commit()
            self.log_execution(
                operation="CLEAR",
                status="SUCCESS",
                file_name="DATABASE_RESET",
                records_count=count,
                details=f"Se eliminaron todos los registros ({count} filas) para cargar datos nuevos."
            )
            return count
        except Exception as e:
            session.rollback()
            self.log_execution(
                operation="CLEAR",
                status="FAILED",
                file_name="DATABASE_RESET",
                records_count=0,
                details=str(e)
            )
            raise e
        finally:
            session.close()

    def clear_inventory(self) -> int:
        """Alias explícito para vaciar ÚNICAMENTE inventario y catálogo."""
        return self.clear_all_records()

    # ==========================================
    # MÉTODOS DE ENTRADAS Y SALIDAS (SIIA / PDF)
    # ==========================================

    def insert_movimientos(self, df: pd.DataFrame, tipo: str, source_filename: str) -> int:
        """
        Inserta registros de Entradas o Salidas en la tabla movimientos_entradas_salidas.
        """
        if df.empty:
            return 0

        session = self.get_session()
        tipo_norm = "ENTRADA" if "entrada" in str(tipo).lower() else "SALIDA"

        try:
            # Evitar duplicados del mismo archivo y tipo (ENTRADA / SALIDA)
            session.query(MovimientoRecord).filter(
                MovimientoRecord.report_source == source_filename,
                MovimientoRecord.tipo == tipo_norm
            ).delete()
            session.flush()

            # Consultar firmas existentes para evitar duplicar movimientos idénticos de distintos orígenes
            existing_signatures = set(
                session.query(
                    MovimientoRecord.tipo,
                    MovimientoRecord.documento,
                    MovimientoRecord.clave,
                    MovimientoRecord.lote,
                    MovimientoRecord.fecha,
                    MovimientoRecord.cantidad
                ).all()
            )

            records = []
            for _, row in df.iterrows():
                row_dict = row.to_dict()

                def parse_float(val, default=0.0):
                    if pd.isna(val) or val is None:
                        return default
                    try:
                        v_str = str(val).replace(",", "").replace("$", "").strip()
                        return float(v_str) if v_str else default
                    except (ValueError, TypeError):
                        return default

                def parse_str(val, default=""):
                    if pd.isna(val) or val is None or str(val).lower() == "nan":
                        return default
                    return str(val).strip()

                clave_val = parse_str(row_dict.get("clave"))
                clave_cli = parse_str(row_dict.get("clave_cliente") or row_dict.get("clave_de_cliente"))
                codigo_bar = parse_str(row_dict.get("codigo_barras") or row_dict.get("codigo"))
                desc = parse_str(row_dict.get("descripcion") or row_dict.get("concepto"))
                lote = parse_str(row_dict.get("lote") or row_dict.get("no_lote"))
                caducidad = parse_str(row_dict.get("caducidad") or row_dict.get("fecha_caducidad"))
                ubicacion = parse_str(row_dict.get("ubicacion"))
                cantidad = parse_float(row_dict.get("cantidad") or row_dict.get("c_surtida") or row_dict.get("cant"))
                costo = parse_float(row_dict.get("costo") or row_dict.get("precio"))
                
                fecha_val = parse_str(row_dict.get("fecha") or row_dict.get("fecha_de_documento") or row_dict.get("fecha_documento"))
                
                doc = parse_str(row_dict.get("documento") or row_dict.get("pedido") or row_dict.get("no_pedido"))
                import re
                clean_doc = re.sub(r'^[Nn]-', '', doc) if doc else ""

                # Extraer día estrictamente de la fecha que tenga la salida (SIIA o PDF)
                dia = None
                if "dia" in row_dict and row_dict["dia"] is not None and not pd.isna(row_dict["dia"]):
                    try:
                        dia = int(row_dict["dia"])
                    except Exception:
                        pass

                fecha_ref = fecha_val or parse_str(row_dict.get("fecha_documento") or row_dict.get("fecha_surtido"))
                if dia is None and fecha_ref:
                    m_dia = re.search(r'\b20[2-3][0-9]-[0-1][0-9]-([0-3][0-9])\b', fecha_ref)
                    if m_dia:
                        dia = int(m_dia.group(1))
                    else:
                        m_dia2 = re.search(r'\b([0-3]?[0-9])[-/][0-1]?[0-9][-/]20[2-3][0-9]\b', fecha_ref)
                        if m_dia2:
                            dia = int(m_dia2.group(1))

                if dia is None:
                    import datetime
                    dia = datetime.date.today().day

                tipo_mov = parse_str(row_dict.get("tipo_movimiento") or row_dict.get("tipo"))
                ref = parse_str(row_dict.get("referencia"))
                ref_sal = parse_str(row_dict.get("referencia_salida"))
                folio_sal = parse_str(row_dict.get("folio_salida_ws") or row_dict.get("folio_salida") or row_dict.get("folio"))
                prov = parse_str(row_dict.get("proveedor"))
                alm = parse_str(row_dict.get("almacen"))
                usr = parse_str(row_dict.get("usuario"))
                cli = parse_str(row_dict.get("cliente"))
                obs = parse_str(row_dict.get("observaciones"))

                record = MovimientoRecord(
                    tipo=tipo_norm,
                    report_source=source_filename,
                    clave=clave_val if clave_val else None,
                    clave_cliente=clave_cli if clave_cli else (clave_val if clave_val else None),
                    codigo_barras=codigo_bar if codigo_bar else None,
                    descripcion=desc if desc else None,
                    lote=lote if lote else None,
                    caducidad=caducidad if caducidad else None,
                    ubicacion=ubicacion if ubicacion else None,
                    cantidad=cantidad,
                    costo=costo,
                    fecha=fecha_val if fecha_val else None,
                    dia=dia,
                    mes="SEPTIEMBRE",
                    tipo_movimiento=tipo_mov if tipo_mov else None,
                    referencia=ref if ref else None,
                    referencia_salida=ref_sal if ref_sal else None,
                    documento=doc if doc else None,
                    folio_salida=folio_sal if folio_sal else None,
                    proveedor=prov if prov else None,
                    almacen=alm if alm else None,
                    usuario=usr if usr else None,
                    cliente=cli if cli else None,
                    observaciones=obs if obs else None
                )

                sig = (tipo_norm, doc if doc else None, clave_val if clave_val else None, lote if lote else None, fecha_val if fecha_val else None, cantidad)
                if sig in existing_signatures:
                    continue
                existing_signatures.add(sig)

                records.append(record)

            session.bulk_save_objects(records)
            session.commit()
            records_inserted = len(records)
            self.log_execution(
                operation=f"IMPORT_{tipo_norm}",
                status="SUCCESS",
                file_name=source_filename,
                records_count=records_inserted,
                details=f"Se insertaron exitosamente {records_inserted} registros en {tipo_norm}."
            )
        except Exception as e:
            session.rollback()
            self.log_execution(
                operation=f"IMPORT_{tipo.upper()}",
                status="FAILED",
                file_name=source_filename,
                records_count=0,
                details=str(e)
            )
            raise e
        finally:
            session.close()

        return records_inserted

    def get_movimientos(self, tipo: Optional[str] = None, search: Optional[str] = None,
                        dia: Optional[int] = None, sort_by: str = "fecha_desc",
                        page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Consulta paginada y filtrada de Entradas y Salidas con KPIs."""
        session = self.get_session()
        try:
            query = session.query(MovimientoRecord)

            if tipo and tipo.upper() in ["ENTRADA", "SALIDA"]:
                query = query.filter(MovimientoRecord.tipo == tipo.upper())

            if dia is not None and dia > 0:
                query = query.filter(MovimientoRecord.dia == dia)

            if search:
                term = f"%{search.strip().lower()}%"
                query = query.filter(
                    or_(
                        func.lower(MovimientoRecord.clave).like(term),
                        func.lower(MovimientoRecord.clave_cliente).like(term),
                        func.lower(MovimientoRecord.codigo_barras).like(term),
                        func.lower(MovimientoRecord.descripcion).like(term),
                        func.lower(MovimientoRecord.lote).like(term),
                        func.lower(MovimientoRecord.documento).like(term),
                        func.lower(MovimientoRecord.referencia).like(term),
                        func.lower(MovimientoRecord.proveedor).like(term),
                        func.lower(MovimientoRecord.almacen).like(term)
                    )
                )

            # KPIs generales
            total_entradas_piezas = session.query(func.sum(MovimientoRecord.cantidad))\
                .filter(MovimientoRecord.tipo == 'ENTRADA').scalar() or 0.0
            total_salidas_piezas = session.query(func.sum(MovimientoRecord.cantidad))\
                .filter(MovimientoRecord.tipo == 'SALIDA').scalar() or 0.0
            total_entradas_count = session.query(MovimientoRecord).filter(MovimientoRecord.tipo == 'ENTRADA').count()
            total_salidas_count = session.query(MovimientoRecord).filter(MovimientoRecord.tipo == 'SALIDA').count()

            total_filtered = query.count()

            # Ordenamiento
            if sort_by == "fecha_asc":
                query = query.order_by(MovimientoRecord.fecha.asc(), MovimientoRecord.id.asc())
            elif sort_by == "cantidad_desc":
                query = query.order_by(MovimientoRecord.cantidad.desc())
            elif sort_by == "cantidad_asc":
                query = query.order_by(MovimientoRecord.cantidad.asc())
            elif sort_by == "clave_asc":
                query = query.order_by(MovimientoRecord.clave_cliente.asc(), MovimientoRecord.clave.asc())
            else:
                query = query.order_by(MovimientoRecord.fecha.desc(), MovimientoRecord.id.desc())

            offset = (page - 1) * page_size
            items = query.offset(offset).limit(page_size).all()

            return {
                "items": [it.to_dict() for it in items],
                "total": total_filtered,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_filtered + page_size - 1) // page_size if page_size else 1,
                "kpis": {
                    "total_entradas_piezas": round(float(total_entradas_piezas), 2),
                    "total_salidas_piezas": round(float(total_salidas_piezas), 2),
                    "total_entradas_registros": total_entradas_count,
                    "total_salidas_registros": total_salidas_count,
                    "total_movimientos": total_entradas_count + total_salidas_count
                }
            }
        finally:
            session.close()

    def clear_movimientos(self) -> int:
        """Elimina ÚNICAMENTE los registros de Entradas y Salidas sin tocar inventario/catálogo."""
        session = self.get_session()
        try:
            count = session.query(MovimientoRecord).delete()
            session.commit()
            self.log_execution(
                operation="CLEAR_MOVIMIENTOS",
                status="SUCCESS",
                file_name="MOVIMIENTOS_RESET",
                records_count=count,
                details=f"Se eliminaron {count} registros de Entradas y Salidas."
            )
            return count
        except Exception as e:
            session.rollback()
            self.log_execution(
                operation="CLEAR_MOVIMIENTOS",
                status="FAILED",
                file_name="MOVIMIENTOS_RESET",
                records_count=0,
                details=str(e)
            )
            raise e
        finally:
            session.close()

    # ==========================================
    # MÉTODOS CLUES
    # ==========================================

    def get_clues_matrix(self, search: Optional[str] = None, dia_inicio: int = 1, dia_fin: int = 30) -> Dict[str, Any]:
        """
        Genera la matriz oficial de CLUES:
        - Encabezado: CLUES ('CSIMB003506'), CLAVE, INVENTARIO DISPONIBLE, LOTE, F_CAD, días 1..30
        - Base: InsumoRecord agrupado por (clave, lote, caducidad), unificando existencias.
        - Salidas: MovimientoRecord (tipo='SALIDA').
        - Si una salida (clave, lote, caducidad) no está en el inventario, se incorpora con INVENTARIO DISPONIBLE = 0.
        """
        session = self.get_session()
        try:
            inv_records = session.query(
                func.coalesce(InsumoRecord.clave_cliente, InsumoRecord.clave).label("cve"),
                InsumoRecord.lote,
                InsumoRecord.caducidad,
                func.max(InsumoRecord.descripcion).label("desc"),
                func.sum(InsumoRecord.cantidad).label("stock")
            ).filter(
                InsumoRecord.clave.isnot(None), InsumoRecord.clave != ""
            ).group_by(
                func.coalesce(InsumoRecord.clave_cliente, InsumoRecord.clave),
                InsumoRecord.lote,
                InsumoRecord.caducidad
            ).all()

            # Catálogo para resolver descripciones oficiales garantizadas
            desc_map = {}
            for row_desc in session.query(InsumoRecord.clave, InsumoRecord.descripcion).filter(
                InsumoRecord.descripcion.isnot(None), InsumoRecord.descripcion != ""
            ).all():
                c_clean = (row_desc.clave or "").strip()
                if c_clean and c_clean not in desc_map:
                    desc_map[c_clean] = row_desc.descripcion.strip()

            # REGLA OFICIAL CLUES:
            # 1. Solo se agregan claves que empiezan con número y tienen la estructura oficial del Sector Salud:
            #    ej. 531.345.0263, 080.889.2533, 060.841.0619, 010.000.3616.00
            #    NUNCA las que empiezan con letra (ej. CS000002, HCDTF001) ni pura descripción.
            # 2. LO VIGENTE QUE ESTÁ CADUCADO NO SE AGREGA como inventario disponible.
            #    Si es de meses anteriores pero tuvo salidas en el mes, se ponen las piezas que salieron con inventario disponible de 0.
            #    Los que tienen inventario disponible NO se ponen si están caducados.
            clues_clave_pattern = re.compile(r'^\d{3}\.\d{3}\.\d{3,5}(\.\d{2})?$')
            today_str = datetime.date.today().strftime('%Y-%m-%d')

            days_list = list(range(dia_inicio, dia_fin + 1))
            matrix_dict = {}

            for r in inv_records:
                cve = (r.cve or "").strip()
                if not clues_clave_pattern.match(cve):
                    continue

                lote = (r.lote or "").strip()
                cad = (r.caducidad or "").strip()

                # Si está caducado (fecha anterior a hoy o meses anteriores), no se agrega como disponible
                if cad and cad[:10] < today_str:
                    continue

                stock_val = round(float(r.stock or 0.0), 2)
                # Solo se incorpora con inventario disponible positivo; si no tiene existencia se incorporará solo si tuvo salidas
                if stock_val <= 0:
                    continue

                key = (cve, lote, cad)
                desc = (r.desc or "").strip() or desc_map.get(cve, "")

                matrix_dict[key] = {
                    "clues": "CSIMB003506",
                    "clave": cve,
                    "descripcion": desc,
                    "inventario_disponible": stock_val,
                    "lote": lote,
                    "f_cad": cad,
                    "dias": {str(d): 0.0 for d in days_list},
                    "total_salidas": 0.0
                }

            # Consultar salidas: SOLAMENTE PEDIDOS hacia CS FARMACIA MAT 2022 (se excluyen ajustes)
            salidas = session.query(
                func.coalesce(MovimientoRecord.clave_cliente, MovimientoRecord.clave).label("cve"),
                MovimientoRecord.lote,
                MovimientoRecord.caducidad,
                MovimientoRecord.dia,
                MovimientoRecord.tipo_movimiento,
                MovimientoRecord.referencia,
                MovimientoRecord.documento,
                MovimientoRecord.cliente,
                func.max(MovimientoRecord.descripcion).label("desc"),
                func.sum(MovimientoRecord.cantidad).label("cant_salida")
            ).filter(
                MovimientoRecord.tipo == 'SALIDA',
                MovimientoRecord.tipo_movimiento == 'PEDIDO'
            ).group_by(
                func.coalesce(MovimientoRecord.clave_cliente, MovimientoRecord.clave),
                MovimientoRecord.lote,
                MovimientoRecord.caducidad,
                MovimientoRecord.dia,
                MovimientoRecord.tipo_movimiento,
                MovimientoRecord.referencia,
                MovimientoRecord.documento,
                MovimientoRecord.cliente
            ).all()

            for s in salidas:
                # Excluir documentos de ajuste o movimientos no de pedido
                doc = (s.documento or "").strip()
                if doc.startswith("AJ_"):
                    continue

                # Filtrar destino: únicamente pedidos hacia CS FARMACIA MAT 2022
                ref = (s.referencia or "").strip().upper()
                cli = (s.cliente or "").strip().upper()
                if ("CS FARMACIA" not in ref) and ("CS FARMACIA" not in cli):
                    continue

                cve = (s.cve or "").strip()
                if not clues_clave_pattern.match(cve):
                    continue

                lote = (s.lote or "").strip()
                cad = (s.caducidad or "").strip()

                # REGLA OFICIAL: Por única ocasión, lo que salió el 15 se pasa al día 14
                dia = s.dia
                if dia == 15:
                    dia = 14

                cant = float(s.cant_salida or 0.0)
                key = (cve, lote, cad)
                desc = (s.desc or "").strip() or desc_map.get(cve, "")

                if key not in matrix_dict:
                    # Insumo sin existencia disponible pero con salidas en el mes
                    matrix_dict[key] = {
                        "clues": "CSIMB003506",
                        "clave": cve,
                        "descripcion": desc,
                        "inventario_disponible": 0.0,
                        "lote": lote,
                        "f_cad": cad,
                        "dias": {str(d): 0.0 for d in days_list},
                        "total_salidas": 0.0
                    }
                elif not matrix_dict[key]["descripcion"] and desc:
                    matrix_dict[key]["descripcion"] = desc

                if dia and str(dia) in matrix_dict[key]["dias"]:
                    matrix_dict[key]["dias"][str(dia)] += cant
                    matrix_dict[key]["total_salidas"] += cant

            rows = list(matrix_dict.values())

            if search:
                term = search.strip().lower()
                rows = [
                    r for r in rows if
                    term in r["clave"].lower() or
                    term in r["lote"].lower() or
                    term in r["descripcion"].lower() or
                    term in r["f_cad"].lower()
                ]

            rows.sort(key=lambda x: (x["clave"], x["lote"]))

            total_stock_disponible = sum(r["inventario_disponible"] for r in rows)
            total_salidas_periodo = sum(r["total_salidas"] for r in rows)
            totales_por_dia = {
                str(d): round(sum(r["dias"].get(str(d), 0.0) for r in rows), 2)
                for d in days_list
            }

            return {
                "days": days_list,
                "dia_actual": dia_inicio,
                "mes": "SEPTIEMBRE",
                "rows": rows,
                "total_rows": len(rows),
                "totales_por_dia": totales_por_dia,
                "kpis": {
                    "total_insumos": len(rows),
                    "total_stock_disponible": round(total_stock_disponible, 2),
                    "total_salidas_periodo": round(total_salidas_periodo, 2)
                }
            }
        finally:
            session.close()

    def get_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de los datos almacenados y logs recientes."""
        session = self.get_session()
        try:
            total_records = session.query(InsumoRecord).count()
            total_files = session.query(InsumoRecord.report_source).distinct().count()
            total_movimientos = session.query(MovimientoRecord).count()
            recent_logs = session.query(ExecutionLog).order_by(ExecutionLog.created_at.desc()).limit(8).all()
            
            return {
                "total_records": total_records,
                "total_source_files": total_files,
                "total_movimientos": total_movimientos,
                "recent_logs": [l.to_dict() for l in recent_logs]
            }
        finally:
            session.close()
