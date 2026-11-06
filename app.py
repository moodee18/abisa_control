import os
import re
import shutil
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request, Response, Depends, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from database import (
    DatabaseManager,
    MovimientoRecord,
    InsumoRecord,
    ALL_PERMISSIONS_CATALOG,
    ROLE_PRESETS,
)
from processor import DataProcessor

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

app = FastAPI(title="SIIA Abisalud - Gestión de Inventario y Catálogo", version="2.0.0")

db = DatabaseManager()

# Modelos Pydantic para validación de entrada
class InsumoCreateRequest(BaseModel):
    clave: str
    descripcion: Optional[str] = ""
    presentacion: Optional[str] = ""
    lote: Optional[str] = ""
    caducidad: Optional[str] = ""
    cantidad: float = 0.0
    unidad_medida: Optional[str] = "PZA"
    precio_unitario: float = 0.0
    importe_total: Optional[float] = None
    almacen_origen: Optional[str] = ""
    almacen_destino: Optional[str] = ""
    proveedor: Optional[str] = ""
    folio_documento: Optional[str] = ""
    fecha_documento: Optional[str] = ""

class InsumoUpdateRequest(BaseModel):
    clave: Optional[str] = None
    descripcion: Optional[str] = None
    presentacion: Optional[str] = None
    lote: Optional[str] = None
    caducidad: Optional[str] = None
    cantidad: Optional[float] = None
    unidad_medida: Optional[str] = None
    precio_unitario: Optional[float] = None
    importe_total: Optional[float] = None
    almacen_origen: Optional[str] = None
    almacen_destino: Optional[str] = None
    proveedor: Optional[str] = None
    folio_documento: Optional[str] = None
    fecha_documento: Optional[str] = None

# Modelos para Control de Inventario por Movimientos
class CatalogoMovRequest(BaseModel):
    clave: str
    descripcion: str
    unidad_medida: Optional[str] = "PZA"
    proveedor_predeterminado: Optional[str] = ""
    procedimiento: Optional[str] = ""
    contrato: Optional[str] = ""
    registro_sanitario: Optional[str] = ""

class ProveedorMovRequest(BaseModel):
    nombre: str
    rfc: Optional[str] = ""
    contacto: Optional[str] = ""

class UnidadMedidaMovRequest(BaseModel):
    clave_unidad: Optional[str] = ""
    codigo: Optional[str] = ""
    descripcion: Optional[str] = ""

class PedidoItemUpdateRequest(BaseModel):
    id: Optional[int] = None
    clave: str
    descripcion: Optional[str] = ""
    cantidad: float = 0.0
    lote_asignado: Optional[str] = ""
    lote: Optional[str] = ""
    fecha_caducidad: Optional[str] = ""

class PedidoCompletoUpdateRequest(BaseModel):
    folio_actual: str
    archivo_actual: Optional[str] = ""
    mes_actual: Optional[str] = "OCTUBRE"
    ano_actual: Optional[int] = 2026
    nuevo_folio: Optional[str] = None
    nueva_fecha: Optional[str] = None
    nuevo_dia: Optional[int] = None
    nuevo_mes: Optional[str] = None
    nuevo_ano: Optional[int] = None
    nuevo_archivo: Optional[str] = None
    items: Optional[List[PedidoItemUpdateRequest]] = None

class IniciarMesRequest(BaseModel):
    mes_origen: Optional[str] = "OCTUBRE"
    ano_origen: Optional[int] = 2026
    mes_destino: Optional[str] = "NOVIEMBRE"
    ano_destino: Optional[int] = 2026

class EntradaMovRequest(BaseModel):
    row_index: Optional[int] = None
    orden_suministro: Optional[str] = ""
    folio_documento: Optional[str] = ""
    folio_administrativo: Optional[str] = ""
    procedimiento: Optional[str] = ""
    no_procedimiento: Optional[str] = ""
    contrato: Optional[str] = ""
    no_contrato: Optional[str] = ""
    registro_sanitario: Optional[str] = ""
    almacen: Optional[str] = "CS ALMACEN 2022"
    proveedor: Optional[str] = ""
    clave: str
    lote: str
    descripcion: Optional[str] = ""
    unidad_medida: Optional[str] = "PZA"
    fecha_ajuste: Optional[str] = ""
    fecha_entrada: Optional[str] = ""
    fecha_fabricacion: Optional[str] = ""
    fecha_caducidad: Optional[str] = ""
    inventario_inicial: float = 0.0
    entrada_ajuste: float = 0.0
    entrada_por_ajuste: Optional[float] = None
    cantidad_recibida: float = 0.0
    dias: Optional[Dict[str, float]] = None
    apoyo_institucional: Optional[float] = 0.0
    fecha_apoyo: Optional[str] = ""
    mes: Optional[str] = "OCTUBRE"
    ano: Optional[int] = 2026
    observaciones: Optional[str] = ""

class SalidaPdfUpdateRequest(BaseModel):
    archivo_pdf: Optional[str] = None
    folio_pedido: Optional[str] = None
    fecha: Optional[str] = None
    dia: Optional[int] = None
    mes: Optional[str] = None
    ano: Optional[int] = None
    clave: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: Optional[float] = None
    lote_asignado: Optional[str] = None
    fecha_caducidad: Optional[str] = None
    cliente_destino: Optional[str] = None
    estado_validacion: Optional[str] = None
    aviso_fefo: Optional[str] = None
    observaciones: Optional[str] = None
    recalcular_fefo: Optional[bool] = True

class ApoyoInstitucionalRequest(BaseModel):
    clave: str
    lote: str
    caducidad: Optional[str] = ""
    descripcion: Optional[str] = ""
    cantidad: float
    institucion: str
    fecha: Optional[str] = ""
    dia: Optional[int] = None
    folio_documento: Optional[str] = ""
    folio_observaciones: Optional[str] = ""
    mes: Optional[str] = "OCTUBRE"
    ano: Optional[int] = 2026
    observaciones: Optional[str] = ""


# ==========================================
# MODELOS Y DEPENDENCIAS DE AUTENTICACIÓN
# ==========================================
SESSION_COOKIE_NAME = "abisalud_session"


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserCreateRequest(BaseModel):
    username: str
    nombre_completo: Optional[str] = ""
    password: str
    rol: Optional[str] = "personalizado"
    is_superadmin: bool = False
    activo: bool = True
    permisos: Optional[Dict[str, bool]] = None


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    nombre_completo: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    is_superadmin: Optional[bool] = None
    activo: Optional[bool] = None
    permisos: Optional[Dict[str, bool]] = None


def extract_session_token(request: Request) -> Optional[str]:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        return token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return None


def get_current_user(request: Request) -> Dict[str, Any]:
    token = extract_session_token(request)
    user = db.get_user_by_session_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Sesión expirada o no autenticada. Por favor inicie sesión.",
        )
    return user


def require_any_permission(*perms: str):
    def _checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user.get("is_superadmin"):
            return user
        user_perms = user.get("permisos") or {}
        if any(bool(user_perms.get(p, False)) for p in perms):
            return user
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: tu cuenta no tiene permisos para realizar esta acción.",
        )
    return _checker


# ==========================================
# VISTAS HTML (LOGIN Y PANEL PRINCIPAL)
# ==========================================

@app.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    token = extract_session_token(request)
    if token and db.get_user_by_session_token(token):
        return RedirectResponse(url="/", status_code=302)
    login_path = config.BASE_DIR / "templates" / "login.html"
    if not login_path.exists():
        raise HTTPException(status_code=404, detail="Plantilla login.html no encontrada")
    return HTMLResponse(content=login_path.read_text(encoding="utf-8"))


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    token = extract_session_token(request)
    if not token or not db.get_user_by_session_token(token):
        return RedirectResponse(url="/login", status_code=302)
    template_path = config.BASE_DIR / "templates" / "index.html"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Plantilla index.html no encontrada")
    return HTMLResponse(content=template_path.read_text(encoding="utf-8"))


# ==========================================
# ENDPOINTS DE AUTENTICACIÓN Y USUARIOS
# ==========================================

@app.post("/api/auth/login")
async def api_login(payload: LoginRequest, request: Request, response: Response):
    try:
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")
        auth_res = db.authenticate_user(
            username=payload.username,
            password=payload.password,
            ip_address=client_ip,
            user_agent=user_agent,
        )
        if not auth_res:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=auth_res["token"],
            httponly=True,
            samesite="lax",
            max_age=7 * 24 * 3600,
            path="/",
        )
        return {
            "status": "success",
            "message": f"Bienvenido, {auth_res['user']['nombre_completo']}",
            "token": auth_res["token"],
            "user": auth_res["user"],
        }
    except ValueError as ve:
        raise HTTPException(status_code=403, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar sesión: {e}")


@app.post("/api/auth/logout")
async def api_logout(request: Request, response: Response):
    token = extract_session_token(request)
    if token:
        db.logout_session(token)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return {"status": "success", "message": "Sesión cerrada correctamente."}


@app.get("/api/auth/me")
async def api_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "user": current_user,
        "permissions_catalog": ALL_PERMISSIONS_CATALOG,
        "role_presets": ROLE_PRESETS,
    }


