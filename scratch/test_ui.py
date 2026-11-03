import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    console_messages = []
    page.on('console', lambda msg: console_messages.append(f'[{msg.type}] {msg.text}'))
    page.on('pageerror', lambda err: console_messages.append(f'[PAGE_ERROR] {err}'))
    
    page.goto('http://127.0.0.1:8000')
    page.wait_for_timeout(2000)
    
    print("Page title:", page.title())
    print("Console messages:")
    for m in console_messages:
        print("  ", m)
        
    buttons = page.locator('button').all()
    print(f"Total buttons: {len(buttons)}")
    for i, b in enumerate(buttons):
        t = b.inner_text().strip().replace('\n', ' ')
        c = b.get_attribute('class') or ''
        oc = b.get_attribute('onclick') or ''
        if 'Sincronizar' in t or 'sync' in oc.lower() or 'siia' in t.lower():
            print(f"Btn {i}: '{t}' | class='{c}' | onclick='{oc}'")
            
    # Try clicking the first Sincronizar button
    btn = page.locator('button:has-text("Sincronizar")').first
    if btn:
        print("Clicking Sincronizar button...")
        btn.click()
        page.wait_for_timeout(1000)
        print("After click console messages:")
        for m in console_messages:
            print("  ", m)
        
        modal = page.locator('#syncModal')
        if modal.count() > 0:
            is_active = modal.evaluate('el => el.classList.contains("active")')
            style = modal.evaluate('el => window.getComputedStyle(el).display')
            print(f"Modal exists. is_active={is_active}, display={style}")
        else:
            print("Modal #syncModal does NOT exist in DOM!")
            
    browser.close()
