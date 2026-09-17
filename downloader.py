import time
from pathlib import Path
from typing import Optional, List
from playwright.sync_api import sync_playwright, Page, BrowserContext, Download
import config

_CURRENT_BROWSER = None
_CURRENT_CONTEXT = None

def force_kill_session():
    """Cierra cualquier sesión activa de Playwright abierta."""
    global _CURRENT_BROWSER, _CURRENT_CONTEXT
    try:
        if _CURRENT_CONTEXT:
            _CURRENT_CONTEXT.close()
        if _CURRENT_BROWSER:
            _CURRENT_BROWSER.close()
    except Exception:
        pass
    finally:
        _CURRENT_BROWSER = None
        _CURRENT_CONTEXT = None

class SiiaDownloader:

    """Automatizador de navegación y descargas para SIIA Abisalud."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, 
                 headless: Optional[bool] = None, download_dir: Optional[Path] = None):
        self.username = username or config.SIIA_USERNAME
        self.password = password or config.SIIA_PASSWORD
        self.headless = headless if headless is not None else config.HEADLESS
        self.download_dir = download_dir or config.DOWNLOAD_DIR
        self.url = config.SIIA_URL

    def login(self, page: Page) -> bool:
        """Realiza el inicio de sesión automático en el portal SIIA."""
        print(f"[RPA] Navegando a {self.url}...")
        try:
            page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"[RPA ADVERTENCIA] Carga inicial: {e}")

        if not self.username or not self.password:
            print("[ADVERTENCIA] No se han especificado credenciales en .env (SIIA_USERNAME, SIIA_PASSWORD).")
            print("[INFO] Puede ingresar las credenciales manualmente en la ventana del navegador.")
            return False

        print(f"[RPA] Intentando inicio de sesión automático como '{self.username}'...")

        try:
            # El formulario se carga vía AJAX con #usr, #psw y #btn
            page.wait_for_selector("#usr, input[name='usr'], input[name='usuario']", timeout=15000)
        except Exception:
            pass

        # Selectores prioritarios según la estructura real de SIIA
        user_selectors = ["#usr", "input[name='usr']", "input[name='usuario']", "input[name='user']", "input[name='login']"]
        pass_selectors = ["#psw", "input[name='psw']", "input[name='password']", "input[name='pass']", "input[name='clave']"]
        btn_selectors = ["#btn", "input[id='btn']", "input[value='Entrar']", "button:has-text('Entrar')"]

        user_filled = False
        for selector in user_selectors:
            if page.locator(selector).count() > 0:
                page.fill(selector, self.username)
                user_filled = True
                break

        pass_filled = False
        for selector in pass_selectors:
            if page.locator(selector).count() > 0:
                page.fill(selector, self.password)
                pass_filled = True
                break

        if user_filled and pass_filled:
            clicked = False
            for selector in btn_selectors:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    clicked = True
                    break
            
            if not clicked:
                page.keyboard.press("Enter")

            try:
                page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass
            print("[RPA] Credenciales enviadas exitosamente.")
            return True
        else:
            print("[ADVERTENCIA] No se detectaron automáticamente los campos de login.")
            return False

    def wait_and_save_download(self, page: Page, trigger_selector: str, target_filename: str) -> Optional[Path]:
        """Hace clic en un elemento de reporte y guarda la descarga generada."""
        print(f"[RPA] Esperando descarga tras hacer clic en '{trigger_selector}'...")
        try:
            with page.expect_download(timeout=60000) as download_info:
                page.click(trigger_selector)
            
            download: Download = download_info.value
            dest_path = self.download_dir / target_filename
            download.save_as(dest_path)
            print(f"[RPA] Archivo descargado exitosamente: {dest_path}")
            return dest_path
        except Exception as e:
            print(f"[RPA ERROR] Falló la descarga: {e}")
            return None

    def cancel_active_session(self):
        """Fuerza el cierre del contexto y navegador activos."""
        global _CURRENT_BROWSER, _CURRENT_CONTEXT
        try:
            if _CURRENT_CONTEXT:
                _CURRENT_CONTEXT.close()
            if _CURRENT_BROWSER:
                _CURRENT_BROWSER.close()
            print("[RPA] Sesión forzada a cerrar.")
        except Exception as e:
            print(f"[RPA ERROR] Al forzar cierre: {e}")
        finally:
            _CURRENT_CONTEXT = None
            _CURRENT_BROWSER = None

    def run_interactive_session(self, target: Optional[str] = None):
        """
        Inicia el navegador para que el usuario navegue, inicie sesión y seleccione
        los reportes manualmente, capturando automáticamente cualquier descarga realizada.
        Si se especifica `target`, navega directamente al reporte correspondiente tras autenticar.
        """
        global _CURRENT_BROWSER, _CURRENT_CONTEXT
        print("[RPA] Iniciando sesión interactiva con Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless, 
                slow_mo=config.SLOW_MO,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                accept_downloads=True,
                no_viewport=True
            )
            _CURRENT_BROWSER = browser
            _CURRENT_CONTEXT = context
            page = context.new_page()

            # Escuchar evento global de descargas
            def on_download(download: Download):
                suggested_filename = download.suggested_filename or f"reporte_{int(time.time())}.xlsx"
                dest_path = self.download_dir / suggested_filename
                download.save_as(dest_path)
                print(f"\n[DESCARGA DETECTADA] Guardado en: {dest_path}")

            page.on("download", on_download)

            # Intentar login inicial automático
            logged_in = self.login(page)

            # Si el usuario solicitó una sección específica, navegar directo
            if logged_in:
                if target == "entradas_salidas":
                    print("[RPA] Navegando directamente a Reporte de Entradas y Salidas (main.php?opc=163)...")
                    try:
                        page.goto("https://siia.abisalud.com/main.php?opc=163", timeout=30000)
                    except Exception as e:
                        print(f"[RPA ADVERTENCIA] Navegación directa: {e}")
                elif target == "inventario":
                    print("[RPA] Navegando directamente a Existencias por Ubicación (main.php?opc=55)...")
                    try:
                        page.goto("https://siia.abisalud.com/main.php?opc=55", timeout=30000)
                    except Exception as e:
                        print(f"[RPA ADVERTENCIA] Navegación directa: {e}")

            print("\n" + "="*60)
            print(" SESIÓN INTERACTIVA ACTIVA")
            print(" - Ya has iniciado sesión automáticamente en SIIA.")
            if target == "entradas_salidas":
                print(" - Estás en el Reporte de Entradas y Salidas.")
                print(" - Selecciona las fechas o filtros deseados y presiona 'Exportar' o 'CSV'.")
            elif target == "inventario":
                print(" - Estás en el Reporte de Existencias por Ubicación.")
                print(" - Presiona 'Exportar' para descargar el archivo de inventario.")
            else:
                print(" - Navega y genera los reportes que desees.")
            print(" - Cualquier archivo descargado se guardará e importará automáticamente.")
            print(" - Cierra la ventana del navegador cuando termines.")
            print("="*60 + "\n")

            try:
                # Mantener abierto hasta que el usuario cierre la página
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            finally:
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass
                _CURRENT_CONTEXT = None
                _CURRENT_BROWSER = None
                print("[RPA] Sesión cerrada.")

