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
    
    # Check selects in iframe
    for s in iframe.locator('select').all():
        print(f"Select id={s.get_attribute('id')}, name={s.get_attribute('name')}")
        
    # Select Localidad 1836
    iframe.select_option('#localidad', '1836')
    page.wait_for_timeout(4000)
    
    # Check if a button or table appears
    print("Iframe text after selecting 1836:")
    print(iframe.locator('body').text_content()[:2000])
    
    # Check buttons and links
    links = iframe.locator('a, button, input[type="button"], img').all()
    print(f"Elements count: {len(links)}")
    for el in links[:30]:
        print("El:", el.get_attribute('title'), el.get_attribute('onclick'), el.get_attribute('src'), el.text_content().strip())

    page.screenshot(path="scratch/seguimiento_1836.png")
    browser.close()

