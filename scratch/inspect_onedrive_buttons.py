import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright

url = "https://1drv.ms/x/c/019ebf93eb1529d0/IQD2itTtsBcWRKAdyQCkEPOPARq7A4hGwcOGNmAQY0HEwd8?e=UAgWRE"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(5000)
    
    page.screenshot(path="scratch/onedrive_excel_view.png")
    
    # Print all buttons or menu items
    elements = page.locator('button, a, div[role="button"], div[role="menuitem"]').all()
    print(f"Total interactive elements: {len(elements)}")
    for el in elements:
        t = el.text_content().strip()
        aria = el.get_attribute('aria-label')
        if any(w in (t or '').lower() or w in (aria or '').lower() for w in ['archivo', 'file', 'descargar', 'download', 'guardar', 'copia']):
            print(f"Element: text='{t}', aria='{aria}', id='{el.get_attribute('id')}', role='{el.get_attribute('role')}'")
            
    browser.close()

