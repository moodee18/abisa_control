import datetime
import hashlib
import hmac
import secrets
import re
from typing import List, Dict, Any, Optional, Tuple
import json
import io
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index, func, or_, and_, desc
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
    hoja_origen = Column(String(100), nullable=True) # Hoja de cálculo de origen (ej. 'Existencias_x_Localidad')
    
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
            "hoja_origen": self.hoja_origen or "",
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
    ano = Column(Integer, default=2026, nullable=True)
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
            "ano": int(self.ano or 2026),
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

# =========================================================================
# MODELOS: SISTEMA PROPUESTO - CONTROL DE INVENTARIO POR MOVIMIENTOS
# =========================================================================

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

    def to_dict(self) -> Dict[str, Any]:
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

    def to_dict(self) -> Dict[str, Any]:
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

    def to_dict(self) -> Dict[str, Any]:
        val = self.clave_unidad or ""
        return {
            "id": self.id,
            "clave_unidad": val,
            "codigo": val,
            "descripcion": self.descripcion or val,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class EntradaMov(Base):
    __tablename__ = "entradas_movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Columnas A:D: Datos administrativos
    folio_documento = Column(String(100), index=True, nullable=True)
    procedimiento = Column(String(150), nullable=True)
    contrato = Column(String(150), nullable=True)
    registro_sanitario = Column(String(150), nullable=True)
    almacen = Column(String(150), default="CS ALMACEN 2022")

    # Proveedor
    proveedor = Column(String(200), nullable=True)

    # Clave y Lote
    clave = Column(String(100), index=True, nullable=False)
    lote = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    unidad_medida = Column(String(50), default="PZA")

    # Fechas
    fecha_ajuste = Column(String(50), nullable=True)
    fecha_entrada = Column(String(50), nullable=True)
    fecha_fabricacion = Column(String(50), nullable=True)
    fecha_caducidad = Column(String(50), nullable=True)

    # Inventario y cantidades
    inventario_inicial = Column(Float, default=0.0)
    entrada_ajuste = Column(Float, default=0.0)
    cantidad_recibida = Column(Float, default=0.0)

    # Detalle por fila para preservar exactamente el Excel importado
    row_index = Column(Integer, default=0, nullable=True)
    dias_salidas = Column(Text, default="{}", nullable=True)
    apoyo_institucional = Column(Float, default=0.0, nullable=True)
    fecha_apoyo = Column(String(50), nullable=True)

    # Periodo
    mes = Column(String(30), default="OCTUBRE", nullable=True)
    ano = Column(Integer, default=2026, nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        inv_ini = float(self.inventario_inicial or 0.0)
        ajuste = float(self.entrada_ajuste or 0.0)
        recibida = float(self.cantidad_recibida or 0.0)
        dias_dict = {str(d): 0.0 for d in range(1, 32)}
        if self.dias_salidas:
            try:
                parsed = json.loads(self.dias_salidas)
                if isinstance(parsed, dict):
                    for dk, dv in parsed.items():
                        d_key = str(int(dk)) if str(dk).isdigit() else str(dk)
                        if d_key in dias_dict:
                            dias_dict[d_key] = float(dv or 0.0)
            except Exception:
                pass
        total_dias = sum(dias_dict.values())
        apoyo_val = float(self.apoyo_institucional or 0.0)
        return {
            "id": self.id,
            "row_index": self.row_index or 0,
            "orden_suministro": self.folio_documento or "",
            "folio_documento": self.folio_documento or "",
            "folio_administrativo": self.folio_documento or "",
            "procedimiento": self.procedimiento or "",
            "no_procedimiento": self.procedimiento or "",
            "contrato": self.contrato or "",
            "no_contrato": self.contrato or "",
            "registro_sanitario": self.registro_sanitario or "",
            "almacen": self.almacen or "CS ALMACEN 2022",
            "proveedor": self.proveedor or "",
            "clave": self.clave,
            "lote": self.lote,
            "descripcion": self.descripcion or "",
            "unidad_medida": self.unidad_medida or "PZA",
            "fecha_ajuste": self.fecha_ajuste or "",
            "fecha_entrada": self.fecha_entrada or "",
            "fecha_fabricacion": self.fecha_fabricacion or "",
            "fecha_caducidad": self.fecha_caducidad or "",
            "inventario_inicial": inv_ini,
            "entrada_ajuste": ajuste,
            "entrada_por_ajuste": ajuste,
            "cantidad_recibida": recibida,
            "inventario_total_mensual": inv_ini + ajuste + recibida,
            "dias": dias_dict,
            "total_dias_salidas": total_dias,
            "apoyo_institucional": apoyo_val,
            "fecha_apoyo": self.fecha_apoyo or "",
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
    estado_validacion = Column(String(50), default="VALIDADO") # 'VALIDADO', 'FEFO_OPTIMO', 'AVISO_FEFO', 'ASIGNADO_FEFO'
    aviso_fefo = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "archivo_pdf": self.archivo_pdf or "",
            "archivo_fuente": self.archivo_pdf or "",
            "folio_pedido": self.folio_pedido or "",
            "pedido_folio": self.folio_pedido or "",
            "fecha": self.fecha or "",
            "fecha_salida": self.fecha or "",
            "dia": int(self.dia or 1),
            "dia_mes": int(self.dia or 1),
            "mes": self.mes or "OCTUBRE",
            "ano": int(self.ano or 2026),
            "clave": self.clave,
            "descripcion": self.descripcion or "",
            "cantidad": float(self.cantidad or 0.0),
            "lote_asignado": self.lote_asignado or "",
            "fecha_caducidad": self.fecha_caducidad or "",
            "fecha_caducidad_lote": self.fecha_caducidad or "",
            "cliente_destino": self.cliente_destino or "",
            "estado_validacion": self.estado_validacion or "VALIDADO",
            "aviso_fefo": self.aviso_fefo or "",
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

    def to_dict(self) -> Dict[str, Any]:
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

# =========================================================================
# MODELOS Y ESQUEMA DE PERMISOS: GESTIÓN DE USUARIOS Y AUTENTICACIÓN
# =========================================================================

ALL_PERMISSIONS_CATALOG = [
    {"key": "ver_catalogo", "label": "Ver Catálogo de Claves", "group": "Inventario, Catálogo y Marbetes"},
    {"key": "ver_inventario", "label": "Ver Inventario por Lotes", "group": "Inventario, Catálogo y Marbetes"},
    {"key": "marbetes", "label": "Marbetes (Crear, Vaciar Cola, Actualizar, PDF e Imprimir)", "group": "Inventario, Catálogo y Marbetes"},
    {"key": "vaciar_inventario", "label": "Vaciar Inventario y Catálogo General", "group": "Inventario, Catálogo y Marbetes"},
    {"key": "actualizar_inventario", "label": "Actualizar Inventario (Sincronizar SIIA / Subir Excel Existencias)", "group": "Inventario, Catálogo y Marbetes"},
    {"key": "editar_inventario", "label": "Agregar, Editar y Eliminar Insumos Individuales", "group": "Inventario, Catálogo y Marbetes"},
    {"key": "exportar_inventario", "label": "Exportar Catálogo e Inventario a Excel", "group": "Inventario, Catálogo y Marbetes"},
    {"key": "ver_movimientos", "label": "Ver Entradas y Salidas (SIIA)", "group": "Entradas, Salidas y Matriz CLUES"},
    {"key": "gestionar_movimientos", "label": "Sincronizar, Subir Excel/PDF, Exportar y Vaciar Entradas/Salidas", "group": "Entradas, Salidas y Matriz CLUES"},
    {"key": "ver_matriz_clues", "label": "Ver y Exportar Matriz Oficial CLUES", "group": "Entradas, Salidas y Matriz CLUES"},
    {"key": "ver_control_movimientos", "label": "Ver Control por Movimientos (Reporte Diario)", "group": "Control por Movimientos"},
    {"key": "gestionar_control_movimientos", "label": "Capturar Entradas, Subir Salidas PDF, Apoyos, Catálogos, Base Excel y Vaciar Control", "group": "Control por Movimientos"},
    {"key": "carga_archivos", "label": "Pestaña Carga de Archivos General", "group": "Sistema y Administración"},
    {"key": "ver_auditoria", "label": "Ver Historial de Auditoría (Logs)", "group": "Sistema y Administración"},
    {"key": "vaciar_sistema_total", "label": "Vaciado Total del Sistema (Reinicio Completo)", "group": "Sistema y Administración"},
    {"key": "gestionar_usuarios", "label": "Crear Usuarios y Asignar Permisos", "group": "Sistema y Administración"},
]

ALL_PERMISSION_KEYS = [p["key"] for p in ALL_PERMISSIONS_CATALOG]

ROLE_PRESETS: Dict[str, Dict[str, bool]] = {
    "superadmin": {k: True for k in ALL_PERMISSION_KEYS},
    "operador": {
        k: (k in {
            "ver_catalogo",
            "ver_inventario",
            "marbetes",
            "vaciar_inventario",
            "actualizar_inventario",
        })
        for k in ALL_PERMISSION_KEYS
    },
    "capturista_control": {
        k: (k in {
            "ver_catalogo",
            "ver_inventario",
            "ver_control_movimientos",
            "gestionar_control_movimientos",
        })
        for k in ALL_PERMISSION_KEYS
    },
    "consulta": {
        k: (k in {"ver_catalogo", "ver_inventario"})
        for k in ALL_PERMISSION_KEYS
    },
}


def hash_password(password: str) -> str:
    """Genera hash criptográfico PBKDF2-HMAC-SHA256 con sal aleatoria."""
    salt = secrets.token_hex(16)
    iterations = 200_000
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${dk}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica de forma segura en tiempo constante una contraseña contra su hash."""
    if not password or not stored_hash:
        return False
    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_dk = parts[3]
        computed_dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            iterations,
        ).hex()
        return hmac.compare_digest(computed_dk, expected_dk)
    except Exception:
        return False


class UserAccount(Base):
    __tablename__ = "usuarios_sistema"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), default="personalizado", nullable=False)
    is_superadmin = Column(Boolean, default=False, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    permisos_json = Column(Text, default="{}", nullable=False)
    ultimo_acceso = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def get_effective_permissions(self) -> Dict[str, bool]:
        if self.is_superadmin or self.rol == "superadmin":
            return {k: True for k in ALL_PERMISSION_KEYS}
        try:
            raw = json.loads(self.permisos_json or "{}")
            if not isinstance(raw, dict):
                raw = {}
        except Exception:
            raw = {}
        return {k: bool(raw.get(k, False)) for k in ALL_PERMISSION_KEYS}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "nombre_completo": self.nombre_completo or self.username,
            "rol": "superadmin" if self.is_superadmin else (self.rol or "personalizado"),
            "is_superadmin": bool(self.is_superadmin),
            "activo": bool(self.activo),
            "permisos": self.get_effective_permissions(),
            "ultimo_acceso": self.ultimo_acceso.strftime("%Y-%m-%d %H:%M:%S") if self.ultimo_acceso else "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }


class UserSession(Base):
    __tablename__ = "sesiones_usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    ip_address = Column(String(80), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


def normalize_caducidad(cad_str: Optional[str]) -> str:
    """Normaliza cualquier cadena de fecha de caducidad a YYYY-MM-DD para comparación cronológica."""
    if not cad_str:
        return "9999-12-31"
    s = str(cad_str).strip()
    if not s or s.lower() in ["none", "nan", "null", "s/f", "sin fecha", "sin caducidad", "-", "--", "---", "s/c", "n/a", "na", ""]:
        return "9999-12-31"

    # 1. YYYY-MM-DD o YYYY/MM/DD
    m = re.match(r'^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    # 2. DD-MM-YYYY o DD/MM/YYYY
    m = re.match(r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', s)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"

    # 3. YYYY-MM o YYYY/MM (fin de mes farmacéutico)
    m = re.match(r'^(\d{4})[-/.](\d{1,2})$', s)
    if m:
        yr, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            import calendar
            last_day = calendar.monthrange(yr, mo)[1]
            return f"{yr:04d}-{mo:02d}-{last_day:02d}"
        return f"{yr:04d}-{mo:02d}-01"

    # 4. MM-YYYY o MM/YYYY (fin de mes farmacéutico)
    m = re.match(r'^(\d{1,2})[-/.](\d{4})$', s)
    if m:
        mo, yr = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            import calendar
            last_day = calendar.monthrange(yr, mo)[1]
            return f"{yr:04d}-{mo:02d}-{last_day:02d}"
        return f"{yr:04d}-{mo:02d}-01"

    return s


def normalize_fecha_referencia(fecha_str: Optional[str], fallback: Optional[str] = None) -> str:
    """Normaliza una fecha de movimiento (YYYY-MM-DD HH:MM:SS, DD/MM/YYYY, etc.) a YYYY-MM-DD."""
    default_dt = fallback or datetime.date.today().strftime("%Y-%m-%d")
    if not fecha_str:
        return default_dt
    s = str(fecha_str).strip()
    if not s:
        return default_dt
    m1 = re.match(r'^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', s)
    if m1:
        return f"{int(m1.group(1)):04d}-{int(m1.group(2)):02d}-{int(m1.group(3)):02d}"
    m2 = re.match(r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', s)
    if m2:
        return f"{int(m2.group(3)):04d}-{int(m2.group(2)):02d}-{int(m2.group(1)):02d}"
    return default_dt


def is_caducidad_vencida(cad_norm: Optional[str], fecha_ref_norm: Optional[str] = None) -> bool:
    """
    Determina si una caducidad normalizada (YYYY-MM-DD) ya está vencida respecto a la fecha
    del movimiento o a la fecha actual (lo que sea mayor). Si no tiene fecha ('9999-12-31'), devuelve False.
    """
    if not cad_norm or cad_norm == "9999-12-31":
        return False
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', cad_norm):
        return False
    today_norm = datetime.date.today().strftime("%Y-%m-%d")
    cutoff = max(fecha_ref_norm, today_norm) if (fecha_ref_norm and re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_ref_norm)) else today_norm
    return cad_norm < cutoff

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
            ("hoja_origen", "VARCHAR(100)"),
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
                try:
                    conn.exec_driver_sql("ALTER TABLE movimientos_entradas_salidas ADD COLUMN ano INTEGER DEFAULT 2026")
                except Exception:
                    pass
                for col, col_type in [
                    ("row_index", "INTEGER DEFAULT 0"),
                    ("dias_salidas", "TEXT DEFAULT '{}'"),
                    ("apoyo_institucional", "FLOAT DEFAULT 0.0"),
                    ("fecha_apoyo", "VARCHAR(50)"),
                    ("fecha_ajuste", "VARCHAR(50)")
                ]:
                    try:
                        conn.exec_driver_sql(f"ALTER TABLE entradas_movimientos ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            self.seed_control_movimientos_defaults()
        except Exception as e:
            print(f"[DB WARN] Error al inicializar defaults de control de movimientos: {e}")

        try:
            self.seed_default_users()
        except Exception as e:
            print(f"[DB WARN] Error al inicializar usuarios por defecto: {e}")

        try:
            self.refresh_fefo_salidas_existentes()
        except Exception as e:
            print(f"[DB WARN] Error al actualizar validaciones FEFO: {e}")

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

                hoja_origen = parse_str(row_dict.get("hoja_origen"))
                if not hoja_origen:
                    if clave_abi or parse_str(row_dict.get("existencia_real_piezas")) or "Ubicaci" in source_filename or "Existencia" in source_filename:
                        hoja_origen = "Existencias_x_Localidad"

                record = InsumoRecord(
                    report_source=source_filename,
                    hoja_origen=hoja_origen,
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
                
                fecha_val = parse_str(
                    row_dict.get("fecha") or
                    row_dict.get("fecha_de_documento") or
                    row_dict.get("fecha_documento") or
                    row_dict.get("fecha_de_captura") or
                    row_dict.get("fecha_captura") or
                    row_dict.get("fecha_surtido")
                )
                
                doc = parse_str(row_dict.get("documento") or row_dict.get("pedido") or row_dict.get("no_pedido"))
                import re
                clean_doc = re.sub(r'^[Nn]-', '', doc) if doc else ""

                MESES_ESP = {
                    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
                    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
                    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
                }

                today_d = datetime.date.today()
                dia = None
                mes = MESES_ESP.get(today_d.month, "SEPTIEMBRE")
                ano = today_d.year

                fecha_ref = fecha_val or parse_str(row_dict.get("fecha_documento") or row_dict.get("fecha_surtido"))
                if fecha_ref:
                    m_ymd = re.search(r'\b(20[2-3][0-9])-([0-1][0-9])-([0-3][0-9])\b', fecha_ref)
                    if m_ymd:
                        ano = int(m_ymd.group(1))
                        m_num = int(m_ymd.group(2))
                        mes = MESES_ESP.get(m_num, mes)
                        dia = int(m_ymd.group(3))
                    else:
                        m_dmy = re.search(r'\b([0-3]?[0-9])[-/]([0-1]?[0-9])[-/](20[2-3][0-9])\b', fecha_ref)
                        if m_dmy:
                            dia = int(m_dmy.group(1))
                            m_num = int(m_dmy.group(2))
                            mes = MESES_ESP.get(m_num, mes)
                            ano = int(m_dmy.group(3))

                if dia is None:
                    if "dia" in row_dict and row_dict["dia"] is not None and not pd.isna(row_dict["dia"]):
                        try:
                            dia = int(row_dict["dia"])
                        except Exception:
                            pass
                if dia is None:
                    dia = today_d.day

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
                    mes=mes,
                    ano=ano,
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

    def get_clues_matrix(self, search: Optional[str] = None, mes: Optional[str] = None, ano: Optional[int] = None, dia_inicio: int = 1, dia_fin: Optional[int] = None) -> Dict[str, Any]:
        """
        Genera la matriz oficial de CLUES para un mes y año seleccionados:
        - Encabezado: CLUES ('CSIMB003506'), CLAVE, INVENTARIO DISPONIBLE, LOTE, F_CAD, días 1..N
        - Base: InsumoRecord agrupado por (clave, lote, caducidad), unificando existencias.
        - Salidas: MovimientoRecord (tipo='SALIDA', filtrado por el mes y año solicitado).
        - Si una salida (clave, lote, caducidad) no está en el inventario, se incorpora con INVENTARIO DISPONIBLE = 0.
        """
        import calendar
        MESES_NUM = {
            "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
            "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
        }
        today = datetime.date.today()
        target_ano = int(ano) if ano else today.year

        MESES_ESP = {v: k for k, v in MESES_NUM.items()}
        if not mes:
            target_mes = MESES_ESP.get(today.month, "SEPTIEMBRE")
        else:
            target_mes = mes.strip().upper()

        m_num = MESES_NUM.get(target_mes, today.month)
        max_dias_mes = calendar.monthrange(target_ano, m_num)[1]

        end_day = int(dia_fin) if (dia_fin is not None and int(dia_fin) > 0) else max_dias_mes
        start_day = int(dia_inicio) if dia_inicio else 1
        days_list = list(range(start_day, end_day + 1))

        session = self.get_session()
        try:
            # FILTRO ESTRICTO OFICIAL: En la Matriz Oficial CLUES solamente deben aparecer los insumos
            # que provienen de la hoja 'Existencias_x_Localidad'
            inv_records = session.query(
                func.coalesce(InsumoRecord.clave_cliente, InsumoRecord.clave).label("cve"),
                InsumoRecord.lote,
                InsumoRecord.caducidad,
                func.max(InsumoRecord.descripcion).label("desc"),
                func.sum(InsumoRecord.cantidad).label("stock")
            ).filter(
                InsumoRecord.clave.isnot(None), 
                InsumoRecord.clave != "",
                or_(
                    InsumoRecord.hoja_origen == "Existencias_x_Localidad",
                    and_(
                        InsumoRecord.hoja_origen.is_(None),
                        InsumoRecord.report_source.notlike("%test_%"),
                        or_(
                            InsumoRecord.clave_abisa.isnot(None),
                            InsumoRecord.report_source.like("%Ubicaci%"),
                            InsumoRecord.report_source.like("%Existencia%")
                        )
                    )
                )
            ).group_by(
                func.coalesce(InsumoRecord.clave_cliente, InsumoRecord.clave),
                InsumoRecord.lote,
                InsumoRecord.caducidad
            ).all()

            # Catálogo para resolver descripciones oficiales garantizadas
            desc_map = {}
            for row_desc in session.query(InsumoRecord.clave, InsumoRecord.descripcion).filter(
                InsumoRecord.descripcion.isnot(None), 
                InsumoRecord.descripcion != "",
                or_(
                    InsumoRecord.hoja_origen == "Existencias_x_Localidad",
                    and_(
                        InsumoRecord.hoja_origen.is_(None),
                        InsumoRecord.report_source.notlike("%test_%")
                    )
                )
            ).all():
                c_clean = (row_desc.clave or "").strip()
                if c_clean and c_clean not in desc_map:
                    desc_map[c_clean] = row_desc.descripcion.strip()

            # REGLA OFICIAL CLUES:
            # 1. Solo claves numéricas del Sector Salud
            # 2. Insumos caducados no se agregan como disponible
            clues_clave_pattern = re.compile(r'^\d{3}\.\d{3}\.\d{3,5}(\.\d{2})?$')
            today_str = datetime.date.today().strftime('%Y-%m-%d')

            matrix_dict = {}

            for r in inv_records:
                cve = (r.cve or "").strip()
                if not clues_clave_pattern.match(cve):
                    continue

                lote = (r.lote or "").strip()
                cad = (r.caducidad or "").strip()

                if cad and cad[:10] < today_str:
                    continue

                stock_val = round(float(r.stock or 0.0), 2)
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

            # Consultar salidas: SOLAMENTE PEDIDOS hacia CS FARMACIA MAT 2022 del MES SOLICITADO
            salidas = session.query(
                func.coalesce(MovimientoRecord.clave_cliente, MovimientoRecord.clave).label("cve"),
                MovimientoRecord.lote,
                MovimientoRecord.caducidad,
                MovimientoRecord.dia,
                MovimientoRecord.mes,
                MovimientoRecord.tipo_movimiento,
                MovimientoRecord.referencia,
                MovimientoRecord.documento,
                MovimientoRecord.cliente,
                func.max(MovimientoRecord.descripcion).label("desc"),
                func.sum(MovimientoRecord.cantidad).label("cant_salida")
            ).filter(
                MovimientoRecord.tipo == 'SALIDA',
                MovimientoRecord.tipo_movimiento == 'PEDIDO',
                or_(
                    MovimientoRecord.mes == target_mes,
                    MovimientoRecord.fecha.like(f"{target_ano}-{m_num:02d}%"),
                    MovimientoRecord.fecha.like(f"%/{m_num:02d}/{target_ano}%")
                )
            ).group_by(
                func.coalesce(MovimientoRecord.clave_cliente, MovimientoRecord.clave),
                MovimientoRecord.lote,
                MovimientoRecord.caducidad,
                MovimientoRecord.dia,
                MovimientoRecord.mes,
                MovimientoRecord.tipo_movimiento,
                MovimientoRecord.referencia,
                MovimientoRecord.documento,
                MovimientoRecord.cliente
            ).all()

            for s in salidas:
                doc = (s.documento or "").strip()
                if doc.startswith("AJ_"):
                    continue

                ref = (s.referencia or "").strip().upper()
                cli = (s.cliente or "").strip().upper()
                if ("CS FARMACIA" not in ref) and ("CS FARMACIA" not in cli):
                    continue

                cve = (s.cve or "").strip()
                if not clues_clave_pattern.match(cve):
                    continue

                lote = (s.lote or "").strip()
                cad = (s.caducidad or "").strip()

                dia = s.dia
                # REGLA OFICIAL SEPTIEMBRE: Por única ocasión, lo que salió el 15 se pasa al día 14
                if target_mes == "SEPTIEMBRE" and dia == 15:
                    dia = 14

                cant = float(s.cant_salida or 0.0)
                key = (cve, lote, cad)
                desc = (s.desc or "").strip() or desc_map.get(cve, "")

                # REGLA ESTRICTA DE LA MATRIZ CLUES:
                # SOLAMENTE deben aparecer insumos que existan en la hoja Existencias_x_Localidad.
                # Si una salida no existe en Existencias_x_Localidad, NUNCA se agrega a la matriz.
                target_entry = matrix_dict.get(key)
                if not target_entry and cad:
                    # Intento de emparejar por fecha corta YYYY-MM-DD
                    cad_prefix = cad[:10]
                    for k, v in matrix_dict.items():
                        if k[0] == cve and k[1] == lote and k[2][:10] == cad_prefix:
                            target_entry = v
                            break
                if not target_entry:
                    # Intento de emparejar solo por clave y lote si es coincidencia única
                    matches = [v for k, v in matrix_dict.items() if k[0] == cve and k[1] == lote]
                    if len(matches) == 1:
                        target_entry = matches[0]

                if target_entry:
                    if not target_entry["descripcion"] and desc:
                        target_entry["descripcion"] = desc

                    if dia and str(dia) in target_entry["dias"]:
                        target_entry["dias"][str(dia)] += cant
                        target_entry["total_salidas"] += cant

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

            # Obtener lista de meses que tienen salidas registradas
            meses_salidas = [m[0] for m in session.query(MovimientoRecord.mes).filter(
                MovimientoRecord.tipo == 'SALIDA',
                MovimientoRecord.mes.isnot(None),
                MovimientoRecord.mes != ""
            ).distinct().all()]

            available_months = sorted(
                list(set(meses_salidas)),
                key=lambda x: MESES_NUM.get(x.upper(), 99)
            )
            if not available_months:
                available_months = ["SEPTIEMBRE"]

            return {
                "days": days_list,
                "dia_actual": start_day,
                "dia_inicio": start_day,
                "dia_fin": end_day,
                "mes": target_mes,
                "ano": target_ano,
                "rows": rows,
                "total_rows": len(rows),
                "totales_por_dia": totales_por_dia,
                "available_months": available_months,
                "kpis": {
                    "total_insumos": len(rows),
                    "total_stock_disponible": round(total_stock_disponible, 2),
                    "total_salidas_periodo": round(total_salidas_periodo, 2),
                    "mes": target_mes,
                    "ano": target_ano,
                    "dia_inicio": start_day,
                    "dia_fin": end_day
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

    # =========================================================================
    # SISTEMA PROPUESTO: CONTROL DE INVENTARIO POR MOVIMIENTOS
    # =========================================================================

    def seed_control_movimientos_defaults(self):
        """Inicializa catálogos predeterminados de unidades, proveedores, claves y existencias iniciales."""
        session = self.get_session()
        try:
            # 1. Unidades de Medida
            if session.query(UnidadMedidaMov).count() == 0:
                unidades = ["ENVASE", "PIEZA", "PAR"]
                for u in unidades:
                    session.add(UnidadMedidaMov(clave_unidad=u, descripcion=u))
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

            # 3. Catálogo de Claves y Descripciones
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

            # 4. Entradas iniciales (Octubre 2026) si la tabla está vacía
            if session.query(EntradaMov).count() == 0:
                ins = session.query(InsumoRecord).filter(
                    InsumoRecord.clave.isnot(None), InsumoRecord.lote.isnot(None)
                ).limit(150).all()
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
                        fecha_entrada=item.fecha_documento or "",
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
            print(f"[ERROR SEED MOVIMIENTOS]: {e}")
        finally:
            session.close()

    # --- CATÁLOGOS ---
    def get_catalogo_movimientos(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            q = session.query(CatalogoInsumoMov)
            if search:
                term = f"%{search.strip().lower()}%"
                q = q.filter(
                    or_(
                        func.lower(CatalogoInsumoMov.clave).like(term),
                        func.lower(CatalogoInsumoMov.descripcion).like(term),
                        func.lower(CatalogoInsumoMov.proveedor_predeterminado).like(term),
                        func.lower(CatalogoInsumoMov.procedimiento).like(term)
                    )
                )
            items = q.order_by(CatalogoInsumoMov.clave.asc()).all()
            return [it.to_dict() for it in items]
        finally:
            session.close()

    def create_catalogo_insumo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        session = self.get_session()
        try:
            clave = str(data.get("clave", "")).strip()
            if not clave:
                raise ValueError("La clave del insumo es obligatoria.")
            exist = session.query(CatalogoInsumoMov).filter_by(clave=clave).first()
            if exist:
                exist.descripcion = data.get("descripcion", exist.descripcion)
                exist.unidad_medida = data.get("unidad_medida", exist.unidad_medida)
                exist.proveedor_predeterminado = data.get("proveedor_predeterminado", exist.proveedor_predeterminado)
                exist.procedimiento = data.get("procedimiento", exist.procedimiento)
                exist.contrato = data.get("contrato", exist.contrato)
                exist.registro_sanitario = data.get("registro_sanitario", exist.registro_sanitario)
                session.commit()
                return exist.to_dict()
            new_item = CatalogoInsumoMov(
                clave=clave,
                descripcion=data.get("descripcion", ""),
                unidad_medida=data.get("unidad_medida", "PZA"),
                proveedor_predeterminado=data.get("proveedor_predeterminado", ""),
                procedimiento=data.get("procedimiento", ""),
                contrato=data.get("contrato", ""),
                registro_sanitario=data.get("registro_sanitario", "")
            )
            session.add(new_item)
            session.commit()
            return new_item.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_catalogo_insumo(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.get_session()
        try:
            item = session.query(CatalogoInsumoMov).filter_by(id=item_id).first()
            if not item:
                return None
            for field in ["clave", "descripcion", "unidad_medida", "proveedor_predeterminado", "procedimiento", "contrato", "registro_sanitario"]:
                if field in data:
                    setattr(item, field, data[field])
            session.commit()
            return item.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_catalogo_insumo(self, item_id: int) -> bool:
        session = self.get_session()
        try:
            item = session.query(CatalogoInsumoMov).filter_by(id=item_id).first()
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def sync_catalogo_from_insumos(self) -> int:
        session = self.get_session()
        try:
            existing_claves = set(c[0] for c in session.query(CatalogoInsumoMov.clave).all())
            distinct_insumos = session.query(
                InsumoRecord.clave,
                func.max(InsumoRecord.descripcion).label("desc"),
                func.max(InsumoRecord.unidad_medida).label("udm"),
                func.max(InsumoRecord.proveedor).label("prov"),
                func.max(InsumoRecord.no_procedimiento).label("proc")
            ).filter(InsumoRecord.clave.isnot(None), InsumoRecord.clave != '').group_by(InsumoRecord.clave).all()

            added = 0
            for row in distinct_insumos:
                cve = row.clave.strip()
                if cve and cve not in existing_claves:
                    session.add(CatalogoInsumoMov(
                        clave=cve,
                        descripcion=row.desc or "Sin descripción",
                        unidad_medida=row.udm or "PZA",
                        proveedor_predeterminado=row.prov or "",
                        procedimiento=row.proc or ""
                    ))
                    existing_claves.add(cve)
                    added += 1
            session.commit()
            return added
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_proveedores_movimientos(self) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            items = session.query(ProveedorMov).order_by(ProveedorMov.nombre.asc()).all()
            return [it.to_dict() for it in items]
        finally:
            session.close()

    def create_proveedor_mov(self, data: Dict[str, Any]) -> Dict[str, Any]:
        session = self.get_session()
        try:
            nombre = str(data.get("nombre", "")).strip()
            if not nombre:
                raise ValueError("El nombre del proveedor es obligatorio.")
            exist = session.query(ProveedorMov).filter_by(nombre=nombre).first()
            if exist:
                return exist.to_dict()
            new_p = ProveedorMov(
                nombre=nombre,
                rfc=data.get("rfc", ""),
                contacto=data.get("contacto", "")
            )
            session.add(new_p)
            session.commit()
            return new_p.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_proveedor_mov(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.get_session()
        try:
            item = session.query(ProveedorMov).filter_by(id=item_id).first()
            if not item:
                return None
            if "nombre" in data:
                nombre = str(data.get("nombre") or "").strip()
                if not nombre:
                    raise ValueError("El nombre del proveedor es obligatorio.")
                dup = session.query(ProveedorMov).filter(
                    func.lower(ProveedorMov.nombre) == nombre.lower(),
                    ProveedorMov.id != item_id
                ).first()
                if dup:
                    raise ValueError(f"Ya existe otro proveedor con el nombre '{nombre}'.")
                item.nombre = nombre
            if "rfc" in data:
                item.rfc = str(data.get("rfc") or "").strip()
            if "contacto" in data:
                item.contacto = str(data.get("contacto") or "").strip()
            session.commit()
            return item.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_proveedor_mov(self, item_id: int) -> bool:
        session = self.get_session()
        try:
            item = session.query(ProveedorMov).filter_by(id=item_id).first()
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_unidades_medida_movimientos(self) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            items = session.query(UnidadMedidaMov).order_by(UnidadMedidaMov.clave_unidad.asc()).all()
            return [it.to_dict() for it in items]
        finally:
            session.close()

    def create_unidad_medida_mov(self, data: Dict[str, Any]) -> Dict[str, Any]:
        session = self.get_session()
        try:
            clave_u = str(data.get("clave_unidad") or data.get("codigo") or "").strip().upper()
            if not clave_u:
                raise ValueError("La clave de la unidad es obligatoria.")
            exist = session.query(UnidadMedidaMov).filter_by(clave_unidad=clave_u).first()
            if exist:
                return exist.to_dict()
            new_u = UnidadMedidaMov(
                clave_unidad=clave_u,
                descripcion=data.get("descripcion", f"Unidad {clave_u}")
            )
            session.add(new_u)
            session.commit()
            return new_u.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_unidad_medida_mov(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.get_session()
        try:
            item = session.query(UnidadMedidaMov).filter_by(id=item_id).first()
            if not item:
                return None
            if "clave_unidad" in data or "codigo" in data:
                clave_u = str(data.get("clave_unidad") if "clave_unidad" in data else data.get("codigo") or "").strip().upper()
                if not clave_u:
                    raise ValueError("La clave de la unidad es obligatoria.")
                dup = session.query(UnidadMedidaMov).filter(
                    func.upper(UnidadMedidaMov.clave_unidad) == clave_u,
                    UnidadMedidaMov.id != item_id
                ).first()
                if dup:
                    raise ValueError(f"Ya existe otra unidad de medida con la clave '{clave_u}'.")
                item.clave_unidad = clave_u
            if "descripcion" in data:
                item.descripcion = str(data.get("descripcion") or "").strip()
            session.commit()
            return item.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_unidad_medida_mov(self, item_id: int) -> bool:
        session = self.get_session()
        try:
            item = session.query(UnidadMedidaMov).filter_by(id=item_id).first()
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # --- ENTRADAS MANUALES ---
    def get_entradas_movimientos(
        self,
        mes: Optional[str] = None,
        ano: Optional[int] = None,
        search: Optional[str] = None,
        only_ingresos: bool = False
    ) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            q = session.query(EntradaMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(EntradaMov.mes == mes.upper())
            if ano and (not mes or mes.upper() != "TODOS"):
                q = q.filter(EntradaMov.ano == ano)
            if only_ingresos:
                # Sólo lo que realmente entró con fecha de entrada o ajuste registrada en el sistema
                q = q.filter(
                    or_(
                        and_(EntradaMov.fecha_entrada != None, EntradaMov.fecha_entrada != ""),
                        and_(EntradaMov.fecha_ajuste != None, EntradaMov.fecha_ajuste != ""),
                        EntradaMov.cantidad_recibida > 0,
                        EntradaMov.entrada_ajuste > 0
                    )
                )
            if search:
                raw_s = search.strip()
                term = f"%{raw_s.lower()}%"
                filters = [
                    func.lower(EntradaMov.clave).like(term),
                    func.lower(EntradaMov.lote).like(term),
                    func.lower(EntradaMov.descripcion).like(term),
                    func.lower(EntradaMov.proveedor).like(term),
                    func.lower(EntradaMov.folio_documento).like(term),
                    func.lower(EntradaMov.procedimiento).like(term),
                    func.lower(EntradaMov.contrato).like(term),
                    func.lower(EntradaMov.registro_sanitario).like(term),
                    func.lower(EntradaMov.fecha_caducidad).like(term),
                    func.lower(EntradaMov.fecha_fabricacion).like(term),
                    func.lower(EntradaMov.fecha_entrada).like(term),
                    func.lower(EntradaMov.fecha_ajuste).like(term),
                    func.lower(EntradaMov.fecha_apoyo).like(term),
                    func.lower(EntradaMov.unidad_medida).like(term),
                    func.lower(EntradaMov.almacen).like(term),
                    func.lower(EntradaMov.observaciones).like(term),
                ]
                if raw_s.isdigit():
                    num_val = int(raw_s)
                    filters.append(EntradaMov.id == num_val)
                    filters.append(EntradaMov.row_index == num_val)
                q = q.filter(or_(*filters))
            items = q.order_by(EntradaMov.id.desc()).all()
            return [it.to_dict() for it in items]
        finally:
            session.close()

    def create_entrada_mov(self, data: Dict[str, Any]) -> Dict[str, Any]:
        session = self.get_session()
        try:
            clave = str(data.get("clave", "")).strip()
            lote = str(data.get("lote", "")).strip()
            if not clave or not lote:
                raise ValueError("La Clave y el Lote son obligatorios.")

            # Autocompletar descripción si viene vacía
            descripcion = data.get("descripcion", "").strip()
            unidad_medida = data.get("unidad_medida", "PZA").strip()
            if not descripcion:
                cat = session.query(CatalogoInsumoMov).filter_by(clave=clave).first()
                if cat:
                    descripcion = cat.descripcion
                    if not unidad_medida and cat.unidad_medida:
                        unidad_medida = cat.unidad_medida
                else:
                    ins = session.query(InsumoRecord).filter_by(clave=clave).first()
                    if ins:
                        descripcion = ins.descripcion or ""
                        if not unidad_medida and ins.unidad_medida:
                            unidad_medida = ins.unidad_medida

            inv_ini = float(data.get("inventario_inicial", 0.0) or 0.0)
            ajuste = float(data.get("entrada_por_ajuste") if data.get("entrada_por_ajuste") is not None else (data.get("entrada_ajuste", 0.0) or 0.0))
            recibida = float(data.get("cantidad_recibida", 0.0) or 0.0)
            mes = str(data.get("mes", "OCTUBRE")).strip().upper()
            ano = int(data.get("ano", 2026))

            raw_orden = data.get("orden_suministro") or data.get("folio_documento") or data.get("folio_administrativo") or ""
            target_cad_raw = data.get("fecha_caducidad") or ""

            # Normalizador de Orden de Suministro para comparaciones robustas
            def _norm_os(val: Any) -> str:
                if val is None:
                    return ""
                s = str(val).strip().upper()
                if s in ("-", "--", "---", "NONE", "NULL", "S/O", "SIN ORDEN", ""):
                    return ""
                return s

            target_clave = clave.upper()
            target_lote = lote.upper()
            target_cad = normalize_caducidad(target_cad_raw)
            target_orden = _norm_os(raw_orden)

            # Buscar si ya existe coincidencia exacta por los 4 criterios (Clave, Lote, Caducidad, Orden)
            candidates = session.query(EntradaMov).filter(
                EntradaMov.mes == mes,
                EntradaMov.ano == ano,
                func.lower(func.trim(EntradaMov.clave)) == clave.lower()
            ).order_by(EntradaMov.row_index.asc(), EntradaMov.id.asc()).all()

            matched_entry = None
            for cand in candidates:
                cand_clave = str(cand.clave or "").strip().upper()
                if cand_clave != target_clave:
                    continue

                cand_lote = str(cand.lote or "").strip().upper()
                if cand_lote != target_lote:
                    continue

                cand_cad = normalize_caducidad(cand.fecha_caducidad)
                if cand_cad != target_cad:
                    continue

                cand_orden = _norm_os(cand.folio_documento)
                if cand_orden != target_orden:
                    continue

                # Coinciden exactamente los 4 criterios
                matched_entry = cand
                break

            apoyo_val = float(data.get("apoyo_institucional", 0.0) or 0.0)
            fecha_apoyo_val = str(data.get("fecha_apoyo", "") or "").strip()
            fecha_ajuste_val = str(data.get("fecha_ajuste", "") or "").strip()
            fecha_entrada_val = str(data.get("fecha_entrada") or "").strip()

            if matched_entry:
                # UNIFICAR: Acumular únicamente las cantidades numéricas, sin modificar metadatos existentes
                matched_entry.inventario_inicial = float(matched_entry.inventario_inicial or 0.0) + inv_ini
                matched_entry.entrada_ajuste = float(matched_entry.entrada_ajuste or 0.0) + ajuste
                matched_entry.cantidad_recibida = float(matched_entry.cantidad_recibida or 0.0) + recibida
                matched_entry.apoyo_institucional = float(matched_entry.apoyo_institucional or 0.0) + apoyo_val
                if fecha_apoyo_val and not matched_entry.fecha_apoyo:
                    matched_entry.fecha_apoyo = fecha_apoyo_val
                if fecha_ajuste_val and not matched_entry.fecha_ajuste:
                    matched_entry.fecha_ajuste = fecha_ajuste_val
                if fecha_entrada_val and not matched_entry.fecha_entrada:
                    matched_entry.fecha_entrada = fecha_entrada_val

                new_obs = str(data.get("observaciones") or "").strip()
                if new_obs:
                    if matched_entry.observaciones:
                        matched_entry.observaciones = f"{matched_entry.observaciones}; {new_obs}"
                    else:
                        matched_entry.observaciones = new_obs

                session.commit()
                res = matched_entry.to_dict()
                res["unified"] = True
                res["message"] = f"Entrada unificada con registro existente (Fila {matched_entry.row_index or matched_entry.id}): Misma Clave, Lote, Caducidad y Orden de Suministro."
                return res

            # Si NO coincide exactamente en los 4 criterios (ej. distinta orden, caducidad, lote):
            # Se agrega como una nueva fila independiente con su propio row_index
            max_idx = session.query(func.max(EntradaMov.row_index)).filter_by(mes=mes, ano=ano).scalar() or 0
            new_row_index = int(max_idx) + 1

            new_entrada = EntradaMov(
                folio_documento=str(raw_orden).strip() if raw_orden else "",
                procedimiento=data.get("procedimiento") or data.get("no_procedimiento", ""),
                contrato=data.get("contrato") or data.get("no_contrato", ""),
                registro_sanitario=data.get("registro_sanitario", ""),
                almacen=data.get("almacen", "CS ALMACEN 2022"),
                proveedor=data.get("proveedor", ""),
                clave=clave,
                lote=lote,
                descripcion=descripcion,
                unidad_medida=unidad_medida or "PZA",
                fecha_ajuste=fecha_ajuste_val,
                fecha_entrada=fecha_entrada_val,
                fecha_fabricacion=data.get("fecha_fabricacion", ""),
                fecha_caducidad=str(target_cad_raw).strip() if target_cad_raw else "",
                inventario_inicial=inv_ini,
                entrada_ajuste=ajuste,
                cantidad_recibida=recibida,
                row_index=new_row_index,
                dias_salidas="{}",
                apoyo_institucional=apoyo_val,
                fecha_apoyo=fecha_apoyo_val,
                mes=mes,
                ano=ano,
                observaciones=data.get("observaciones", "")
            )
            session.add(new_entrada)
            session.commit()
            res = new_entrada.to_dict()
            res["unified"] = False
            res["message"] = f"Nueva entrada registrada con éxito en fila independiente (Fila {new_row_index})."
            return res
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_entrada_mov(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.get_session()
        try:
            item = session.query(EntradaMov).filter_by(id=item_id).first()
            if not item:
                return None

            if "clave" in data:
                new_cve = str(data.get("clave") or "").strip()
                if not new_cve:
                    raise ValueError("La Clave no puede quedar vacía.")
                item.clave = new_cve

            if "lote" in data:
                new_lot = str(data.get("lote") or "").strip()
                if not new_lot:
                    raise ValueError("El Lote no puede quedar vacío.")
                item.lote = new_lot

            for field in [
                "registro_sanitario", "almacen", "proveedor", "descripcion",
                "unidad_medida", "fecha_ajuste", "fecha_entrada",
                "fecha_fabricacion", "fecha_caducidad", "observaciones"
            ]:
                if field in data and data[field] is not None:
                    setattr(item, field, str(data[field]).strip())

            # Orden de suministro / folio_documento (permite vaciar a "")
            if "orden_suministro" in data and data["orden_suministro"] is not None:
                item.folio_documento = str(data["orden_suministro"]).strip()
            elif "folio_documento" in data and data["folio_documento"] is not None:
                item.folio_documento = str(data["folio_documento"]).strip()
            elif "folio_administrativo" in data and data["folio_administrativo"] is not None:
                item.folio_documento = str(data["folio_administrativo"]).strip()

            # Procedimiento (permite vaciar a "")
            if "procedimiento" in data and data["procedimiento"] is not None:
                item.procedimiento = str(data["procedimiento"]).strip()
            elif "no_procedimiento" in data and data["no_procedimiento"] is not None:
                item.procedimiento = str(data["no_procedimiento"]).strip()

            # Contrato (permite vaciar a "")
            if "contrato" in data and data["contrato"] is not None:
                item.contrato = str(data["contrato"]).strip()
            elif "no_contrato" in data and data["no_contrato"] is not None:
                item.contrato = str(data["no_contrato"]).strip()

            if "mes" in data and data.get("mes"):
                item.mes = str(data["mes"]).strip().upper()
            if "ano" in data and data.get("ano") is not None:
                item.ano = int(data["ano"] or 2026)
            if "row_index" in data and data.get("row_index") is not None:
                item.row_index = int(data["row_index"])

            if "inventario_inicial" in data and data.get("inventario_inicial") is not None:
                item.inventario_inicial = float(data["inventario_inicial"] or 0.0)
            if "entrada_por_ajuste" in data and data.get("entrada_por_ajuste") is not None:
                item.entrada_ajuste = float(data["entrada_por_ajuste"] or 0.0)
            elif "entrada_ajuste" in data and data.get("entrada_ajuste") is not None:
                item.entrada_ajuste = float(data["entrada_ajuste"] or 0.0)
            if "cantidad_recibida" in data and data.get("cantidad_recibida") is not None:
                item.cantidad_recibida = float(data["cantidad_recibida"] or 0.0)
            if "apoyo_institucional" in data and data.get("apoyo_institucional") is not None:
                item.apoyo_institucional = float(data["apoyo_institucional"] or 0.0)
            if "fecha_apoyo" in data and data.get("fecha_apoyo") is not None:
                item.fecha_apoyo = str(data["fecha_apoyo"]).strip()

            # Salidas diarias 01..31 almacenadas en la partida (dias / dias_salidas)
            if "dias" in data and isinstance(data.get("dias"), dict):
                clean_dias = {}
                for d_num in range(1, 32):
                    dk = str(d_num)
                    raw_v = data["dias"].get(dk, data["dias"].get(d_num, 0.0))
                    val_f = float(raw_v or 0.0)
                    if val_f != 0.0:
                        clean_dias[dk] = val_f
                item.dias_salidas = json.dumps(clean_dias)
            elif "dias_salidas" in data and isinstance(data.get("dias_salidas"), str):
                item.dias_salidas = data["dias_salidas"]

            target_mes = item.mes
            target_ano = item.ano
            session.commit()
            res = item.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        try:
            self.refresh_fefo_salidas_existentes(mes=target_mes, ano=target_ano)
        except Exception:
            pass
        return res

    def delete_entrada_mov(self, item_id: int) -> bool:
        session = self.get_session()
        try:
            item = session.query(EntradaMov).filter_by(id=item_id).first()
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def iniciar_nuevo_mes(self, mes_origen: str = "OCTUBRE", ano_origen: int = 2026, mes_destino: str = "NOVIEMBRE", ano_destino: int = 2026) -> Dict[str, Any]:
        """
        Inicia un nuevo mes de operaciones en Control por Movimientos trasladando la existencia final
        (Inventario Disponible) del mes anterior como Inventario Inicial del nuevo mes.
        Preserva exactamente procedimiento, contrato, orden, registro sanitario, proveedor,
        descripcion, clave, lote, unidad_medida, caducidad y fabricacion.
        """
        session = self.get_session()
        try:
            target_mes_origen = (mes_origen or "OCTUBRE").strip().upper()
            target_mes_destino = (mes_destino or "NOVIEMBRE").strip().upper()
            target_ano_origen = int(ano_origen or 2026)
            target_ano_destino = int(ano_destino or 2026)

            # Obtener matriz consolidada calculada del mes origen
            matriz_origen = self.get_reporte_movimientos_matriz(mes=target_mes_origen, ano=target_ano_origen)
            rows_origen = matriz_origen.get("rows", [])
            if not rows_origen:
                raise ValueError(f"No hay registros en el periodo origen {target_mes_origen} {target_ano_origen}.")

            # Limpiar entradas previas del periodo destino si ya existen
            session.query(EntradaMov).filter(
                EntradaMov.mes == target_mes_destino,
                EntradaMov.ano == target_ano_destino
            ).delete()

            total_insertadas = 0
            total_stock_inicial = 0.0

            for idx, r in enumerate(rows_origen, 1):
                inv_disponible = float(r.get("inventario_disponible", 0.0) or 0.0)
                nueva_entrada = EntradaMov(
                    row_index=idx,
                    folio_documento=r.get("orden_suministro") or r.get("folio_documento") or "",
                    procedimiento=r.get("procedimiento") or "",
                    contrato=r.get("contrato") or "",
                    registro_sanitario=r.get("registro_sanitario") or "",
                    almacen=r.get("almacen") or "CS ALMACEN 2022",
                    proveedor=r.get("proveedor") or "",
                    clave=r.get("clave"),
                    lote=r.get("lote"),
                    descripcion=r.get("descripcion") or "",
                    unidad_medida=r.get("unidad_medida") or "PZA",
                    fecha_ajuste="",
                    entrada_ajuste=0.0,
                    fecha_entrada="",
                    cantidad_recibida=0.0,
                    inventario_inicial=inv_disponible,
                    fecha_fabricacion=r.get("fecha_fabricacion") or "",
                    fecha_caducidad=r.get("fecha_caducidad") or "",
                    dias_salidas="{}",
                    apoyo_institucional=0.0,
                    fecha_apoyo="",
                    mes=target_mes_destino,
                    ano=target_ano_destino,
                    observaciones=f"Inventario inicial trasladado desde disponible de {target_mes_origen} {target_ano_origen}"
                )
                session.add(nueva_entrada)
                total_insertadas += 1
                total_stock_inicial += inv_disponible

            session.commit()
            return {
                "status": "success",
                "mes_origen": target_mes_origen,
                "ano_origen": target_ano_origen,
                "mes_destino": target_mes_destino,
                "ano_destino": target_ano_destino,
                "total_partidas": total_insertadas,
                "total_inventario_inicial": round(total_stock_inicial, 2)
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # --- SALIDAS DESDE PDF (FEFO AUTOMÁTICO) ---
    def _build_lotes_fefo_por_clave(self, session: Session, target_mes: str, target_ano: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Construye el mapa de lotes por clave para auditoría FEFO del periodo (mes, año):
        - Prioriza EntradaMov del periodo sumando ingresos y descontando salidas/apoyos base.
        - Descuenta apoyos institucionales externos registrados en el periodo.
        - Sólo complementa con InsumoRecord (con cantidad > 0) para claves que NO existan en EntradaMov.
        """
        entradas_lotes = session.query(EntradaMov).filter(
            EntradaMov.mes == target_mes,
            EntradaMov.ano == target_ano
        ).all()

        grouped: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for e in entradas_lotes:
            cve = (e.clave or "").strip()
            lot = (e.lote or "").strip()
            if not cve or not lot:
                continue
            lot_k = lot.upper()
            ingresado = float((e.inventario_inicial or 0.0) + (e.entrada_ajuste or 0.0) + (e.cantidad_recibida or 0.0))
            dias_out = 0.0
            if e.dias_salidas:
                try:
                    parsed = json.loads(e.dias_salidas)
                    if isinstance(parsed, dict):
                        dias_out = sum(float(v or 0.0) for v in parsed.values())
                except Exception:
                    dias_out = 0.0
            apoyo_base = float(e.apoyo_institucional or 0.0)
            avail = ingresado - dias_out - apoyo_base

            if cve not in grouped:
                grouped[cve] = {}
            if lot_k not in grouped[cve]:
                cad_raw = (e.fecha_caducidad or "").strip()
                grouped[cve][lot_k] = {
                    "lote": lot,
                    "caducidad_raw": cad_raw,
                    "caducidad_norm": normalize_caducidad(cad_raw),
                    "ingresado": 0.0,
                    "stock": 0.0,
                }
            elif not grouped[cve][lot_k]["caducidad_raw"] and e.fecha_caducidad:
                cad_raw = e.fecha_caducidad.strip()
                grouped[cve][lot_k]["caducidad_raw"] = cad_raw
                grouped[cve][lot_k]["caducidad_norm"] = normalize_caducidad(cad_raw)

            grouped[cve][lot_k]["ingresado"] += ingresado
            grouped[cve][lot_k]["stock"] += avail

        # Descontar apoyos institucionales externos del periodo
        apoyos_ext = session.query(ApoyoInstitucionalMov).filter(
            ApoyoInstitucionalMov.mes == target_mes,
            ApoyoInstitucionalMov.ano == target_ano
        ).all()
        for a in apoyos_ext:
            if "importad" in (a.observaciones or "").lower():
                continue
            cve = (a.clave or "").strip()
            lot_k = (a.lote or "").strip().upper()
            if cve in grouped and lot_k in grouped[cve]:
                grouped[cve][lot_k]["stock"] -= float(a.cantidad or 0.0)

        # Sólo para claves que NO tengan entradas en el periodo, consultar existencias reales > 0 en InsumoRecord
        insumos_db = session.query(InsumoRecord).filter(InsumoRecord.cantidad > 0).all()
        claves_con_entradas = set(grouped.keys())
        for ins in insumos_db:
            if not ins.clave or not ins.lote:
                continue
            cve = ins.clave.strip()
            if cve in claves_con_entradas:
                continue
            lot = ins.lote.strip()
            lot_k = lot.upper()
            cant_ins = float(ins.cantidad or 0.0)
            if cant_ins <= 0:
                continue
            grouped.setdefault(cve, {})
            if lot_k not in grouped[cve]:
                cad_raw = (ins.caducidad or "").strip()
                grouped[cve][lot_k] = {
                    "lote": lot,
                    "caducidad_raw": cad_raw,
                    "caducidad_norm": normalize_caducidad(cad_raw),
                    "ingresado": cant_ins,
                    "stock": cant_ins,
                }
            else:
                grouped[cve][lot_k]["ingresado"] += cant_ins
                grouped[cve][lot_k]["stock"] += cant_ins

        lotes_por_clave: Dict[str, List[Dict[str, Any]]] = {}
        for cve, lot_dict in grouped.items():
            lst = list(lot_dict.values())
            lst.sort(key=lambda x: x["caducidad_norm"])
            lotes_por_clave[cve] = lst
        return lotes_por_clave

    def refresh_fefo_salidas_existentes(self, mes: Optional[str] = None, ano: Optional[int] = None) -> int:
        """
        Reevalúa estado_validacion y aviso_fefo de las salidas registradas excluyendo lotes ya caducados
        o sin stock disponible, sin modificar cantidades, claves ni lotes surtidos.
        """
        session = self.get_session()
        updated_count = 0
        try:
            q_periods = session.query(SalidaPdfMov.mes, SalidaPdfMov.ano).distinct()
            if mes and mes.upper() != "TODOS":
                q_periods = q_periods.filter(SalidaPdfMov.mes == mes.upper())
            if ano:
                q_periods = q_periods.filter(SalidaPdfMov.ano == int(ano))
            periods = q_periods.all()
            if not periods:
                return 0

            catalog_set = set(c[0] for c in session.query(CatalogoInsumoMov.clave).all())
            if not catalog_set:
                catalog_set = set(c[0] for c in session.query(InsumoRecord.clave).filter(InsumoRecord.clave.isnot(None)).all())

            for p_mes, p_ano in periods:
                t_mes = (p_mes or "OCTUBRE").upper()
                t_ano = int(p_ano or 2026)
                lotes_por_clave = self._build_lotes_fefo_por_clave(session, t_mes, t_ano)

                salidas_periodo = session.query(SalidaPdfMov).filter(
                    SalidaPdfMov.mes == t_mes,
                    SalidaPdfMov.ano == t_ano
                ).order_by(SalidaPdfMov.id.asc()).all()

                # Descontar del stock disponible todas las salidas PDF externas del periodo
                for s in salidas_periodo:
                    obs = s.observaciones or ""
                    if "importada de base Excel" in obs or "Importado de base" in obs:
                        continue
                    cve = (s.clave or "").strip()
                    lot_k = (s.lote_asignado or "").strip().upper()
                    for cand in lotes_por_clave.get(cve, []):
                        if cand["lote"].upper() == lot_k:
                            cand["stock"] -= float(s.cantidad or 0.0)
                            break

                for s in salidas_periodo:
                    if s.estado_validacion in ("ASIGNADO_FEFO", "SIN_STOCK_FEFO"):
                        continue
                    cve = (s.clave or "").strip()
                    lote_s = (s.lote_asignado or "").strip()
                    if not cve or not lote_s:
                        continue

                    obs = s.observaciones or ""
                    is_base_excel = ("importada de base Excel" in obs or "Importado de base" in obs)
                    fecha_ref = normalize_fecha_referencia(s.fecha)
                    lotes_clave = lotes_por_clave.get(cve, [])

                    cad_asignada = (s.fecha_caducidad or "").strip()
                    if not cad_asignada:
                        match_l = next((x for x in lotes_clave if x["lote"].upper() == lote_s.upper()), None)
                        if match_l and match_l["caducidad_raw"]:
                            cad_asignada = match_l["caducidad_raw"]
                    cad_asignada_norm = normalize_caducidad(cad_asignada)
                    es_valida = cve in catalog_set

                    # Candidatos vigentes (NO caducados) y con existencia
                    if is_base_excel:
                        candidatos_vigentes = [
                            x for x in lotes_clave
                            if x["ingresado"] > 0
                            and x["caducidad_norm"] != "9999-12-31"
                            and not is_caducidad_vencida(x["caducidad_norm"], fecha_ref)
                        ]
                    else:
                        candidatos_vigentes = [
                            x for x in lotes_clave
                            if x["stock"] > 0
                            and x["caducidad_norm"] != "9999-12-31"
                            and not is_caducidad_vencida(x["caducidad_norm"], fecha_ref)
                        ]
                    candidatos_vigentes.sort(key=lambda x: x["caducidad_norm"])
                    fefo_candidate = candidatos_vigentes[0] if candidatos_vigentes else None

                    if is_caducidad_vencida(cad_asignada_norm, fecha_ref):
                        new_estado = "VALIDADO" if es_valida else "CLAVE_NO_CATALOGO"
                        new_aviso = f"ℹ️ Lote '{lote_s}' (cad: {cad_asignada}): material caducado, sin alerta FEFO."
                    elif fefo_candidate and fefo_candidate["lote"].upper() != lote_s.upper() and fefo_candidate["caducidad_norm"] < cad_asignada_norm:
                        fefo_lote = fefo_candidate["lote"]
                        fefo_cad_raw = fefo_candidate["caducidad_raw"] or fefo_candidate["caducidad_norm"]
                        new_estado = "AVISO_FEFO"
                        new_aviso = f"⚠️ AVISO FEFO: Se dio salida al lote '{lote_s}' (cad: {cad_asignada or 'S/F'}), pero en almacén existe el lote '{fefo_lote}' con caducidad más próxima ({fefo_cad_raw})."
                    elif lotes_clave:
                        new_estado = "FEFO_OPTIMO"
                        new_aviso = f"✅ Cumple FEFO: El lote '{lote_s}' es el de caducidad más próxima ({cad_asignada or 'S/F'})."
                    else:
                        new_estado = "VALIDADO" if es_valida else "CLAVE_NO_CATALOGO"
                        new_aviso = f"ℹ️ Lote único / Nuevo: Lote '{lote_s}' registrado según PDF."

                    if s.estado_validacion != new_estado or s.aviso_fefo != new_aviso:
                        s.estado_validacion = new_estado
                        s.aviso_fefo = new_aviso
                        updated_count += 1

            if updated_count > 0:
                session.commit()
            return updated_count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _ensure_fefo_sin_caducados(self, mes: Optional[str] = None, ano: Optional[int] = None):
        """Re-evalúa automáticamente cualquier AVISO_FEFO almacenado si el lote candidato o surtido ya caducó."""
        try:
            check_sess = self.get_session()
            try:
                aviso_rows = check_sess.query(SalidaPdfMov.aviso_fefo, SalidaPdfMov.fecha_caducidad, SalidaPdfMov.fecha).filter(
                    SalidaPdfMov.estado_validacion == "AVISO_FEFO"
                ).all()
                needs_refresh = False
                for av_txt, f_cad, f_mov in aviso_rows:
                    f_ref = normalize_fecha_referencia(f_mov)
                    if is_caducidad_vencida(normalize_caducidad(f_cad), f_ref):
                        needs_refresh = True
                        break
                    m_cand = re.search(r'\(([^()]+)\)\.$', av_txt or "")
                    if m_cand and is_caducidad_vencida(normalize_caducidad(m_cand.group(1)), f_ref):
                        needs_refresh = True
                        break
            finally:
                check_sess.close()
            if needs_refresh:
                self.refresh_fefo_salidas_existentes(mes=mes, ano=ano)
        except Exception:
            pass

    def get_salidas_pdf_movimientos(self, mes: Optional[str] = None, ano: Optional[int] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        self._ensure_fefo_sin_caducados(mes=mes, ano=ano)

        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.upper())
            if ano and (not mes or mes.upper() != "TODOS"):
                q = q.filter(SalidaPdfMov.ano == ano)
            if search:
                term = f"%{search.strip().lower()}%"
                q = q.filter(
                    or_(
                        func.lower(SalidaPdfMov.clave).like(term),
                        func.lower(SalidaPdfMov.lote_asignado).like(term),
                        func.lower(SalidaPdfMov.descripcion).like(term),
                        func.lower(SalidaPdfMov.folio_pedido).like(term),
                        func.lower(SalidaPdfMov.archivo_pdf).like(term)
                    )
                )
            items = q.order_by(SalidaPdfMov.id.desc()).all()
            return [it.to_dict() for it in items]
        finally:
            session.close()

    def process_salidas_pdf_items(self, items: List[Dict[str, Any]], archivo_nombre: str, mes: Optional[str] = "OCTUBRE", ano: Optional[int] = 2026) -> Dict[str, Any]:
        """
        Procesa partidas extraídas de PDF de salida:
        1. Asigna la salida EXACTAMENTE por la Clave y Lote proporcionados en el PDF.
        2. Audita la Regla FEFO excluyendo cualquier material/lote que ya esté caducado o sin stock disponible:
           si en almacén existe un lote VIGENTE (no caducado) y con stock > 0 cuya fecha de caducidad sea anterior
           a la del lote surtido, genera un AVISO FEFO sin modificar clave ni lote del documento.
        3. Si el material ya está caducado, NO marca alerta FEFO.
        4. Si el PDF no especifica lote, asigna automáticamente el lote vigente disponible más próximo a caducar (FEFO).
        """
        session = self.get_session()
        target_mes = (mes or "OCTUBRE").upper()
        target_ano = int(ano or 2026)
        total_procesados = 0
        total_validos = 0
        total_alertas = 0
        total_fefo_optimo = 0
        total_avisos_fefo = 0
        avisos_fefo_lista = []

        try:
            # Precargar catálogo de claves para validación veloz
            catalog_set = set(c[0] for c in session.query(CatalogoInsumoMov.clave).all())
            if not catalog_set:
                catalog_set = set(c[0] for c in session.query(InsumoRecord.clave).filter(InsumoRecord.clave.isnot(None)).all())

            # Cargar lotes del periodo con stock disponible real
            lotes_por_clave = self._build_lotes_fefo_por_clave(session, target_mes, target_ano)

            # Descontar salidas PDF externas previas ya registradas en el periodo
            salidas_previas = session.query(SalidaPdfMov).filter(
                SalidaPdfMov.mes == target_mes,
                SalidaPdfMov.ano == target_ano
            ).all()
            for sp in salidas_previas:
                obs = sp.observaciones or ""
                if "importada de base Excel" in obs or "Importado de base" in obs:
                    continue
                cve_sp = (sp.clave or "").strip()
                lot_sp = (sp.lote_asignado or "").strip().upper()
                for cand in lotes_por_clave.get(cve_sp, []):
                    if cand["lote"].upper() == lot_sp:
                        cand["stock"] -= float(sp.cantidad or 0.0)
                        break

            # Pre-descontar las partidas con lote explícito de este mismo PDF (surtidos divididos entre dos lotes)
            for it_pre in items:
                cve_pre = str(it_pre.get("clave") or it_pre.get("clave_cliente", "")).strip()
                lot_pre = str(it_pre.get("lote", "")).strip()
                if not cve_pre or lot_pre.lower() in ["none", "nan", "null", "s/l", "sin lote", ""]:
                    continue
                cant_pre = float(it_pre.get("cantidad") or it_pre.get("c_surtida") or it_pre.get("c_pedida", 0.0) or 0.0)
                for cand in lotes_por_clave.get(cve_pre, []):
                    if cand["lote"].upper() == lot_pre.upper():
                        cand["stock"] -= cant_pre
                        break

            for it in items:
                clave = str(it.get("clave") or it.get("clave_cliente", "")).strip()
                if not clave:
                    continue

                total_procesados += 1
                cantidad = float(it.get("cantidad") or it.get("c_surtida") or it.get("c_pedida", 0.0))
                folio = str(it.get("pedido") or it.get("documento") or it.get("folio_salida", "")).strip()
                desc = it.get("descripcion", "").strip()
                fecha_surtido = it.get("fecha", "") or it.get("fecha_documento", "") or datetime.date.today().strftime("%Y-%m-%d")
                fecha_ref = normalize_fecha_referencia(fecha_surtido)
                dia_mov = int(it.get("dia") or datetime.date.today().day)
                if dia_mov < 1 or dia_mov > 31:
                    dia_mov = datetime.date.today().day

                cliente = it.get("localidad") or it.get("cliente", "")

                # 1. Validación de Clave en Catálogo
                es_valida = clave in catalog_set

                # 2. Asignación EXACTA de Clave y Lote dada en el PDF
                lote_pdf = str(it.get("lote", "")).strip()
                caducidad_pdf = str(it.get("caducidad", "")).strip()
                if lote_pdf.lower() in ["none", "nan", "null", "s/l", "sin lote", ""]:
                    lote_pdf = ""

                lotes_clave = lotes_por_clave.get(clave, [])
                # Candidatos FEFO: únicamente lotes NO CADUCADOS y con stock disponible > 0
                candidatos_vigentes = [
                    x for x in lotes_clave
                    if x["stock"] > 0
                    and x["caducidad_norm"] != "9999-12-31"
                    and not is_caducidad_vencida(x["caducidad_norm"], fecha_ref)
                ]
                candidatos_vigentes.sort(key=lambda x: x["caducidad_norm"])
                fefo_candidate = candidatos_vigentes[0] if len(candidatos_vigentes) > 0 else None

                if lote_pdf:
                    # El PDF trae lote especificado: SE ASIGNA EXACTAMENTE ESE LOTE
                    lote_asignado = lote_pdf

                    # Obtener caducidad del lote asignado
                    if caducidad_pdf and caducidad_pdf.lower() not in ["none", "nan", "null", ""]:
                        caducidad_asignada = caducidad_pdf
                    else:
                        match_lote = next((x for x in lotes_clave if x["lote"].upper() == lote_pdf.upper()), None)
                        if match_lote and match_lote["caducidad_raw"]:
                            caducidad_asignada = match_lote["caducidad_raw"]
                        else:
                            ins_match = session.query(InsumoRecord).filter(
                                InsumoRecord.clave == clave,
                                func.upper(InsumoRecord.lote) == lote_pdf.upper()
                            ).first()
                            caducidad_asignada = (ins_match.caducidad or "") if ins_match else ""

                    cad_asignada_norm = normalize_caducidad(caducidad_asignada)

                    # --- EVALUACIÓN DE LA REGLA FEFO (SIN MARCAR ALERTA SI EL MATERIAL YA ESTÁ CADUCADO) ---
                    if is_caducidad_vencida(cad_asignada_norm, fecha_ref):
                        aviso_fefo = f"ℹ️ Lote '{lote_pdf}' (cad: {caducidad_asignada}): material caducado, sin alerta FEFO."
                        estado_val = "VALIDADO" if es_valida else "CLAVE_NO_CATALOGO"
                        total_validos += 1
                    elif fefo_candidate and fefo_candidate["lote"].upper() != lote_pdf.upper() and fefo_candidate["caducidad_norm"] < cad_asignada_norm:
                        fefo_lote = fefo_candidate["lote"]
                        fefo_cad_norm = fefo_candidate["caducidad_norm"]
                        fefo_cad_raw = fefo_candidate["caducidad_raw"] or fefo_cad_norm
                        aviso_fefo = f"⚠️ AVISO FEFO: Se dio salida al lote '{lote_pdf}' (cad: {caducidad_asignada or 'S/F'}), pero en almacén existe el lote '{fefo_lote}' con caducidad más próxima ({fefo_cad_raw})."
                        estado_val = "AVISO_FEFO"
                        total_avisos_fefo += 1
                        total_alertas += 1
                        avisos_fefo_lista.append({
                            "clave": clave,
                            "lote_surtido": lote_pdf,
                            "caducidad_surtido": caducidad_asignada,
                            "lote_fefo": fefo_lote,
                            "caducidad_fefo": fefo_cad_raw,
                            "mensaje": aviso_fefo
                        })
                    elif lotes_clave:
                        aviso_fefo = f"✅ Cumple FEFO: El lote '{lote_pdf}' es el de caducidad más próxima ({caducidad_asignada or 'S/F'})."
                        estado_val = "FEFO_OPTIMO"
                        total_fefo_optimo += 1
                        total_validos += 1
                    else:
                        aviso_fefo = f"ℹ️ Lote único / Nuevo: Lote '{lote_pdf}' registrado según PDF."
                        estado_val = "VALIDADO" if es_valida else "CLAVE_NO_CATALOGO"
                        total_validos += 1

                else:
                    # El PDF NO especificó lote: Asignar lote vigente disponible con fecha más próxima (FEFO)
                    if fefo_candidate:
                        lote_asignado = fefo_candidate["lote"]
                        caducidad_asignada = fefo_candidate["caducidad_raw"] or fefo_candidate["caducidad_norm"]
                        fefo_candidate["stock"] -= cantidad
                        aviso_fefo = f"ℹ️ Sin lote en PDF: Asignado automáticamente lote '{lote_asignado}' por regla FEFO (cad: {caducidad_asignada})."
                        estado_val = "ASIGNADO_FEFO"
                        total_validos += 1
                    else:
                        lote_asignado = "SIN_LOTE_FEFO"
                        caducidad_asignada = ""
                        aviso_fefo = "⚠️ Sin lote en PDF y no hay existencias vigentes en almacén para asignar lote FEFO."
                        estado_val = "SIN_STOCK_FEFO" if es_valida else "CLAVE_NO_CATALOGO"
                        total_alertas += 1

                # Auto-detección inteligente del mes y año según la fecha real del PDF
                doc_mes = target_mes
                doc_ano = target_ano
                if fecha_surtido:
                    m_iso = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', str(fecha_surtido))
                    m_dmy = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', str(fecha_surtido))
                    meses_map = {
                        1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL", 5: "MAYO", 6: "JUNIO",
                        7: "JULIO", 8: "AGOSTO", 9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
                    }
                    if m_iso:
                        doc_ano = int(m_iso.group(1))
                        m_idx = int(m_iso.group(2))
                        if m_idx in meses_map:
                            doc_mes = meses_map[m_idx]
                    elif m_dmy:
                        doc_ano = int(m_dmy.group(3))
                        m_idx = int(m_dmy.group(2))
                        if m_idx in meses_map:
                            doc_mes = meses_map[m_idx]

                salida_rec = SalidaPdfMov(
                    archivo_pdf=archivo_nombre,
                    folio_pedido=folio,
                    fecha=fecha_surtido,
                    dia=dia_mov,
                    mes=doc_mes,
                    ano=doc_ano,
                    clave=clave,
                    descripcion=desc,
                    cantidad=cantidad,
                    lote_asignado=lote_asignado,
                    fecha_caducidad=caducidad_asignada,
                    cliente_destino=cliente,
                    estado_validacion=estado_val,
                    aviso_fefo=aviso_fefo,
                    observaciones=f"Importado de PDF {archivo_nombre}"
                )
                session.add(salida_rec)

            session.commit()
            return {
                "total_procesados": total_procesados,
                "total_validos": total_validos,
                "total_alertas": total_alertas,
                "total_fefo_optimo": total_fefo_optimo,
                "total_avisos_fefo": total_avisos_fefo,
                "avisos_fefo": avisos_fefo_lista,
                "archivo": archivo_nombre,
                "mes": target_mes,
                "ano": target_ano
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_salida_pdf_mov(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        recalc = bool(data.get("recalcular_fefo", True))
        session = self.get_session()
        try:
            item = session.query(SalidaPdfMov).filter_by(id=item_id).first()
            if not item:
                return None

            if "clave" in data and data.get("clave") is not None:
                cve = str(data["clave"]).strip()
                if not cve:
                    raise ValueError("La Clave no puede quedar vacía.")
                item.clave = cve

            if "lote_asignado" in data and data.get("lote_asignado") is not None:
                item.lote_asignado = str(data["lote_asignado"]).strip()
            elif "lote" in data and data.get("lote") is not None:
                item.lote_asignado = str(data["lote"]).strip()

            if "fecha_caducidad" in data and data.get("fecha_caducidad") is not None:
                item.fecha_caducidad = str(data["fecha_caducidad"]).strip()
            elif "fecha_caducidad_lote" in data and data.get("fecha_caducidad_lote") is not None:
                item.fecha_caducidad = str(data["fecha_caducidad_lote"]).strip()

            if "fecha" in data and data.get("fecha") is not None:
                item.fecha = str(data["fecha"]).strip()
            elif "fecha_salida" in data and data.get("fecha_salida") is not None:
                item.fecha = str(data["fecha_salida"]).strip()

            if "dia" in data and data.get("dia") is not None:
                d_val = int(data["dia"] or 1)
                item.dia = max(1, min(31, d_val))
            elif "dia_mes" in data and data.get("dia_mes") is not None:
                d_val = int(data["dia_mes"] or 1)
                item.dia = max(1, min(31, d_val))

            if "mes" in data and data.get("mes"):
                item.mes = str(data["mes"]).strip().upper()
            if "ano" in data and data.get("ano") is not None:
                item.ano = int(data["ano"] or 2026)

            if "cantidad" in data and data.get("cantidad") is not None:
                item.cantidad = float(data["cantidad"] or 0.0)

            if "folio_pedido" in data and data.get("folio_pedido") is not None:
                item.folio_pedido = str(data["folio_pedido"]).strip()
            elif "pedido_folio" in data and data.get("pedido_folio") is not None:
                item.folio_pedido = str(data["pedido_folio"]).strip()

            if "archivo_pdf" in data and data.get("archivo_pdf") is not None:
                item.archivo_pdf = str(data["archivo_pdf"]).strip()
            elif "archivo_fuente" in data and data.get("archivo_fuente") is not None:
                item.archivo_pdf = str(data["archivo_fuente"]).strip()

            for field in ["descripcion", "cliente_destino", "observaciones"]:
                if field in data and data.get(field) is not None:
                    setattr(item, field, str(data[field]).strip())

            if not recalc:
                if "estado_validacion" in data and data.get("estado_validacion") is not None:
                    item.estado_validacion = str(data["estado_validacion"]).strip()
                if "aviso_fefo" in data and data.get("aviso_fefo") is not None:
                    item.aviso_fefo = str(data["aviso_fefo"]).strip()

            target_mes = item.mes
            target_ano = item.ano
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        if recalc:
            try:
                self.refresh_fefo_salidas_existentes(mes=target_mes, ano=target_ano)
            except Exception:
                pass

        read_sess = self.get_session()
        try:
            refreshed = read_sess.query(SalidaPdfMov).filter_by(id=item_id).first()
            return refreshed.to_dict() if refreshed else None
        finally:
            read_sess.close()

    def delete_salida_pdf_mov(self, item_id: int) -> bool:
        session = self.get_session()
        try:
            item = session.query(SalidaPdfMov).filter_by(id=item_id).first()
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def clear_salidas_pdf_mov(self, mes: Optional[str] = None, ano: Optional[int] = None) -> int:
        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == ano)
            count = q.delete()
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_pedidos_resumen(
        self,
        mes: Optional[str] = None,
        ano: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Agrupa las salidas registradas en SalidaPdfMov por Pedido (folio_pedido + archivo_pdf + mes + ano).
        Retorna la lista de pedidos consolidados con el total de partidas, piezas surtidas y estado FEFO.
        """
        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.upper())
            if ano and (not mes or mes.upper() != "TODOS"):
                q = q.filter(SalidaPdfMov.ano == int(ano))

            items = q.order_by(SalidaPdfMov.dia.desc(), SalidaPdfMov.id.desc()).all()

            grouped = {}
            for it in items:
                f_ped = (it.folio_pedido or "").strip()
                f_arch = (it.archivo_pdf or "").strip()
                m_val = (it.mes or "").strip().upper()
                a_val = int(it.ano or 2026)

                group_key = (f_ped, f_arch, m_val, a_val)
                if group_key not in grouped:
                    grouped[group_key] = {
                        "folio_pedido": f_ped or "SIN_FOLIO",
                        "archivo_pdf": f_arch or "SIN_ARCHIVO",
                        "mes": m_val or "OCTUBRE",
                        "ano": a_val,
                        "dia": int(it.dia or 1),
                        "fecha": it.fecha or "",
                        "cliente_destino": it.cliente_destino or "",
                        "total_partidas": 0,
                        "total_piezas": 0.0,
                        "claves": set(),
                        "lotes": set(),
                        "has_fefo_alert": False,
                        "items_ids": [],
                    }

                g = grouped[group_key]
                g["total_partidas"] += 1
                g["total_piezas"] += float(it.cantidad or 0.0)
                if it.clave:
                    g["claves"].add(it.clave)
                if it.lote_asignado:
                    g["lotes"].add(it.lote_asignado)
                if it.aviso_fefo and ("AVISO FEFO" in it.aviso_fefo or "⚠️" in it.aviso_fefo):
                    g["has_fefo_alert"] = True
                g["items_ids"].append(it.id)

            res = []
            search_t = search.strip().lower() if search else None

            for g in grouped.values():
                g["total_piezas"] = round(g["total_piezas"], 2)
                g["total_claves"] = len(g["claves"])
                claves_str = ", ".join(sorted(list(g["claves"])))
                lotes_str = ", ".join(sorted(list(g["lotes"])))
                del g["claves"]
                del g["lotes"]

                if search_t:
                    match = (
                        search_t in g["folio_pedido"].lower() or
                        search_t in g["archivo_pdf"].lower() or
                        search_t in claves_str.lower() or
                        search_t in lotes_str.lower() or
                        search_t in str(g["dia"]).lower() or
                        search_t in g["fecha"].lower()
                    )
                    if not match:
                        continue

                res.append(g)

            res.sort(key=lambda x: (x.get("dia", 0), x.get("total_piezas", 0)), reverse=True)
            return res
        finally:
            session.close()

    def get_pedido_detalle(
        self,
        folio_pedido: str,
        archivo_pdf: Optional[str] = None,
        mes: Optional[str] = None,
        ano: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna la cabecera consolidada de un pedido y todas las partidas individuales que lo componen.
        """
        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            target_fol = (folio_pedido or "").strip()
            if target_fol:
                q = q.filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower())
            if archivo_pdf and archivo_pdf.strip():
                q = q.filter(func.lower(SalidaPdfMov.archivo_pdf) == archivo_pdf.strip().lower())
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.strip().upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == int(ano))

            items = q.order_by(SalidaPdfMov.id.asc()).all()
            if not items:
                if target_fol:
                    items = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower()).all()

            if not items:
                return None

            first = items[0]
            items_dicts = [it.to_dict() for it in items]

            total_piezas = round(sum(float(it.cantidad or 0.0) for it in items), 2)
            has_alert = any("AVISO FEFO" in (it.aviso_fefo or "") or "⚠️" in (it.aviso_fefo or "") for it in items)

            return {
                "folio_pedido": first.folio_pedido or "",
                "archivo_pdf": first.archivo_pdf or "",
                "fecha": first.fecha or "",
                "dia": int(first.dia or 1),
                "mes": first.mes or "OCTUBRE",
                "ano": int(first.ano or 2026),
                "cliente_destino": first.cliente_destino or "",
                "total_partidas": len(items),
                "total_piezas": total_piezas,
                "has_fefo_alert": has_alert,
                "items": items_dicts
            }
        finally:
            session.close()

    def update_pedido_completo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifica un pedido completo:
        - Actualiza campos a nivel de pedido (folio, fecha, día, mes, año, archivo) aplicándolos a todas sus partidas.
        - Actualiza cantidades, claves, lotes y caducidades de las partidas existentes.
        - Elimina partidas que hayan sido retiradas del pedido.
        - Crea nuevas partidas si se agregaron filas al pedido.
        - Recalcula auditoría FEFO y actualiza el impacto en inventario.
        """
        folio_actual = str(data.get("folio_actual") or "").strip()
        archivo_actual = str(data.get("archivo_actual") or "").strip()
        mes_actual = str(data.get("mes_actual") or "").strip().upper()
        ano_actual = int(data.get("ano_actual") or 2026)

        nuevo_folio = str(data.get("nuevo_folio") or folio_actual).strip()
        nueva_fecha = str(data.get("nueva_fecha") or "").strip()
        nuevo_dia = int(data.get("nuevo_dia") or 1)
        nuevo_mes = str(data.get("nuevo_mes") or mes_actual).strip().upper()
        nuevo_ano = int(data.get("nuevo_ano") or ano_actual)
        nuevo_archivo = str(data.get("nuevo_archivo") or archivo_actual).strip()

        if not nuevo_folio:
            raise ValueError("El folio del pedido no puede estar vacío.")

        items_input = data.get("items", [])

        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            if folio_actual:
                q = q.filter(func.lower(SalidaPdfMov.folio_pedido) == folio_actual.lower())
            if archivo_actual:
                q = q.filter(func.lower(SalidaPdfMov.archivo_pdf) == archivo_actual.lower())
            if mes_actual and mes_actual != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes_actual)
            if ano_actual:
                q = q.filter(SalidaPdfMov.ano == ano_actual)

            existing_items = q.all()
            if not existing_items and folio_actual:
                existing_items = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == folio_actual.lower()).all()

            if not existing_items:
                raise ValueError(f"No se encontró el pedido '{folio_actual}' en el sistema.")

            existing_map = {it.id: it for it in existing_items}
            submitted_ids = set()

            for item_data in items_input:
                item_id = item_data.get("id")
                cve = str(item_data.get("clave") or "").strip()
                if not cve:
                    continue

                lote_val = str(item_data.get("lote_asignado") or item_data.get("lote") or "").strip()
                cant_val = float(item_data.get("cantidad") or 0.0)
                cad_val = str(item_data.get("fecha_caducidad") or item_data.get("fecha_caducidad_lote") or "").strip()
                desc_val = str(item_data.get("descripcion") or "").strip()

                if item_id and int(item_id) in existing_map:
                    it_obj = existing_map[int(item_id)]
                    submitted_ids.add(int(item_id))
                    it_obj.folio_pedido = nuevo_folio
                    if nueva_fecha:
                        it_obj.fecha = nueva_fecha
                    it_obj.dia = max(1, min(31, nuevo_dia))
                    it_obj.mes = nuevo_mes
                    it_obj.ano = nuevo_ano
                    if nuevo_archivo:
                        it_obj.archivo_pdf = nuevo_archivo
                    it_obj.clave = cve
                    it_obj.lote_asignado = lote_val
                    it_obj.cantidad = cant_val
                    it_obj.fecha_caducidad = cad_val
                    if desc_val:
                        it_obj.descripcion = desc_val
                else:
                    new_salida = SalidaPdfMov(
                        archivo_pdf=nuevo_archivo or "PEDIDO_MANUAL.pdf",
                        folio_pedido=nuevo_folio,
                        fecha=nueva_fecha or f"{nuevo_ano}-{nuevo_mes[:3]}-{nuevo_dia:02d}",
                        dia=max(1, min(31, nuevo_dia)),
                        mes=nuevo_mes,
                        ano=nuevo_ano,
                        clave=cve,
                        descripcion=desc_val,
                        cantidad=cant_val,
                        lote_asignado=lote_val,
                        fecha_caducidad=cad_val,
                        estado_validacion="VALIDADO"
                    )
                    session.add(new_salida)

            if items_input:
                for eid, eit in existing_map.items():
                    if eid not in submitted_ids:
                        session.delete(eit)
            else:
                for it_obj in existing_items:
                    it_obj.folio_pedido = nuevo_folio
                    if nueva_fecha:
                        it_obj.fecha = nueva_fecha
                    it_obj.dia = max(1, min(31, nuevo_dia))
                    it_obj.mes = nuevo_mes
                    it_obj.ano = nuevo_ano
                    if nuevo_archivo:
                        it_obj.archivo_pdf = nuevo_archivo

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        for m, a in {(mes_actual, ano_actual), (nuevo_mes, nuevo_ano)}:
            if m and a:
                try:
                    self.refresh_fefo_salidas_existentes(mes=m, ano=a)
                except Exception:
                    pass

        return {
            "success": True,
            "message": f"Pedido '{nuevo_folio}' actualizado correctamente.",
            "folio_pedido": nuevo_folio,
            "mes": nuevo_mes,
            "ano": nuevo_ano
        }

    def delete_pedido_completo(
        self,
        folio_pedido: str,
        archivo_pdf: Optional[str] = None,
        mes: Optional[str] = None,
        ano: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Elimina todas las partidas de un pedido completo.
        """
        target_fol = (folio_pedido or "").strip()
        if not target_fol:
            raise ValueError("Debe especificar el folio del pedido a eliminar.")

        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower())
            if archivo_pdf and archivo_pdf.strip():
                q = q.filter(func.lower(SalidaPdfMov.archivo_pdf) == archivo_pdf.strip().lower())
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.strip().upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == int(ano))

            items = q.all()
            if not items:
                items = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower()).all()

            if not items:
                raise ValueError(f"No se encontraron partidas para el pedido '{target_fol}'.")

            count = len(items)
            total_piezas = round(sum(float(it.cantidad or 0.0) for it in items), 2)
            affected_mes = items[0].mes
            affected_ano = items[0].ano

            for it in items:
                session.delete(it)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        if affected_mes and affected_ano:
            try:
                self.refresh_fefo_salidas_existentes(mes=affected_mes, ano=affected_ano)
            except Exception:
                pass

        return {
            "success": True,
            "message": f"Pedido '{target_fol}' eliminado exitosamente ({count} partidas, {total_piezas:,.0f} piezas eliminadas).",
            "folio_pedido": target_fol,
            "deleted_items": count,
            "deleted_piezas": total_piezas
        }

    # --- APOYO INSTITUCIONAL ---
    def get_apoyos_institucionales(self, mes: Optional[str] = None, ano: Optional[int] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            q = session.query(ApoyoInstitucionalMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(ApoyoInstitucionalMov.mes == mes.upper())
            if ano and (not mes or mes.upper() != "TODOS"):
                q = q.filter(ApoyoInstitucionalMov.ano == ano)
            if search:
                term = f"%{search.strip().lower()}%"
                q = q.filter(
                    or_(
                        func.lower(ApoyoInstitucionalMov.clave).like(term),
                        func.lower(ApoyoInstitucionalMov.lote).like(term),
                        func.lower(ApoyoInstitucionalMov.institucion).like(term),
                        func.lower(ApoyoInstitucionalMov.descripcion).like(term),
                        func.lower(ApoyoInstitucionalMov.folio_documento).like(term)
                    )
                )
            items = q.order_by(ApoyoInstitucionalMov.id.desc()).all()
            return [it.to_dict() for it in items]
        finally:
            session.close()

    def create_apoyo_institucional(self, data: Dict[str, Any]) -> Dict[str, Any]:
        session = self.get_session()
        try:
            clave = str(data.get("clave", "")).strip()
            lote = str(data.get("lote", "")).strip()
            institucion = str(data.get("institucion", "")).strip()
            cantidad = float(data.get("cantidad", 0.0) or 0.0)
            fecha = str(data.get("fecha", datetime.date.today().strftime("%Y-%m-%d"))).strip()

            if not clave or not lote or not institucion:
                raise ValueError("La Clave, el Lote y la Institución son obligatorios.")

            descripcion = data.get("descripcion", "").strip()
            if not descripcion:
                cat = session.query(CatalogoInsumoMov).filter_by(clave=clave).first()
                if cat:
                    descripcion = cat.descripcion
                else:
                    ins = session.query(InsumoRecord).filter_by(clave=clave).first()
                    if ins:
                        descripcion = ins.descripcion or ""

            dia = 1
            try:
                m_dia = re.search(r'\b[0-3]?[0-9]\b', fecha.split("-")[-1])
                if m_dia:
                    dia = int(m_dia.group(0))
            except Exception:
                dia = datetime.date.today().day

            mes = str(data.get("mes", "OCTUBRE")).strip().upper()
            ano = int(data.get("ano", 2026))

            new_apoyo = ApoyoInstitucionalMov(
                clave=clave,
                lote=lote,
                descripcion=descripcion,
                cantidad=cantidad,
                institucion=institucion,
                fecha=fecha,
                dia=dia,
                mes=mes,
                ano=ano,
                folio_documento=data.get("folio_documento") or data.get("folio_observaciones", ""),
                observaciones=data.get("observaciones") or data.get("folio_observaciones", "")
            )
            session.add(new_apoyo)
            session.commit()
            return new_apoyo.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_apoyo_institucional(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.get_session()
        try:
            item = session.query(ApoyoInstitucionalMov).filter_by(id=item_id).first()
            if not item:
                return None

            if "clave" in data and data.get("clave") is not None:
                cve = str(data["clave"]).strip()
                if not cve:
                    raise ValueError("La Clave no puede quedar vacía.")
                item.clave = cve

            if "lote" in data and data.get("lote") is not None:
                lot = str(data["lote"]).strip()
                if not lot:
                    raise ValueError("El Lote no puede quedar vacío.")
                item.lote = lot

            if "institucion" in data and data.get("institucion") is not None:
                inst = str(data["institucion"]).strip()
                if not inst:
                    raise ValueError("La Institución no puede quedar vacía.")
                item.institucion = inst

            if "descripcion" in data and data.get("descripcion") is not None:
                item.descripcion = str(data["descripcion"]).strip()

            if "cantidad" in data and data.get("cantidad") is not None:
                item.cantidad = float(data["cantidad"] or 0.0)

            if "fecha" in data and data.get("fecha") is not None:
                item.fecha = str(data["fecha"]).strip()

            if "dia" in data and data.get("dia") is not None:
                d_val = int(data["dia"] or 1)
                item.dia = max(1, min(31, d_val))
            elif "fecha" in data and item.fecha:
                try:
                    m_dia = re.search(r'\b[0-3]?[0-9]\b', item.fecha.split("-")[-1])
                    if m_dia:
                        item.dia = max(1, min(31, int(m_dia.group(0))))
                except Exception:
                    pass

            if "mes" in data and data.get("mes"):
                item.mes = str(data["mes"]).strip().upper()
            if "ano" in data and data.get("ano") is not None:
                item.ano = int(data["ano"] or 2026)

            if "folio_documento" in data and data.get("folio_documento") is not None:
                item.folio_documento = str(data["folio_documento"]).strip()
            if "observaciones" in data and data.get("observaciones") is not None:
                new_obs = str(data["observaciones"]).strip()
                if "importad" in (item.observaciones or "").lower() and "importad" not in new_obs.lower():
                    new_obs = f"Apoyo importado base. {new_obs}".strip()
                item.observaciones = new_obs

            session.commit()
            return item.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_apoyo_institucional(self, item_id: int) -> bool:
        session = self.get_session()
        try:
            item = session.query(ApoyoInstitucionalMov).filter_by(id=item_id).first()
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def clear_control_entradas(self, mes: Optional[str] = None, ano: Optional[int] = None) -> int:
        session = self.get_session()
        try:
            q = session.query(EntradaMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(EntradaMov.mes == mes.upper())
            if ano:
                q = q.filter(EntradaMov.ano == int(ano))
            count = q.delete(synchronize_session=False)
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def clear_control_apoyos(self, mes: Optional[str] = None, ano: Optional[int] = None) -> int:
        session = self.get_session()
        try:
            q = session.query(ApoyoInstitucionalMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(ApoyoInstitucionalMov.mes == mes.upper())
            if ano:
                q = q.filter(ApoyoInstitucionalMov.ano == int(ano))
            count = q.delete(synchronize_session=False)
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def clear_control_movimientos(self, mes: Optional[str] = None, ano: Optional[int] = None, clear_catalog: bool = False) -> Dict[str, int]:
        """
        Vacía los registros del módulo Control de Movimientos (Entradas, Salidas PDF y Apoyos).
        Si se especifica mes/año, vacía solo ese periodo. Si no, vacía todo el módulo.
        """
        session = self.get_session()
        counts = {}
        try:
            q_ent = session.query(EntradaMov)
            q_sal = session.query(SalidaPdfMov)
            q_apo = session.query(ApoyoInstitucionalMov)

            if mes and mes.upper() != "TODOS":
                m = mes.strip().upper()
                q_ent = q_ent.filter(EntradaMov.mes == m)
                q_sal = q_sal.filter(SalidaPdfMov.mes == m)
                q_apo = q_apo.filter(ApoyoInstitucionalMov.mes == m)
            if ano:
                a = int(ano)
                q_ent = q_ent.filter(EntradaMov.ano == a)
                q_sal = q_sal.filter(SalidaPdfMov.ano == a)
                q_apo = q_apo.filter(ApoyoInstitucionalMov.ano == a)

            counts["entradas"] = q_ent.delete(synchronize_session=False)
            counts["salidas_pdf"] = q_sal.delete(synchronize_session=False)
            counts["apoyos"] = q_apo.delete(synchronize_session=False)

            if clear_catalog:
                counts["catalogo"] = session.query(CatalogoInsumoMov).delete()

            session.commit()
            self.log_execution(
                operation="CLEAR_CONTROL_MOVIMIENTOS",
                status="SUCCESS",
                file_name="CONTROL_MOV_RESET",
                records_count=sum(counts.values()),
                details=f"Control de movimientos vaciado ({mes or 'TODOS'} {ano or ''}): {counts}"
            )
            return counts
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def clear_all_system_data(self, keep_catalogs: bool = False) -> Dict[str, int]:
        """
        VACIADO TOTAL DEL SISTEMA:
        Elimina absolutamente todos los registros de todos los módulos:
        - Inventario general SIIA (insumos_report)
        - Movimientos SIIA (movimientos_entradas_salidas)
        - Entradas Manuales (entradas_movimientos)
        - Salidas PDF (salidas_pdf_movimientos)
        - Apoyos Institucionales (apoyo_institucional_movimientos)
        - Catálogo de movimientos, proveedores y unidades (opcional)
        """
        session = self.get_session()
        counts = {}
        try:
            counts["inventario_siia"] = session.query(InsumoRecord).delete()
            counts["movimientos_siia"] = session.query(MovimientoRecord).delete()
            counts["entradas_movimientos"] = session.query(EntradaMov).delete()
            counts["salidas_pdf_movimientos"] = session.query(SalidaPdfMov).delete()
            counts["apoyo_institucional"] = session.query(ApoyoInstitucionalMov).delete()
            if not keep_catalogs:
                counts["catalogo_movimientos"] = session.query(CatalogoInsumoMov).delete()
                counts["proveedores_movimientos"] = session.query(ProveedorMov).delete()
                counts["unidades_medida_movimientos"] = session.query(UnidadMedidaMov).delete()

            session.commit()
            self.log_execution(
                operation="CLEAR_ALL_SYSTEM",
                status="SUCCESS",
                file_name="SYSTEM_FULL_RESET",
                records_count=sum(counts.values()),
                details=f"Vaciado total del sistema completado: {counts}"
            )
            return counts
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_lotes_disponibles_clave(self, clave: str, mes: Optional[str] = "OCTUBRE", ano: Optional[int] = 2026) -> List[Dict[str, Any]]:
        """Devuelve los lotes activos con su caducidad y stock actual disponible para una clave dada."""
        session = self.get_session()
        try:
            target_mes = (mes or "OCTUBRE").upper()
            target_ano = int(ano or 2026)
            cve = clave.strip()

            entradas = session.query(EntradaMov).filter(
                EntradaMov.clave == cve,
                EntradaMov.mes == target_mes,
                EntradaMov.ano == target_ano
            ).all()

            lotes = []
            for e in entradas:
                tot_ingresado = float((e.inventario_inicial or 0.0) + (e.entrada_ajuste or 0.0) + (e.cantidad_recibida or 0.0))
                
                salidas_pdf = session.query(func.sum(SalidaPdfMov.cantidad)).filter(
                    SalidaPdfMov.clave == cve,
                    SalidaPdfMov.lote_asignado == e.lote,
                    SalidaPdfMov.mes == target_mes,
                    SalidaPdfMov.ano == target_ano
                ).scalar() or 0.0

                apoyos = session.query(func.sum(ApoyoInstitucionalMov.cantidad)).filter(
                    ApoyoInstitucionalMov.clave == cve,
                    ApoyoInstitucionalMov.lote == e.lote,
                    ApoyoInstitucionalMov.mes == target_mes,
                    ApoyoInstitucionalMov.ano == target_ano
                ).scalar() or 0.0

                disponible = tot_ingresado - (salidas_pdf + apoyos)
                lotes.append({
                    "lote": e.lote,
                    "fecha_caducidad": e.fecha_caducidad or "",
                    "fecha_fabricacion": e.fecha_fabricacion or "",
                    "inventario_total": tot_ingresado,
                    "total_surtido": salidas_pdf + apoyos,
                    "inventario_disponible": max(0.0, disponible)
                })

            if not lotes:
                ins_list = session.query(InsumoRecord).filter_by(clave=cve).all()
                for ins in ins_list:
                    if ins.lote:
                        lotes.append({
                            "lote": ins.lote,
                            "fecha_caducidad": ins.caducidad or "",
                            "fecha_fabricacion": "",
                            "inventario_total": float(ins.cantidad or 0.0),
                            "total_surtido": 0.0,
                            "inventario_disponible": float(ins.cantidad or 0.0)
                        })

            return lotes
        finally:
            session.close()

    @staticmethod
    def derive_proc_cont(os_val: str, cve: str = "") -> Tuple[str, str]:
        os_clean = (os_val or "").strip()
        m_itp = re.match(r'OS-ITPBMX-(\d+)-(\d{4})', os_clean, re.I)
        if m_itp:
            num, yr = m_itp.group(1), m_itp.group(2)
            return ('IA-12-NEF-012NEF001-I-30-2025', f'CS/ITPBMX/{num}/{yr}')
        
        m_lc = re.match(r'OS-LCBMX-(\d+)-(\d{4})', os_clean, re.I)
        if m_lc:
            num, yr = m_lc.group(1), m_lc.group(2)
            proc = 'LA-12-NEF-012NEF001-I-59-2025' if num in ['019', '023', '026'] else 'LA-12-NEF-012NEF001-I-97-2025'
            return (proc, f'LC/BMX/{num}/{yr}')

        m_ad = re.match(r'OS-ADBMX-(\d+)-(\d{4})', os_clean, re.I)
        if m_ad:
            num, yr = m_ad.group(1), m_ad.group(2)
            n_int = int(num)
            if yr == '2026':
                proc = 'AA-12-NEF-012NEF001-I-91-2026'
            elif n_int in [86, 296, 297, 299, 303, 308, 312, 313, 329, 334]:
                proc = 'AA-12-NEF-012NEF001-I-31-2025'
            elif n_int in [87, 88, 93, 97, 106, 111]:
                proc = 'AA-12-NEF-012NEF001-I-17-2025'
            elif n_int in [170, 171, 178]:
                proc = 'AA-12-NEF-012NEF001-I-18-2025'
            elif n_int in [251]:
                proc = 'AA-12-NEF-012NEF001-I-31-2025'
            elif n_int in [426]:
                proc = 'AA-12-NEF-012NEF001-I-45-2025'
            elif n_int in [507, 519]:
                proc = 'AA-12-NEF-012NEF001-I-67-2025'
            else:
                proc = 'AA-12-NEF-012NEF001-I-31-2025'
            return (proc, f'CS/AD/{num}/{yr}')

        return ('', '')

    # --- REPORTE CONSOLIDADO DIARIO Y MATRIZ ---
    def get_reporte_movimientos_matriz(self, mes: Optional[str] = "OCTUBRE", ano: Optional[int] = 2026, search: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcula el reporte diario consolidado por Clave + Lote:
        - Inventario Total Mensual = Inventario + Entrada_por_ajuste + Cantidad_recibida
        - Total Surtido = SUMA(Salidas_diarias) + Apoyo_institucional
        - Inventario Disponible = Inventario_total_mensual - Total_surtido
        """
        self._ensure_fefo_sin_caducados(mes=mes, ano=ano)
        session = self.get_session()
        try:
            target_mes = (mes or "OCTUBRE").upper()
            target_ano = int(ano or 2026)

            # 1. Obtener Entradas individuales (cada fila del Excel es una partida independiente)
            q_ent = session.query(EntradaMov).filter(EntradaMov.mes == target_mes, EntradaMov.ano == target_ano)
            entradas = q_ent.order_by(EntradaMov.row_index.asc(), EntradaMov.id.asc()).all()

            rows_list = []
            lote_index_map = {}

            for e in entradas:
                dias_dict = {str(d): 0.0 for d in range(1, 32)}
                if e.dias_salidas:
                    try:
                        parsed = json.loads(e.dias_salidas)
                        if isinstance(parsed, dict):
                            for dk, dv in parsed.items():
                                dias_dict[str(dk)] = float(dv or 0.0)
                    except Exception:
                        pass

                row_item = {
                    "id": e.id,
                    "row_index": e.row_index or 0,
                    "orden_suministro": e.folio_documento or "",
                    "folio_documento": e.folio_documento or "",
                    "procedimiento": e.procedimiento or "",
                    "contrato": e.contrato or "",
                    "registro_sanitario": e.registro_sanitario or "",
                    "almacen": e.almacen or "CS ALMACEN 2022",
                    "proveedor": e.proveedor or "",
                    "clave": e.clave.strip(),
                    "lote": e.lote.strip(),
                    "descripcion": e.descripcion or "",
                    "unidad_medida": e.unidad_medida or "PZA",
                    "fecha_ajuste": getattr(e, "fecha_ajuste", "") or "",
                    "fecha_entrada": e.fecha_entrada or "",
                    "fecha_fabricacion": e.fecha_fabricacion or "",
                    "fecha_caducidad": e.fecha_caducidad or "",
                    "inventario_inicial": float(e.inventario_inicial or 0.0),
                    "entrada_por_ajuste": float(e.entrada_ajuste or 0.0),
                    "entrada_ajuste": float(e.entrada_ajuste or 0.0),
                    "cantidad_recibida": float(e.cantidad_recibida or 0.0),
                    "dias": dias_dict,
                    "apoyo_institucional": float(e.apoyo_institucional or 0.0),
                    "fecha_apoyo": e.fecha_apoyo or "",
                    "observaciones_apoyo": e.fecha_apoyo or "",
                    "aviso_fefo": ""
                }
                rows_list.append(row_item)

                cve_lote_k = (e.clave.strip(), e.lote.strip())
                if cve_lote_k not in lote_index_map:
                    lote_index_map[cve_lote_k] = []
                lote_index_map[cve_lote_k].append(row_item)

            # 2. Salidas PDF
            salidas = session.query(SalidaPdfMov).filter(SalidaPdfMov.mes == target_mes, SalidaPdfMov.ano == target_ano).all()
            for s_item in salidas:
                cve_k = s_item.clave.strip()
                lot_k = (s_item.lote_asignado or "").strip()
                target_rows = lote_index_map.get((cve_k, lot_k), [])

                obs = s_item.observaciones or ""
                # Si vino del Excel base, ya está cargado exactamente en la fila correspondiente
                if "importada de base Excel" in obs or "Importado de base" in obs:
                    if s_item.aviso_fefo and ("AVISO FEFO" in s_item.aviso_fefo or "⚠️" in s_item.aviso_fefo):
                        for r_item in target_rows:
                            r_item["aviso_fefo"] = s_item.aviso_fefo
                    continue

                # Salida externa registrada por PDF manual
                if target_rows:
                    r_item = target_rows[0]
                    if s_item.dia:
                        d_str = str(s_item.dia)
                        if d_str in r_item["dias"]:
                            r_item["dias"][d_str] += float(s_item.cantidad or 0.0)
                    if s_item.aviso_fefo and ("AVISO FEFO" in s_item.aviso_fefo or "⚠️" in s_item.aviso_fefo):
                        r_item["aviso_fefo"] = s_item.aviso_fefo
                else:
                    cat_item = session.query(CatalogoInsumoMov).filter_by(clave=cve_k).first()
                    orphan = {
                        "id": None,
                        "row_index": 999999,
                        "orden_suministro": "",
                        "folio_documento": "",
                        "procedimiento": "",
                        "contrato": "",
                        "registro_sanitario": "",
                        "almacen": "CS ALMACEN 2022",
                        "proveedor": (cat_item.proveedor_predeterminado if cat_item else "") or "Remisión PDF",
                        "clave": cve_k,
                        "lote": lot_k or "SIN_LOTE",
                        "descripcion": s_item.descripcion or (cat_item.descripcion if cat_item else ""),
                        "unidad_medida": cat_item.unidad_medida if cat_item else "PZA",
                        "fecha_ajuste": "",
                        "fecha_entrada": "",
                        "fecha_fabricacion": "",
                        "fecha_caducidad": s_item.fecha_caducidad or "",
                        "inventario_inicial": 0.0,
                        "entrada_por_ajuste": 0.0,
                        "entrada_ajuste": 0.0,
                        "cantidad_recibida": 0.0,
                        "dias": {str(d): (float(s_item.cantidad or 0.0) if s_item.dia == d else 0.0) for d in range(1, 32)},
                        "apoyo_institucional": 0.0,
                        "fecha_apoyo": "",
                        "observaciones_apoyo": "",
                        "aviso_fefo": s_item.aviso_fefo or ""
                    }
                    rows_list.append(orphan)
                    if (cve_k, lot_k) not in lote_index_map:
                        lote_index_map[(cve_k, lot_k)] = []
                    lote_index_map[(cve_k, lot_k)].append(orphan)

            # 3. Apoyo Institucional
            apoyos = session.query(ApoyoInstitucionalMov).filter(ApoyoInstitucionalMov.mes == target_mes, ApoyoInstitucionalMov.ano == target_ano).all()
            for a_item in apoyos:
                obs = a_item.observaciones or ""
                if "importad" in obs.lower():
                    continue

                cve_k = a_item.clave.strip()
                lot_k = a_item.lote.strip()
                target_rows = lote_index_map.get((cve_k, lot_k), [])
                if target_rows:
                    target_rows[0]["apoyo_institucional"] += float(a_item.cantidad or 0.0)
                    if a_item.fecha:
                        existing_fa = target_rows[0].get("fecha_apoyo", "")
                        target_rows[0]["fecha_apoyo"] = f"{existing_fa} {a_item.fecha}".strip() if existing_fa else a_item.fecha
                        target_rows[0]["observaciones_apoyo"] = target_rows[0]["fecha_apoyo"]
                else:
                    cat_item = session.query(CatalogoInsumoMov).filter_by(clave=cve_k).first()
                    orphan = {
                        "id": None,
                        "row_index": 999999,
                        "orden_suministro": "",
                        "folio_documento": "",
                        "procedimiento": "",
                        "contrato": "",
                        "registro_sanitario": "",
                        "almacen": "CS ALMACEN 2022",
                        "proveedor": (cat_item.proveedor_predeterminado if cat_item else "") or "Apoyo Inst.",
                        "clave": cve_k,
                        "lote": lot_k,
                        "descripcion": a_item.descripcion or (cat_item.descripcion if cat_item else ""),
                        "unidad_medida": cat_item.unidad_medida if cat_item else "PZA",
                        "fecha_ajuste": "",
                        "fecha_entrada": "",
                        "fecha_fabricacion": "",
                        "fecha_caducidad": "",
                        "inventario_inicial": 0.0,
                        "entrada_por_ajuste": 0.0,
                        "entrada_ajuste": 0.0,
                        "cantidad_recibida": 0.0,
                        "dias": {str(d): 0.0 for d in range(1, 32)},
                        "apoyo_institucional": float(a_item.cantidad or 0.0),
                        "fecha_apoyo": a_item.fecha or "",
                        "observaciones_apoyo": a_item.fecha or "",
                        "aviso_fefo": ""
                    }
                    rows_list.append(orphan)
                    if (cve_k, lot_k) not in lote_index_map:
                        lote_index_map[(cve_k, lot_k)] = []
                    lote_index_map[(cve_k, lot_k)].append(orphan)

            # Procedimiento, Contrato, Orden de Suministro y Registro Sanitario respetan exactamente el valor almacenado o editado en la fila
            for item in rows_list:
                item["orden_suministro"] = str(item.get("orden_suministro") or "").strip()
                item["procedimiento"] = str(item.get("procedimiento") or "").strip()
                item["contrato"] = str(item.get("contrato") or "").strip()
                item["registro_sanitario"] = str(item.get("registro_sanitario") or "").strip()

            # 4. Cálculos automáticos de totales
            final_rows = []
            tot_ini = 0.0
            tot_ajuste = 0.0
            tot_recibida = 0.0
            tot_mensual = 0.0
            tot_salidas = 0.0
            tot_apoyo = 0.0
            tot_surtido = 0.0
            tot_disponible = 0.0
            totales_por_dia = {str(d): 0.0 for d in range(1, 32)}

            search_term = search.strip().lower() if search else None

            for item in rows_list:
                if search_term:
                    match = (
                        search_term in item["clave"].lower() or
                        search_term in item["lote"].lower() or
                        search_term in item["descripcion"].lower() or
                        search_term in item["proveedor"].lower() or
                        search_term in item["folio_documento"].lower() or
                        search_term in item.get("orden_suministro", "").lower() or
                        search_term in item.get("procedimiento", "").lower() or
                        search_term in item.get("contrato", "").lower() or
                        search_term in item.get("registro_sanitario", "").lower()
                    )
                    if not match:
                        continue

                # =Inventario + Entrada_por_ajuste + Cantidad_recibida
                inv_total_mensual = item["inventario_inicial"] + item["entrada_ajuste"] + item["cantidad_recibida"]
                
                # =SUMA(Salidas_diarias) + Apoyo_institucional
                salidas_diarias_sum = sum(item["dias"].values())
                total_surtido_calc = salidas_diarias_sum + item["apoyo_institucional"]
                
                # =Inventario_total_mensual - Total_surtido
                inv_disponible_calc = inv_total_mensual - total_surtido_calc

                item["inventario_total_mensual"] = round(inv_total_mensual, 2)
                item["salidas_diarias_total"] = round(salidas_diarias_sum, 2)
                item["total_surtido"] = round(total_surtido_calc, 2)
                item["inventario_disponible"] = round(inv_disponible_calc, 2)

                tot_ini += item["inventario_inicial"]
                tot_ajuste += item["entrada_ajuste"]
                tot_recibida += item["cantidad_recibida"]
                tot_mensual += inv_total_mensual
                tot_salidas += salidas_diarias_sum
                tot_apoyo += item["apoyo_institucional"]
                tot_surtido += total_surtido_calc
                tot_disponible += inv_disponible_calc

                for d in range(1, 32):
                    totales_por_dia[str(d)] += item["dias"][str(d)]

                final_rows.append(item)

            final_rows.sort(key=lambda x: x.get("row_index", 0) if x.get("row_index") else 999999)

            # Meses disponibles
            months_found = session.query(EntradaMov.mes).distinct().all()
            available_months = sorted(list(set([m[0] for m in months_found if m[0]] + ["SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"])))

            return {
                "mes": target_mes,
                "ano": target_ano,
                "days": list(range(1, 32)),
                "items": final_rows,
                "rows": final_rows,
                "total_rows": len(final_rows),
                "totales_por_dia": totales_por_dia,
                "available_months": available_months,
                "kpis": {
                    "total_claves": len(set(r["clave"] for r in final_rows)),
                    "total_lotes": len(final_rows),
                    "total_inventario_inicial": round(tot_ini, 2),
                    "total_entrada_ajuste": round(tot_ajuste, 2),
                    "total_cantidad_recibida": round(tot_recibida, 2),
                    "total_inventario_mensual": round(tot_mensual, 2),
                    "total_salidas_pdf": round(tot_salidas, 2),
                    "total_apoyo_institucional": round(tot_apoyo, 2),
                    "total_surtido": round(tot_surtido, 2),
                    "total_surtido_mensual": round(tot_surtido, 2),
                    "total_inventario_disponible": round(tot_disponible, 2)
                }
            }
        finally:
            session.close()

    def export_reporte_movimientos_excel(self, mes: Optional[str] = "OCTUBRE", ano: Optional[int] = 2026) -> io.BytesIO:
        """
        Genera el archivo Excel oficial propuesto con 5 hojas independientes y fórmulas dinámicas:
        1. Reporte Diario (con fórmulas =SUM(...) e inventarios calculados automáticamente).
        2. Entradas (captura manual).
        3. Salidas PDF (importación y validación FEFO).
        4. Apoyo Institucional (captura manual separada).
        5. Catálogos (claves, descripciones, proveedores y unidades).
        """
        matrix_data = self.get_reporte_movimientos_matriz(mes=mes, ano=ano)
        rows = matrix_data.get("rows", [])
        target_mes = matrix_data.get("mes", "OCTUBRE")
        target_ano = matrix_data.get("ano", 2026)

        wb = openpyxl.Workbook()

        header_fill = PatternFill(start_color="1E7145", end_color="1E7145", fill_type="solid")
        header_font = Font(name="Aptos Narrow", size=10, bold=True, color="FFFFFF")
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style="thin", color="135824"),
            right=Side(style="thin", color="135824"),
            top=Side(style="thin", color="135824"),
            bottom=Side(style="thin", color="135824")
        )
        data_border = Border(
            left=Side(style="thin", color="D1D5DB"),
            right=Side(style="thin", color="D1D5DB"),
            top=Side(style="thin", color="D1D5DB"),
            bottom=Side(style="thin", color="D1D5DB")
        )
        data_font = Font(name="Aptos Narrow", size=9)

        # ----------------------------------------------------
        # HOJA 1: Reporte Diario (Orden exacto INVETARIO SIMPLIFICADO OCT.xlsx)
        # ----------------------------------------------------
        ws1 = wb.active
        ws1.title = "Reporte Diario"

        totales_por_dia = matrix_data.get("totales_por_dia", {})
        active_days = sorted([
            d for d in range(1, 32)
            if float(totales_por_dia.get(str(d), 0.0) or 0.0) != 0.0
        ])
        export_days = active_days if active_days else list(range(1, 32))

        first_day_col = 16  # Columna P
        last_day_col = 15 + len(export_days)
        apoyo_col = last_day_col + 1
        surtido_col = last_day_col + 2
        disp_col = last_day_col + 3
        cad_col = last_day_col + 4
        fab_col = last_day_col + 5
        f_apoyo_col = last_day_col + 6
        total_cols = f_apoyo_col

        apoyo_let = get_column_letter(apoyo_col)
        surtido_let = get_column_letter(surtido_col)

        # Fila 1: Indicador de mes en O1 igual al documento ejemplo
        o1_cell = ws1["O1"]
        o1_cell.value = f"MES DE SURTIMIENTO: {target_mes}"
        o1_cell.font = Font(name="Aptos Narrow", size=8, bold=False, color="000000")
        o1_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Filas 2 y 3: Encabezados combinados exactamente en el orden del ejemplo
        ws1.row_dimensions[2].height = 27.2
        ws1.row_dimensions[3].height = 19.7

        left_headers = [
            "PROCEDIMIENTO",
            "CONTRATO",
            "ORDEN DE SUMINISTRO/INSTITUCION",
            "REGISTRO SANITARIO",
            "PROVEEDOR",
            "DESCRIPCION",
            "CLAVE",
            "LOTE",
            "UNIDAD DE MEDIDA",
            "FECHA DE AJUSTE",
            "ENTRADA POR AJUSTE",
            "FECHA DE ENTRADA",
            "CANTIDAD RECIBIDA",
            "INVENTARIO ",
            "INVENTARIO TOTAL MENSUAL",
        ]

        for col_idx, h_text in enumerate(left_headers, 1):
            c2 = ws1.cell(2, col_idx, h_text)
            c3 = ws1.cell(3, col_idx)
            for cell in (c2, c3):
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align
                cell.border = thin_border
            ws1.merge_cells(start_row=2, start_column=col_idx, end_row=3, end_column=col_idx)

        day_sub_fill = PatternFill(start_color="E2F0D9", end_color="E2F0D9", fill_type="solid")
        day_sub_font = Font(name="Aptos Narrow", size=9, bold=True, color="135824")
        for offset, d in enumerate(export_days):
            col_d = first_day_col + offset
            c2 = ws1.cell(2, col_d, None)
            c2.fill = header_fill
            c2.font = header_font
            c2.alignment = center_align
            c2.border = thin_border

            c3 = ws1.cell(3, col_d, f"{d:02d}")
            c3.number_format = "@"
            c3.fill = day_sub_fill
            c3.font = day_sub_font
            c3.alignment = center_align
            c3.border = thin_border

        right_headers = [
            "APOYO INSTITUCIONAL",
            "TOTAL SURTIDO",
            "INVENTARIO DISPONIBLE",
            "FECHA DE CADUCIDAD",
            "FECHA DE FABRICACION",
            "APOYO INSTITUCIONAL / FECHA",
        ]

        for offset, h_text in enumerate(right_headers, 1):
            col_idx = last_day_col + offset
            c2 = ws1.cell(2, col_idx, h_text)
            c3 = ws1.cell(3, col_idx)
            for cell in (c2, c3):
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align
                cell.border = thin_border
            ws1.merge_cells(start_row=2, start_column=col_idx, end_row=3, end_column=col_idx)

        first_data_row = 4
        curr_row = first_data_row
        for r in rows:
            ws1.cell(curr_row, 1, r.get("procedimiento", "")).alignment = Alignment(horizontal="left")
            ws1.cell(curr_row, 2, r.get("contrato", "")).alignment = Alignment(horizontal="left")
            ws1.cell(curr_row, 3, r.get("orden_suministro") or r.get("folio_documento", "")).alignment = Alignment(horizontal="center")
            ws1.cell(curr_row, 4, r.get("registro_sanitario", "")).alignment = Alignment(horizontal="center")
            ws1.cell(curr_row, 5, r.get("proveedor", "")).alignment = Alignment(horizontal="left")
            ws1.cell(curr_row, 6, r.get("descripcion", "")).alignment = Alignment(horizontal="left")
            ws1.cell(curr_row, 7, r.get("clave", "")).alignment = Alignment(horizontal="center")
            ws1.cell(curr_row, 8, r.get("lote", "")).alignment = Alignment(horizontal="center")
            ws1.cell(curr_row, 9, r.get("unidad_medida", "PZA")).alignment = Alignment(horizontal="center")
            ws1.cell(curr_row, 10, r.get("fecha_ajuste", "")).alignment = Alignment(horizontal="center")

            aju_val = float(r.get("entrada_ajuste", 0.0) or 0.0)
            c_aju = ws1.cell(curr_row, 11, aju_val if aju_val != 0.0 else None)
            c_aju.number_format = "#,##0"
            c_aju.alignment = Alignment(horizontal="center")

            ws1.cell(curr_row, 12, r.get("fecha_entrada", "")).alignment = Alignment(horizontal="center")

            rec_val = float(r.get("cantidad_recibida", 0.0) or 0.0)
            c_rec = ws1.cell(curr_row, 13, rec_val if rec_val != 0.0 else None)
            c_rec.number_format = "#,##0"
            c_rec.alignment = Alignment(horizontal="center")

            ini_val = float(r.get("inventario_inicial", 0.0) or 0.0)
            c_ini = ws1.cell(curr_row, 14, ini_val)
            c_ini.number_format = "#,##0"
            c_ini.alignment = Alignment(horizontal="center")

            c_tot_m = ws1.cell(curr_row, 15, f"=M{curr_row}+N{curr_row}+K{curr_row}")
            c_tot_m.number_format = "#,##0"
            c_tot_m.font = Font(name="Aptos Narrow", size=9, bold=True, color="1E3A8A")
            c_tot_m.alignment = Alignment(horizontal="center")

            for offset, d in enumerate(export_days):
                col_d = first_day_col + offset
                val_d = float(r.get("dias", {}).get(str(d), 0.0) or 0.0)
                c_d = ws1.cell(curr_row, col_d, val_d if val_d != 0.0 else None)
                c_d.number_format = "#,##0"
                c_d.alignment = Alignment(horizontal="center")

            apoyo_val = float(r.get("apoyo_institucional", 0.0) or 0.0)
            c_apoyo = ws1.cell(curr_row, apoyo_col, apoyo_val if apoyo_val != 0.0 else None)
            c_apoyo.number_format = "#,##0"
            c_apoyo.alignment = Alignment(horizontal="center")

            c_surt = ws1.cell(curr_row, surtido_col, f"=SUM(P{curr_row}:{apoyo_let}{curr_row})")
            c_surt.number_format = "#,##0"
            c_surt.font = Font(name="Aptos Narrow", size=9, bold=True, color="92400E")
            c_surt.alignment = Alignment(horizontal="center")

            c_disp = ws1.cell(curr_row, disp_col, f"=O{curr_row}-{surtido_let}{curr_row}")
            c_disp.number_format = "#,##0"
            c_disp.font = Font(name="Aptos Narrow", size=9, bold=True, color="065F46")
            c_disp.alignment = Alignment(horizontal="center")

            ws1.cell(curr_row, cad_col, r.get("fecha_caducidad", "")).alignment = Alignment(horizontal="center")
            ws1.cell(curr_row, fab_col, r.get("fecha_fabricacion", "")).alignment = Alignment(horizontal="center")
            ws1.cell(curr_row, f_apoyo_col, r.get("observaciones_apoyo", "") or r.get("fecha_apoyo", "")).alignment = Alignment(horizontal="left")

            for col in range(1, total_cols + 1):
                cell = ws1.cell(curr_row, col)
                if not cell.font or cell.font.name != "Aptos Narrow":
                    cell.font = data_font
                cell.border = data_border

            curr_row += 1

        last_data_row = curr_row - 1 if curr_row > first_data_row else first_data_row

        tot_row = curr_row
        ws1.row_dimensions[tot_row].height = 24
        tot_fill = PatternFill(start_color="E2F0D9", end_color="E2F0D9", fill_type="solid")
        tot_font = Font(name="Aptos Narrow", size=10, bold=True, color="1E7145")
        tot_border = Border(
            left=Side(style="thin", color="1E7145"),
            right=Side(style="thin", color="1E7145"),
            top=Side(style="thin", color="1E7145"),
            bottom=Side(style="double", color="1E7145")
        )

        ws1.cell(tot_row, 1, "TOTALES GENERALES").alignment = Alignment(horizontal="center")
        for c in range(2, 11):
            ws1.cell(tot_row, c, "").alignment = Alignment(horizontal="center")
        ws1.cell(tot_row, 12, "").alignment = Alignment(horizontal="center")

        for col_idx in [11, 13, 14, 15]:
            col_let = get_column_letter(col_idx)
            cell = ws1.cell(tot_row, col_idx, f"=SUM({col_let}{first_data_row}:{col_let}{last_data_row})")
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="center")

        for col_idx in range(first_day_col, last_day_col + 1):
            col_let = get_column_letter(col_idx)
            cell = ws1.cell(tot_row, col_idx, f"=SUM({col_let}{first_data_row}:{col_let}{last_data_row})")
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="center")

        for col_idx in [apoyo_col, surtido_col, disp_col]:
            col_let = get_column_letter(col_idx)
            cell = ws1.cell(tot_row, col_idx, f"=SUM({col_let}{first_data_row}:{col_let}{last_data_row})")
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="center")

        for col_idx in [cad_col, fab_col, f_apoyo_col]:
            ws1.cell(tot_row, col_idx, "-").alignment = Alignment(horizontal="center")

        for col in range(1, total_cols + 1):
            cell = ws1.cell(tot_row, col)
            cell.fill = tot_fill
            cell.font = tot_font
            cell.border = tot_border

        ws1.column_dimensions["A"].width = 25.4
        ws1.column_dimensions["B"].width = 14.6
        ws1.column_dimensions["C"].width = 23.1
        ws1.column_dimensions["D"].width = 23.1
        ws1.column_dimensions["E"].width = 31.9
        ws1.column_dimensions["F"].width = 29.6
        ws1.column_dimensions["G"].width = 12.9
        ws1.column_dimensions["H"].width = 15.3
        ws1.column_dimensions["I"].width = 17.0
        ws1.column_dimensions["J"].width = 10.3
        ws1.column_dimensions["K"].width = 10.0
        ws1.column_dimensions["L"].width = 13.0
        ws1.column_dimensions["M"].width = 13.0
        ws1.column_dimensions["N"].width = 9.6
        ws1.column_dimensions["O"].width = 12.3
        for col_idx in range(first_day_col, last_day_col + 1):
            ws1.column_dimensions[get_column_letter(col_idx)].width = 6.5
        ws1.column_dimensions[get_column_letter(apoyo_col)].width = 11.5
        ws1.column_dimensions[get_column_letter(surtido_col)].width = 11.5
        ws1.column_dimensions[get_column_letter(disp_col)].width = 13.0
        ws1.column_dimensions[get_column_letter(cad_col)].width = 13.7
        ws1.column_dimensions[get_column_letter(fab_col)].width = 13.7
        ws1.column_dimensions[get_column_letter(f_apoyo_col)].width = 25.3

        # ----------------------------------------------------
        # HOJA 2: Entradas (SOLAMENTE LO QUE ENTRÓ CON FECHA REGISTRADA)
        # ----------------------------------------------------
        ws2 = wb.create_sheet(title="Entradas")
        raw_entradas = self.get_entradas_movimientos(mes="TODOS", ano=None, only_ingresos=True)
        # Si no tiene una fecha de entrada o ajuste registrada en el sistema, no debe aparecer en la hoja Entradas
        raw_filtered = [
            e for e in raw_entradas
            if str(e.get("fecha_entrada") or "").strip() or str(e.get("fecha_ajuste") or "").strip()
        ]

        def _normalize_date_for_sort(d_str: str) -> str:
            d_str = str(d_str or "").strip()
            if not d_str:
                return "9999-99-99"
            m = re.match(r"^(\d{2})/(\d{2})/(\d{4})", d_str)
            if m:
                return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
            m2 = re.match(r"^(\d{4})-(\d{2})-(\d{2})", d_str)
            if m2:
                return f"{m2.group(1)}-{m2.group(2)}-{m2.group(3)}"
            return d_str

        # Desglosar dinámicamente si cualquier registro contuviera múltiples fechas separadas por espacios
        expanded_entradas = []
        for e in raw_filtered:
            f_ent = str(e.get("fecha_entrada") or "").strip()
            f_aju = str(e.get("fecha_ajuste") or "").strip()
            dates_ent = re.findall(r"\b\d{2,4}[/-]\d{2}[/-]\d{2,4}\b", f_ent)
            dates_aju = re.findall(r"\b\d{2,4}[/-]\d{2}[/-]\d{2,4}\b", f_aju)

            if len(dates_ent) > 1:
                qty_tot = float(e.get("cantidad_recibida", 0.0) or 0.0)
                split_qty = round(qty_tot / len(dates_ent), 2)
                for d in dates_ent:
                    ec = dict(e)
                    ec["fecha_entrada"] = _normalize_date_for_sort(d)
                    ec["cantidad_recibida"] = split_qty
                    expanded_entradas.append(ec)
            elif len(dates_aju) > 1:
                qty_tot = float(e.get("entrada_por_ajuste") if e.get("entrada_por_ajuste") is not None else (e.get("entrada_ajuste", 0.0) or 0.0))
                split_qty = round(qty_tot / len(dates_aju), 2)
                for d in dates_aju:
                    ec = dict(e)
                    ec["fecha_ajuste"] = _normalize_date_for_sort(d)
                    ec["entrada_ajuste"] = split_qty
                    ec["entrada_por_ajuste"] = split_qty
                    expanded_entradas.append(ec)
            else:
                expanded_entradas.append(e)

        entradas_data = expanded_entradas
        entradas_data.sort(
            key=lambda x: (
                _normalize_date_for_sort(x.get("fecha_entrada") or x.get("fecha_ajuste") or ""),
                x.get("row_index") if x.get("row_index") else 999999,
                x.get("id") or 0
            )
        )
        ent_headers = [
            "PROCEDIMIENTO",
            "CONTRATO",
            "ORDEN DE SUMINISTRO/INSTITUCION",
            "REGISTRO SANITARIO",
            "PROVEEDOR",
            "DESCRIPCION",
            "CLAVE",
            "LOTE",
            "UNIDAD DE MEDIDA",
            "FECHA DE AJUSTE",
            "ENTRADA POR AJUSTE",
            "FECHA DE ENTRADA",
            "CANTIDAD RECIBIDA",
            "INVENTARIO ",
            "INVENTARIO TOTAL MENSUAL",
            "APOYO INSTITUCIONAL",
            "FECHA DE CADUCIDAD",
            "FECHA DE FABRICACION",
            "APOYO INSTITUCIONAL / FECHA",
        ]
        ws2.row_dimensions[1].height = 27.2
        for idx, h in enumerate(ent_headers, 1):
            c = ws2.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        for r_idx, e in enumerate(entradas_data, 2):
            f_ent = str(e.get("fecha_entrada") or "").strip()
            f_aju = str(e.get("fecha_ajuste") or "").strip()
            e_rec = float(e.get("cantidad_recibida", 0.0) or 0.0)
            e_aju = float(e.get("entrada_por_ajuste") if e.get("entrada_por_ajuste") is not None else (e.get("entrada_ajuste", 0.0) or 0.0))

            val_f_ent = f_ent if f_ent else ""
            val_c_rec = e_rec if e_rec > 0 else (float(e.get("inventario_inicial", 0.0) or 0.0) if float(e.get("inventario_inicial", 0.0) or 0.0) > 0 and f_ent else None)

            val_f_aju = f_aju if f_aju else ""
            val_c_aju = e_aju if e_aju > 0 else (float(e.get("inventario_inicial", 0.0) or 0.0) if float(e.get("inventario_inicial", 0.0) or 0.0) > 0 and f_aju and not f_ent else None)

            ws2.cell(r_idx, 1, e.get("procedimiento") or e.get("no_procedimiento", ""))
            ws2.cell(r_idx, 2, e.get("contrato") or e.get("no_contrato", ""))
            ws2.cell(r_idx, 3, e.get("orden_suministro") or e.get("folio_documento", ""))
            ws2.cell(r_idx, 4, e.get("registro_sanitario", ""))
            ws2.cell(r_idx, 5, e.get("proveedor", ""))
            ws2.cell(r_idx, 6, e.get("descripcion", ""))
            ws2.cell(r_idx, 7, e.get("clave", ""))
            ws2.cell(r_idx, 8, e.get("lote", ""))
            ws2.cell(r_idx, 9, e.get("unidad_medida", "PZA"))

            # Columnas J, K, L, M, N, O
            ws2.cell(r_idx, 10, val_f_aju)
            ws2.cell(r_idx, 11, val_c_aju if val_c_aju is not None else None).number_format = "#,##0"
            ws2.cell(r_idx, 12, val_f_ent)
            ws2.cell(r_idx, 13, val_c_rec if val_c_rec is not None else None).number_format = "#,##0"
            ws2.cell(r_idx, 14, None).number_format = "#,##0"
            ws2.cell(r_idx, 15, f"=M{r_idx}+N{r_idx}+K{r_idx}").number_format = "#,##0"

            e_apo = float(e.get("apoyo_institucional", 0.0) or 0.0)
            ws2.cell(r_idx, 16, e_apo if e_apo != 0.0 else None).number_format = "#,##0"
            ws2.cell(r_idx, 17, e.get("fecha_caducidad", ""))
            ws2.cell(r_idx, 18, e.get("fecha_fabricacion", ""))
            ws2.cell(r_idx, 19, e.get("fecha_apoyo", "") or e.get("observaciones", ""))

            for c in range(1, 20):
                cell = ws2.cell(r_idx, c)
                cell.font = data_font
                cell.border = data_border

        # Fila de Totales en Hoja 2 Entradas
        last_ent_row = len(entradas_data) + 1 if len(entradas_data) > 0 else 1
        tot_ent_row = last_ent_row + 1
        ws2.row_dimensions[tot_ent_row].height = 22
        ws2.cell(tot_ent_row, 1, "TOTALES GENERALES").alignment = Alignment(horizontal="center")
        for col_idx in range(2, 10):
            ws2.cell(tot_ent_row, col_idx, "").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 10, "").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 11, f"=SUM(K2:K{last_ent_row})").number_format = "#,##0"
        ws2.cell(tot_ent_row, 12, "").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 13, f"=SUM(M2:M{last_ent_row})").number_format = "#,##0"
        ws2.cell(tot_ent_row, 14, "-").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 15, f"=SUM(O2:O{last_ent_row})").number_format = "#,##0"
        ws2.cell(tot_ent_row, 16, f"=SUM(P2:P{last_ent_row})").number_format = "#,##0"
        for col_idx in range(17, 20):
            ws2.cell(tot_ent_row, col_idx, "-").alignment = Alignment(horizontal="center")

        tot_ent_fill = PatternFill(start_color="E2F0D9", end_color="E2F0D9", fill_type="solid")
        tot_ent_font = Font(name="Aptos Narrow", size=10, bold=True, color="1E7145")
        tot_ent_border = Border(
            left=Side(style="thin", color="1E7145"),
            right=Side(style="thin", color="1E7145"),
            top=Side(style="thin", color="1E7145"),
            bottom=Side(style="double", color="1E7145")
        )
        for col in range(1, 20):
            c_tot = ws2.cell(tot_ent_row, col)
            c_tot.fill = tot_ent_fill
            c_tot.font = tot_ent_font
            c_tot.border = tot_ent_border

        ent_widths = [25.4, 14.6, 23.1, 23.1, 31.9, 29.6, 12.9, 15.3, 17.0, 10.3, 10.0, 13.0, 13.0, 10.0, 12.3, 11.5, 13.7, 13.7, 25.3]
        for idx, w in enumerate(ent_widths, 1):
            ws2.column_dimensions[get_column_letter(idx)].width = w

        # ----------------------------------------------------
        # HOJA 3: Salidas PDF (Histórico Completo)
        # ----------------------------------------------------
        ws3 = wb.create_sheet(title="Salidas PDF")
        salidas_pdf_data = sorted(
            self.get_salidas_pdf_movimientos(mes="TODOS", ano=None),
            key=lambda x: (x.get("fecha", ""), x.get("id") or 0)
        )
        sal_headers = [
            "ARCHIVO PDF", "FOLIO PEDIDO", "FECHA SURTIDO", "DÍA MES", "CLAVE",
            "DESCRIPCIÓN", "CANTIDAD SURTIDA", "LOTE SURTIDO (PDF)", "CADUCIDAD LOTE",
            "DESTINO / CLIENTE", "ESTADO VALIDACIÓN", "AVISO REGLA FEFO", "OBSERVACIONES"
        ]
        ws3.row_dimensions[1].height = 24
        for idx, h in enumerate(sal_headers, 1):
            c = ws3.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        for r_idx, s in enumerate(salidas_pdf_data, 2):
            ws3.cell(r_idx, 1, s.get("archivo_pdf", ""))
            ws3.cell(r_idx, 2, s.get("folio_pedido", ""))
            ws3.cell(r_idx, 3, s.get("fecha", ""))
            ws3.cell(r_idx, 4, int(s.get("dia", 1)))
            ws3.cell(r_idx, 5, s.get("clave", ""))
            ws3.cell(r_idx, 6, s.get("descripcion", ""))
            ws3.cell(r_idx, 7, float(s.get("cantidad", 0.0))).number_format = "#,##0"
            ws3.cell(r_idx, 8, s.get("lote_asignado", ""))
            ws3.cell(r_idx, 9, s.get("fecha_caducidad", ""))
            ws3.cell(r_idx, 10, s.get("cliente_destino", ""))
            ws3.cell(r_idx, 11, s.get("estado_validacion", "VALIDADO"))
            
            c_fefo = ws3.cell(r_idx, 12, s.get("aviso_fefo", ""))
            aviso_txt = str(s.get("aviso_fefo", "") or "")
            if "AVISO FEFO" in aviso_txt or "⚠️" in aviso_txt:
                c_fefo.fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
                c_fefo.font = Font(name="Calibri", size=9, bold=True, color="B45309")
            elif "Cumple FEFO" in aviso_txt or "✅" in aviso_txt:
                c_fefo.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
                c_fefo.font = Font(name="Calibri", size=9, bold=True, color="047857")

            ws3.cell(r_idx, 13, s.get("observaciones", ""))

            for c in range(1, 14):
                cell = ws3.cell(r_idx, c)
                if c != 12:
                    cell.font = data_font
                cell.border = data_border

        for col in range(1, 14):
            ws3.column_dimensions[get_column_letter(col)].width = 28 if col == 12 else 18

        # ----------------------------------------------------
        # # HOJA 4: Apoyo Institucional (Histórico Completo)
        # ----------------------------------------------------
        ws4 = wb.create_sheet(title="Apoyo Institucional")
        raw_apoyos = self.get_apoyos_institucionales(mes="TODOS", ano=None)

        # Desglosar dinámicamente si cualquier fila contuviera múltiples fechas separadas por espacios
        expanded_apoyos = []
        for a in raw_apoyos:
            f_apo = str(a.get("fecha") or "").strip()
            dates_apo = re.findall(r"\b\d{2,4}[/-]\d{2}[/-]\d{2,4}\b", f_apo)
            if len(dates_apo) > 1:
                tot_qty = float(a.get("cantidad", 0.0) or 0.0)
                split_qty = round(tot_qty / len(dates_apo), 2)
                for d in dates_apo:
                    ac = dict(a)
                    norm_d = _normalize_date_for_sort(d)
                    ac["fecha"] = norm_d
                    try:
                        ac["dia"] = int(norm_d.split("-")[2])
                    except Exception:
                        pass
                    ac["cantidad"] = split_qty
                    expanded_apoyos.append(ac)
            else:
                ac = dict(a)
                ac["fecha"] = _normalize_date_for_sort(f_apo)
                try:
                    ac["dia"] = int(ac["fecha"].split("-")[2])
                except Exception:
                    pass
                expanded_apoyos.append(ac)

        apoyos_data = sorted(
            expanded_apoyos,
            key=lambda x: (_normalize_date_for_sort(x.get("fecha", "")), x.get("id") or 0)
        )
        apoyo_headers = [
            "FOLIO / OFICIO", "FECHA", "DÍA MES", "INSTITUCIÓN RECEPTORA",
            "CLAVE", "LOTE", "DESCRIPCIÓN", "CANTIDAD DONADA / ENTREGADA", "OBSERVACIONES"
        ]
        ws4.row_dimensions[1].height = 24
        for idx, h in enumerate(apoyo_headers, 1):
            c = ws4.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        for r_idx, a in enumerate(apoyos_data, 2):
            ws4.cell(r_idx, 1, a.get("folio_documento", ""))
            ws4.cell(r_idx, 2, a.get("fecha", ""))
            ws4.cell(r_idx, 3, int(a.get("dia", 1)))
            ws4.cell(r_idx, 4, a.get("institucion", ""))
            ws4.cell(r_idx, 5, a.get("clave", ""))
            ws4.cell(r_idx, 6, a.get("lote", ""))
            ws4.cell(r_idx, 7, a.get("descripcion", ""))
            ws4.cell(r_idx, 8, float(a.get("cantidad", 0.0))).number_format = "#,##0"
            ws4.cell(r_idx, 9, a.get("observaciones", ""))

            for c in range(1, 10):
                cell = ws4.cell(r_idx, c)
                cell.font = data_font
                cell.border = data_border

        last_apo_row = len(apoyos_data) + 1 if len(apoyos_data) > 0 else 1
        tot_apo_row = last_apo_row + 1
        ws4.row_dimensions[tot_apo_row].height = 22
        ws4.cell(tot_apo_row, 1, "TOTALES GENERALES").alignment = Alignment(horizontal="center")
        for col_idx in range(2, 8):
            ws4.cell(tot_apo_row, col_idx, "").alignment = Alignment(horizontal="center")
        ws4.cell(tot_apo_row, 8, f"=SUM(H2:H{last_apo_row})").number_format = "#,##0"
        ws4.cell(tot_apo_row, 9, "").alignment = Alignment(horizontal="center")
        for c in range(1, 10):
            cell = ws4.cell(tot_apo_row, c)
            cell.font = Font(name="Aptos Narrow", size=9, bold=True)
            cell.border = data_border

        for col in range(1, 10):
            ws4.column_dimensions[get_column_letter(col)].width = 18

        # ----------------------------------------------------
        # HOJA 5: Catálogos
        # ----------------------------------------------------
        ws5 = wb.create_sheet(title="Catálogos")
        cat_data = self.get_catalogo_movimientos()
        prov_data = self.get_proveedores_movimientos()
        udm_data = self.get_unidades_medida_movimientos()

        cat_headers = ["CLAVE", "DESCRIPCIÓN", "UDM", "PROVEEDOR PREDETERMINADO", "PROCEDIMIENTO", "CONTRATO"]
        for idx, h in enumerate(cat_headers, 1):
            c = ws5.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.border = thin_border

        for r_idx, item in enumerate(cat_data, 2):
            ws5.cell(r_idx, 1, item.get("clave", ""))
            ws5.cell(r_idx, 2, item.get("descripcion", ""))
            ws5.cell(r_idx, 3, item.get("unidad_medida", "PZA"))
            ws5.cell(r_idx, 4, item.get("proveedor_predeterminado", ""))
            ws5.cell(r_idx, 5, item.get("procedimiento", ""))
            ws5.cell(r_idx, 6, item.get("contrato", ""))
            for c in range(1, 7):
                ws5.cell(r_idx, c).font = data_font
                ws5.cell(r_idx, c).border = data_border

        ws5.cell(1, 8, "PROVEEDORES").fill = header_fill
        ws5.cell(1, 8).font = header_font
        ws5.cell(1, 8).border = thin_border
        for r_idx, p in enumerate(prov_data, 2):
            ws5.cell(r_idx, 8, p.get("nombre", "")).font = data_font
            ws5.cell(r_idx, 8).border = data_border

        ws5.cell(1, 10, "UNIDADES DE MEDIDA").fill = header_fill
        ws5.cell(1, 10).font = header_font
        ws5.cell(1, 10).border = thin_border
        for r_idx, u in enumerate(udm_data, 2):
            ws5.cell(r_idx, 10, u.get("clave_unidad", "")).font = data_font
            ws5.cell(r_idx, 10).border = data_border

        ws5.column_dimensions["A"].width = 18
        ws5.column_dimensions["B"].width = 35
        ws5.column_dimensions["C"].width = 10
        ws5.column_dimensions["D"].width = 25
        ws5.column_dimensions["E"].width = 18
        ws5.column_dimensions["F"].width = 18
        ws5.column_dimensions["H"].width = 30
        ws5.column_dimensions["J"].width = 20

        output_stream = io.BytesIO()
        wb.save(output_stream)
        output_stream.seek(0)
        wb.close()
        return output_stream

    def import_inventario_simplificado_excel(self, file_source: Any, mes: Optional[str] = "OCTUBRE", ano: Optional[int] = 2026, source_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Importa base de datos Excel (nuevo archivo .xlsx subido por el usuario o archivo base predeterminado):
        1. Detección dinámica de hoja y cabeceras por nombre (compatible con plantilla nueva de 52 columnas y formato anterior).
        2. Registra Catálogo de Claves (con Procedimiento, Contrato, Reg. Sanitario), Proveedores y Unidades de Medida.
        3. Registra Entradas con Inventario Inicial, Entradas por Ajuste, Cantidades Recibidas, Fechas de Entrada y Fabricación.
        4. Registra Salidas Diarias columna por columna (Día 1 a 31) auditando y evaluando la Regla FEFO.
        5. Registra Apoyos Institucionales.
        """
        meses_num = {
            "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
            "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
        }
        target_mes = (mes or "OCTUBRE").upper()
        target_ano = int(ano or 2026)
        m_num = meses_num.get(target_mes, 10)
        source_label = source_name or "INVETARIO SIMPLIFICADO OCT.xlsx"

        wb = openpyxl.load_workbook(file_source, data_only=True)

        # 1. Selección inteligente de la hoja
        ws = None
        for sname in wb.sheetnames:
            s_up = sname.strip().upper()
            if s_up == target_mes or s_up == target_mes[:3] or target_mes[:3] in s_up:
                ws = wb[sname]
                break
        if ws is None:
            ws = wb.active

        session = self.get_session()
        try:
            # 2. Detección dinámica de cabeceras en filas 1 a 3
            headers_by_col = {}
            for c in range(1, ws.max_column + 1):
                texts = []
                for r in range(1, 4):
                    val = ws.cell(r, c).value
                    if val is not None:
                        texts.append(str(val).strip())
                headers_by_col[c] = " | ".join(texts)

            # Detectar columnas de días (números 1 a 31)
            day_cols = {}
            for c in range(1, ws.max_column + 1):
                for r in [3, 2, 1]:
                    val = ws.cell(r, c).value
                    if val is not None:
                        val_s = str(val).strip()
                        if val_s.isdigit() and 1 <= int(val_s) <= 31:
                            day_cols[c] = int(val_s)
                            break

            # Mapeo semántico de columnas
            col_map = {}
            for c, text in headers_by_col.items():
                if c in day_cols:
                    continue
                t = text.upper()
                if "PROCEDIMIENTO" in t:
                    col_map["procedimiento"] = c
                elif "CONTRATO" in t:
                    col_map["contrato"] = c
                elif "REGISTRO SANITARIO" in t or "REG. SANITARIO" in t:
                    col_map["registro_sanitario"] = c
                elif "ORDEN DE SUMINISTRO" in t or "ORDEN DE COMPRA" in t or ("ORDEN" in t and "PROVEEDOR" not in t):
                    col_map["orden"] = c
                elif "PROVEEDOR" in t or "LABORATORIO" in t:
                    col_map["proveedor"] = c
                elif "DESCRIPCION" in t or "DESCRIPCIÓN" in t or "CONCEPTO" in t:
                    col_map["descripcion"] = c
                elif "CLAVE" in t and "CORTA" not in t:
                    col_map["clave"] = c
                elif "LOTE" in t:
                    col_map["lote"] = c
                elif "UNIDAD DE MEDIDA" in t or "UDM" in t or "PRESENTACION" in t:
                    col_map["udm"] = c
                elif "FECHA DE AJUSTE" in t or "F. AJUSTE" in t or "F_AJUSTE" in t or "FECHA AJUSTE" in t:
                    col_map["fecha_ajuste"] = c
                elif "FECHA DE ENTRADA" in t or "F. ENTRADA" in t or "F_ENTRADA" in t or "FECHA ENTRADA" in t:
                    col_map["fecha_entrada"] = c
                elif "ENTRADA POR AJUSTE" in t or "AJUSTE" in t:
                    col_map["ajuste"] = c
                elif "FECHA DE FABRICACION" in t or "FABRICACION" in t or "FABRICACIÓN" in t or "RECEPCION" in t or "RECEPCIÓN" in t:
                    col_map["fecha_fabricacion"] = c
                elif "CANTIDAD RECIBIDA" in t or "RECIBIDA" in t:
                    col_map["recibida"] = c
                elif "INVENTARIO TOTAL" in t or "TOTAL MENSUAL" in t:
                    col_map["total_mensual"] = c
                elif "INVENTARIO" in t and "TOTAL" not in t and "DISPONIBLE" not in t:
                    col_map["inv_inicial"] = c
                elif "FECHA DE CADUCIDAD" in t or "CADUCIDAD" in t or "F_CAD" in t or "F. CAD" in t:
                    col_map["caducidad"] = c
                elif "APOYO INSTITUCIONAL / FECHA" in t or "FECHA APOYO" in t or "FECHA DE APOYO" in t:
                    col_map["fecha_apoyo"] = c
                elif "APOYO INSTITUCIONAL" in t or "APOYO" in t:
                    col_map["apoyo"] = c
                elif "TOTAL SURTIDO" in t or "SURTIDO" in t:
                    col_map["total_surtido"] = c
                elif "DISPONIBLE" in t or "INVENTARIO DISPONIBLE" in t:
                    col_map["disponible"] = c

            # Fallbacks inteligentes si no se encontraron cabeceras explícitas
            col1_txt = headers_by_col.get(1, "").upper()
            if "PROCEDIMIENTO" in col1_txt:
                # Plantilla ordenada oficial (INVETARIO SIMPLIFICADO OCT.xlsx)
                defaults = {
                    "procedimiento": 1, "contrato": 2, "orden": 3, "registro_sanitario": 4,
                    "proveedor": 5, "descripcion": 6, "clave": 7, "lote": 8, "udm": 9,
                    "fecha_ajuste": 10, "ajuste": 11, "fecha_entrada": 12, "recibida": 13,
                    "inv_inicial": 14, "total_mensual": 15
                }
                for k, v in defaults.items():
                    if k not in col_map:
                        col_map[k] = v
            else:
                # Plantilla base clásica (INVETARIO SIMPLIFICADO OCT.xlsx)
                defaults = {
                    "orden": 1, "proveedor": 2, "descripcion": 3, "clave": 4, "lote": 5,
                    "udm": 6, "ajuste": 7, "recibida": 8, "inv_inicial": 9, "total_mensual": 10,
                    "apoyo": 30, "total_surtido": 31, "disponible": 32, "caducidad": 33, "fecha_apoyo": 34
                }
                for k, v in defaults.items():
                    if k not in col_map:
                        col_map[k] = v

            # Si aún no hay días detectados en fila 3, usar columnas 11 a 29 por defecto
            if not day_cols:
                for c in range(11, 30):
                    val_h = str(ws.cell(3, c).value or '').strip()
                    if val_h.isdigit():
                        day_cols[c] = int(val_h)

            col_cve_idx = col_map.get("clave", 4)
            data_start_row = 4
            for check_r in range(2, 6):
                val_c = str(ws.cell(check_r, col_cve_idx).value or '').strip()
                if val_c and ("." in val_c or any(ch.isdigit() for ch in val_c)) and "CLAVE" not in val_c.upper():
                    data_start_row = check_r
                    break

            # Limpiar datos previos de este periodo
            session.query(EntradaMov).filter(EntradaMov.mes == target_mes, EntradaMov.ano == target_ano).delete()
            session.query(SalidaPdfMov).filter(SalidaPdfMov.mes == target_mes, SalidaPdfMov.ano == target_ano).delete()
            session.query(ApoyoInstitucionalMov).filter(ApoyoInstitucionalMov.mes == target_mes, ApoyoInstitucionalMov.ano == target_ano).delete()
            session.commit()

            rows_data = []
            lotes_por_clave = {}
            unique_claves = {}
            unique_provs = set()
            unique_udms = set()
            row_seq = 0

            for r in range(data_start_row, ws.max_row + 1):
                cve_val = ws.cell(r, col_cve_idx).value
                if cve_val is None or not str(cve_val).strip():
                    continue
                cve = str(cve_val).strip()
                if cve in ('-', 'TOTALES', 'TOTALES GENERALES', 'TOTAL', 'CLAVE') or 'TOTAL' in cve.upper():
                    continue
                first_cell = str(ws.cell(r, 1).value or '').strip().upper()
                if 'TOTAL' in first_cell:
                    continue
                lote = str(ws.cell(r, col_map.get("lote", 5)).value or '').strip()
                desc = str(ws.cell(r, col_map.get("descripcion", 3)).value or '').strip()
                prov = str(ws.cell(r, col_map.get("proveedor", 2)).value or '').strip()
                udm = str(ws.cell(r, col_map.get("udm", 6)).value or 'PZA').strip().upper()
                orden = str(ws.cell(r, col_map.get("orden", 1)).value or '').strip() if "orden" in col_map else ""

                proc = str(ws.cell(r, col_map["procedimiento"]).value or '').strip() if "procedimiento" in col_map else ""
                cont = str(ws.cell(r, col_map["contrato"]).value or '').strip() if "contrato" in col_map else ""
                reg_san = str(ws.cell(r, col_map["registro_sanitario"]).value or '').strip() if "registro_sanitario" in col_map else ""

                # REGLA ESTRICTA: El procedimiento y contrato SOLO se agregan si vienen en el Excel adjunto.
                # NUNCA autocompletar, ni derivar, ni inventar datos administrativos para filas donde estén vacíos.
                if not orden:
                    proc = ""
                    cont = ""
                    reg_san = ""

                cad_col = col_map.get("caducidad", 33)
                cad_raw = ws.cell(r, cad_col).value if cad_col else None
                if isinstance(cad_raw, (datetime.datetime, datetime.date)):
                    cad_str = cad_raw.strftime("%Y-%m-%d")
                else:
                    cad_str = str(cad_raw or '').strip()
                    if cad_str.endswith("00:00:00"):
                        cad_str = cad_str.replace("00:00:00", "").strip()
                cad_norm = normalize_caducidad(cad_str)

                f_aju_col = col_map.get("fecha_ajuste")
                f_aju_raw = ws.cell(r, f_aju_col).value if f_aju_col else None
                if isinstance(f_aju_raw, (datetime.datetime, datetime.date)):
                    f_aju = f_aju_raw.strftime("%Y-%m-%d")
                elif isinstance(f_aju_raw, (int, float)) and 40000 <= f_aju_raw <= 60000:
                    f_aju = (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(f_aju_raw))).strftime("%Y-%m-%d")
                else:
                    f_aju = str(f_aju_raw or '').strip()
                    if f_aju.endswith("00:00:00"):
                        f_aju = f_aju.replace("00:00:00", "").strip()
                    if f_aju.upper() in ("-", "--", "---", "NONE", "NULL", "N/A", "S/F", "NAN"):
                        f_aju = ""

                f_ent_col = col_map.get("fecha_entrada")
                f_ent_raw = ws.cell(r, f_ent_col).value if f_ent_col else None
                if isinstance(f_ent_raw, (datetime.datetime, datetime.date)):
                    f_ent = f_ent_raw.strftime("%Y-%m-%d")
                else:
                    f_ent = str(f_ent_raw or '').strip()
                    if f_ent.endswith("00:00:00"):
                        f_ent = f_ent.replace("00:00:00", "").strip()
                    if f_ent.upper() in ("-", "--", "---", "NONE", "NULL", "N/A", "S/F", "NAN"):
                        f_ent = ""

                f_fab_col = col_map.get("fecha_fabricacion")
                f_fab_raw = ws.cell(r, f_fab_col).value if f_fab_col else None
                if isinstance(f_fab_raw, (datetime.datetime, datetime.date)):
                    f_fab = f_fab_raw.strftime("%Y-%m-%d")
                else:
                    f_fab = str(f_fab_raw or '').strip()
                    if f_fab.endswith("00:00:00"):
                        f_fab = f_fab.replace("00:00:00", "").strip()

                try:
                    inv_ini = float(ws.cell(r, col_map.get("inv_inicial", 9)).value or 0.0)
                except:
                    inv_ini = 0.0
                try:
                    ajuste = float(ws.cell(r, col_map.get("ajuste", 7)).value or 0.0)
                except:
                    ajuste = 0.0
                try:
                    recibida = float(ws.cell(r, col_map.get("recibida", 8)).value or 0.0)
                except:
                    recibida = 0.0
                try:
                    apoyo = float(ws.cell(r, col_map.get("apoyo", 30)).value or 0.0)
                except:
                    apoyo = 0.0

                fecha_apoyo_col = col_map.get("fecha_apoyo", 34)
                col_fecha_apoyo_raw = ws.cell(r, fecha_apoyo_col).value if fecha_apoyo_col else None
                if isinstance(col_fecha_apoyo_raw, (datetime.datetime, datetime.date)):
                    col_fecha_apoyo_val = col_fecha_apoyo_raw.strftime("%d/%m/%Y")
                else:
                    col_fecha_apoyo_val = str(col_fecha_apoyo_raw or '').strip()
                    if col_fecha_apoyo_val.endswith("00:00:00"):
                        col_fecha_apoyo_val = col_fecha_apoyo_val.replace("00:00:00", "").strip()

                salidas_fila = {}
                for col_idx, dia_num in day_cols.items():
                    v = ws.cell(r, col_idx).value
                    try:
                        fv = float(v or 0.0)
                        if fv > 0:
                            salidas_fila[dia_num] = fv
                    except:
                        pass

                row_seq += 1
                row_obj = {
                    "row_index": row_seq,
                    "orden": orden,
                    "procedimiento": proc,
                    "contrato": cont,
                    "registro_sanitario": reg_san,
                    "prov": prov,
                    "desc": desc,
                    "cve": cve,
                    "lote": lote,
                    "udm": udm,
                    "fecha_ajuste": f_aju,
                    "fecha_entrada": f_ent,
                    "fecha_fabricacion": f_fab,
                    "inv_ini": inv_ini,
                    "ajuste": ajuste,
                    "recibida": recibida,
                    "cad_str": cad_str,
                    "cad_norm": cad_norm,
                    "apoyo": apoyo,
                    "col_fecha_apoyo": col_fecha_apoyo_val,
                    "salidas": salidas_fila
                }
                rows_data.append(row_obj)

                if cve not in unique_claves:
                    unique_claves[cve] = {
                        "desc": desc,
                        "udm": udm,
                        "prov": prov,
                        "proc": proc,
                        "cont": cont,
                        "reg_san": reg_san
                    }
                if prov:
                    unique_provs.add(prov)
                if udm:
                    unique_udms.add(udm)

                if cve not in lotes_por_clave:
                    lotes_por_clave[cve] = []
                lotes_por_clave[cve].append({
                    "lote": lote,
                    "cad_str": cad_str,
                    "cad_norm": cad_norm,
                    "stock": inv_ini + ajuste + recibida
                })

            for cve in lotes_por_clave:
                lotes_por_clave[cve].sort(key=lambda x: x["cad_norm"])

            # 3. Registrar / Actualizar Catálogos
            for cve, info in unique_claves.items():
                cat = session.query(CatalogoInsumoMov).filter_by(clave=cve).first()
                if not cat:
                    cat = CatalogoInsumoMov(
                        clave=cve,
                        descripcion=info["desc"],
                        unidad_medida=info["udm"],
                        proveedor_predeterminado=info["prov"],
                        procedimiento=info.get("proc", ""),
                        contrato=info.get("cont", ""),
                        registro_sanitario=info.get("reg_san", "")
                    )
                    session.add(cat)
                else:
                    if not cat.descripcion and info["desc"]:
                        cat.descripcion = info["desc"]
                    if not cat.proveedor_predeterminado and info["prov"]:
                        cat.proveedor_predeterminado = info["prov"]
                    if info.get("proc"):
                        cat.procedimiento = info["proc"]
                    if info.get("cont"):
                        cat.contrato = info["cont"]
                    if info.get("reg_san"):
                        cat.registro_sanitario = info["reg_san"]

            for p_name in unique_provs:
                prov_rec = session.query(ProveedorMov).filter_by(nombre=p_name).first()
                if not prov_rec:
                    session.add(ProveedorMov(nombre=p_name))

            for u_name in unique_udms:
                udm_rec = session.query(UnidadMedidaMov).filter_by(clave_unidad=u_name).first()
                if not udm_rec:
                    session.add(UnidadMedidaMov(clave_unidad=u_name))

            session.commit()

            # 4. Insertar Entradas, Salidas y Apoyos
            total_entradas = 0
            total_salidas = 0
            total_apoyos = 0
            total_fefo_alertas = 0

            for it in rows_data:
                entrada_rec = EntradaMov(
                    row_index=it["row_index"],
                    folio_documento=it["orden"],
                    procedimiento=it["procedimiento"],
                    contrato=it["contrato"],
                    registro_sanitario=it["registro_sanitario"],
                    almacen="CS ALMACEN 2022",
                    proveedor=it["prov"],
                    clave=it["cve"],
                    lote=it["lote"],
                    descripcion=it["desc"],
                    unidad_medida=it["udm"],
                    fecha_ajuste=it.get("fecha_ajuste", ""),
                    fecha_entrada=it["fecha_entrada"],
                    fecha_caducidad=it["cad_str"],
                    fecha_fabricacion=it["fecha_fabricacion"],
                    inventario_inicial=it["inv_ini"],
                    entrada_ajuste=it["ajuste"],
                    cantidad_recibida=it["recibida"],
                    dias_salidas=json.dumps(it["salidas"]),
                    apoyo_institucional=it["apoyo"],
                    fecha_apoyo=it["col_fecha_apoyo"],
                    mes=target_mes,
                    ano=target_ano,
                    observaciones=f"Importado de base {source_label}"
                )
                session.add(entrada_rec)
                total_entradas += 1

                cve_candidates = lotes_por_clave.get(it["cve"], [])

                for dia_num, cant in it["salidas"].items():
                    mov_date = f"{target_ano}-{m_num:02d}-{dia_num:02d}"
                    valid_candidates = [
                        x for x in cve_candidates
                        if x["stock"] > 0
                        and x["cad_norm"] != "9999-12-31"
                        and not is_caducidad_vencida(x["cad_norm"], mov_date)
                    ]
                    fefo_candidate = valid_candidates[0] if len(valid_candidates) > 0 else None

                    if is_caducidad_vencida(it["cad_norm"], mov_date):
                        aviso_fefo = f"ℹ️ Lote '{it['lote']}' (cad: {it['cad_str'] or 'S/F'}): material caducado, sin alerta FEFO."
                        estado_val = "VALIDADO"
                    elif fefo_candidate and fefo_candidate["lote"].upper() != it["lote"].upper() and fefo_candidate["cad_norm"] < it["cad_norm"]:
                        aviso_fefo = f"⚠️ AVISO FEFO: Se dio salida al lote '{it['lote']}' (cad: {it['cad_str'] or 'S/F'}), pero en almacén existe el lote '{fefo_candidate['lote']}' con caducidad más próxima ({fefo_candidate['cad_str']})."
                        estado_val = "AVISO_FEFO"
                        total_fefo_alertas += 1
                    else:
                        aviso_fefo = f"✅ Cumple FEFO: El lote '{it['lote']}' es el de caducidad más próxima ({it['cad_str']})."
                        estado_val = "FEFO_OPTIMO"

                    salida_rec = SalidaPdfMov(
                        archivo_pdf=source_label,
                        folio_pedido=it["orden"] or f"SALIDA-DIA-{dia_num:02d}",
                        fecha=f"{target_ano}-{m_num:02d}-{dia_num:02d}",
                        dia=dia_num,
                        mes=target_mes,
                        ano=target_ano,
                        clave=it["cve"],
                        descripcion=it["desc"],
                        cantidad=cant,
                        lote_asignado=it["lote"],
                        fecha_caducidad=it["cad_str"],
                        cliente_destino="DISPENSARIO / FARMACIA",
                        estado_validacion=estado_val,
                        aviso_fefo=aviso_fefo,
                        observaciones=f"Salida día {dia_num} importada de base Excel"
                    )
                    session.add(salida_rec)
                    total_salidas += 1

                if it["apoyo"] > 0:
                    fecha_apoyo = it["col_fecha_apoyo"] or f"{target_ano}-{m_num:02d}-15"
                    dia_apoyo = 15
                    for candidate_d in [16, 8, 6, 5, 15]:
                        if f"{candidate_d:02d}" in fecha_apoyo or str(candidate_d) in fecha_apoyo:
                            dia_apoyo = candidate_d
                            break

                    apoyo_rec = ApoyoInstitucionalMov(
                        clave=it["cve"],
                        lote=it["lote"],
                        descripcion=it["desc"],
                        cantidad=it["apoyo"],
                        institucion="SECRETARIA DE SALUD / OTRA INSTITUCION",
                        fecha=fecha_apoyo,
                        dia=dia_apoyo,
                        mes=target_mes,
                        ano=target_ano,
                        folio_documento=it["orden"],
                        observaciones=f"Apoyo importado. Fechas registradas: {it['col_fecha_apoyo']}"
                    )
                    session.add(apoyo_rec)
                    total_apoyos += 1

            session.commit()
            return {
                "status": "success",
                "message": f"Base de inventario ({source_label}) importada exitosamente: {total_entradas} entradas registradas, {total_salidas} salidas distribuidas ({total_fefo_alertas} alertas FEFO), {total_apoyos} apoyos y {len(unique_claves)} claves de catálogo.",
                "total_entradas": total_entradas,
                "total_salidas": total_salidas,
                "total_apoyos": total_apoyos,
                "total_fefo_alertas": total_fefo_alertas,
                "total_claves": len(unique_claves),
                "total_proveedores": len(unique_provs),
                "total_udms": len(unique_udms)
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # =========================================================================
    # AUTENTICACIÓN, SESIONES Y ADMINISTRACIÓN DE USUARIOS Y PERMISOS
    # =========================================================================

    def seed_default_users(self):
        """Inicializa el Superadministrador y el usuario Operador si la tabla de usuarios está vacía."""
        session = self.get_session()
        try:
            count = session.query(UserAccount).count()
            if count > 0:
                return

            superadmin_user = UserAccount(
                username="admin",
                nombre_completo="Superadministrador",
                password_hash=hash_password("admin123"),
                rol="superadmin",
                is_superadmin=True,
                activo=True,
                permisos_json=json.dumps(ROLE_PRESETS["superadmin"], ensure_ascii=False),
            )
            operador_user = UserAccount(
                username="operador",
                nombre_completo="Operador Inventario y Marbetes",
                password_hash=hash_password("operador123"),
                rol="operador",
                is_superadmin=False,
                activo=True,
                permisos_json=json.dumps(ROLE_PRESETS["operador"], ensure_ascii=False),
            )
            session.add(superadmin_user)
            session.add(operador_user)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def _sanitize_permissions(raw_perms: Optional[Dict[str, Any]], is_superadmin: bool = False) -> Dict[str, bool]:
        if is_superadmin:
            return {k: True for k in ALL_PERMISSION_KEYS}
        clean = {}
        src = raw_perms if isinstance(raw_perms, dict) else {}
        for k in ALL_PERMISSION_KEYS:
            clean[k] = bool(src.get(k, False))
        return clean

    @staticmethod
    def _detect_role_name(perms: Dict[str, bool], is_superadmin: bool, requested_rol: Optional[str] = None) -> str:
        if is_superadmin:
            return "superadmin"
        for preset_name in ("operador", "capturista_control", "consulta"):
            if perms == ROLE_PRESETS[preset_name]:
                return preset_name
        if requested_rol and requested_rol not in ("superadmin", "operador", "capturista_control", "consulta"):
            return requested_rol
        return "personalizado"

    def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str = "",
        user_agent: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Valida credenciales, crea sesión segura y retorna token + perfil del usuario."""
        uname = (username or "").strip().lower()
        if not uname or not password:
            return None

        session = self.get_session()
        try:
            user = session.query(UserAccount).filter(func.lower(UserAccount.username) == uname).first()
            if not user or not verify_password(password, user.password_hash):
                return None

            if not user.activo:
                raise ValueError("Esta cuenta se encuentra desactivada. Contacte al Superadministrador.")

            now = datetime.datetime.utcnow()
            # Limpiar sesiones caducadas
            session.query(UserSession).filter(UserSession.expires_at < now).delete(synchronize_session=False)

            token = secrets.token_urlsafe(48)
            expires_at = now + datetime.timedelta(days=7)
            user_session = UserSession(
                token=token,
                user_id=user.id,
                ip_address=(ip_address or "")[:80],
                user_agent=(user_agent or "")[:255],
                created_at=now,
                expires_at=expires_at,
            )
            user.ultimo_acceso = datetime.datetime.now()
            session.add(user_session)
            session.commit()

            user_dict = user.to_dict()
            self.log_execution(
                operation="LOGIN",
                status="SUCCESS",
                file_name=user.username,
                records_count=1,
                details=f"Inicio de sesión exitoso de '{user.username}' ({user.rol})",
            )
            return {
                "token": token,
                "user": user_dict,
                "expires_at": expires_at.isoformat(),
            }
        except ValueError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_by_session_token(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Obtiene el usuario activo correspondiente a un token de sesión vigente."""
        if not token:
            return None
        session = self.get_session()
        try:
            now = datetime.datetime.utcnow()
            sess = session.query(UserSession).filter(
                UserSession.token == token,
                UserSession.expires_at >= now,
            ).first()
            if not sess:
                return None

            user = session.query(UserAccount).filter(
                UserAccount.id == sess.user_id,
                UserAccount.activo == True,
            ).first()
            if not user:
                return None
            return user.to_dict()
        finally:
            session.close()

    def logout_session(self, token: Optional[str]) -> bool:
        """Cierra e invalida una sesión activa."""
        if not token:
            return False
        session = self.get_session()
        try:
            deleted = session.query(UserSession).filter(UserSession.token == token).delete()
            session.commit()
            return deleted > 0
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def list_users(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todos los usuarios del sistema."""
        session = self.get_session()
        try:
            q = session.query(UserAccount)
            if search and search.strip():
                term = f"%{search.strip().lower()}%"
                q = q.filter(
                    or_(
                        func.lower(UserAccount.username).like(term),
                        func.lower(UserAccount.nombre_completo).like(term),
                        func.lower(UserAccount.rol).like(term),
                    )
                )
            users = q.order_by(UserAccount.is_superadmin.desc(), UserAccount.id.asc()).all()
            return [u.to_dict() for u in users]
        finally:
            session.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        session = self.get_session()
        try:
            u = session.query(UserAccount).filter(UserAccount.id == user_id).first()
            return u.to_dict() if u else None
        finally:
            session.close()

    def create_user(self, data: Dict[str, Any], actor_username: str = "admin") -> Dict[str, Any]:
        """Crea un nuevo usuario con permisos granulares."""
        session = self.get_session()
        try:
            username = re.sub(r"\s+", "", str(data.get("username") or "").strip().lower())
            if len(username) < 3:
                raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
            if not re.match(r"^[a-z0-9._-]+$", username):
                raise ValueError("El nombre de usuario solo puede contener letras, números, puntos, guiones o guion bajo.")

            existing = session.query(UserAccount).filter(func.lower(UserAccount.username) == username).first()
            if existing:
                raise ValueError(f"El usuario '{username}' ya existe en el sistema.")

            password = str(data.get("password") or "")
            if len(password) < 4:
                raise ValueError("La contraseña debe tener al menos 4 caracteres.")

            nombre_completo = str(data.get("nombre_completo") or username).strip() or username
            is_superadmin = bool(data.get("is_superadmin", False))
            activo = bool(data.get("activo", True))

            clean_perms = self._sanitize_permissions(data.get("permisos"), is_superadmin=is_superadmin)
            rol = self._detect_role_name(clean_perms, is_superadmin=is_superadmin, requested_rol=data.get("rol"))

            new_user = UserAccount(
                username=username,
                nombre_completo=nombre_completo,
                password_hash=hash_password(password),
                rol=rol,
                is_superadmin=is_superadmin,
                activo=activo,
                permisos_json=json.dumps(clean_perms, ensure_ascii=False),
            )
            session.add(new_user)
            session.commit()
            res = new_user.to_dict()

            self.log_execution(
                operation="USER_CREATE",
                status="SUCCESS",
                file_name=username,
                records_count=1,
                details=f"Usuario '{username}' ({rol}) creado por '{actor_username}'.",
            )
            return res
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_user(
        self,
        user_id: int,
        data: Dict[str, Any],
        current_user_id: int,
        actor_username: str = "admin",
    ) -> Dict[str, Any]:
        """Actualiza datos, estado, contraseña opcional y permisos granulares de un usuario."""
        session = self.get_session()
        try:
            user = session.query(UserAccount).filter(UserAccount.id == user_id).first()
            if not user:
                raise LookupError("Usuario no encontrado.")

            if "username" in data and data["username"] is not None:
                new_uname = re.sub(r"\s+", "", str(data["username"]).strip().lower())
                if len(new_uname) < 3:
                    raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
                if not re.match(r"^[a-z0-9._-]+$", new_uname):
                    raise ValueError("El nombre de usuario solo puede contener letras, números, puntos, guiones o guion bajo.")
                dup = session.query(UserAccount).filter(
                    func.lower(UserAccount.username) == new_uname,
                    UserAccount.id != user_id,
                ).first()
                if dup:
                    raise ValueError(f"El nombre de usuario '{new_uname}' ya está en uso.")
                user.username = new_uname

            if "nombre_completo" in data and data["nombre_completo"] is not None:
                nc = str(data["nombre_completo"]).strip()
                if nc:
                    user.nombre_completo = nc

            new_activo = bool(data["activo"]) if "activo" in data and data["activo"] is not None else user.activo
            new_super = bool(data["is_superadmin"]) if "is_superadmin" in data and data["is_superadmin"] is not None else user.is_superadmin

            # Reglas de protección contra bloqueo accidental
            if user.id == current_user_id:
                if not new_activo:
                    raise ValueError("No puedes desactivar tu propia cuenta mientras tienes sesión iniciada.")
                if user.is_superadmin and not new_super:
                    raise ValueError("No puedes quitarte el rol de Superadministrador a ti mismo.")

            if user.is_superadmin and (not new_super or not new_activo):
                other_supers = session.query(UserAccount).filter(
                    UserAccount.id != user.id,
                    UserAccount.is_superadmin == True,
                    UserAccount.activo == True,
                ).count()
                if other_supers == 0:
                    raise ValueError("Debe existir al menos un Superadministrador activo en el sistema.")

            user.activo = new_activo
            user.is_superadmin = new_super

            raw_perms = data.get("permisos")
            if raw_perms is not None or "is_superadmin" in data:
                base_perms = raw_perms if raw_perms is not None else user.get_effective_permissions()
                clean_perms = self._sanitize_permissions(base_perms, is_superadmin=user.is_superadmin)
                user.permisos_json = json.dumps(clean_perms, ensure_ascii=False)
                user.rol = self._detect_role_name(clean_perms, is_superadmin=user.is_superadmin, requested_rol=data.get("rol"))

            new_password = str(data.get("password") or "")
            if new_password:
                if len(new_password) < 4:
                    raise ValueError("La nueva contraseña debe tener al menos 4 caracteres.")
                user.password_hash = hash_password(new_password)

            if not user.activo:
                session.query(UserSession).filter(UserSession.user_id == user.id).delete()

            session.commit()
            res = user.to_dict()

            self.log_execution(
                operation="USER_UPDATE",
                status="SUCCESS",
                file_name=user.username,
                records_count=1,
                details=f"Usuario '{user.username}' actualizado por '{actor_username}' (rol={user.rol}, activo={user.activo}).",
            )
            return res
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def change_own_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Permite al usuario autenticado cambiar su propia contraseña validando la actual."""
        if not new_password or len(new_password) < 4:
            raise ValueError("La nueva contraseña debe tener al menos 4 caracteres.")
        session = self.get_session()
        try:
            user = session.query(UserAccount).filter(UserAccount.id == user_id).first()
            if not user:
                raise LookupError("Usuario no encontrado.")
            if not verify_password(current_password, user.password_hash):
                raise ValueError("La contraseña actual es incorrecta.")
            user.password_hash = hash_password(new_password)
            session.commit()
            self.log_execution(
                operation="PASSWORD_CHANGE",
                status="SUCCESS",
                file_name=user.username,
                records_count=1,
                details=f"El usuario '{user.username}' actualizó su contraseña.",
            )
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_user(self, user_id: int, current_user_id: int, actor_username: str = "admin") -> bool:
        """Elimina un usuario del sistema validando que no sea la propia cuenta ni el último superadmin."""
        if user_id == current_user_id:
            raise ValueError("No puedes eliminar tu propia cuenta activa.")

        session = self.get_session()
        try:
            user = session.query(UserAccount).filter(UserAccount.id == user_id).first()
            if not user:
                return False

            if user.is_superadmin:
                other_supers = session.query(UserAccount).filter(
                    UserAccount.id != user.id,
                    UserAccount.is_superadmin == True,
                    UserAccount.activo == True,
                ).count()
                if other_supers == 0:
                    raise ValueError("No se puede eliminar al único Superadministrador activo del sistema.")

            uname = user.username
            session.query(UserSession).filter(UserSession.user_id == user.id).delete()
            session.delete(user)
            session.commit()

            self.log_execution(
                operation="USER_DELETE",
                status="SUCCESS",
                file_name=uname,
                records_count=1,
                details=f"Usuario '{uname}' eliminado por '{actor_username}'.",
            )
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


