import sys
import os
import re
import json
import time
import openpyxl
from collections import defaultdict

sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import config

PROGRESS_FILE = "scratch/seguimiento_progress.json"
PROOF_DIR = "scratch/proofs_inventarios"
os.makedirs(PROOF_DIR, exist_ok=True)
os.makedirs("scratch", exist_ok=True)

def sanitize_name(name):
    clean = re.sub(r'[\\/*?:"<>|.]', '_', name)
    return re.sub(r'\s+', '_', clean).strip('_')

def load_excel_data():
    wb = openpyxl.load_workbook('data/INV_OCTUBRE_11.xlsx', data_only=True)
    ws = wb['Hoja2']
    
    data_by_almacen = defaultdict(list)
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not any(r):
            continue
        cod, clave, desc, lote, alm, cant, cad = r[:7]
        if alm:
            alm_norm = str(alm).strip().upper()
            data_by_almacen[alm_norm].append({
                'cod': str(cod).strip() if cod is not None else '',
                'clave': str(clave).strip() if clave is not None else '',
                'desc': str(desc).strip() if desc is not None else '',
                'lote': str(lote).strip() if lote is not None else '',
                'cad': str(cad).strip()[:10] if cad is not None else '',
                'cant': cant if cant is not None else 0
            })
    return data_by_almacen

def load_seguimiento_ids():
    seg = {}
    with open('scratch/seguimiento_almacenes.txt', encoding='utf-8') as f:
        for line in f:
            if '|' in line:
                v, n = line.strip().split('|', 1)
                v = v.strip()
                n = n.strip()
                if v != '-1':
                    seg[n.upper()] = v
    return seg

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_progress(prog):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

