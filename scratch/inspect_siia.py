from downloader import SiiaDownloader
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    downloader = SiiaDownloader()
    downloader.login(page)
    
    print('--- Navigating to opc=55 (Inventario) ---')
    page.goto('https://siia.abisalud.com/main.php?opc=55', timeout=30000)
    page.wait_for_timeout(3000)
    print('Page title:', page.title())
    buttons_55 = page.evaluate('''() => {
        const els = Array.from(document.querySelectorAll('input, button, a, img'));
        return els.map(e => ({
            tag: e.tagName,
            text: (e.innerText || e.value || e.alt || e.title || '').trim(),
            id: e.id,
            name: e.name,
            class: e.className,
            href: e.href || '',
            src: e.src || '',
            onclick: e.getAttribute('onclick') || ''
        })).filter(x => x.text || x.onclick || x.id);
    }''')
    print(f'Total elements on opc=55: {len(buttons_55)}')
    for b in buttons_55:
        txt = (b['text'] or '').lower()
        clk = (b['onclick'] or '').lower()
        if any(w in txt or w in clk for w in ['export', 'excel', 'descarg', 'gener', 'reporte', 'existenc', 'csv', 'filtr']):
            print('  MATCH opc=55:', b)

    print('\n--- Navigating to opc=163 (Entradas y Salidas) ---')
    page.goto('https://siia.abisalud.com/main.php?opc=163', timeout=30000)
    page.wait_for_timeout(3000)
    print('Page title:', page.title())
    buttons_163 = page.evaluate('''() => {
        const els = Array.from(document.querySelectorAll('input, button, a, img'));
        return els.map(e => ({
            tag: e.tagName,
            text: (e.innerText || e.value || e.alt || e.title || '').trim(),
            id: e.id,
            name: e.name,
            class: e.className,
            href: e.href || '',
            src: e.src || '',
            onclick: e.getAttribute('onclick') || ''
        })).filter(x => x.text || x.onclick || x.id);
    }''')
    print(f'Total elements on opc=163: {len(buttons_163)}')
    for b in buttons_163:
        txt = (b['text'] or '').lower()
        clk = (b['onclick'] or '').lower()
        if any(w in txt or w in clk for w in ['export', 'excel', 'descarg', 'gener', 'reporte', 'entrad', 'salid', 'csv', 'filtr', 'btn']):
            print('  MATCH opc=163:', b)

    browser.close()
