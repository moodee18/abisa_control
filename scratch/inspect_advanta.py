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
    
    # ADVANTA PHARMA SAPI DE CV is 302823
    iframe.select_option('#almacen', '302823')
    page.wait_for_timeout(3000)
    
    rows = iframe.locator('#tbl_productos tr').all()
    print(f"ADVANTA PHARMA rows count: {len(rows)}")
    
    pag = iframe.locator('#paginacion')
    if pag.count() > 0:
        opts = [o.text_content().strip() for o in pag.locator('option').all()]
        print(f"Paginacion options: {opts}")
        
    for i, r in enumerate(rows[:5]):
        lote = r.locator('td').nth(2).text_content().strip()
        cod = r.locator('td').nth(3).text_content().strip()
        desc = r.locator('td').nth(4).text_content().strip()[:40]
        cad = r.locator('td').nth(5).locator('input').input_value()
        cant = r.locator('td').nth(6).locator('input').input_value()
        print(f"  Row {i+1}: Lote={lote}, Cod={cod}, Cad={cad}, Cant={cant}, Desc={desc}")
        
    browser.close()

