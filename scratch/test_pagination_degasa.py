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
    
    row1_p1 = iframe.locator('#tbl_productos tr td').nth(2).text_content().strip()
    print("Page 1 first lote:", row1_p1)
    
    # Change to page 2
    print("Changing to page 2...")
    iframe.select_option('#paginacion', '2')
    # wait for table update
    page.wait_for_timeout(3000)
    
    row1_p2 = iframe.locator('#tbl_productos tr td').nth(2).text_content().strip()
    pg_ant = iframe.locator('#pg_ant').input_value()
    print("Page 2 first lote:", row1_p2, "pg_ant:", pg_ant)
    print("Rows count on page 2:", len(iframe.locator('#tbl_productos tr').all()))
    
    browser.close()

