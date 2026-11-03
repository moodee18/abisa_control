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

    def get_authenticated_session_cookies(self) -> dict:
        """Inicia sesión silenciosa (headless) y extrae las cookies de sesión válidas."""
        global _CURRENT_BROWSER, _CURRENT_CONTEXT
        print("[RPA HEADLESS] Iniciando sesión sin ventana para obtener cookies de autenticación...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(accept_downloads=True, ignore_https_errors=True)
            _CURRENT_BROWSER = browser
            _CURRENT_CONTEXT = context
            page = context.new_page()

            logged_in = self.login(page)
            if not logged_in:
                browser.close()
                _CURRENT_BROWSER = None
                _CURRENT_CONTEXT = None
                raise RuntimeError("No se pudo iniciar sesión automáticamente en SIIA. Verifique SIIA_USERNAME y SIIA_PASSWORD en .env.")

            cookies = {c['name']: c['value'] for c in context.cookies()}
            browser.close()
            _CURRENT_BROWSER = None
            _CURRENT_CONTEXT = None
            return cookies

    def download_existencias_auto(self, localidad_id: str = "1836", progress_callback=None) -> Path:
        """
        Descarga automática y desatendida del reporte oficial de existencias (CS ALMACEN 2022 o id indicado).
        Funciona 100% en segundo plano sin abrir ninguna ventana en el escritorio, ideal para llamadas desde red WiFi.
        """
        import ssl
        import urllib.request

        if progress_callback:
            progress_callback("Iniciando sesión silenciosa en SIIA...")

        cookies = self.get_authenticated_session_cookies()

        if progress_callback:
            progress_callback("Descargando reporte oficial de existencias desde SIIA...")

        url = f"https://siia.abisalud.com/reportes/almacen/existencias_ubicacion/excel_existencias.php?localidad={localidad_id}&localidad_t={localidad_id}&almacen=-999&codigo_barras=-999"
        cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url,
            headers={
                "Cookie": cookie_header,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        dest_path = self.download_dir / "Existiencias_x_Ubicación.xlsx"
        print(f"[RPA HEADLESS] Descargando existencias desde {url}...")
        with urllib.request.urlopen(req, context=ctx, timeout=180) as resp:
            content = resp.read()
            if len(content) < 1000:
                raise RuntimeError("El archivo descargado está vacío o la sesión expiró.")
            with open(dest_path, "wb") as f:
                f.write(content)

        print(f"[RPA HEADLESS] Reporte de existencias descargado exitosamente: {dest_path} ({len(content):,} bytes)")
        if progress_callback:
            progress_callback(f"Reporte descargado ({len(content):,} bytes). Importando...")

        return dest_path

    def download_movimientos_auto(self, fecha_inicio: str, fecha_fin: str, localidad_id: str = "1836", progress_callback=None) -> list:
        """
        Descarga automática y desatendida del reporte de Entradas y Salidas en un rango de fechas (YYYY-MM-DD).
        Si el rango abarca más de un mes o períodos largos, lo divide automáticamente en bloques mensuales
        para evitar que el servidor de SIIA sature la base de datos o corte la conexión por tiempo límite (timeout).
        """
        import ssl
        import urllib.request
        import calendar
        from datetime import datetime, date

        def get_monthly_date_chunks(start_str: str, end_str: str):
            start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_str, "%Y-%m-%d").date()
            if start_dt > end_dt:
                start_dt, end_dt = end_dt, start_dt
            chunks = []
            curr = start_dt
            while curr <= end_dt:
                last_day = calendar.monthrange(curr.year, curr.month)[1]
                m_end = date(curr.year, curr.month, last_day)
                chunk_end = min(m_end, end_dt)
                chunks.append((curr.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
                if m_end >= end_dt:
                    break
                if curr.month == 12:
                    curr = date(curr.year + 1, 1, 1)
                else:
                    curr = date(curr.year, curr.month + 1, 1)
            return chunks

        chunks = get_monthly_date_chunks(fecha_inicio, fecha_fin)
        total_chunks = len(chunks)

        if progress_callback:
            if total_chunks > 1:
                progress_callback(f"Rango de {total_chunks} meses detectado ({fecha_inicio} al {fecha_fin}). Conectando a SIIA...")
            else:
                progress_callback(f"Iniciando sesión silenciosa en SIIA ({fecha_inicio} al {fecha_fin})...")

        cookies = self.get_authenticated_session_cookies()
        cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        downloaded_paths = []
        for idx, (c_start, c_end) in enumerate(chunks, 1):
            if progress_callback:
                if total_chunks > 1:
                    progress_callback(f"Descargando bloque {idx} de {total_chunks}: {c_start} al {c_end} (SIIA procesando consulta)...")
                else:
                    progress_callback(f"Descargando Entradas y Salidas ({c_start} al {c_end})...")

            url = f"https://siia.abisalud.com/reportes/almacen/entradas_salidas/excel.php?localidad={localidad_id}&localidad_t={localidad_id}&almacen=-999&codigo_barras=-999&fecha_inicio={c_start}&fecha_fin={c_end}&tipo_reporte=1&lotes=-999"
            req = urllib.request.Request(
                url,
                headers={
                    "Cookie": cookie_header,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )

            dest_path = self.download_dir / f"Entradas_Salidas_{c_start}_al_{c_end}.xlsx"
            print(f"[RPA HEADLESS] Descargando bloque {idx}/{total_chunks} ({c_start} al {c_end})...")

            try:
                with urllib.request.urlopen(req, context=ctx, timeout=240) as resp:
                    content = resp.read()
                    if len(content) < 1000:
                        print(f"[RPA ADVERTENCIA] El bloque {c_start} al {c_end} devolvió menos de 1000 bytes (posiblemente sin movimientos).")
                        continue
                    with open(dest_path, "wb") as f:
                        f.write(content)
                    downloaded_paths.append(dest_path)
                    print(f"[RPA HEADLESS] Bloque {idx}/{total_chunks} guardado: {dest_path} ({len(content):,} bytes)")
            except Exception as e:
                print(f"[RPA ERROR] Error en bloque {c_start} al {c_end}: {e}")
                if total_chunks == 1:
                    raise e
                if progress_callback:
                    progress_callback(f"Advertencia: Bloque {c_start} al {c_end} no respondió ({e}). Continuando con siguientes meses...")

        if not downloaded_paths:
            raise RuntimeError(f"No se pudieron descargar datos para el rango especificado ({fecha_inicio} al {fecha_fin}).")

        if progress_callback:
            progress_callback(f"{len(downloaded_paths)} bloque(s) descargados exitosamente. Importando a la base de datos...")

        return downloaded_paths

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