@app.post("/api/auth/change-password")
async def api_change_own_password(
    payload: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        db.change_own_password(
            user_id=current_user["id"],
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
        return {"status": "success", "message": "Contraseña actualizada exitosamente."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users")
async def api_list_users(
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_usuarios")),
):
    try:
        return {
            "users": db.list_users(search=search),
            "permissions_catalog": ALL_PERMISSIONS_CATALOG,
            "role_presets": ROLE_PRESETS,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users")
async def api_create_user(
    payload: UserCreateRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_usuarios")),
):
    try:
        if payload.is_superadmin and not current_user.get("is_superadmin"):
            raise HTTPException(
                status_code=403,
                detail="Solo un Superadministrador puede asignar el rol de Superadministrador.",
            )
        created = db.create_user(payload.model_dump(), actor_username=current_user["username"])
        return {
            "status": "success",
            "message": f"Usuario '{created['username']}' creado exitosamente.",
            "user": created,
        }
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/users/{user_id}")
async def api_update_user(
    user_id: int,
    payload: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_usuarios")),
):
    try:
        target = db.get_user_by_id(user_id)
        if not target:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        if (target.get("is_superadmin") or payload.is_superadmin) and not current_user.get("is_superadmin"):
            raise HTTPException(
                status_code=403,
                detail="Solo un Superadministrador puede modificar cuentas de Superadministrador.",
            )
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        updated = db.update_user(
            user_id=user_id,
            data=data,
            current_user_id=current_user["id"],
            actor_username=current_user["username"],
        )
        return {
            "status": "success",
            "message": f"Usuario '{updated['username']}' actualizado correctamente.",
            "user": updated,
        }
    except HTTPException:
        raise
    except LookupError as le:
        raise HTTPException(status_code=404, detail=str(le))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/users/{user_id}")
async def api_delete_user(
    user_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_usuarios")),
):
    try:
        target = db.get_user_by_id(user_id)
        if not target:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        if target.get("is_superadmin") and not current_user.get("is_superadmin"):
            raise HTTPException(
                status_code=403,
                detail="Solo un Superadministrador puede eliminar a otro Superadministrador.",
            )
        ok = db.delete_user(
            user_id=user_id,
            current_user_id=current_user["id"],
            actor_username=current_user["username"],
        )
        if not ok:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return {"status": "success", "message": "Usuario eliminado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# ENDPOINTS REST API
# ==========================================

@app.get("/api/kpis")
async def get_kpis(
    current_user: Dict[str, Any] = Depends(
        require_any_permission("ver_catalogo", "ver_inventario", "ver_control_movimientos", "marbetes")
    )
):
    """Retorna métricas generales del inventario."""
    try:
        return db.get_inventory_kpis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog")
async def get_catalog(
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_catalogo", "marbetes")),
):
    """Retorna catálogo agrupado y consolidado por Clave única."""
    try:
        return db.get_catalog_by_clave(search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory")
async def get_inventory(
    search: Optional[str] = Query(None),
    clave: Optional[str] = Query(None),
    lote: Optional[str] = Query(None),
    almacen: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_inventario", "ver_catalogo", "marbetes")),
):
    """Retorna lista detallada de registros de inventario con filtros."""
    try:
        return db.get_records(clave=clave, search=search, lote=lote, almacen=almacen, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/{record_id}")
async def get_record(
    record_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_inventario", "editar_inventario")),
):
    """Obtiene un registro específico por su ID."""
    record = db.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return record

@app.post("/api/inventory")
async def create_record(
    item: InsumoCreateRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("editar_inventario")),
):
    """Crea un nuevo insumo / lote en la base de datos."""
    try:
        data = item.model_dump()
        result = db.create_record(data)
        return {"status": "success", "message": "Insumo registrado correctamente", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear insumo: {e}")

@app.put("/api/inventory/{record_id}")
async def update_record(
    record_id: int,
    item: InsumoUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("editar_inventario")),
):
    """Actualiza un insumo existente."""
    try:
        data = {k: v for k, v in item.model_dump().items() if v is not None}
        result = db.update_record(record_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Insumo no encontrado para actualizar")
        return {"status": "success", "message": "Insumo actualizado correctamente", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al actualizar insumo: {e}")

@app.delete("/api/inventory/{record_id}")
async def delete_record(
    record_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("editar_inventario")),
):
    """Elimina un registro de insumo."""
    success = db.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Insumo no encontrado para eliminar")
    return {"status": "success", "message": f"Insumo ID {record_id} eliminado exitosamente"}

@app.post("/api/clear")
@app.post("/api/inventory/clear")
@app.delete("/api/inventory")
async def clear_inventory(
    current_user: Dict[str, Any] = Depends(require_any_permission("vaciar_inventario", "vaciar_sistema_total"))
):
    """Vacía exclusivamente los datos de inventario y catálogo."""
    try:
        deleted_count = db.clear_inventory()
        return {
            "status": "success",
            "message": f"Inventario vaciado exitosamente. Se eliminaron {deleted_count} registros. Las Entradas y Salidas permanecen intactas.",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al vaciar inventario: {e}")

@app.post("/api/movimientos/clear")
async def clear_movimientos(
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_movimientos", "vaciar_sistema_total"))
):
    """Vacía exclusivamente los datos de Entradas y Salidas sin alterar inventario ni catálogo."""
    try:
        deleted_count = db.clear_movimientos()
        return {
            "status": "success",
            "message": f"Entradas y Salidas vaciadas exitosamente. Se eliminaron {deleted_count} registros. El Inventario y Catálogo permanecen intactos.",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al vaciar Entradas y Salidas: {e}")

@app.post("/api/system/clear-all")
async def clear_all_system(
    keep_catalogs: bool = Query(False),
    current_user: Dict[str, Any] = Depends(require_any_permission("vaciar_sistema_total")),
):
    """VACIADO TOTAL: Elimina todos los registros de todos los módulos del sistema."""
    try:
        res = db.clear_all_system_data(keep_catalogs=keep_catalogs)
        total_del = sum(res.values())
        return {
            "status": "success",
            "message": f"Sistema vaciado por completo. Se eliminaron {total_del} registros en total.",
            "details": res,
            "total_deleted": total_del
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al vaciar sistema: {e}")

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(
        require_any_permission("actualizar_inventario", "carga_archivos", "editar_inventario")
    ),
):
    """Sube y procesa un archivo Excel, CSV, PDF o JSON directamente al inventario."""
    try:
        file_path = config.DOWNLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df, file_type = DataProcessor.process_file(file_path)
        if df.empty:
            return JSONResponse(status_code=400, content={"status": "warning", "message": "El archivo no contiene registros legibles."})

        inserted = db.insert_dataframe(df, source_filename=file.filename)
        
        # Mover a procesados
        dest = config.PROCESSED_DIR / file.filename
        try:
            shutil.move(str(file_path), str(dest))
        except Exception:
            pass

        return {
            "status": "success",
            "message": f"Archivo {file.filename} ({file_type}) procesado con éxito.",
            "records_inserted": inserted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {e}")

@app.post("/api/movimientos/upload-excel")
async def upload_movimientos_excel(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_movimientos")),
):
    """Sube y procesa el archivo Excel descargado del SIIA con hojas 'Entradas' y 'Salidas'."""
    try:
        file_path = config.DOWNLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        res = DataProcessor.read_entradas_salidas_excel(file_path)
        df_entradas = res.get("entradas", pd.DataFrame())
        df_salidas = res.get("salidas", pd.DataFrame())

        if df_entradas.empty and df_salidas.empty:
            return JSONResponse(status_code=400, content={"status": "warning", "message": "No se encontraron hojas de 'Entradas' o 'Salidas' legibles en el archivo."})

        c_ent = db.insert_movimientos(df_entradas, "ENTRADA", file.filename) if not df_entradas.empty else 0
        c_sal = db.insert_movimientos(df_salidas, "SALIDA", file.filename) if not df_salidas.empty else 0

        dest = config.PROCESSED_DIR / file.filename
        try:
            shutil.move(str(file_path), str(dest))
        except Exception:
            pass

        return {
            "status": "success",
            "message": f"Archivo de Entradas y Salidas procesado: {c_ent} entradas y {c_sal} salidas importadas exitosamente.",
            "entradas_count": c_ent,
            "salidas_count": c_sal
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo de Entradas y Salidas: {e}")

@app.post("/api/movimientos/upload-pdf")
async def upload_movimientos_pdf(
    files: List[UploadFile] = File(...),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_movimientos")),
):
    """Sube y procesa una o varias Hojas De Entrega De Pedido en formato PDF para alimentar las salidas día con día."""
    try:
        total_items = 0
        pedidos_list = []
        for file in files:
            file_path = config.DOWNLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            doc_info, items = DataProcessor.read_hoja_pedido_pdf(file_path)
            if items:
                df_pdf = pd.DataFrame(items)
                c = db.insert_movimientos(df_pdf, "SALIDA", file.filename)
                total_items += c
                pedidos_list.append(f"{doc_info.get('pedido', 'S/N')} ({len(items)} partidas)")

            dest = config.PROCESSED_DIR / file.filename
            try:
                shutil.move(str(file_path), str(dest))
            except Exception:
                pass

        if total_items == 0:
            return JSONResponse(status_code=400, content={"status": "warning", "message": "No se pudieron extraer partidas de salida de los PDFs proporcionados."})

        return {
            "status": "success",
            "message": f"Se procesaron {len(files)} archivo(s) PDF con éxito. Se registraron {total_items} salidas de los pedidos: {', '.join(pedidos_list)}.",
            "total_items": total_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar PDFs de salida: {e}")

@app.get("/api/movimientos")
async def get_movimientos(
    tipo: Optional[str] = None,
    search: Optional[str] = None,
    dia: Optional[int] = None,
    sort_by: str = "fecha_desc",
    page: int = 1,
    page_size: int = 50,
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_movimientos", "gestionar_movimientos")),
):
    """Obtiene el listado de entradas y salidas con filtros, búsqueda y paginación."""
    try:
        return db.get_movimientos(tipo=tipo, search=search, dia=dia, sort_by=sort_by, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clues/matrix")
async def get_clues_matrix(
    search: Optional[str] = None,
    mes: Optional[str] = None,
    ano: Optional[int] = None,
    dia_inicio: int = 1,
    dia_fin: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_matriz_clues")),
):
    """Obtiene la matriz oficial de CLUES (CSIMB003506) con stock unificado y salidas distribuidas por día y mes."""
    try:
        return db.get_clues_matrix(search=search, mes=mes, ano=ano, dia_inicio=dia_inicio, dia_fin=dia_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_clues_official_excel(db_mgr: DatabaseManager, out_path: Path, mes: Optional[str] = None, ano: Optional[int] = None):
    """
    Genera el archivo Excel oficial idéntico a inventario_siplificado_cluesEnMayucula_ REPORTE DIARIO CAMBIOOOOOS.xlsx:
    - Hoja 1 'salidas por dia':
      * Fila 1: Banner verde superior 'SALIDAS {MES}' sobre columnas F1:..1.
      * Fila 2: Encabezados en mayúsculas: CLUES, CLAVE, INVENTARIO DISPONIBLE, LOTE, F_CAD, 1..N.
      * Filas de datos: Registros consolidados por Clave y Lote.
      * Fila Inferior: 'TOTAL SALIDAS POR DÍA', con fórmulas =SUM(...) de piezas por cada día y total disponible.
      * Anchos y estilos fieles a la plantilla.
    - Hoja 2 'Salidas': Detalle cronológico de salidas con los 23 campos oficiales filtrado por mes y año.
    - Hoja 3 'existencia': Reporte de existencias agrupadas.
    """
    import sqlalchemy

    # 1. Obtener datos de la matriz para el mes y año solicitados
    matrix_data = db_mgr.get_clues_matrix(mes=mes, ano=ano, dia_inicio=1, dia_fin=None)
    rows = matrix_data.get("rows", [])
    days_list = matrix_data.get("days", list(range(1, 31)))
    target_mes = matrix_data.get("mes", "SEPTIEMBRE")
    target_ano = matrix_data.get("ano", 2026)
    num_days = len(days_list)
    last_col_idx = 5 + num_days
    last_col_letter = get_column_letter(last_col_idx)

    wb = openpyxl.Workbook()
    # Hoja 1: salidas por dia
    ws1 = wb.active
    ws1.title = "salidas por dia"

    header_fill = PatternFill(start_color="1E7145", end_color="1E7145", fill_type="solid")
    header_font = Font(name="Aptos Narrow", size=11, bold=True, color="FFFFFF")
    center_align = Alignment(horizontal="center", vertical="center")
    thin_border_side = Side(style="thin", color="135824")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    # Banner verde superior combinado: SALIDAS {target_mes}
    ws1.merge_cells(f"F1:{last_col_letter}1")
    f1 = ws1["F1"]
    f1.value = f"SALIDAS {target_mes}"

    for col in range(6, last_col_idx + 1):
        cell = ws1.cell(1, col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = cell_border

    # Fila 2: Encabezados en mayúsculas
    headers_row2 = ["CLUES", "CLAVE", "INVENTARIO DISPONIBLE", "LOTE", "F_CAD"] + [str(d) for d in days_list]
    ws1.row_dimensions[2].height = 26
    for idx, h in enumerate(headers_row2, 1):
        cell = ws1.cell(2, idx)
        cell.value = int(h) if h.isdigit() else h
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = cell_border

    # Filas de datos
    data_font = Font(name="Aptos Narrow", size=10)
    data_side = Side(style="thin", color="D1D5DB")
    data_border = Border(left=data_side, right=data_side, top=data_side, bottom=data_side)

    current_row = 3
    for r in rows:
        ws1.cell(current_row, 1, r.get("clues", "CSIMB003506")).alignment = Alignment(horizontal="center")
        ws1.cell(current_row, 2, r.get("clave", "")).alignment = Alignment(horizontal="left")

        c_inv = ws1.cell(current_row, 3, float(r.get("inventario_disponible", 0.0)))
        c_inv.number_format = "#,##0"
        c_inv.alignment = Alignment(horizontal="right")

        ws1.cell(current_row, 4, r.get("lote", "")).alignment = Alignment(horizontal="center")
        ws1.cell(current_row, 5, r.get("f_cad", "")).alignment = Alignment(horizontal="center")

        # Días 1 al N
        for d_idx, d in enumerate(days_list, 6):
            val = float(r.get("dias", {}).get(str(d), 0.0))
            c_day = ws1.cell(current_row, d_idx, val)
            c_day.number_format = "#,##0"
            c_day.alignment = Alignment(horizontal="right")

        for c in range(1, last_col_idx + 1):
            ws1.cell(current_row, c).font = data_font
            ws1.cell(current_row, c).border = data_border

        current_row += 1

    last_data_row = current_row - 1

    # FILA INFERIOR DE TOTALES: cuantas piezas salieron por día
    tot_row = current_row
    ws1.row_dimensions[tot_row].height = 24

    tot_fill = PatternFill(start_color="E2F0D9", end_color="E2F0D9", fill_type="solid")
    tot_font = Font(name="Aptos Narrow", size=11, bold=True, color="1E7145")
    tot_border = Border(
        left=thin_border_side,
        right=thin_border_side,
        top=Side(style="thin", color="1E7145"),
        bottom=Side(style="double", color="1E7145")
    )

    cell_tot_lbl = ws1.cell(tot_row, 1, "TOTAL SALIDAS POR DÍA")
    cell_tot_lbl.alignment = Alignment(horizontal="center", vertical="center")
    cell_tot_sub = ws1.cell(tot_row, 2, "TOTALES")
    cell_tot_sub.alignment = Alignment(horizontal="center", vertical="center")

    if last_data_row >= 3:
        cell_tot_inv = ws1.cell(tot_row, 3, f"=SUM(C3:C{last_data_row})")
    else:
        cell_tot_inv = ws1.cell(tot_row, 3, 0)
    cell_tot_inv.number_format = "#,##0"
    cell_tot_inv.alignment = Alignment(horizontal="right", vertical="center")

    ws1.cell(tot_row, 4, "-").alignment = Alignment(horizontal="center", vertical="center")
    ws1.cell(tot_row, 5, "-").alignment = Alignment(horizontal="center", vertical="center")

    for c_idx in range(6, last_col_idx + 1):
        col_letter = get_column_letter(c_idx)
        if last_data_row >= 3:
            c_tot_day = ws1.cell(tot_row, c_idx, f"=SUM({col_letter}3:{col_letter}{last_data_row})")
        else:
            c_tot_day = ws1.cell(tot_row, c_idx, 0)
        c_tot_day.number_format = "#,##0"
        c_tot_day.alignment = Alignment(horizontal="right", vertical="center")

    for c in range(1, last_col_idx + 1):
        cell = ws1.cell(tot_row, c)
        cell.fill = tot_fill
        cell.font = tot_font
        cell.border = tot_border

    # Anchos de columna fidedignos
    ws1.column_dimensions["A"].width = 15
    ws1.column_dimensions["B"].width = 18
    ws1.column_dimensions["C"].width = 25
    ws1.column_dimensions["D"].width = 17
    ws1.column_dimensions["E"].width = 19
    for c in range(6, last_col_idx + 1):
        ws1.column_dimensions[get_column_letter(c)].width = 7.5

    # ==========================================
    # Hoja 2: Salidas (Detalle)
    # ==========================================
    ws2 = wb.create_sheet(title="Salidas")
    ws2.cell(1, 1, "Localidad(es)")
    ws2.cell(1, 2, "CS ALMACEN 2022")
    ws2.cell(2, 1, "Fecha de Generación")
    ws2.cell(2, 2, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ws2.cell(3, 1, "Periodo")

    m_num_map = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
        "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }
    m_num = m_num_map.get(target_mes, 9)
    periodo_str = f"{target_ano}-{m_num:02d}-01 - {target_ano}-{m_num:02d}-{num_days:02d}"
    ws2.cell(3, 2, periodo_str)

    salidas_headers = [
        "Clave", "Clave Cliente", "Codigo Barras", "Descripción", "Lote", "Costo",
        "Caducidad", "Ubicacion", "Cantidad", "Fecha", "Tipo", "Referencia",
        "Documento", "Almacen", "Usuario", "Cliente", "Observaciones",
        "Folio Salida WS", "Proveedor", "No de procedimiento", "Fuente de adquisicion", "Año", "Servicio"
    ]

    ws2.row_dimensions[5].height = 24
    for idx, h in enumerate(salidas_headers, 1):
        cell = ws2.cell(5, idx, h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = cell_border

    session = db_mgr.get_session()
    try:
        valid_matrix_keys = {(r.get("clave"), r.get("lote")) for r in rows}

        # Catálogo para resolver descripciones faltantes
        desc_map = {}
        for row_desc in session.query(InsumoRecord.clave, InsumoRecord.descripcion).filter(
            InsumoRecord.descripcion.isnot(None), InsumoRecord.descripcion != "",
            sqlalchemy.or_(
                InsumoRecord.hoja_origen == "Existencias_x_Localidad",
                sqlalchemy.and_(
                    InsumoRecord.hoja_origen.is_(None),
                    InsumoRecord.report_source.notlike("%test_%")
                )
            )
        ).all():
            c_clean = (row_desc.clave or "").strip()
            if c_clean and c_clean not in desc_map:
                desc_map[c_clean] = row_desc.descripcion.strip()

        clues_pattern = re.compile(r'^\d{3}\.\d{3}\.\d{3,5}(\.\d{2})?$')

        salidas_records = session.query(MovimientoRecord).filter(
            MovimientoRecord.tipo == "SALIDA",
            MovimientoRecord.tipo_movimiento == "PEDIDO",
            sqlalchemy.or_(
                MovimientoRecord.mes == target_mes,
                MovimientoRecord.fecha.like(f"{target_ano}-{m_num:02d}%"),
                MovimientoRecord.fecha.like(f"%/{m_num:02d}/{target_ano}%")
            )
        ).order_by(MovimientoRecord.fecha.desc()).all()

        r_idx = 6
        for s in salidas_records:
            # Excluir documentos de ajuste explícitos
            doc = (s.documento or "").strip()
            if doc.startswith("AJ_"):
                continue

            # Filtrar destino: únicamente pedidos hacia CS FARMACIA MAT 2022
            ref = (s.referencia or "").strip().upper()
            cli = (s.cliente or "").strip().upper()
            if ("CS FARMACIA" not in ref) and ("CS FARMACIA" not in cli):
                continue

            cve_val = (s.clave_cliente or s.clave or "").strip()
            # En CLUES solo se agregan claves que tienen estructura numérica oficial
            if not clues_pattern.match(cve_val):
                continue

            # REGLA ESTRICTA: Solo incluir salidas de insumos pertenecientes a Existencias_x_Localidad
            if (cve_val, (s.lote or "").strip()) not in valid_matrix_keys:
                continue

            desc_val = (s.descripcion or "").strip() or desc_map.get(cve_val, "")

            row_data = [
                s.clave or "",
                cve_val,
                s.codigo_barras or "",
                desc_val,
                s.lote or "",
                float(s.costo or 0.0),
                s.caducidad or "",
                s.ubicacion or "",
                float(s.cantidad or 0.0),
                s.fecha or "",
                s.tipo_movimiento or "PEDIDO",
                s.referencia or "",
                s.documento or "",
                s.almacen or "",
                s.usuario or "",
                s.cliente or "",
                s.observaciones or "",
                s.folio_salida or "",
                s.proveedor or "",
                "", "", "", ""
            ]
            for c_idx, val in enumerate(row_data, 1):
                c_cell = ws2.cell(r_idx, c_idx, val)
                c_cell.font = data_font
                c_cell.border = data_border
                if isinstance(val, float):
                    c_cell.number_format = "#,##0.00" if c_idx == 6 else "#,##0"
            r_idx += 1

        # ==========================================
        # Hoja 3: existencia
        # ==========================================
        ws3 = wb.create_sheet(title="existencia")
        existencia_headers = ["Clave Cliente", "Descripción", "Lote", "Existencia Real piezas", "Caducidad"]
        ws3.row_dimensions[1].height = 24
        for idx, h in enumerate(existencia_headers, 1):
            cell = ws3.cell(1, idx, h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = cell_border

        inv_records = session.query(InsumoRecord).filter(
            InsumoRecord.cantidad > 0,
            sqlalchemy.or_(
                InsumoRecord.hoja_origen == "Existencias_x_Localidad",
                sqlalchemy.and_(
                    InsumoRecord.hoja_origen.is_(None),
                    InsumoRecord.report_source.notlike("%test_%"),
                    sqlalchemy.or_(
                        InsumoRecord.clave_abisa.isnot(None),
                        InsumoRecord.report_source.like("%Ubicaci%"),
                        InsumoRecord.report_source.like("%Existencia%")
                    )
                )
            )
        ).order_by(InsumoRecord.clave.asc()).all()
        r_idx3 = 2
        for inv in inv_records:
            cve_val = (inv.clave_cliente or inv.clave or "").strip()
            # En CLUES solo se agregan claves que tienen estructura numérica oficial
            if not clues_pattern.match(cve_val):
                continue

            cad_val = (inv.caducidad or "").strip()
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            # Lo vigente que está caducado no se agrega
            if cad_val and cad_val[:10] < today_str:
                continue

            desc_val = (inv.descripcion or "").strip() or desc_map.get(cve_val, "")

            row_data3 = [
                cve_val,
                desc_val,
                inv.lote or "",
                float(inv.cantidad or 0.0),
                inv.caducidad or ""
            ]
            for c_idx, val in enumerate(row_data3, 1):
                c_cell = ws3.cell(r_idx3, c_idx, val)
                c_cell.font = data_font
                c_cell.border = data_border
                if c_idx == 4:
                    c_cell.number_format = "#,##0"
            r_idx3 += 1

    finally:
        session.close()

    wb.save(out_path)
    wb.close()

@app.get("/api/export")
async def export_excel(
    tab: str = "tab-inventory",
    mes: Optional[str] = None,
    ano: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Genera y descarga el archivo Excel correspondiente a la pestaña activa en la interfaz."""
    if not current_user.get("is_superadmin"):
        perms = current_user.get("permisos") or {}
        if tab == "tab-movimientos" and not (perms.get("gestionar_movimientos") or perms.get("ver_movimientos")):
            raise HTTPException(status_code=403, detail="No tiene permisos para exportar Entradas y Salidas.")
        elif tab == "tab-clues" and not perms.get("ver_matriz_clues"):
            raise HTTPException(status_code=403, detail="No tiene permisos para exportar la Matriz CLUES.")
        elif tab not in ("tab-movimientos", "tab-clues") and not perms.get("exportar_inventario"):
            raise HTTPException(status_code=403, detail="No tiene permisos para exportar Catálogo o Inventario a Excel.")

    try:
        today_str = datetime.date.today().strftime('%Y%m%d')
        out_path = config.BASE_DIR / f"reporte_export_{tab}.xlsx"

        if tab == "tab-catalog":
            cat = db.get_catalog_by_clave()
            if not cat:
                raise HTTPException(status_code=404, detail="No hay claves en el catálogo para exportar.")
            df = pd.DataFrame(cat)
            df.rename(columns={
                "clave": "Clave Cliente",
                "clave_abisa": "Clave Abisa",
                "codigo_barras": "Código de Barras",
                "descripcion": "Descripción",
                "presentacion": "Presentación",
                "unidad_medida": "Unidad de Medida",
                "total_existencia": "Existencia Total (Piezas)",
                "total_valor": "Valor Total ($)",
                "precio_promedio": "Precio Promedio ($)",
                "total_lotes_registrados": "Total Lotes"
            }, inplace=True)
            df.to_excel(out_path, sheet_name="Catálogo de Claves", index=False)
            filename = f"catalogo_claves_abisalud_{today_str}.xlsx"

        elif tab == "tab-movimientos":
            session = db.get_session()
            try:
                ent_recs = session.query(MovimientoRecord).filter(MovimientoRecord.tipo == 'ENTRADA').order_by(MovimientoRecord.fecha.desc()).all()
                sal_recs = session.query(MovimientoRecord).filter(MovimientoRecord.tipo == 'SALIDA').order_by(MovimientoRecord.fecha.desc()).all()
                df_ent = pd.DataFrame([r.to_dict() for r in ent_recs])
                df_sal = pd.DataFrame([r.to_dict() for r in sal_recs])
            finally:
                session.close()

            if df_ent.empty and df_sal.empty:
                raise HTTPException(status_code=404, detail="No hay movimientos de entradas ni salidas para exportar.")

            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                if not df_ent.empty:
                    df_ent.to_excel(writer, sheet_name="Entradas", index=False)
                if not df_sal.empty:
                    df_sal.to_excel(writer, sheet_name="Salidas", index=False)
            filename = f"entradas_y_salidas_{today_str}.xlsx"

        elif tab == "tab-clues":
            generate_clues_official_excel(db, out_path, mes=mes, ano=ano)
            mes_tag = f"_{mes.upper()}" if mes else "_SEPTIEMBRE"
            filename = f"inventario_siplificado_clues{mes_tag}_REPORTE_DIARIO_{today_str}.xlsx"

        else: # tab-inventory por defecto
            query = "SELECT * FROM insumos_report ORDER BY id DESC"
            df = pd.read_sql(query, con=db.engine)
            if df.empty:
                raise HTTPException(status_code=404, detail="No hay datos registrados en el inventario para exportar.")
            if "raw_json" in df.columns:
                df = df.drop(columns=["raw_json"])
            df.to_excel(out_path, sheet_name="Inventario por Lotes", index=False)
            filename = f"inventario_por_lotes_abisalud_{today_str}.xlsx"

        return FileResponse(
            path=out_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================================
# RUTAS API: SISTEMA PROPUESTO - CONTROL DE INVENTARIO POR MOVIMIENTOS
# =========================================================================

# --- 1. CATÁLOGOS ---
@app.get("/api/control-movimientos/catalogo")
async def get_control_catalogo(
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_catalogo_movimientos(search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/catalogo")
async def create_control_catalogo(
    item: CatalogoMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.create_catalogo_insumo(item.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/control-movimientos/catalogo/{item_id}")
async def update_control_catalogo(
    item_id: int,
    item: CatalogoMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.update_catalogo_insumo(item_id, item.dict())
        if not res:
            raise HTTPException(status_code=404, detail="Insumo de catálogo no encontrado")
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/control-movimientos/catalogo/{item_id}")
async def delete_control_catalogo(
    item_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        ok = db.delete_catalogo_insumo(item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Insumo no encontrado")
        return {"status": "success", "message": "Insumo eliminado del catálogo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/catalogo/sync-from-insumos")
async def sync_control_catalogo(
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        added = db.sync_catalogo_from_insumos()
        return {"status": "success", "message": f"Se sincronizaron {added} claves nuevas desde los insumos del sistema.", "added_count": added}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/control-movimientos/proveedores")
async def get_control_proveedores(
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_proveedores_movimientos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/proveedores")
async def create_control_proveedor(
    item: ProveedorMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.create_proveedor_mov(item.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/control-movimientos/proveedores/{item_id}")
async def update_control_proveedor(
    item_id: int,
    item: ProveedorMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.update_proveedor_mov(item_id, item.dict(exclude_unset=True))
        if not res:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/control-movimientos/proveedores/{item_id}")
async def delete_control_proveedor(
    item_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        ok = db.delete_proveedor_mov(item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return {"status": "success", "message": "Proveedor eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/control-movimientos/unidades")
async def get_control_unidades(
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_unidades_medida_movimientos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/unidades")
async def create_control_unidad(
    item: UnidadMedidaMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.create_unidad_medida_mov(item.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/control-movimientos/unidades/{item_id}")
async def update_control_unidad(
    item_id: int,
    item: UnidadMedidaMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.update_unidad_medida_mov(item_id, item.dict(exclude_unset=True))
        if not res:
            raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/control-movimientos/unidades/{item_id}")
async def delete_control_unidad(
    item_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        ok = db.delete_unidad_medida_mov(item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
        return {"status": "success", "message": "Unidad de medida eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. ENTRADAS MANUALES ---
@app.get("/api/control-movimientos/entradas")
async def get_control_entradas(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    only_ingresos: Optional[bool] = Query(True),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_entradas_movimientos(mes=mes, ano=target_ano, search=search, only_ingresos=only_ingresos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/entradas")
async def create_control_entrada(
    item: EntradaMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.create_entrada_mov(item.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/control-movimientos/entradas/{item_id}")
async def update_control_entrada(
    item_id: int,
    item: EntradaMovRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.update_entrada_mov(item_id, item.dict(exclude_unset=True))
        if not res:
            raise HTTPException(status_code=404, detail="Entrada no encontrada")
        db.log_execution(
            operation="CONTROL_UPDATE_ENTRADA",
            status="SUCCESS",
            file_name=f"{res.get('clave', '')} | {res.get('lote', '')}",
            records_count=1,
            details=f"Registro de partida #{item_id} modificado por '{current_user.get('username', 'admin')}'",
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/control-movimientos/entradas/{item_id}")
async def delete_control_entrada(
    item_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        ok = db.delete_entrada_mov(item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Entrada no encontrada")
        return {"status": "success", "message": "Entrada eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. SALIDAS DESDE PDF (FEFO) ---
@app.get("/api/control-movimientos/salidas-pdf")
async def get_control_salidas_pdf(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_salidas_pdf_movimientos(mes=mes, ano=target_ano, search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/salidas-pdf/upload")
async def upload_control_movimientos_pdf(
    files: List[UploadFile] = File(...),
    mes: Optional[str] = Form("OCTUBRE"),
    ano: Optional[int] = Form(2026),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        total_procesados = 0
        total_validos = 0
        total_alertas = 0
        total_fefo_optimo = 0
        total_avisos_fefo = 0
        avisos_fefo_lista = []
        archivos_procesados = []

        for file in files:
            file_path = config.DOWNLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            doc_info, items = DataProcessor.read_hoja_pedido_pdf(file_path)
            if items:
                res = db.process_salidas_pdf_items(items, file.filename, mes=mes, ano=ano)
                total_procesados += res["total_procesados"]
                total_validos += res["total_validos"]
                total_alertas += res["total_alertas"]
                total_fefo_optimo += res.get("total_fefo_optimo", 0)
                total_avisos_fefo += res.get("total_avisos_fefo", 0)
                avisos_fefo_lista.extend(res.get("avisos_fefo", []))
                archivos_procesados.append(file.filename)

            dest = config.PROCESSED_DIR / file.filename
            try:
                shutil.move(str(file_path), str(dest))
            except Exception:
                pass

        if total_procesados == 0:
            return JSONResponse(status_code=400, content={"status": "warning", "message": "No se pudieron extraer partidas válidas de los PDFs."})

        msg = f"Se procesaron {len(files)} archivo(s) PDF con {total_procesados} partidas registradas exactamente por Clave y Lote del PDF."
        if total_avisos_fefo > 0:
            msg += f" ⚠️ AVISO FEFO: Se detectaron {total_avisos_fefo} salidas cuyo lote en PDF no tiene la caducidad más próxima disponible en almacén."
        else:
            msg += " ✅ Todas las salidas cumplen con la regla FEFO o corresponden a lotes únicos."

        return {
            "status": "warning" if total_avisos_fefo > 0 else "success",
            "message": msg,
            "total_procesados": total_procesados,
            "salidas_insertadas": total_procesados,
            "archivos_procesados": len(archivos_procesados),
            "total_validos": total_validos,
            "total_alertas": total_alertas,
            "total_fefo_optimo": total_fefo_optimo,
            "total_avisos_fefo": total_avisos_fefo,
            "avisos_fefo": avisos_fefo_lista,
            "archivos": archivos_procesados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar PDFs para control de movimientos: {e}")

@app.put("/api/control-movimientos/salidas-pdf/{item_id}")
async def update_control_salida_pdf(
    item_id: int,
    item: SalidaPdfUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.update_salida_pdf_mov(item_id, item.dict(exclude_unset=True))
        if not res:
            raise HTTPException(status_code=404, detail="Salida PDF no encontrada")
        db.log_execution(
            operation="CONTROL_UPDATE_SALIDA_PDF",
            status="SUCCESS",
            file_name=f"{res.get('clave', '')} | {res.get('lote_asignado', '')}",
            records_count=1,
            details=f"Salida PDF #{item_id} modificada por '{current_user.get('username', 'admin')}'",
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/control-movimientos/salidas-pdf/{item_id}")
async def delete_control_salida_pdf(
    item_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        ok = db.delete_salida_pdf_mov(item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Salida PDF no encontrada")
        return {"status": "success", "message": "Salida PDF eliminada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/salidas-pdf/clear")
async def clear_control_salidas_pdf(
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        count = db.clear_salidas_pdf_mov(mes=mes, ano=ano)
        period_str = f" del periodo {mes} {ano}" if mes else " de todos los periodos"
        return {"status": "success", "message": f"Se eliminaron {count} salidas PDF{period_str}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- GESTIÓN DE PEDIDOS COMPLETOS (MODIFICAR O ELIMINAR PEDIDO ENTERO) ---
@app.get("/api/control-movimientos/pedidos")
async def get_control_pedidos(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_pedidos_resumen(mes=mes, ano=target_ano, search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/control-movimientos/pedido")
async def get_control_pedido_detalle(
    folio: str = Query(...),
    archivo: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        detalle = db.get_pedido_detalle(folio_pedido=folio, archivo_pdf=archivo, mes=mes, ano=ano)
        if not detalle:
            raise HTTPException(status_code=404, detail=f"Pedido '{folio}' no encontrado.")
        return detalle
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/control-movimientos/pedido")
async def update_control_pedido(
    req: PedidoCompletoUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.update_pedido_completo(req.dict())
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/control-movimientos/pedido")
async def delete_control_pedido(
    folio: str = Query(...),
    archivo: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.delete_pedido_completo(folio_pedido=folio, archivo_pdf=archivo, mes=mes, ano=ano)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. APOYO INSTITUCIONAL ---
@app.get("/api/control-movimientos/apoyo-institucional")
async def get_control_apoyos(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_apoyos_institucionales(mes=mes, ano=target_ano, search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/apoyo-institucional")
async def create_control_apoyo(
    item: ApoyoInstitucionalRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.create_apoyo_institucional(item.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/control-movimientos/apoyo-institucional/{item_id}")
async def update_control_apoyo(
    item_id: int,
    item: ApoyoInstitucionalRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.update_apoyo_institucional(item_id, item.dict(exclude_unset=True))
        if not res:
            raise HTTPException(status_code=404, detail="Registro de apoyo no encontrado")
        db.log_execution(
            operation="CONTROL_UPDATE_APOYO",
            status="SUCCESS",
            file_name=f"{res.get('clave', '')} | {res.get('lote', '')}",
            records_count=1,
            details=f"Apoyo institucional #{item_id} modificado por '{current_user.get('username', 'admin')}'",
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/control-movimientos/apoyo-institucional/{item_id}")
async def delete_control_apoyo(
    item_id: int,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        ok = db.delete_apoyo_institucional(item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Registro de apoyo no encontrado")
        return {"status": "success", "message": "Apoyo institucional eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control-movimientos/apoyo-institucional/upload-excel")
async def upload_control_apoyos_excel(
    files: List[UploadFile] = File(...),
    mes: Optional[str] = Form("NOVIEMBRE"),
    ano: Optional[int] = Form(2026),
    institucion: Optional[str] = Form("Apoyo Institucional"),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    if not files:
        raise HTTPException(status_code=400, detail="No se seleccionó ningún archivo Excel.")

    results = []
    total_imported_records = 0
    total_imported_piezas = 0.0

    for file in files:
        fname = file.filename or "archivo.xlsx"
        if not (fname.lower().endswith(".xlsx") or fname.lower().endswith(".xls")):
            continue
        try:
            content = await file.read()
            res = db.import_apoyo_institucional_excel(
                file_source=content,
                filename=fname,
                default_mes=mes or "NOVIEMBRE",
                default_ano=ano or 2026,
                default_institucion=institucion or "Apoyo Institucional"
            )
            results.append(res)
            total_imported_records += res.get("total_partidas", 0)
            total_imported_piezas += res.get("total_piezas", 0.0)
        except Exception as e:
            results.append({
                "success": False,
                "filename": fname,
                "error": str(e)
            })

    db.log_execution(
        operation="CONTROL_UPLOAD_APOYOS_EXCEL",
        status="SUCCESS" if total_imported_records > 0 else "WARNING",
        file_name=", ".join([f.filename for f in files]),
        records_count=total_imported_records,
        details=f"Se importaron {total_imported_records} partidas ({total_imported_piezas} piezas) de apoyo institucional desde Excel por '{current_user.get('username', 'admin')}'"
    )

    return {
        "status": "success",
        "total_files": len(files),
        "total_partidas": total_imported_records,
        "total_piezas": round(total_imported_piezas, 2),
        "results": results
    }


@app.delete("/api/control-movimientos/apoyo-institucional/by-folio/{folio:path}")
async def delete_control_apoyos_by_folio(
    folio: str,
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        count = db.delete_apoyo_institucional_by_folio(folio, mes=mes, ano=ano)
        db.log_execution(
            operation="CONTROL_DELETE_APOYO_FOLIO",
            status="SUCCESS",
            file_name=folio,
            records_count=count,
            details=f"Se eliminó el vale completo '{folio}' ({count} partidas) por '{current_user.get('username', 'admin')}'"
        )
        return {"status": "success", "deleted_count": count, "message": f"Se eliminaron {count} partidas del vale '{folio}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/control-movimientos/apoyo-institucional/by-folio/{folio:path}")
async def update_control_apoyos_by_folio(
    folio: str,
    data: Dict[str, Any] = Body(...),
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        count = db.update_apoyo_institucional_by_folio(folio, data, mes=mes, ano=ano)
        db.log_execution(
            operation="CONTROL_UPDATE_APOYO_FOLIO",
            status="SUCCESS",
            file_name=folio,
            records_count=count,
            details=f"Se actualizaron {count} partidas del vale '{folio}' por '{current_user.get('username', 'admin')}'"
        )
        return {"status": "success", "updated_count": count, "message": f"Se actualizaron {count} partidas del vale '{folio}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/iniciar-mes")
async def api_iniciar_nuevo_mes(
    data: IniciarMesRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.iniciar_nuevo_mes(
            mes_origen=data.mes_origen,
            ano_origen=data.ano_origen,
            mes_destino=data.mes_destino,
            ano_destino=data.ano_destino,
        )
        db.log_execution(
            operation="CONTROL_INICIAR_MES",
            status="SUCCESS",
            file_name=f"{data.mes_destino} {data.ano_destino}",
            records_count=res.get("total_partidas", 0),
            details=f"Mes {data.mes_destino} {data.ano_destino} iniciado desde {data.mes_origen} {data.ano_origen} por '{current_user.get('username', 'admin')}' (Total inicial: {res.get('total_inventario_inicial')})",
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/control-movimientos/clear")
async def clear_control_movimientos_endpoint(
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    clear_catalog: bool = Query(False),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        res = db.clear_control_movimientos(mes=mes, ano=ano, clear_catalog=clear_catalog)
        tot = sum(res.values())
        period_str = f"del periodo {mes} {ano}" if mes else "de todos los periodos"
        return {
            "status": "success",
            "message": f"Se vaciaron {tot} registros de Control de Movimientos {period_str}.",
            "details": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/entradas/clear")
async def clear_control_entradas_endpoint(
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        count = db.clear_control_entradas(mes=mes, ano=ano)
        period_str = f" del periodo {mes} {ano}" if mes else ""
        return {"status": "success", "message": f"Se eliminaron {count} entradas manuales{period_str}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control-movimientos/apoyo-institucional/clear")
async def clear_control_apoyos_endpoint(
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        count = db.clear_control_apoyos(mes=mes, ano=ano)
        period_str = f" del periodo {mes} {ano}" if mes else ""
        return {"status": "success", "message": f"Se eliminaron {count} registros de apoyo institucional{period_str}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/control-movimientos/lotes-disponibles/{clave}")
async def get_control_lotes_disponibles(
    clave: str,
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_lotes_disponibles_clave(clave=clave, mes=mes, ano=ano)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 5. REPORTE DIARIO CONSOLIDADO Y EXCEL ---
@app.get("/api/control-movimientos/matriz")
async def get_control_matriz(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        search_term = q if q is not None else search
        return db.get_reporte_movimientos_matriz(mes=mes, ano=ano, search=search_term)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/control-movimientos/export-excel")
async def export_control_excel(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        stream = db.export_reporte_movimientos_excel(mes=mes, ano=ano)
        filename = f"Control_Inventario_Movimientos_{mes}_{ano}.xlsx"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar Excel: {e}")

@app.post("/api/control-movimientos/import-base-excel")
async def import_control_base_excel(
    file: Optional[UploadFile] = File(None),
    mes: Optional[str] = Form("OCTUBRE"),
    ano: Optional[int] = Form(2026),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        import io
        filename_source = "INVETARIO SIMPLIFICADO OCT.xlsx"
        if file is not None and file.filename:
            content = await file.read()
            excel_source = io.BytesIO(content)
            filename_source = file.filename
        else:
            local_file = config.DATA_DIR / "INVETARIO_SIMPLIFICADO_OCT.xlsx"
            if not local_file.exists():
                raise HTTPException(status_code=404, detail="No se encontró el archivo base local INVETARIO_SIMPLIFICADO_OCT.xlsx")
            excel_source = local_file

        res = db.import_inventario_simplificado_excel(excel_source, mes=mes, ano=ano, source_name=filename_source)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al importar base Excel: {e}")

import threading
import subprocess
import sys

# Estado global del proceso de sincronización RPA
RPA_STATE = {
    "running": False,
    "status": "idle",
    "message": "En espera",
    "records_inserted": 0,
    "error": None
}

def _run_rpa_task(target: Optional[str] = "inventario", mode: str = "auto", fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    global RPA_STATE
    RPA_STATE["running"] = True
    RPA_STATE["status"] = "running"
    RPA_STATE["error"] = None

    def update_progress(msg: str):
        RPA_STATE["message"] = msg
        print(f"[RPA PROGRESO] {msg}")

    try:
        from downloader import SiiaDownloader
        from main import process_all_downloads
        downloader = SiiaDownloader()

        if mode == "auto":
            # ==========================================
            # MODO 100% AUTOMÁTICO (HEADLESS - WIFI READY)
            # ==========================================
            if target == "inventario":
                update_progress("Iniciando sesión silenciosa en SIIA...")
                downloader.download_existencias_auto(localidad_id="1836", progress_callback=update_progress)
                update_progress("Actualizando existencias en la base de datos...")
                db.clear_inventory()
                process_all_downloads()
                RPA_STATE["status"] = "completed"
                RPA_STATE["message"] = "¡Inventario sincronizado exitosamente! Existencias actualizadas."

            elif target == "entradas_salidas":
                today = datetime.date.today()
                f_ini = fecha_inicio or today.strftime("%Y-%m-01")
                f_fin = fecha_fin or today.strftime("%Y-%m-%d")

                update_progress(f"Iniciando descarga silenciosa de Entradas y Salidas ({f_ini} al {f_fin})...")
                downloader.download_movimientos_auto(fecha_inicio=f_ini, fecha_fin=f_fin, localidad_id="1836", progress_callback=update_progress)
                update_progress("Importando movimientos a la base de datos...")
                process_all_downloads()
                RPA_STATE["status"] = "completed"
                RPA_STATE["message"] = f"¡Entradas y Salidas ({f_ini} al {f_fin}) sincronizadas exitosamente!"

            elif target == "ambos":
                today = datetime.date.today()
                f_ini = fecha_inicio or today.strftime("%Y-%m-01")
                f_fin = fecha_fin or today.strftime("%Y-%m-%d")

                update_progress("1/2: Descargando existencias completas...")
                downloader.download_existencias_auto(localidad_id="1836", progress_callback=update_progress)

                update_progress(f"2/2: Descargando Entradas y Salidas ({f_ini} al {f_fin})...")
                downloader.download_movimientos_auto(fecha_inicio=f_ini, fecha_fin=f_fin, localidad_id="1836", progress_callback=update_progress)

                update_progress("Importando todos los archivos a la base de datos...")
                process_all_downloads()
                RPA_STATE["status"] = "completed"
                RPA_STATE["message"] = "¡Sincronización completa (Existencias + Movimientos) finalizada con éxito!"

        else:
            # ==========================================
            # MODO INTERACTIVO (CON VENTANA EN EL SERVIDOR)
            # ==========================================
            target_text = "Entradas y Salidas" if target == "entradas_salidas" else ("Inventario" if target == "inventario" else "SIIA")
            update_progress(f"Iniciando sesión interactiva en {target_text}... Descargue el reporte y cierre la ventana para importar.")
            downloader.run_interactive_session(target=target)
            update_progress("Procesando descargas automáticas...")
            process_all_downloads()
            RPA_STATE["status"] = "completed"
            RPA_STATE["message"] = "Sincronización interactiva completada exitosamente."

    except Exception as e:
        RPA_STATE["status"] = "failed"
        RPA_STATE["error"] = str(e)
        RPA_STATE["message"] = f"Error en sincronización: {e}"
        print(f"[RPA ERROR] {e}")
    finally:
        RPA_STATE["running"] = False

@app.post("/api/rpa-sync")
async def rpa_sync(
    force: bool = False, 
    target: Optional[str] = "inventario",
    mode: str = "auto",
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_any_permission("actualizar_inventario", "gestionar_movimientos")),
):
    """
    Inicia la sincronización con SIIA.
    - mode="auto": Descarga en segundo plano sin ventana (recomendado para uso en red WiFi).
    - mode="interactive": Abre la ventana de Chromium en la máquina servidor.
    """
    if not current_user.get("is_superadmin"):
        perms = current_user.get("permisos") or {}
        if target in ("entradas_salidas", "ambos") and not perms.get("gestionar_movimientos"):
            raise HTTPException(
                status_code=403,
                detail="No tiene permisos para sincronizar Entradas y Salidas. Solo puede actualizar Existencias de Inventario.",
            )
        if target == "inventario" and not perms.get("actualizar_inventario"):
            raise HTTPException(
                status_code=403,
                detail="No tiene permisos para actualizar el Inventario desde SIIA.",
            )

    global RPA_STATE
    if RPA_STATE["running"]:
        if not force:
            return {"status": "busy", "message": "Ya hay una sincronización en curso. Puedes forzar el cierre si la sesión anterior quedó trabada."}
        # Forzar cierre de la sesión anterior
        try:
            from downloader import force_kill_session
            force_kill_session()
        except Exception:
            pass
        RPA_STATE["running"] = False
        RPA_STATE["status"] = "cancelled"

    # Iniciar en hilo independiente para no bloquear el servidor FastAPI
    threading.Thread(
        target=_run_rpa_task, 
        args=(target, mode, fecha_inicio, fecha_fin), 
        daemon=True
    ).start()

    msg = "Iniciando sincronización automática en segundo plano (WiFi)..." if mode == "auto" else "Abriendo ventana asistida de SIIA en el servidor..."
    return {"status": "started", "message": msg, "mode": mode, "target": target}

@app.post("/api/rpa-cancel")
async def rpa_cancel(
    current_user: Dict[str, Any] = Depends(require_any_permission("actualizar_inventario", "gestionar_movimientos"))
):
    """Cancela y libera forzosamente cualquier sesión de RPA activa."""
    global RPA_STATE
    try:
        from downloader import force_kill_session
        force_kill_session()
    except Exception as e:
        print(f"[ERROR CANCEL] {e}")
    
    RPA_STATE["running"] = False
    RPA_STATE["status"] = "idle"
    RPA_STATE["message"] = "Sesión cancelada y liberada. Ya puedes iniciar de nuevo."
    RPA_STATE["error"] = None
    return {"status": "success", "message": "Sesión cerrada correctamente."}

@app.get("/api/rpa-status")
async def rpa_status(
    current_user: Dict[str, Any] = Depends(require_any_permission("actualizar_inventario", "gestionar_movimientos"))
):
    """Consulta el estado del proceso de sincronización RPA."""
    return RPA_STATE

@app.get("/api/siia-config")
async def get_siia_config(
    current_user: Dict[str, Any] = Depends(require_any_permission("actualizar_inventario", "gestionar_movimientos"))
):
    """Retorna la configuración, credenciales e IP de red local para el portal SIIA."""
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    return {
        "url": config.SIIA_URL,
        "username": config.SIIA_USERNAME,
        "password": config.SIIA_PASSWORD,
        "url_inventario": "https://siia.abisalud.com/main.php?opc=55",
        "url_movimientos": "https://siia.abisalud.com/main.php?opc=163",
        "local_ip": local_ip,
        "server_url": f"http://{local_ip}:{config.APP_PORT}"
    }

@app.get("/api/logs")
async def get_logs(
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_auditoria"))
):
    """Retorna historial de auditoría."""
    try:
        return db.get_summary()["recent_logs"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_lote_font_size_grande(val: str) -> str:
    l = len(str(val or '').strip())
    if l <= 10:
        return '28pt'
    elif l <= 13:
        return '23pt'
    elif l <= 16:
        return '19pt'
    elif l <= 20:
        return '16pt'
    elif l <= 25:
        return '13pt'
    elif l <= 32:
        return '11pt'
    else:
        return '9.5pt'

def get_lote_font_size_chico(val: str) -> str:
    l = len(str(val or '').strip())
    if l <= 9:
        return '7.8pt'
    elif l <= 12:
        return '6.8pt'
    elif l <= 16:
        return '5.8pt'
    elif l <= 20:
        return '5pt'
    elif l <= 26:
        return '4.4pt'
    else:
        return '3.8pt'

@app.post("/api/marbetes/generate-pdf")
async def generate_marbetes_pdf(
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_any_permission("marbetes")),
):
    """
    Genera un archivo PDF fiel a los formatos oficiales tamaño Carta
    recibiendo la lista de marbetes y el formato ('grande' o 'chico').
    """
    import tempfile
    from playwright.async_api import async_playwright

    items = payload.get("items", [])
    formato = payload.get("formato", "grande")

    if not items:
        raise HTTPException(status_code=400, detail="No se proporcionaron marbetes para generar el PDF.")

    fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y")
    items_per_page = 2 if formato == "grande" else 9
    total_pages = (len(items) + items_per_page - 1) // items_per_page

    pages_html = ""
    for p in range(total_pages):
        page_items = items[p * items_per_page : (p + 1) * items_per_page]
        
        if formato == "grande":
            cards_html = ""
            for it in page_items:
                raw_desc = (it.get('descripcion') or '').strip()
                it_fecha = it.get('fecha_conteo') or fecha_hoy
                raw_cant = it.get('cantidad')
                it_cant = '' if raw_cant is None or str(raw_cant).strip() == '' else str(raw_cant).strip()
                # Si la descripción es excesivamente larga, recortar con elipsis para evitar que desborde y empuje a 2 páginas
                if len(raw_desc) > 165:
                    disp_desc = raw_desc[:162].rstrip() + "..."
                else:
                    disp_desc = raw_desc

                cards_html += f"""
                <div class="marbete-grande">
                    <div class="mg-inner">
                        <div class="mg-header-row">
                            <div class="mg-header-label">CLAVE</div>
                        <div class="mg-header-clave">{it.get('clave', '')}</div>
                    </div>
                    <div class="mg-number-row">
                        <div class="mg-number-center">{it.get('clave_corta', '')}</div>
                        <div class="mg-status-side">
                            <span>Verde</span>
                            <span>Amarillo</span>
                            <span>Rojo</span>
                        </div>
                    </div>
                    <div class="mg-desc-container">
                        <div class="mg-desc-title">Descripción</div>
                        <div class="mg-desc-text">{disp_desc}</div>
                    </div>
                    <div class="mg-lote-cad-titles">
                        <div class="mg-col-half">Lote</div>
                        <div class="mg-col-half">Caducidad</div>
                    </div>
                    <div class="mg-lote-cad-vals">
                        <div class="mg-lote-val" style="font-size: {get_lote_font_size_grande(it.get('lote', ''))};">{it.get('lote', '')}</div>
                        <div class="mg-cad-val" style="font-size: {get_lote_font_size_grande(it.get('caducidad', ''))};">{it.get('caducidad', '')}</div>
                    </div>
                    <table class="mg-table-ctrl">
                        <tr>
                            <th class="header-col">Fecha</th>
                            <td class="val-col first-date">{it_fecha}</td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                        <tr>
                            <th class="header-col">Cantidad</th>
                            <td class="val-col first-val">{it_cant}</td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                    </table>
                    </div>
                </div>
                """
            pages_html += f'<div class="print-page page-grande">{cards_html}</div>'
        else:
            cards_html = ""
            for it in page_items:
                raw_desc = (it.get('descripcion') or '').strip()
                it_fecha = it.get('fecha_conteo') or fecha_hoy
                raw_cant = it.get('cantidad')
                it_cant = '' if raw_cant is None or str(raw_cant).strip() == '' else str(raw_cant).strip()
                if len(raw_desc) > 130:
                    disp_desc = raw_desc[:127].rstrip() + "..."
                else:
                    disp_desc = raw_desc

                cards_html += f"""
                <div class="marbete-chico">
                    <div class="mc-header-row">
                        <div class="mc-header-label">Clave</div>
                        <div class="mc-header-clave">{it.get('clave', '')}</div>
                    </div>
                    <div class="mc-number-row">
                        <div class="mc-number-center">{it.get('clave_corta', '')}</div>
                    </div>
                    <div class="mc-desc-container">
                        <div class="mc-desc-text">{disp_desc}</div>
                    </div>
                    <div class="mc-lote-cad-titles">
                        <div class="mc-col-half">Lote</div>
                        <div class="mc-col-half">Caducidad</div>
                    </div>
                    <div class="mc-lote-cad-vals">
                        <div class="mc-col-half" style="border-right: 1.2px solid #000000; font-size: {get_lote_font_size_chico(it.get('lote', ''))};">{it.get('lote', '')}</div>
                        <div class="mc-col-half" style="font-size: {get_lote_font_size_chico(it.get('caducidad', ''))};">{it.get('caducidad', '')}</div>
                    </div>
                    <table class="mc-table-ctrl">
                        <tr>
                            <th class="header-col">Fecha</th>
                            <td class="val-col first-date">{it_fecha}</td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                        <tr>
                            <th class="header-col">Cant.</th>
                            <td class="val-col first-val">{it_cant}</td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                        <tr>
                            <th class="header-col">Fecha</th>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                        <tr>
                            <th class="header-col">Cant.</th>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                    </table>
                </div>
                """
            pages_html += f'<div class="print-page page-chico">{cards_html}</div>'

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif; }}
    @page {{ size: Letter portrait; margin: 12mm 13mm 12mm 13mm; }}
    body {{ background: #ffffff; color: #000000; }}
    .print-page {{
        width: 186mm;
        page-break-after: always;
        break-after: page;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-sizing: border-box;
    }}
    .print-page:last-child {{
        page-break-after: auto;
        break-after: auto;
    }}
    /* GRANDE (185mm de ancho x 120mm de largo con zoom general sin espacios en blanco) */
    .page-grande {{ width: 186mm; gap: 6mm; justify-content: flex-start; margin: 0 auto; }}
    .marbete-grande {{
        width: 185mm;
        height: 120mm;
        box-sizing: border-box;
        border: 1.5px solid #000000;
        background: #ffffff;
        color: #000000;
        overflow: hidden;
    }}
    .mg-inner {{
        width: 180mm;
        height: 115mm;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        transform: scale(calc(185 / 180), calc(120 / 115));
        transform-origin: top left;
    }}
    .mg-header-row {{ display: flex; border-bottom: 1.2px solid #000000; height: 12.5mm; }}
    .mg-header-label {{ width: 63%; border-right: 1.2px solid #000000; font-size: 15.5pt; font-weight: bold; display: flex; align-items: center; padding-left: 10px; letter-spacing: 0.5px; }}
    .mg-header-clave {{ width: 37%; font-size: 15pt; font-weight: bold; display: flex; align-items: center; justify-content: center; }}
    .mg-number-row {{ display: flex; border-bottom: 1.2px solid #000000; height: 27.5mm; align-items: center; position: relative; }}
    .mg-number-center {{ flex: 1; text-align: center; font-size: 62pt; font-weight: 800; line-height: 1; }}
    .mg-status-side {{ position: absolute; right: 18px; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; gap: 2px; font-size: 7.5pt; font-weight: bold; line-height: 1.15; }}
    .mg-desc-container {{ border-bottom: 1.2px solid #000000; padding: 0; height: 26mm; display: flex; flex-direction: column; overflow: hidden; }}
    .mg-desc-title {{ text-align: center; font-size: 10pt; font-weight: bold; height: 7mm; display: flex; align-items: center; justify-content: center; border-bottom: 1.2px solid #000000; margin: 0; }}
    .mg-desc-text {{ font-size: 8.5pt; font-weight: bold; text-align: center; line-height: 1.25; text-transform: uppercase; padding: 2px 8px; flex: 1; display: flex; align-items: center; justify-content: center; overflow: hidden; word-break: break-word; }}
    .mg-lote-cad-titles {{ display: flex; border-bottom: 1.2px solid #000000; font-size: 10.5pt; font-weight: bold; text-align: center; height: 8mm; align-items: center; }}
    .mg-col-half {{ width: 50%; padding: 0 4px; }}
    .mg-col-half:first-child {{ border-right: 1.2px solid #000000; }}
    .mg-lote-cad-vals {{ display: flex; text-align: center; height: 25mm; align-items: center; }}
    .mg-lote-val, .mg-cad-val {{
        width: 50%;
        height: 100%;
        font-size: 28pt;
        font-weight: bold;
        letter-spacing: 0.5px;
        font-family: Arial, Helvetica, sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-sizing: border-box;
        word-break: break-all;
        overflow-wrap: anywhere;
        line-height: 1.15;
        padding: 0 4px;
        overflow: hidden;
    }}
    .mg-lote-val {{ border-right: 1.2px solid #000000; }}
    .mg-table-ctrl {{ width: 100%; border-collapse: collapse; margin-top: auto; }}
    .mg-table-ctrl th, .mg-table-ctrl td {{ border: 1.2px solid #000000; text-align: center; font-weight: bold; }}
    .mg-table-ctrl tr:first-child th, .mg-table-ctrl tr:first-child td {{ height: 5.2mm; font-size: 8pt; }}
    .mg-table-ctrl tr:last-child th, .mg-table-ctrl tr:last-child td {{ height: 10.2mm; font-size: 8pt; }}
    .mg-table-ctrl tr:last-child td.first-val {{ font-size: 15pt; font-weight: bold; }}
    .mg-table-ctrl th.header-col {{ width: 12.5%; }}
    .mg-table-ctrl td.val-col {{ width: 12.5%; }}

    /* CHICO (Fiel a marbete chico.pdf - 3x3, 6.5cm de alto) */
    .page-chico {{
        display: grid !important;
        grid-template-columns: repeat(3, 58mm);
        grid-template-rows: repeat(3, 65mm);
        gap: 5mm 5mm;
        justify-content: center;
        align-content: start;
        margin: 0 auto;
    }}
    .marbete-chico {{
        width: 58mm;
        height: 65mm;
        box-sizing: border-box;
        border: 1.2px solid #000000;
        background: #ffffff;
        color: #000000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }}
    .mc-header-row {{ display: flex; border-bottom: 1.2px solid #000000; height: 6mm; align-items: center; }}
    .mc-header-label {{ width: 35%; border-right: 1.2px solid #000000; font-size: 7.5pt; font-weight: bold; text-align: center; }}
    .mc-header-clave {{ width: 65%; font-size: 7.2pt; font-weight: bold; text-align: center; overflow: hidden; white-space: nowrap; }}
    .mc-number-row {{ height: 13.5mm; display: flex; align-items: center; justify-content: center; border-bottom: 1.2px solid #000000; }}
    .mc-number-center {{ font-size: 26pt; font-weight: 800; line-height: 1; }}
    .mc-desc-container {{ height: 16mm; padding: 2px 4px; border-bottom: 1.2px solid #000000; display: flex; align-items: center; justify-content: center; text-align: center; overflow: hidden; }}
    .mc-desc-text {{ font-size: 5.6pt; font-weight: bold; line-height: 1.15; text-transform: uppercase; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }}
    .mc-lote-cad-titles {{ display: flex; border-bottom: 1.2px solid #000000; font-size: 6.8pt; font-weight: bold; text-align: center; height: 4.8mm; align-items: center; }}
    .mc-col-half {{ width: 50%; }}
    .mc-col-half:first-child {{ border-right: 1.2px solid #000000; }}
    .mc-lote-cad-vals {{ display: flex; border-bottom: 1.2px solid #000000; font-size: 7.8pt; font-weight: bold; text-align: center; height: 7.5mm; align-items: center; }}
    .mc-lote-cad-vals .mc-col-half {{
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-sizing: border-box;
        padding: 0 2px;
        word-break: break-all;
        overflow-wrap: anywhere;
        line-height: 1.1;
        overflow: hidden;
    }}
    .mc-table-ctrl {{ width: 100%; border-collapse: collapse; margin-top: 0; flex: 1; }}
    .mc-table-ctrl th, .mc-table-ctrl td {{ border: 1.2px solid #000000; text-align: center; font-size: 5.5pt; font-weight: bold; padding: 0 1px; vertical-align: middle; }}
    .mc-table-ctrl th.header-col {{ width: 22%; min-width: 12mm; font-size: 5.5pt; letter-spacing: -0.2px; }}
    .mc-table-ctrl td.val-col {{ width: 15.6%; }}
    .mc-table-ctrl td.first-date {{ font-size: 4.5pt; line-height: 1.05; font-weight: bold; padding: 0; }}
    .mc-table-ctrl td.first-val {{ font-size: 7pt; font-weight: 800; }}
</style>
</head>
<body>
{pages_html}
</body>
</html>"""

    # Guardar en archivo temporal y convertir a PDF mediante Playwright
    pdf_path = config.DOWNLOAD_DIR / f"marbetes_{formato}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    try:
        from playwright.sync_api import sync_playwright
        import concurrent.futures

        def _generate_sync():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_content(html_content, wait_until="load")
                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    print_background=True,
                    margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
                )
                browser.close()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _generate_sync)

        if not pdf_path.exists():
            raise HTTPException(status_code=500, detail="No se pudo crear el archivo PDF.")

        return FileResponse(
            path=str(pdf_path),
            filename=pdf_path.name,
            media_type="application/pdf"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print(f"\n[SERVIDOR] Iniciando Dashboard SIIA Abisalud en http://localhost:{config.APP_PORT} ...")
    uvicorn.run("app:app", host=config.APP_HOST, port=config.APP_PORT, reload=True)
