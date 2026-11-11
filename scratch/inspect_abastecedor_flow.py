import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import config

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 768})
    
    page.goto(config.SIIA_URL, timeout=45000)
    page.wait_for_timeout(2000)
    
    user_selectors = ["#usr", "input[name='usr']", "input[name='usuario']"]
    pass_selectors = ["#psw", "input[name='psw']", "input[name='password']"]
    btn_selectors = ["#btn", "input[id='btn']", "input[value='Entrar']", "button:has-text('Entrar')"]
    
    for s in user_selectors:
        if page.locator(s).count() > 0:
            page.fill(s, config.SIIA_USERNAME)
            break
            
    for s in pass_selectors:
        if page.locator(s).count() > 0:
            page.fill(s, config.SIIA_PASSWORD)
            break
            
    for s in btn_selectors:
        if page.locator(s).count() > 0:
            page.click(s)
            break
            
    page.wait_for_timeout(4000)
    
    page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(3000)
    
    iframe = page.frames[1]
    
    # Select Localidad 1836 (CS ALMACEN 2022)
    print("Selecting Localidad 1836...")
    iframe.select_option('#localidad', '1836')
    page.wait_for_timeout(3000)
    
    # Look for ABASTECEDOR TERAPEUTICO SA DE C.V in #almacen options
    almacen_options = iframe.locator('#almacen option').all()
    target_val = None
    for opt in almacen_options:
        text = opt.text_content().strip()
        val = opt.get_attribute('value')
        if 'ABASTECEDOR TERAPEUTICO' in text.upper():
            print(f"Found option: val={val}, text={text}")
            target_val = val
            break
            
    if target_val:
        print(f"Selecting Almacen {target_val}...")
        iframe.select_option('#almacen', target_val)
        page.wait_for_timeout(4000)
        
        page.screenshot(path="scratch/after_select_abastecedor.png")
        
        # Save iframe html for inspection
        html = iframe.content()
        with open("scratch/iframe_abastecedor.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Table rows in #tbl_productos:")
        rows = iframe.locator('#tbl_productos tr').all()
        print(f"Total rows: {len(rows)}")
        for i, r in enumerate(rows):
            print(f"Row {i}: {r.text_content().strip()}")
            # Inputs in row
            inputs = r.locator('input').all()
            for inp in inputs:
                print(f"  Input id={inp.get_attribute('id')}, name={inp.get_attribute('name')}, type={inp.get_attribute('type')}, value={inp.get_attribute('value')}")
                
        # Check Finalizado checkbox
        fin = iframe.locator('input[type="checkbox"]').all()
        for chk in fin:
            print(f"Checkbox id={chk.get_attribute('id')}, name={chk.get_attribute('name')}, checked={chk.is_checked()}")
            
        # Check buttons
        btns = iframe.locator('input[type="button"], button').all()
        for b in btns:
            print(f"Button id={b.get_attribute('id')}, value={b.get_attribute('value')}, onclick={b.get_attribute('onclick')}, text={b.text_content().strip()}")
            
        # Check pagination
        pag = iframe.locator('#paginacion')
        if pag.count() > 0:
            print(f"Paginacion tag: val={pag.input_value()}")
            p_opts = pag.locator('option').all()
            print(f"Paginacion options count: {len(p_opts)}")
            for po in p_opts:
                print(f"  Pag option: val={po.get_attribute('value')}, text={po.text_content().strip()}")
                
    browser.close()

