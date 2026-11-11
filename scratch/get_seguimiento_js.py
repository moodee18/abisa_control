import sys
sys.path.insert(0, '.')
import urllib.request
import ssl
from downloader import SiiaDownloader

downloader = SiiaDownloader()
cookies = downloader.get_authenticated_session_cookies()
cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://siia.abisalud.com/js/almacen/inventarios/seguimiento_inventario.js"
req = urllib.request.Request(url, headers={"Cookie": cookie_header, "User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req, context=ctx) as resp:
    code = resp.read().decode('utf-8', errors='ignore')

print("Downloaded seguimiento_inventario.js, length:", len(code))
for line in code.split('\n'):
    if 'pdf.php' in line or 'function pdf' in line or 'excel' in line:
        print("MATCH:", line[:120])

