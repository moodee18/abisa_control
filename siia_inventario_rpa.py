"""
Módulo de Automatización Robótica (RPA) para Inventarios en SIIA Abisalud.
Soporta:
1. Alta de Inventario Masiva (opc=78): Generación de cortes periódicos y descarga de PDFs.
2. Seguimiento de Inventario Masivo (opc=82): Captura de cantidades detalladas por hoja y finalización/ajuste.
"""

import os
import re
import sys
import json
import time
import shutil
import zipfile
import threading
import urllib.request
import ssl
from collections import defaultdict
from typing import Dict, Any, Optional, List, Callable
import openpyxl

import config

class SiiaInventarioRPA:
    def __init__(self):
        self.state: Dict[str, Any] = {
            "running": False,
            "type": None,           # 'alta' | 'seguimiento'
            "status": "idle",       # 'idle' | 'running' | 'completed' | 'cancelled' | 'failed'
            "message": "En espera",
            "progress_percent": 0,
            "current_item": "",
            "current_index": 0,
            "total_items": 0,
            "current_page": 0,
            "total_pages": 0,
            "matched_count": 0,
            "total_records": 0,
            "items_results": [],    # Detalle por almacén
            "logs": [],             # Bitácora de eventos
            "zip_url": None,
            "error": None
        }
        self.cancel_requested = False
        self._lock = threading.Lock()

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.state)

    def log(self, message: str):
        print(f"[SIIA RPA] {message}")
        with self._lock:
            self.state["message"] = message
            timestamp = time.strftime("%H:%M:%S")
            self.state["logs"].append(f"[{timestamp}] {message}")
            if len(self.state["logs"]) > 200:
                self.state["logs"] = self.state["logs"][-200:]

    def cancel(self):
        with self._lock:
            self.cancel_requested = True
            self.state["status"] = "cancelling"
            self.state["message"] = "Cancelación solicitada..."

    # =========================================================================
    # 1. ALTA DE INVENTARIOS (opc=78)
    # =========================================================================
    def ejecutar_alta_masiva(
        self,
        excel_path: str,
        localidad_id: str = "1836",
        tipo_captura: str = "1",
        descargar_pdfs: bool = True
    ):
        with self._lock:
            self.state.update({
                "running": True,
                "type": "alta",
                "status": "running",
                "message": "Iniciando proceso de Alta de Inventarios...",
                "progress_percent": 0,
                "current_index": 0,
                "total_items": 0,
                "items_results": [],
                "logs": [],
                "zip_url": None,
                "error": None
            })
            self.cancel_requested = False

        try:
            # 1. Leer almacenes del Excel
            almacenes = self._extract_almacenes_from_excel(excel_path)
            if not almacenes:
                raise ValueError("No se encontraron nombres de almacén válidos en el archivo Excel proporcionado.")

            with self._lock:
                self.state["total_items"] = len(almacenes)

            self.log(f"Se cargaron {len(almacenes)} almacenes para procesar en Alta de Inventario.")

            # Directorios de descarga
            out_dir = os.path.abspath("downloads/altas_inventario_pdf")
            os.makedirs(out_dir, exist_ok=True)
            zip_path = os.path.abspath("downloads/Altas_Inventario_SIIA.zip")

            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': 1366, 'height': 850})

                dialogs = []
                def on_dialog(dialog):
                    msg = dialog.message
                    dialogs.append(msg)
                    self.log(f"Alerta del sistema: {msg}")
                    dialog.accept()

                page.on("dialog", on_dialog)

                self.log("Iniciando sesión en SIIA...")
                page.goto(config.SIIA_URL, timeout=45000)
                page.wait_for_timeout(2000)
                page.fill("#usr", config.SIIA_USERNAME)
                page.fill("#psw", config.SIIA_PASSWORD)
                page.click("#btn")
                page.wait_for_timeout(4000)

                self.log("Navegando al módulo Alta de Inventario (opc=78)...")
                page.goto("https://siia.abisalud.com/main.php?opc=78", wait_until="networkidle", timeout=45000)
                page.wait_for_timeout(3000)

                iframe = page.frames[1]

                # Seleccionar localidad
                iframe.select_option('#localidad', localidad_id)
                page.wait_for_timeout(2500)

                # Obtener catálogo de almacenes del select
                opts = iframe.locator('#almacen option').all()
                siia_map = {}
                for opt in opts:
                    val = opt.get_attribute('value')
                    txt = opt.text_content().strip().upper()
                    if val and val != '-1':
                        siia_map[txt] = val

                self.log(f"Catálogo de almacenes en SIIA cargado ({len(siia_map)} disponibles).")

                # Sesión HTTP para descargas directas de PDFs
                from downloader import SiiaDownloader
                dl = SiiaDownloader()
                cookies = dl.get_authenticated_session_cookies()
                cookie_hdr = '; '.join([f'{k}={v}' for k, v in cookies.items()])
                ctx_ssl = ssl.create_default_context()
                ctx_ssl.check_hostname = False
                ctx_ssl.verify_mode = ssl.CERT_NONE

                pdf_files_generated = []

                for idx, alm_nombre in enumerate(almacenes, start=1):
                    if self.cancel_requested:
                        self.log("Operación cancelada por el usuario.")
                        break

                    alm_norm = alm_nombre.strip().upper()
                    alm_id = siia_map.get(alm_norm)
                    if not alm_id:
                        for k, v in siia_map.items():
                            if alm_norm in k or k in alm_norm:
                                alm_id = v
                                break

                    percent = int((idx / len(almacenes)) * 100)
                    with self._lock:
                        self.state["current_index"] = idx
                        self.state["current_item"] = alm_nombre
                        self.state["progress_percent"] = percent

                    if not alm_id:
                        self.log(f"[{idx}/{len(almacenes)}] No se encontró en SIIA: {alm_nombre}")
                        with self._lock:
                            self.state["items_results"].append({
                                "num": idx,
                                "almacen": alm_nombre,
                                "id": None,
                                "estado": "NO_ENCONTRADO",
                                "mensaje": "Almacén no existe en el catálogo de SIIA"
                            })
                        continue

                    self.log(f"[{idx}/{len(almacenes)}] Generando alta para: {alm_nombre} (ID: {alm_id})...")
                    dialogs.clear()

                    try:
                        iframe.select_option('#almacen', alm_id)
                        page.wait_for_timeout(1000)

                        # Selección de Tipo de Captura (PC / HandHeld) si el campo está presente y visible
                        tipo_cap = iframe.locator('#tipo_captura')
                        if tipo_cap.count() > 0 and tipo_cap.is_visible():
                            try:
                                tipo_cap.select_option(str(tipo_captura))
                                page.wait_for_timeout(500)
                                self.log(f"   [Tipo Captura] Seleccionada opción '{tipo_captura}' (PC)")
                            except Exception as e_tc:
                                self.log(f"   [Aviso Tipo Captura] {e_tc}")

                        if iframe.locator('#btn_generar').count() > 0:
                            iframe.click('#btn_generar')
                        else:
                            iframe.click('input[value="Generar"]')
                        page.wait_for_timeout(3500)

                        last_dialog = dialogs[-1] if dialogs else ""
                        estado = "GENERADO"
                        if "Ajuste Pendiente" in last_dialog:
                            estado = "AJUSTE_PENDIENTE"
                        elif "previamente" in last_dialog:
                            estado = "YA_EXISTE"

                        # Descarga de PDF si se solicitó y existe
                        pdf_path = None
                        if descargar_pdfs:
                            clean_fn = f"{idx:02d}_{re.sub(r'[^a-zA-Z0-9_-]', '_', alm_norm[:40])}.pdf"
                            dest_pdf = os.path.join(out_dir, clean_fn)
                            pdf_url = f"https://siia.abisalud.com/almacen/inventarios/inventario_periodico/pdf.php?localidad={localidad_id}&almacen={alm_id}&opc=1"
                            try:
                                req = urllib.request.Request(pdf_url, headers={'Cookie': cookie_hdr, 'User-Agent': 'Mozilla/5.0'})
                                with urllib.request.urlopen(req, context=ctx_ssl, timeout=15) as r:
                                    data = r.read()
                                    if data.startswith(b'%PDF'):
                                        with open(dest_pdf, 'wb') as f_pdf:
                                            f_pdf.write(data)
                                        pdf_files_generated.append((clean_fn, dest_pdf))
                                        pdf_path = dest_pdf
                            except Exception as e_pdf:
                                print(f"Error descargando PDF para {alm_nombre}: {e_pdf}")

                        with self._lock:
                            self.state["items_results"].append({
                                "num": idx,
                                "almacen": alm_nombre,
                                "id": alm_id,
                                "estado": estado,
                                "mensaje": last_dialog or "Alta procesada",
                                "pdf": os.path.basename(pdf_path) if pdf_path else None
                            })

                    except Exception as e_item:
                        self.log(f"Error en almacén {alm_nombre}: {e_item}")
                        with self._lock:
                            self.state["items_results"].append({
                                "num": idx,
                                "almacen": alm_nombre,
                                "id": alm_id,
                                "estado": "ERROR",
                                "mensaje": str(e_item)
                            })

                browser.close()

            # Empaquetar ZIP si hay archivos
            if pdf_files_generated:
                self.log(f"Empaquetando {len(pdf_files_generated)} PDFs en {zip_path}...")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                    for arcname, fpath in pdf_files_generated:
                        z.write(fpath, arcname=arcname)
                # Copiar a Descargas de Windows
                user_dl = os.path.join(os.path.expanduser("~"), "Downloads", "Altas_Inventario_SIIA.zip")
                try:
                    shutil.copy2(zip_path, user_dl)
                except:
                    pass
                with self._lock:
                    self.state["zip_url"] = "/api/siia-rpa/download/altas-zip"

            with self._lock:
                self.state["status"] = "cancelled" if self.cancel_requested else "completed"
                self.state["running"] = False
                self.state["progress_percent"] = 100
                self.state["message"] = f"Proceso de Altas terminado. {len(self.state['items_results'])} almacenes procesados."

        except Exception as e_main:
            self.log(f"ERROR CRÍTICO: {e_main}")
            with self._lock:
                self.state["status"] = "failed"
                self.state["running"] = False
                self.state["error"] = str(e_main)
                self.state["message"] = f"Fallo en el proceso de altas: {e_main}"

    # =========================================================================
    # 2. SEGUIMIENTO DE INVENTARIO (opc=82)
    # =========================================================================
    def ejecutar_seguimiento_masivo(
        self,
        excel_path: str,
        localidad_id: str = "1836",
        auto_finalizar: bool = True,
        guardar_evidencias: bool = True
    ):
        with self._lock:
            self.state.update({
                "running": True,
                "type": "seguimiento",
                "status": "running",
                "message": "Iniciando Seguimiento de Inventario Masivo...",
                "progress_percent": 0,
                "current_index": 0,
                "total_items": 0,
                "current_page": 0,
                "total_pages": 0,
                "matched_count": 0,
                "total_records": 0,
                "items_results": [],
                "logs": [],
                "zip_url": None,
                "error": None
            })
            self.cancel_requested = False

        try:
            # 1. Cargar datos del Excel
            excel_data, total_recs = self._extract_seguimiento_from_excel(excel_path)
            if not excel_data:
                raise ValueError("El archivo Excel no contiene datos válidos o columnas reconocibles (Código Barras, Lote, Almacén, Cantidad).")

            almacenes_list = sorted(excel_data.keys())
            with self._lock:
                self.state["total_items"] = len(almacenes_list)
                self.state["total_records"] = total_recs

            self.log(f"Se cargaron {len(almacenes_list)} almacenes y {total_recs} registros del Excel.")

            proofs_dir = os.path.abspath("downloads/evidencias_seguimiento")
            os.makedirs(proofs_dir, exist_ok=True)
            zip_path = os.path.abspath("downloads/Evidencias_Seguimiento_Inventarios.zip")
            proof_files = []

            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': 1366, 'height': 850})

                def on_dialog(dialog):
                    self.log(f"  [DIALOG] {dialog.type.upper()}: '{dialog.message}' -> Aceptado")
                    dialog.accept()

                page.on("dialog", on_dialog)

                self.log("Iniciando sesión en SIIA...")
                page.goto(config.SIIA_URL, timeout=45000)
                page.wait_for_timeout(2000)
                page.fill("#usr", config.SIIA_USERNAME)
                page.fill("#psw", config.SIIA_PASSWORD)
                page.click("#btn")
                page.wait_for_timeout(4000)

                self.log("Navegando a Seguimiento de Inventario (opc=82)...")
                page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle", timeout=45000)
                page.wait_for_timeout(3000)

                iframe = page.frames[1]

                # Cargar localidades y almacenes
                iframe.select_option('#localidad', localidad_id)
                try:
                    iframe.wait_for_function(
                        "() => { const a = document.getElementById('almacen'); return a && !a.disabled && a.options.length > 1; }",
                        timeout=12000
                    )
                except Exception:
                    page.wait_for_timeout(3000)
                page.wait_for_timeout(1000)

                # Mapeo de inventarios abiertos
                seg_map = {}
                for opt in iframe.locator('#almacen option').all():
                    v = opt.get_attribute('value')
                    t = opt.text_content().strip().upper()
                    if v and v != '-1':
                        seg_map[t] = v

                self.log(f"Inventarios activos encontrados en SIIA: {len(seg_map)}")

                for idx, alm_nombre in enumerate(almacenes_list, start=1):
                    if self.cancel_requested:
                        self.log("Operación cancelada por el usuario.")
                        break

                    alm_norm = alm_nombre.strip().upper()
                    inv_id = seg_map.get(alm_norm)
                    if not inv_id:
                        for k, v in seg_map.items():
                            if alm_norm in k or k in alm_norm:
                                inv_id = v
                                break

                    percent = int((idx / len(almacenes_list)) * 100)
                    with self._lock:
                        self.state["current_index"] = idx
                        self.state["current_item"] = alm_nombre
                        self.state["progress_percent"] = percent

                    if not inv_id:
                        self.log(f"[{idx}/{len(almacenes_list)}] No se encontró corte activo en SIIA: {alm_nombre}")
                        with self._lock:
                            self.state["items_results"].append({
                                "num": idx,
                                "almacen": alm_nombre,
                                "id": None,
                                "paginas": 0,
                                "insumos_excel": len(excel_data[alm_nombre]),
                                "insumos_capturados": 0,
                                "estado": "SIN_CORTE_ACTIVO",
                                "mensaje": "No se encontró un corte de inventario activo para este almacén."
                            })
                        continue

                    self.log(f"\n=======================================================")
                    self.log(f"[{idx}/{len(almacenes_list)}] Procesando: {alm_nombre} (ID: {inv_id})")

                    try:
                        # Asegurar localidad activa
                        if iframe.locator('#localidad').input_value() != localidad_id or iframe.locator('#almacen option').count() <= 1:
                            iframe.select_option('#localidad', localidad_id)
                            try:
                                iframe.wait_for_function(
                                    "() => { const a = document.getElementById('almacen'); return a && !a.disabled && a.options.length > 1; }",
                                    timeout=12000
                                )
                            except Exception:
                                page.wait_for_timeout(3000)
                            page.wait_for_timeout(1000)

                        iframe.select_option('#almacen', inv_id)
                        page.wait_for_timeout(3500)

                        pool = list(excel_data[alm_nombre])
                        total_almacen_excel = len(pool)
                        total_matched_almacen = 0

                        # Detectar paginación
                        pag_select = iframe.locator('#paginacion')
                        if pag_select.count() > 0 and pag_select.is_visible():
                            opts_pag = [o.get_attribute('value') for o in pag_select.locator('option').all()]
                            tot_pages = len(opts_pag) if opts_pag else 1
                        else:
                            tot_pages = 1

                        with self._lock:
                            self.state["total_pages"] = tot_pages

                        self.log(f"Almacén: {alm_nombre} | Insumos: {total_almacen_excel} | Hojas en SIIA: {tot_pages}")

                        # Procesar página por página
                        for p_num in range(1, tot_pages + 1):
                            with self._lock:
                                self.state["current_page"] = p_num

                            if p_num > 1:
                                self.log(f" -> Navegando a Página {p_num} de {tot_pages}...")
                                iframe.select_option('#paginacion', str(p_num))
                                page.wait_for_timeout(3000)

                            rows = iframe.locator('#tbl_productos tr').all()
                            p_matched = 0

                            for r in rows:
                                try:
                                    lote = r.locator('td').nth(2).text_content().strip()
                                    cod = r.locator('td').nth(3).text_content().strip()
                                    cad = r.locator('td').nth(5).locator('input').input_value().strip()[:10]
                                    inp_cant = r.locator('td').nth(6).locator('input')

                                    match_idx = None
                                    # 1. lote + cod + cad
                                    for i, itm in enumerate(pool):
                                        if itm['lote'] == lote and itm['cod'] == cod and itm['cad'] == cad:
                                            match_idx = i
                                            break
                                    # 2. lote + cod
                                    if match_idx is None:
                                        for i, itm in enumerate(pool):
                                            if itm['lote'] == lote and itm['cod'] == cod:
                                                match_idx = i
                                                break
                                    # 3. lote
                                    if match_idx is None:
                                        for i, itm in enumerate(pool):
                                            if itm['lote'] == lote:
                                                match_idx = i
                                                break

                                    if match_idx is not None:
                                        matched_item = pool.pop(match_idx)
                                        cant_val = str(matched_item['cant'])
                                        inp_cant.fill(cant_val)
                                        inp_cant.dispatch_event('change')
                                        inp_cant.dispatch_event('keyup')
                                        total_matched_almacen += 1
                                        p_matched += 1
                                        with self._lock:
                                            self.state["matched_count"] += 1
                                except Exception:
                                    pass

                            self.log(f"   Página {p_num}: {p_matched} insumos llenados. Guardando...")
                            iframe.click('#btn_guardar')
                            page.wait_for_timeout(2500)

                        # Finalización y Captura de Evidencia Fotográfica
                        if auto_finalizar:
                            self.log(f" -> Marcando casilla 'Finalizado' para {alm_nombre}...")
                            iframe.locator('#finalizar').check()
                            page.wait_for_timeout(800)

                        # Captura de pantalla de evidencia ANTES del guardado final
                        # para que muestre el almacén seleccionado, los insumos con cantidades capturadas
                        # y la casilla 'Finalizado' marcada con su palomita (evitando el formulario reseteado en blanco)
                        clean_fn = f"{idx:02d}_{re.sub(r'[^a-zA-Z0-9_-]', '_', alm_norm[:35])}.png"
                        proof_path = os.path.join(proofs_dir, clean_fn)
                        if guardar_evidencias:
                            try:
                                page.screenshot(path=proof_path)
                                proof_files.append((clean_fn, proof_path))
                                self.log(f"   [Foto] Evidencia capturada con almacén '{alm_nombre}' e insumos en pantalla.")
                            except Exception as e_shot:
                                self.log(f"   [Aviso Foto] No se pudo guardar captura de evidencia: {e_shot}")

                        if auto_finalizar:
                            self.log(" -> Guardando consolidación final en SIIA...")
                            iframe.click('#btn_guardar')
                            page.wait_for_timeout(4000)

                        with self._lock:
                            self.state["items_results"].append({
                                "num": idx,
                                "almacen": alm_nombre,
                                "id": inv_id,
                                "paginas": tot_pages,
                                "insumos_excel": total_almacen_excel,
                                "insumos_capturados": total_matched_almacen,
                                "estado": "FINALIZADO" if auto_finalizar else "GUARDADO",
                                "mensaje": f"{total_matched_almacen}/{total_almacen_excel} insumos capturados en {tot_pages} hojas"
                            })

                        self.log(f"[{idx}/{len(almacenes_list)}] OK: {alm_nombre} finalizado con éxito.")

                    except Exception as e_alm:
                        self.log(f"Error procesando {alm_nombre}: {e_alm}")
                        with self._lock:
                            self.state["items_results"].append({
                                "num": idx,
                                "almacen": alm_nombre,
                                "id": inv_id,
                                "paginas": 0,
                                "insumos_excel": len(excel_data[alm_nombre]),
                                "insumos_capturados": 0,
                                "estado": "ERROR",
                                "mensaje": str(e_alm)
                            })
                        # Restaurar vista limpia
                        try:
                            page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle", timeout=30000)
                            page.wait_for_timeout(3000)
                        except:
                            pass

                browser.close()

            # Empaquetar evidencias en ZIP
            if proof_files:
                self.log(f"Empaquetando {len(proof_files)} evidencias en {zip_path}...")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                    for arcname, fpath in proof_files:
                        z.write(fpath, arcname=arcname)
                # Copiar a Descargas
                user_dl = os.path.join(os.path.expanduser("~"), "Downloads", "Evidencias_Seguimiento_Inventarios.zip")
                try:
                    shutil.copy2(zip_path, user_dl)
                except:
                    pass
                with self._lock:
                    self.state["zip_url"] = "/api/siia-rpa/download/evidencias-zip"

            with self._lock:
                self.state["status"] = "cancelled" if self.cancel_requested else "completed"
                self.state["running"] = False
                self.state["progress_percent"] = 100
                self.state["message"] = f"Seguimiento terminado. {len(self.state['items_results'])} almacenes procesados."

        except Exception as e_main:
            self.log(f"ERROR CRÍTICO: {e_main}")
            with self._lock:
                self.state["status"] = "failed"
                self.state["running"] = False
                self.state["error"] = str(e_main)
                self.state["message"] = f"Fallo en seguimiento: {e_main}"

    # =========================================================================
    # HELPERS DE EXTRACCIÓN EXCEL
    # =========================================================================
    def _extract_almacenes_from_excel(self, path: str) -> List[str]:
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        almacenes = []
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []

        # Buscar índice de columna de almacén
        header = [str(c or '').strip().lower() for c in rows[0]]
        alm_col_idx = 0
        for i, h in enumerate(header):
            if any(k in h for k in ['almacen', 'almacén', 'nombre']):
                alm_col_idx = i
                break

        for r in rows[1:]:
            if r and len(r) > alm_col_idx and r[alm_col_idx]:
                val = str(r[alm_col_idx]).strip()
                if val and val.lower() not in ['almacen', 'almacén', 'nombre'] and val not in almacenes:
                    almacenes.append(val)

        return almacenes

    def _extract_seguimiento_from_excel(self, path: str):
        wb = openpyxl.load_workbook(path, data_only=True)
        # Buscar hoja2 o hoja activa
        ws = wb['Hoja2'] if 'Hoja2' in wb.sheetnames else wb.active
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            return {}, 0

        header = [str(c or '').strip().lower() for c in rows[0]]
        # Identificar columnas
        col_map = {'cod': 0, 'clave': 1, 'desc': 2, 'lote': 3, 'alm': 4, 'cant': 5, 'cad': 6}
        for i, h in enumerate(header):
            if 'barras' in h or 'codigo' in h or 'código' in h: col_map['cod'] = i
            elif 'clave' in h: col_map['clave'] = i
            elif 'descrip' in h: col_map['desc'] = i
            elif 'lote' in h: col_map['lote'] = i
            elif 'alma' in h: col_map['alm'] = i
            elif 'cant' in h: col_map['cant'] = i
            elif 'caduc' in h: col_map['cad'] = i

        data_by_alm = defaultdict(list)
        total_recs = 0

        for r in rows[1:]:
            if not any(r):
                continue
            alm_val = r[col_map['alm']] if len(r) > col_map['alm'] else None
            if not alm_val:
                continue

            alm_norm = str(alm_val).strip().upper()
            cod_val = str(r[col_map['cod']] or '').strip() if len(r) > col_map['cod'] else ''
            clave_val = str(r[col_map['clave']] or '').strip() if len(r) > col_map['clave'] else ''
            desc_val = str(r[col_map['desc']] or '').strip() if len(r) > col_map['desc'] else ''
            lote_val = str(r[col_map['lote']] or '').strip() if len(r) > col_map['lote'] else ''
            cant_val = r[col_map['cant']] if len(r) > col_map['cant'] and r[col_map['cant']] is not None else 0
            cad_val = str(r[col_map['cad']] or '').strip()[:10] if len(r) > col_map['cad'] else ''

            data_by_alm[alm_norm].append({
                'cod': cod_val,
                'clave': clave_val,
                'desc': desc_val,
                'lote': lote_val,
                'cant': cant_val,
                'cad': cad_val
            })
            total_recs += 1

        return data_by_alm, total_recs

# Instancia singleton
siia_rpa_manager = SiiaInventarioRPA()

