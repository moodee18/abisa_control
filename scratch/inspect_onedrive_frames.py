import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright

url = "https://1drv.ms/x/c/019ebf93eb1529d0/IQD2itTtsBcWRKAdyQCkEPOPARq7A4hGwcOGNmAQY0HEwd8?e=UAgWRE"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(6000)
    
    print(f"Total frames: {len(page.frames)}")
    for i, f in enumerate(page.frames):
        print(f"Frame {i}: url={f.url[:100]}, name={f.name}")
        elements = f.locator('button, a, div[role="button"], div[role="tab"], span').all()
        matching = []
        for el in elements:
            try:
                t = (el.text_content() or '').strip()
                aria = (el.get_attribute('aria-label') or '').strip()
                if any(w in t.lower() or w in aria.lower() for w in ['archivo', 'file', 'descargar', 'download', 'guardar']):
                    matching.append(f"text='{t}', aria='{aria}'")
            except:
                pass
        if matching:
            print(f"  Frame {i} matching ({len(matching)}): {matching[:5]}")
            
    browser.close()

