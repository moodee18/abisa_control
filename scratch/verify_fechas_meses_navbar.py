import os
import sys
import time
from playwright.sync_api import sync_playwright

def run():
    token = "FnRey7StNwab1s95PEHYYGkWD_vr_umOEGibNEQvRkejhEhXqZD3IFZIq4frOtsu"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        context.add_cookies([{
            "name": "abisalud_session",
            "value": token,
            "domain": "127.0.0.1",
            "path": "/"
        }])

        page = context.new_page()
        page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        time.sleep(1)

        # 1. Header Row Check
        header = page.locator("header")
        header_box = header.bounding_box()
        print(f"Header bounding box: {header_box}")

        logo_box = page.locator(".logo-area").bounding_box()
        clock_box = page.locator("#headerLiveClock").bounding_box()
        actions_box = page.locator(".header-actions").bounding_box()

        print(f"Logo area: y={logo_box['y']}, height={logo_box['height']}")
        print(f"Clock pill: y={clock_box['y']}, height={clock_box['height']}")
        print(f"Header actions: y={actions_box['y']}, height={actions_box['height']}")

        # Header height should be approximately 54-60px (single row, not ~100-120px 2 rows)
        print(f"Header height is {header_box['height']}px (Single row check: {'PASSED' if header_box['height'] < 75 else 'FAILED - TWO ROWS'})")

        # Take header screenshot
        header.screenshot(path="scratch/verified_header_single_row.png")
        print("Header screenshot saved to scratch/verified_header_single_row.png")

        # 2. Check Control por Movimientos
        btn_mov = page.locator("button.tab-btn:has-text('Control por Movimientos')")
        btn_mov.click()
        time.sleep(1.5)

        # Check button Iniciar Nuevo Mes
        btn_iniciar = page.locator("button:has-text('Iniciar Nuevo Mes')")
        print(f"Button 'Iniciar Nuevo Mes' visible: {btn_iniciar.is_visible()}")

        # Check October KPIs
        surtido_txt = page.locator("#ctrlKpiTotalSurtido").inner_text()
        disp_txt = page.locator("#ctrlKpiInvDisponible").inner_text()
        print(f"OCTUBRE UI - Total Surtido: {surtido_txt}, Disponible: {disp_txt}")

        page.screenshot(path="scratch/verified_control_movimientos_octubre.png")
        print("October screenshot saved.")

        # Switch to NOVIEMBRE
        page.locator("#ctrlMonthSelect").select_option("NOVIEMBRE")
        time.sleep(1.5)

        surtido_nov = page.locator("#ctrlKpiTotalSurtido").inner_text()
        disp_nov = page.locator("#ctrlKpiInvDisponible").inner_text()
        inv_nov = page.locator("#ctrlKpiInvTotalMensual").inner_text()
        print(f"NOVIEMBRE UI - Inicial/Mensual: {inv_nov}, Total Surtido: {surtido_nov}, Disponible: {disp_nov}")

        page.screenshot(path="scratch/verified_control_movimientos_noviembre.png")
        print("November screenshot saved.")

        browser.close()

if __name__ == "__main__":
    run()

