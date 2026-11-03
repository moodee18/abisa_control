from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('http://127.0.0.1:8000')
    page.wait_for_timeout(1000)
    
    # Click header sync button
    btn = page.locator('button:has-text("Sincronizar con SIIA")').first
    btn.click()
    page.wait_for_timeout(800)
    
    parent_tag = page.evaluate('() => document.getElementById("syncModal").parentElement.tagName')
    parent_id = page.evaluate('() => document.getElementById("syncModal").parentElement.id')
    is_visible = page.locator('#syncModal').is_visible()
    modal_title = page.locator('#syncModal h3').inner_text()
    
    print(f"syncModal parent: <{parent_tag} id='{parent_id}'>")
    print(f"is_visible: {is_visible}")
    print(f"Modal title: '{modal_title}'")
    
    page.screenshot(path='scratch/modal_open.png')
    print("Screenshot saved to scratch/modal_open.png")
    
    # Close modal
    page.locator('#syncModal .modal-close').click()
    page.wait_for_timeout(500)
    print("Modal closed. is_visible:", page.locator('#syncModal').is_visible())
    
    # Switch to Movimientos tab and click Sincronizar con SIIA there
    page.locator('button:has-text("Movimientos")').first.click()
    page.wait_for_timeout(500)
    btn_mov = page.locator('#tab-movimientos button:has-text("Sincronizar con SIIA")')
    if btn_mov.count() > 0:
        btn_mov.click()
        page.wait_for_timeout(500)
        print("Movimientos Sincronizar clicked. is_visible:", page.locator('#syncModal').is_visible())
        page.screenshot(path='scratch/modal_mov_open.png')
    else:
        print("btn_mov not found!")

    browser.close()
