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

        # Go to Control por Movimientos
        btn_mov = page.locator("button.tab-btn:has-text('Control por Movimientos')")
        btn_mov.click()
        time.sleep(1)

        # Switch to subtab 3: Salidas desde PDF
        btn_salidas = page.locator("#btnCtrlSubTabSalidas")
        btn_salidas.click()
        time.sleep(1.5)

        # 1. Check toolbar button
        btn_gestionar = page.locator("button:has-text('Modificar / Eliminar Pedido')")
        print(f"Toolbar button 'Modificar / Eliminar Pedido' visible: {btn_gestionar.is_visible()}")

        # 2. Check table row folio pills
        folio_pills = page.locator(".btn-pedido-pill")
        print(f"Total folio pills in table: {folio_pills.count()}")
        if folio_pills.count() > 0:
            print(f"First folio pill text: {folio_pills.first.inner_text()}")

        page.screenshot(path="scratch/verified_salidas_table_pedidos.png")
        print("Saved scratch/verified_salidas_table_pedidos.png")

        # 3. Click 'Modificar / Eliminar Pedido' to open modalGestionarPedidos
        btn_gestionar.click()
        time.sleep(1.5)

        modal_gest = page.locator("#modalGestionarPedidos")
        print(f"modalGestionarPedidos visible: {modal_gest.is_visible()}")

        summary_txt = page.locator("#gestionarPedidosCountSummary").inner_text()
        print(f"Orders summary text: {summary_txt}")

        rows_orders = page.locator("#gestionarPedidosTableBody tr")
        print(f"Orders rows in modal: {rows_orders.count()}")

        page.screenshot(path="scratch/verified_gestionar_pedidos_modal.png")
        print("Saved scratch/verified_gestionar_pedidos_modal.png")

        # 4. In the modal, click 'Modificar' on the first order
        btn_mod_first = page.locator("#gestionarPedidosTableBody tr button:has-text('Modificar')").first
        btn_mod_first.click()
        time.sleep(1.5)

        modal_mod = page.locator("#modalModificarPedidoCompleto")
        print(f"modalModificarPedidoCompleto visible: {modal_mod.is_visible()}")

        folio_badge = page.locator("#modPedFolioBadge").inner_text()
        print(f"Modal Folio badge: {folio_badge}")

        subtitle = page.locator("#modPedSubtitle").inner_text()
        print(f"Modal Subtitle: {subtitle}")

        items_rows = page.locator("#modPedItemsTableBody tr.mod-ped-item-row")
        print(f"Items rows in edit modal: {items_rows.count()}")

        page.screenshot(path="scratch/verified_modificar_pedido_modal.png")
        print("Saved scratch/verified_modificar_pedido_modal.png")

        browser.close()
        print("Playwright test completed successfully!")

if __name__ == "__main__":
    run()

