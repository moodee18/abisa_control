import time, sys
sys.path.insert(0, ".")
from downloader import SiiaDownloader
import ssl, urllib.request

d = SiiaDownloader(download_dir="data/downloads")
cookies = d.get_authenticated_session_cookies()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

def test_fetch(start, end, timeout=120):
    url = f"https://siia.abisalud.com/reportes/almacen/entradas_salidas/excel.php?localidad=1836&localidad_t=1836&almacen=-999&codigo_barras=-999&fecha_inicio={start}&fecha_fin={end}&tipo_reporte=1&lotes=-999"
    req = urllib.request.Request(
        url,
        headers={
            "Cookie": cookie_header,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    t0 = time.time()
    print(f"\n--- Testing {start} to {end} (timeout={timeout}s) ---")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            data = resp.read()
            elapsed = time.time() - t0
            print(f"SUCCESS in {elapsed:.2f}s! Received {len(data):,} bytes")
            return len(data)
    except Exception as e:
        elapsed = time.time() - t0
        print(f"FAILED after {elapsed:.2f}s with error: {e}")
        return None

# Test September (current month)
test_fetch("2026-09-01", "2026-09-23", timeout=60)

# Test August
test_fetch("2026-08-01", "2026-08-31", timeout=120)

# Test January with larger timeout (180s) to see if it finishes or if it takes e.g. 100s
test_fetch("2026-01-01", "2026-01-31", timeout=180)
