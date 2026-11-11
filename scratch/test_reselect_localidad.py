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
    
    # Select localidad
    iframe.select_option('#localidad', '1836')
    iframe.wait_for_function("() => { const a = document.getElementById('almacen'); return a && !a.disabled && a.options.length > 5; }", timeout=15000)
    
    opts_len = iframe.locator('#almacen option').count()
    print(f"Almacen options count after selecting 1836: {opts_len}")
    
    # Simulate limpiar()
    iframe.evaluate("limpiar()")
    print("Called limpiar(). Localidad is now:", iframe.locator('#localidad').input_value())
    print("Almacen disabled:", iframe.locator('#almacen').is_disabled())
    
    # Reselect localidad 1836
    iframe.select_option('#localidad', '1836')
    iframe.wait_for_function("() => { const a = document.getElementById('almacen'); return a && !a.disabled && a.options.length > 5; }", timeout=15000)
    print("Reselected 1836! Almacen options count:", iframe.locator('#almacen option').count())
    
    browser.close()

