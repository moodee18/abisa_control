import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    
    print("Opening localhost:8000...")
    page.goto("http://localhost:8000", wait_until="networkidle")
    page.wait_for_timeout(2000)
    
    # Check if login is required
    if "login" in page.url.lower():
        print("Logging in to dashboard...")
        page.fill("#usernameInput", "superadmin")
        page.fill("#passwordInput", "admin123")
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)
        
    print("Dashboard loaded, title:", page.title())
    page.wait_for_timeout(2000)
    
    # Check for tabBtnSiiaRpa
    btn_rpa = page.locator('#tabBtnSiiaRpa')
    print("tabBtnSiiaRpa count:", btn_rpa.count(), "visible:", btn_rpa.is_visible())
    
    if btn_rpa.count() > 0:
        print("Clicking tabBtnSiiaRpa...")
        btn_rpa.click()
        page.wait_for_timeout(2000)
        
        page.screenshot(path="scratch/ui_siia_rpa_alta.png")
        print("Saved scratch/ui_siia_rpa_alta.png")
        
        # Test switching to Seguimiento subtab
        print("Switching to Seguimiento subtab...")
        page.click('#subtabBtnSeguimiento')
        page.wait_for_timeout(2000)
        
        page.screenshot(path="scratch/ui_siia_rpa_seguimiento.png")
        print("Saved scratch/ui_siia_rpa_seguimiento.png")
        
    # Check console errors
    print("Checking console...")
    browser.close()
