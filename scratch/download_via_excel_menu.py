import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import os

url = "https://1drv.ms/x/c/019ebf93eb1529d0/IQD2itTtsBcWRKAdyQCkEPOPARq7A4hGwcOGNmAQY0HEwd8?e=UAgWRE"
dest_path = os.path.abspath("data/INV_OCTUBRE_11.xlsx")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True, viewport={'width': 1366, 'height': 850})
    page = context.new_page()
    
    print("Navigating to OneDrive...")
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(6000)
    
    # Locate frame WacFrame_Excel_0
    frame = page.frame(name="WacFrame_Excel_0")
    if not frame:
        for f in page.frames:
            if "excel.officeapps.live.com" in f.url:
                frame = f
                break
                
    print("Found Excel frame:", frame.name if frame else "None")
    
    # Click File tab
    file_btn = frame.locator('#FileMenuLauncher, button:has-text("File"), [aria-label="File"]').first
    print("Clicking File button...")
    file_btn.click()
    page.wait_for_timeout(2000)
    
    # Look for "Save As" or "Guardar como" or "Download a Copy" or "Descargar una copia"
    menu_items = frame.locator('button, a, div[role="menuitem"], span').all()
    print("Menu items visible in File menu:")
    for m in menu_items:
        t = (m.text_content() or '').strip()
        if any(w in t.lower() for w in ['save as', 'guardar como', 'download', 'descargar', 'copia']):
            print(f"  Item: '{t}' (tag={m.evaluate('el => el.tagName')})")
            
    # Try clicking "Save As"
    save_as = frame.locator('text="Save As", text="Guardar como", [aria-label*="Save As"]').first
    if save_as.count() > 0:
        print("Clicking Save As...")
        save_as.click()
        page.wait_for_timeout(2000)
        
    # Now look for "Download a Copy"
    dl_copy = frame.locator('text="Download a Copy", text="Descargar una copia", [aria-label*="Download a Copy"]').first
    if dl_copy.count() > 0:
        print("Clicking Download a Copy...")
        with page.expect_download(timeout=15000) as dl_info:
            dl_copy.click()
        download = dl_info.value
        download.save_as(dest_path)
        print("SUCCESS! File saved to:", dest_path)
    else:
        print("Could not find Download a Copy button.")
        page.screenshot(path="scratch/onedrive_file_menu.png")
        
    browser.close()

if os.path.exists(dest_path):
    print("Downloaded file size:", os.path.getsize(dest_path))

