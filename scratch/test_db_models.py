import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path.cwd()))

from database import Base, DatabaseManager, InsumoRecord, MovimientoRecord
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, func, or_, and_, desc
)
import datetime

class CatalogoInsumoMov(Base):
    __tablename__ = "catalogo_movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(100), unique=True, index=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    unidad_medida = Column(String(50), default="PZA")
    proveedor_predeterminado = Column(String(200), nullable=True)
    procedimiento = Column(String(150), nullable=True)
    contrato = Column(String(150), nullable=True)
    registro_sanitario = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "clave": self.clave,
            "descripcion": self.descripcion or "",
            "unidad_medida": self.unidad_medida or "PZA",
            "proveedor_predeterminado": self.proveedor_predeterminado or "",
            "procedimiento": self.procedimiento or "",
            "contrato": self.contrato or "",
            "registro_sanitario": self.registro_sanitario or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class ProveedorMov(Base):
    __tablename__ = "proveedores_movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), unique=True, index=True, nullable=False)
    rfc = Column(String(50), nullable=True)
    contacto = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "rfc": self.rfc or "",
            "contacto": self.contacto or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class UnidadMedidaMov(Base):
    __tablename__ = "unidades_medida_movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clave_unidad = Column(String(50), unique=True, index=True, nullable=False)
    descripcion = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "clave_unidad": self.clave_unidad,
            "descripcion": self.descripcion or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class EntradaMov(Base):
    __tablename__ = "entradas_movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    folio_documento = Column(String(100), index=True, nullable=True)
    procedimiento = Column(String(150), nullable=True)
    contrato = Column(String(150), nullable=True)
    registro_sanitario = Column(String(150), nullable=True)
    almacen = Column(String(150), default="CS ALMACEN 2022")

    proveedor = Column(String(200), nullable=True)
    clave = Column(String(100), index=True, nullable=False)
    lote = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    unidad_medida = Column(String(50), default="PZA")

    fecha_entrada = Column(String(50), nullable=True)
    fecha_fabricacion = Column(String(50), nullable=True)
    fecha_caducidad = Column(String(50), nullable=True)

    inventario_inicial = Column(Float, default=0.0)
    entrada_ajuste = Column(Float, default=0.0)
    cantidad_recibida = Column(Float, default=0.0)

    mes = Column(String(30), default="OCTUBRE", nullable=True)
    ano = Column(Integer, default=2026, nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        inv_ini = float(self.inventario_inicial or 0.0)
        ajuste = float(self.entrada_ajuste or 0.0)
        recibida = float(self.cantidad_recibida or 0.0)
        return {
            "id": self.id,
            "folio_documento": self.folio_documento or "",
            "procedimiento": self.procedimiento or "",
            "contrato": self.contrato or "",
            "registro_sanitario": self.registro_sanitario or "",
            "almacen": self.almacen or "CS ALMACEN 2022",
            "proveedor": self.proveedor or "",
            "clave": self.clave,
            "lote": self.lote,
            "descripcion": self.descripcion or "",
            "unidad_medida": self.unidad_medida or "PZA",
            "fecha_entrada": self.fecha_entrada or "",
            "fecha_fabricacion": self.fecha_fabricacion or "",
            "fecha_caducidad": self.fecha_caducidad or "",
            "inventario_inicial": inv_ini,
            "entrada_ajuste": ajuste,
            "cantidad_recibida": recibida,
            "inventario_total_mensual": inv_ini + ajuste + recibida,
            "mes": self.mes or "OCTUBRE",
            "ano": int(self.ano or 2026),
            "observaciones": self.observaciones or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class SalidaPdfMov(Base):
    __tablename__ = "salidas_pdf_movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    archivo_pdf = Column(String(255), nullable=True)
    folio_pedido = Column(String(100), index=True, nullable=True)
    fecha = Column(String(50), nullable=True)
    dia = Column(Integer, index=True, nullable=True)
    mes = Column(String(30), default="OCTUBRE", nullable=True)
    ano = Column(Integer, default=2026, nullable=True)
    clave = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    cantidad = Column(Float, default=0.0)
    lote_asignado = Column(String(100), index=True, nullable=True)
    fecha_caducidad = Column(String(50), nullable=True)
    cliente_destino = Column(String(200), nullable=True)
    estado_validacion = Column(String(50), default="VALIDADO")
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "archivo_pdf": self.archivo_pdf or "",
            "folio_pedido": self.folio_pedido or "",
            "fecha": self.fecha or "",
            "dia": int(self.dia or 1),
            "mes": self.mes or "OCTUBRE",
            "ano": int(self.ano or 2026),
            "clave": self.clave,
            "descripcion": self.descripcion or "",
            "cantidad": float(self.cantidad or 0.0),
            "lote_asignado": self.lote_asignado or "",
            "fecha_caducidad": self.fecha_caducidad or "",
            "cliente_destino": self.cliente_destino or "",
            "estado_validacion": self.estado_validacion or "VALIDADO",
            "observaciones": self.observaciones or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class ApoyoInstitucionalMov(Base):
    __tablename__ = "apoyo_institucional_movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(100), index=True, nullable=False)
    lote = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    cantidad = Column(Float, default=0.0)
    institucion = Column(String(200), index=True, nullable=False)
    fecha = Column(String(50), nullable=False)
    dia = Column(Integer, index=True, nullable=True)
    mes = Column(String(30), default="OCTUBRE", nullable=True)
    ano = Column(Integer, default=2026, nullable=True)
    folio_documento = Column(String(100), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "clave": self.clave,
            "lote": self.lote,
            "descripcion": self.descripcion or "",
            "cantidad": float(self.cantidad or 0.0),
            "institucion": self.institucion,
            "fecha": self.fecha,
            "dia": int(self.dia or 1),
            "mes": self.mes or "OCTUBRE",
            "ano": int(self.ano or 2026),
            "folio_documento": self.folio_documento or "",
            "observaciones": self.observaciones or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

db = DatabaseManager()
Base.metadata.create_all(db.engine)
print("Tables created successfully!")
