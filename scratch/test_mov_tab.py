from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('http://127.0.0.1:8000')
    page.wait_for_timeout(1000)
    
    # Click Movimientos tab using onclick attribute
    tab = page.locator('button[onclick*="tab-movimientos"]')
    print(f"Tab found: {tab.count()}")
    tab.click()
    page.wait_for_timeout(600)
    
    # Click Sincronizar button inside Movimientos tab
    btn = page.locator('#tab-movimientos button[onclick*="openSyncModal"]')
    print(f"Btn inside Movimientos found: {btn.count()}")
    btn.click()
    page.wait_for_timeout(600)
    
    modal = page.locator('#syncModal')
    print(f"Modal is_visible: {modal.is_visible()}")
    page.screenshot(path='scratch/modal_mov_open.png')
    print("Screenshot saved to scratch/modal_mov_open.png")
    
    browser.close()
