import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('http://127.0.0.1:8000')
    page.wait_for_timeout(1000)
    
    # Open modal
    page.locator('button:has-text("Sincronizar con SIIA")').first.click()
    page.wait_for_timeout(500)
    
    # Click Mes Actual preset button
    page.locator('button:has-text("Mes Actual (Rápido)")').click()
    page.wait_for_timeout(300)
    
    f_ini = page.locator('#syncAutoFechaIni').input_value()
    f_fin = page.locator('#syncAutoFechaFin').input_value()
    print(f"Dates set: {f_ini} to {f_fin}")
    
    # Click Sincronizar Movimientos
    page.locator('#btnSyncAutoMov').click()
    page.wait_for_timeout(2000)
    
    print("Auto sync started!")
    browser.close()
