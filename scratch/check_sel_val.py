import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import config

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 768})
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
    iframe.select_option('#almacen', '302778')
    page.wait_for_timeout(3000)
    
    rows = iframe.locator('#tbl_productos tr').all()
    for i, r in enumerate(rows):
        sel = r.locator('select.combo')
        val = sel.input_value()
        sel_text = sel.locator('option:checked').text_content() if sel.count() > 0 else "None"
        print(f"Row {i} Ubicacion select val: {val}, text: {sel_text}")
        
    browser.close()
