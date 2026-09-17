import os
import re
import shutil
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from database import DatabaseManager, MovimientoRecord, InsumoRecord
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

# Servir la interfaz HTML principal
@app.get("/", response_class=HTMLResponse)
async def get_index():
    template_path = config.BASE_DIR / "templates" / "index.html"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Plantilla index.html no encontrada")
    return HTMLResponse(content=template_path.read_text(encoding="utf-8"))

# ==========================================
# ENDPOINTS REST API
# ==========================================

@app.get("/api/kpis")
async def get_kpis():
    """Retorna métricas generales del inventario."""
    try:
        return db.get_inventory_kpis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog")
async def get_catalog(search: Optional[str] = Query(None)):
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
    offset: int = Query(0, ge=0)
):
    """Retorna lista detallada de registros de inventario con filtros."""
    try:
        return db.get_records(clave=clave, search=search, lote=lote, almacen=almacen, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/{record_id}")
async def get_record(record_id: int):
    """Obtiene un registro específico por su ID."""
    record = db.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return record

@app.post("/api/inventory")
async def create_record(item: InsumoCreateRequest):
    """Crea un nuevo insumo / lote en la base de datos."""
    try:
        data = item.model_dump()
        result = db.create_record(data)
        return {"status": "success", "message": "Insumo registrado correctamente", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear insumo: {e}")

@app.put("/api/inventory/{record_id}")
async def update_record(record_id: int, item: InsumoUpdateRequest):
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
async def delete_record(record_id: int):
    """Elimina un registro de insumo."""
    success = db.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Insumo no encontrado para eliminar")
    return {"status": "success", "message": f"Insumo ID {record_id} eliminado exitosamente"}

@app.post("/api/clear")
@app.post("/api/inventory/clear")
@app.delete("/api/inventory")
async def clear_inventory():
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
async def clear_movimientos():
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

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
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
async def upload_movimientos_excel(file: UploadFile = File(...)):
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
async def upload_movimientos_pdf(files: List[UploadFile] = File(...)):
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
    page_size: int = 50
):
    """Obtiene el listado de entradas y salidas con filtros, búsqueda y paginación."""
    try:
        return db.get_movimientos(tipo=tipo, search=search, dia=dia, sort_by=sort_by, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clues/matrix")
async def get_clues_matrix(
    search: Optional[str] = None,
    dia_inicio: int = 1,
    dia_fin: int = 30
):
    """Obtiene la matriz oficial de CLUES (CSIMB003506) con stock unificado y salidas distribuidas por día."""
    try:
        return db.get_clues_matrix(search=search, dia_inicio=dia_inicio, dia_fin=dia_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_clues_official_excel(db_mgr: DatabaseManager, out_path: Path):
    """
    Genera el archivo Excel oficial idéntico a inventario_siplificado_cluesEnMayucula_ REPORTE DIARIO CAMBIOOOOOS.xlsx:
    - Hoja 1 'salidas por dia':
      * Fila 1: Banner verde superior 'SALIDAS SEPTIEMBRE' sobre columnas F1:AI1.
      * Fila 2: Encabezados en mayúsculas: CLUES, CLAVE, INVENTARIO DISPONIBLE, LOTE, F_CAD, 1..30.
      * Filas de datos: Registros consolidados por Clave y Lote.
      * Fila Inferior: 'TOTAL SALIDAS POR DÍA', con fórmulas =SUM(...) de piezas por cada día y total disponible.
      * Anchos y estilos fieles a la plantilla.
    - Hoja 2 'Salidas': Detalle cronológico de salidas con los 23 campos oficiales.
    - Hoja 3 'existencia': Reporte de existencias agrupadas.
    """
    wb = openpyxl.Workbook()
    # Hoja 1: salidas por dia
    ws1 = wb.active
    ws1.title = "salidas por dia"

    # 1. Fila 1: Banner verde superior combinado SALIDAS SEPTIEMBRE
    ws1.merge_cells("F1:AI1")
    f1 = ws1["F1"]
    f1.value = "SALIDAS SEPTIEMBRE"

    header_fill = PatternFill(start_color="1E7145", end_color="1E7145", fill_type="solid")
    header_font = Font(name="Aptos Narrow", size=11, bold=True, color="FFFFFF")
    center_align = Alignment(horizontal="center", vertical="center")
    thin_border_side = Side(style="thin", color="135824")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    for col in range(6, 36):
        cell = ws1.cell(1, col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = cell_border

    # 2. Fila 2: Encabezados en mayúsculas
    headers_row2 = ["CLUES", "CLAVE", "INVENTARIO DISPONIBLE", "LOTE", "F_CAD"] + [str(d) for d in range(1, 31)]
    ws1.row_dimensions[2].height = 26
    for idx, h in enumerate(headers_row2, 1):
        cell = ws1.cell(2, idx)
        cell.value = int(h) if h.isdigit() else h
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = cell_border

    # 3. Filas de datos (Días 1 al 30)
    matrix_data = db_mgr.get_clues_matrix(dia_inicio=1, dia_fin=30)
    rows = matrix_data.get("rows", [])
    days_list = matrix_data.get("days", list(range(1, 31)))

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

        # Días 1 al 30
        for d_idx, d in enumerate(days_list, 6):
            val = float(r.get("dias", {}).get(str(d), 0.0))
            c_day = ws1.cell(current_row, d_idx, val)
            c_day.number_format = "#,##0"
            c_day.alignment = Alignment(horizontal="right")

        for c in range(1, 36):
            ws1.cell(current_row, c).font = data_font
            ws1.cell(current_row, c).border = data_border

        current_row += 1

    last_data_row = current_row - 1

    # 4. FILA INFERIOR DE TOTALES: cuantas piezas salieron por día
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

    for c_idx in range(6, 36):
        col_letter = get_column_letter(c_idx)
        if last_data_row >= 3:
            c_tot_day = ws1.cell(tot_row, c_idx, f"=SUM({col_letter}3:{col_letter}{last_data_row})")
        else:
            c_tot_day = ws1.cell(tot_row, c_idx, 0)
        c_tot_day.number_format = "#,##0"
        c_tot_day.alignment = Alignment(horizontal="right", vertical="center")

    for c in range(1, 36):
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
    for c in range(6, 36):
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
    ws2.cell(3, 2, "2026-09-01 - 2026-09-30")

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
        # Catálogo para resolver descripciones faltantes
        desc_map = {}
        for row_desc in session.query(InsumoRecord.clave, InsumoRecord.descripcion).filter(
            InsumoRecord.descripcion.isnot(None), InsumoRecord.descripcion != ""
        ).all():
            c_clean = (row_desc.clave or "").strip()
            if c_clean and c_clean not in desc_map:
                desc_map[c_clean] = row_desc.descripcion.strip()

        clues_pattern = re.compile(r'^\d{3}\.\d{3}\.\d{3,5}(\.\d{2})?$')

        salidas_records = session.query(MovimientoRecord).filter(
            MovimientoRecord.tipo == "SALIDA",
            MovimientoRecord.tipo_movimiento == "PEDIDO"
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
            InsumoRecord.cantidad > 0
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
async def export_excel(tab: str = "tab-inventory"):
    """Genera y descarga el archivo Excel correspondiente a la pestaña activa en la interfaz."""
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
            generate_clues_official_excel(db, out_path)
            filename = f"inventario_siplificado_cluesEnMayucula_REPORTE_DIARIO_{today_str}.xlsx"

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

def _run_rpa_task(target: Optional[str] = None):
    global RPA_STATE
    RPA_STATE["running"] = True
    RPA_STATE["status"] = "running"
    target_text = "Entradas y Salidas" if target == "entradas_salidas" else ("Inventario" if target == "inventario" else "SIIA")
    RPA_STATE["message"] = f"Iniciando sesión automática en {target_text}... Descargue el reporte y CIERRE LA VENTANA para importar los datos."
    RPA_STATE["error"] = None

    try:
        from downloader import SiiaDownloader
        from main import process_all_downloads
        
        # 1. Ejecutar descarga asistida con login automático y navegación
        downloader = SiiaDownloader()
        downloader.run_interactive_session(target=target)
        
        # 2. Procesar descargas automáticamente
        RPA_STATE["message"] = "Procesando archivos descargados e importando a la base de datos..."
        process_all_downloads()

        RPA_STATE["status"] = "completed"
        RPA_STATE["message"] = "Sincronización e importación completada exitosamente."
    except Exception as e:
        RPA_STATE["status"] = "failed"
        RPA_STATE["error"] = str(e)
        RPA_STATE["message"] = f"Error en sincronización: {e}"
    finally:
        RPA_STATE["running"] = False

@app.post("/api/rpa-sync")
async def rpa_sync(force: bool = False, target: Optional[str] = None):
    """Inicia la sesión asistida del navegador para descargar reportes de SIIA en segundo plano."""
    global RPA_STATE
    if RPA_STATE["running"]:
        if not force:
            return {"status": "busy", "message": "Ya hay una sesión de sincronización en curso. Puedes forzar el cierre si la sesión anterior quedó trabada."}
        # Forzar cierre de la sesión anterior
        try:
            from downloader import force_kill_session
            force_kill_session()
        except Exception:
            pass
        RPA_STATE["running"] = False
        RPA_STATE["status"] = "cancelled"

    # Iniciar en hilo independiente para no bloquear el servidor FastAPI
    threading.Thread(target=_run_rpa_task, args=(target,), daemon=True).start()
    return {"status": "started", "message": "Se ha iniciado sesión automáticamente en SIIA. Al terminar de descargar, cierre la ventana para importar los datos."}

@app.post("/api/rpa-cancel")
async def rpa_cancel():
    """Cancela y libera forzosamente cualquier sesión de RPA activa."""
    global RPA_STATE
    try:
        from downloader import force_kill_session
        force_kill_session()
    except Exception as e:
        print(f"[ERROR CANCEL] {e}")
    
    RPA_STATE["running"] = False
    RPA_STATE["status"] = "idle"
    RPA_STATE["message"] = "Sesión cancelada y liberada. Ya puedes iniciar sesión de nuevo."
    RPA_STATE["error"] = None
    return {"status": "success", "message": "Sesión cerrada correctamente. Ya puedes ingresar."}

@app.get("/api/rpa-status")
async def rpa_status():
    """Consulta el estado del proceso de sincronización RPA."""
    return RPA_STATE

@app.get("/api/logs")
async def get_logs():
    """Retorna historial de auditoría."""
    try:
        return db.get_summary()["recent_logs"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/marbetes/generate-pdf")
async def generate_marbetes_pdf(payload: Dict[str, Any]):
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

    items_per_page = 2 if formato == "grande" else 9
    total_pages = (len(items) + items_per_page - 1) // items_per_page

    pages_html = ""
    for p in range(total_pages):
        page_items = items[p * items_per_page : (p + 1) * items_per_page]
        
        if formato == "grande":
            cards_html = ""
            for it in page_items:
                raw_desc = (it.get('descripcion') or '').strip()
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
                        <div class="mg-lote-val">{it.get('lote', '')}</div>
                        <div class="mg-cad-val">{it.get('caducidad', '')}</div>
                    </div>
                    <table class="mg-table-ctrl">
                        <tr>
                            <th class="header-col">Fecha</th>
                            <td class="val-col first-date">{it.get('fecha_conteo', '')}</td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                        <tr>
                            <th class="header-col">Cantidad</th>
                            <td class="val-col first-val">{it.get('cantidad', '')}</td>
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
                        <div class="mc-col-half" style="border-right: 1.2px solid #000000; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; padding: 0 2px;">{it.get('lote', '')}</div>
                        <div class="mc-col-half" style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis; padding: 0 2px;">{it.get('caducidad', '')}</div>
                    </div>
                    <table class="mc-table-ctrl">
                        <tr>
                            <th class="header-col">Fecha</th>
                            <td class="val-col first-date">{it.get('fecha_conteo', '')}</td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                            <td class="val-col"></td>
                        </tr>
                        <tr>
                            <th class="header-col">Cant.</th>
                            <td class="val-col first-val">{it.get('cantidad', '')}</td>
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
    .mg-lote-val, .mg-cad-val {{ width: 50%; font-size: 28pt; font-weight: bold; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; padding: 0 6px; }}
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
