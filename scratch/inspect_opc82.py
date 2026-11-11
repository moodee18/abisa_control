import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import config

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 768})
    
    page.goto(config.SIIA_URL, timeout=45000)
    page.wait_for_timeout(2000)
    
    # Login
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
    
    print("Navigating to opc=82 (Seguimiento Inventario)...")
    page.goto("https://siia.abisalud.com/main.php?opc=82", wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(3000)
    
    print("Frames on opc=82:", len(page.frames))
    for i, fr in enumerate(page.frames):
        print(f"Frame {i}: {fr.url}")
        
    iframe = page.frames[1] if len(page.frames) > 1 else page
    print("Iframe title/text:", iframe.locator('body').text_content()[:500])
    
    page.screenshot(path="scratch/opc82_seguimiento.png")
    
    browser.close()

