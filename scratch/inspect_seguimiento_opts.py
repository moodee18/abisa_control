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
    iframe.select_option('#localidad', '1836')
    page.wait_for_timeout(3000)
    
    options = iframe.locator('#almacen option').all()
    print(f"Total options in seguimiento #almacen: {len(options)}")
    
    with open("scratch/seguimiento_almacenes.txt", "w", encoding="utf-8") as f:
        for opt in options:
            val = opt.get_attribute('value')
            text = opt.text_content().strip()
            f.write(f"{val} | {text}\n")
            
    print("First 20 options:")
    for opt in options[:20]:
        print(f"  val='{opt.get_attribute('value')}' -> text='{opt.text_content().strip()}'")
        
    browser.close()

