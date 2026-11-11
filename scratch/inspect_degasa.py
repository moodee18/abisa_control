import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import config

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    page.goto(config.SIIA_URL)
    page.fill("#usr", config.SIIA_USERNAME)
    page.fill("#psw", config.SIIA_PASSWORD)
    page.click("#btn")
    page.wait_for_timeout(3000)
    
    page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle")
    page.wait_for_timeout(2000)
    
    iframe = page.frames[1]
    iframe.select_option('#localidad', '1836')
    page.wait_for_timeout(2000)
    
    # DEGASA SA DE C.V CONS is 302869
    iframe.select_option('#almacen', '302869')
    page.wait_for_timeout(3000)
    
    rows = iframe.locator('#tbl_productos tr').all()
    print(f"DEGASA rows count on page 1: {len(rows)}")
    
    pag = iframe.locator('#paginacion')
    if pag.count() > 0:
        opts = [o.text_content().strip() for o in pag.locator('option').all()]
        print(f"Paginacion options for DEGASA: {opts}")
        
    browser.close()

