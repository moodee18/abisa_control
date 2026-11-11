import sys
import os
import time
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import config

def run():
    print("=== INICIANDO CAPTURA DE SEGUIMIENTO DE INVENTARIO ===")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 850})
        page = context.new_page()
        
        dialog_events = []
        def on_dialog(dialog):
            print(f"[DIALOG] {dialog.type.upper()}: '{dialog.message}' -> Aceptando...")
            dialog_events.append({'type': dialog.type, 'message': dialog.message})
            dialog.accept()
            
        page.on('dialog', on_dialog)
        
        # 1. Login
        print("Iniciando sesión en SIIA...")
        page.goto(config.SIIA_URL, timeout=45000)
        page.wait_for_timeout(2000)
        
        page.fill("#usr", config.SIIA_USERNAME)
        page.fill("#psw", config.SIIA_PASSWORD)
        page.click("#btn")
        page.wait_for_timeout(4000)
        
        # 2. Ir a Seguimiento de Inventario
        print("Navegando a Seguimiento de Inventario (opc=82)...")
        page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(3000)
        
        iframe = page.frames[1]
        
        # 3. Seleccionar Localidad 1836 (CS ALMACEN 2022)
        print("Paso 1: Seleccionando Localidad: CS ALMACEN 2022...")
        iframe.select_option('#localidad', '1836')
        page.wait_for_timeout(3000)
        
        # 4. Seleccionar Almacén ABASTECEDOR TERAPEUTICO SA DE C.V
        print("Paso 2: Seleccionando Almacén: ABASTECEDOR TERAPEUTICO SA DE C.V...")
        almacen_opts = iframe.locator('#almacen option').all()
        target_val = None
        for opt in almacen_opts:
            t = opt.text_content().strip().upper()
            if 'ABASTECEDOR TERAPEUTICO' in t:
                target_val = opt.get_attribute('value')
                print(f"Almacén encontrado con ID={target_val}: {opt.text_content().strip()}")
                break
                
        if not target_val:
            raise Exception("No se encontró ABASTECEDOR TERAPEUTICO en el catálogo de almacenes.")
            
        iframe.select_option('#almacen', target_val)
        page.wait_for_timeout(4000)
        
        page.screenshot(path="scratch/step1_abastecedor_cargado.png")
        print("Screenshot paso 1 guardado.")
        
        # 5. Verificar filas cargadas
        rows = iframe.locator('#tbl_productos tr').all()
        print(f"Total registros cargados en tabla: {len(rows)}")
        
        cantidades_mapeadas = {
            '0004328539': '10',
            '0004332598': '90'
        }
        
        for i, row in enumerate(rows):
            # Obtener lote (celda 2)
            lote = row.locator('td').nth(2).text_content().strip()
            codigo = row.locator('td').nth(3).text_content().strip()
            desc = row.locator('td').nth(4).text_content().strip()
            cad = row.locator('td').nth(5).locator('input').input_value().strip()
            
            # Cantidad es el input en la celda 6
            inp_cant = row.locator('td').nth(6).locator('input')
            
            if lote in cantidades_mapeadas:
                cant_a_poner = cantidades_mapeadas[lote]
                print(f"Fila {i+1}: Lote={lote}, Código={codigo}, Cad={cad} -> Asignando Cantidad: {cant_a_poner}")
                inp_cant.fill(cant_a_poner)
                # Disparar eventos onchange/onkeyup
                inp_cant.dispatch_event('change')
                inp_cant.dispatch_event('keyup')
            else:
                print(f"Fila {i+1}: Lote={lote} NO coincide con la lista!")
                
        page.wait_for_timeout(1000)
        page.screenshot(path="scratch/step2_cantidades_capturadas.png")
        print("Screenshot paso 2 guardado.")
        
        # 6. Dar clic en Guardar (primera fase)
        print("Paso 3: Dando clic en Guardar...")
        iframe.click('#btn_guardar')
        page.wait_for_timeout(4000)
        
        page.screenshot(path="scratch/step3_despues_primer_guardar.png")
        print("Screenshot paso 3 guardado.")
        
        # 7. Verificar paginación
        pag_select = iframe.locator('#paginacion')
        if pag_select.count() > 0:
            pag_val = pag_select.input_value()
            total_pags = len(pag_select.locator('option').all())
            print(f"Paginación actual: Página {pag_val} de {total_pags}")
        else:
            print("No hay control de paginación múltiple.")
            
        # 8. Marcar Finalizado y Guardar nuevamente
        print("Paso 4: Marcando casilla 'Finalizado'...")
        chk_finalizar = iframe.locator('#finalizar')
        chk_finalizar.check()
        page.wait_for_timeout(1000)
        
        page.screenshot(path="scratch/step4_finalizado_marcado.png")
        print("Screenshot paso 4 guardado.")
        
        print("Paso 5: Dando clic en Guardar con Finalizado marcado...")
        iframe.click('#btn_guardar')
        page.wait_for_timeout(5000)
        
        page.screenshot(path="scratch/step5_seguimiento_completado.png")
        print("Screenshot paso 5 guardado.")
        
        print("\n=== RESUMEN DE DIÁLOGOS CAPTURADOS ===")
        for d in dialog_events:
            print(f" - [{d['type']}] {d['message']}")
            
        browser.close()
        print("\n=== PROCESO FINALIZADO EXITOSAMENTE ===")

if __name__ == '__main__':
    run()