def main():
    print("=== INICIANDO PROCESO MASIVO DE SEGUIMIENTO DE INVENTARIOS (75 ALMACENES) ===")
    
    excel_data = load_excel_data()
    seg_ids = load_seguimiento_ids()
    progress = load_progress()
    
    almacenes_a_procesar = sorted(excel_data.keys())
    total_almacenes = len(almacenes_a_procesar)
    print(f"Total almacenes en archivo Excel: {total_almacenes}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 850})
        page = context.new_page()
        
        dialog_history = []
        def on_dialog(dialog):
            print(f"  [DIALOG] {dialog.type.upper()}: '{dialog.message}' -> Aceptado")
            dialog_history.append({'type': dialog.type, 'message': dialog.message, 'time': time.time()})
            dialog.accept()
            
        page.on('dialog', on_dialog)
        
        # Login
        print("Iniciando sesión en SIIA...")
        page.goto(config.SIIA_URL, timeout=45000)
        page.wait_for_timeout(2000)
        page.fill("#usr", config.SIIA_USERNAME)
        page.fill("#psw", config.SIIA_PASSWORD)
        page.click("#btn")
        page.wait_for_timeout(4000)
        
        page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(3000)
        
        for idx, alm_nombre in enumerate(almacenes_a_procesar, start=1):
            if alm_nombre in progress and progress[alm_nombre].get('status') == 'FINALIZADO':
                print(f"[{idx:02d}/{total_almacenes}] YA FINALIZADO PREVIAMENTE: {alm_nombre}")
                continue
                
            inv_id = seg_ids.get(alm_nombre)
            if not inv_id:
                for s_name, s_id in seg_ids.items():
                    if alm_nombre == s_name or alm_nombre in s_name or s_name in alm_nombre:
                        inv_id = s_id
                        break
                        
            if not inv_id:
                print(f"[{idx:02d}/{total_almacenes}] ERROR: No se encontró ID en SIIA para {alm_nombre}")
                progress[alm_nombre] = {'num': idx, 'status': 'ERROR_NO_ID', 'error': 'No matching ID in SIIA'}
                save_progress(progress)
                continue
                
            print(f"\n=======================================================")
            print(f"[{idx:02d}/{total_almacenes}] PROCESANDO: {alm_nombre} (ID: {inv_id})")
            print(f"=======================================================")
            
            try:
                iframe = page.frames[1]
                
                # 1. Asegurar Localidad 1836 y catálogo de almacenes cargado
                loc_val = iframe.locator('#localidad').input_value()
                alm_opts_cnt = iframe.locator('#almacen option').count()
                
                if loc_val != '1836' or alm_opts_cnt <= 1:
                    print("Seleccionando Localidad: CS ALMACEN 2022...")
                    iframe.select_option('#localidad', '1836')
                    iframe.wait_for_function(
                        "() => { const a = document.getElementById('almacen'); return a && !a.disabled && a.options.length > 5; }",
                        timeout=15000
                    )
                    page.wait_for_timeout(1000)
                    
                # 2. Seleccionar el Almacén
                print(f"Seleccionando Almacén ID: {inv_id}...")
                iframe.select_option('#almacen', inv_id)
                # Esperar a que cargue la tabla de productos
                page.wait_for_timeout(3500)
                
                pool = list(excel_data[alm_nombre])
                total_items_excel = len(pool)
                total_matched = 0
                
                # 3. Detectar páginas
                pag_select = iframe.locator('#paginacion')
                if pag_select.count() > 0 and pag_select.is_visible():
                    opts = [o.get_attribute('value') for o in pag_select.locator('option').all()]
                    total_pages = len(opts) if opts else 1
                else:
                    total_pages = 1
                    
                print(f"Total registros en Excel: {total_items_excel} | Total páginas en SIIA: {total_pages}")
                
                # 4. Recorrer cada página
                for p_num in range(1, total_pages + 1):
                    p_str = str(p_num)
                    if p_num > 1:
                        print(f" -> Navegando a Página {p_num} de {total_pages}...")
                        iframe.select_option('#paginacion', p_str)
                        # Esperar a que se actualice la página
                        page.wait_for_timeout(3000)
                        
                    rows = iframe.locator('#tbl_productos tr').all()
                    print(f"   Página {p_num}: {len(rows)} filas detectadas en tabla SIIA")
                    
                    page_matched = 0
                    for row_idx, r in enumerate(rows):
                        try:
                            lote = r.locator('td').nth(2).text_content().strip()
                            cod = r.locator('td').nth(3).text_content().strip()
                            cad = r.locator('td').nth(5).locator('input').input_value().strip()[:10]
                            inp_cant = r.locator('td').nth(6).locator('input')
                            
                            # Buscar en pool
                            match_idx = None
                            # Nivel 1: lote + cod + cad
                            for i, item in enumerate(pool):
                                if item['lote'] == lote and item['cod'] == cod and item['cad'] == cad:
                                    match_idx = i
                                    break
                            # Nivel 2: lote + cod
                            if match_idx is None:
                                for i, item in enumerate(pool):
                                    if item['lote'] == lote and item['cod'] == cod:
                                        match_idx = i
                                        break
                            # Nivel 3: lote
                            if match_idx is None:
                                for i, item in enumerate(pool):
                                    if item['lote'] == lote:
                                        match_idx = i
                                        break
                                        
                            if match_idx is not None:
                                matched_item = pool.pop(match_idx)
                                cant_val = str(matched_item['cant'])
                                inp_cant.fill(cant_val)
                                inp_cant.dispatch_event('change')
                                inp_cant.dispatch_event('keyup')
                                total_matched += 1
                                page_matched += 1
                        except Exception as e_row:
                            print(f"   Advertencia fila {row_idx}: {e_row}")
                            
                    print(f"   Página {p_num}: {page_matched} insumos capturados. Guardando página...")
                    iframe.click('#btn_guardar')
                    page.wait_for_timeout(2500)
                    
                # 5. Marcar Finalizado y Capturar Evidencia Fotográfica antes de resetear
                print(f" -> Marcando 'Finalizado' para {alm_nombre}...")
                chk_fin = iframe.locator('#finalizar')
                chk_fin.check()
                page.wait_for_timeout(800)
                
                # Captura de pantalla de evidencia ANTES del guardado final
                # para que muestre el almacén seleccionado, la tabla llena de insumos con cantidades y la casilla 'Finalizado' marcada
                safe_name = sanitize_name(alm_nombre)
                proof_path = os.path.join(PROOF_DIR, f"{idx:02d}_{safe_name}.png")
                page.screenshot(path=proof_path)
                print(f"   [Foto] Evidencia capturada con insumos y almacén en pantalla: {proof_path}")
                
                print(" -> Consolidando y finalizando inventario...")
                iframe.click('#btn_guardar')
                # Esperar a que se procese el confirm y alert
                page.wait_for_timeout(4000)
                
                progress[alm_nombre] = {
                    'num': idx,
                    'status': 'FINALIZADO',
                    'almacen_id': inv_id,
                    'total_excel': total_items_excel,
                    'total_matched': total_matched,
                    'total_pages': total_pages,
                    'proof_img': proof_path,
                    'completed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                save_progress(progress)
                print(f"[{idx:02d}/{total_almacenes}] OK: {alm_nombre} finalizado con éxito ({total_matched}/{total_items_excel} insumos).")
                
            except Exception as ex:
                print(f"[{idx:02d}/{total_almacenes}] ERROR procesando {alm_nombre}: {ex}")
                safe_name = sanitize_name(alm_nombre)
                err_path = os.path.join(PROOF_DIR, f"{idx:02d}_ERROR_{safe_name}.png")
                try:
                    page.screenshot(path=err_path)
                except:
                    pass
                progress[alm_nombre] = {
                    'num': idx,
                    'status': 'ERROR',
                    'error': str(ex),
                    'time': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                save_progress(progress)
                try:
                    page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(3000)
                except:
                    pass
                    
        browser.close()
        
    print("\n=== PROCESO GENERAL COMPLETADO ===")
    finalizados = sum(1 for v in progress.values() if v.get('status') == 'FINALIZADO')
    print(f"Resultado final: {finalizados}/{total_almacenes} almacenes finalizados correctamente.")

if __name__ == '__main__':
    main()
