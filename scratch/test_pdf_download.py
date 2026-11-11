import sys
sys.path.insert(0, '.')
import urllib.request
import ssl
from downloader import SiiaDownloader

dl = SiiaDownloader()
cookies = dl.get_authenticated_session_cookies()
cookie_header = '; '.join([f'{k}={v}' for k, v in cookies.items()])

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ('inventario_periodico_pdf', 'https://siia.abisalud.com/almacen/inventarios/inventario_periodico/pdf.php?localidad=1836&almacen=5811&idInv=302810'),
    ('seguimiento_inventario_pdf', 'https://siia.abisalud.com/almacen/inventarios/seguimiento_inventario/pdf_seguimiento_inventario.php?localidad=1836&inventario=302810'),
    ('marbetes_pdf', 'https://siia.abisalud.com/almacen/inventarios/inventario_periodico/pdf_marbetes.php?localidad=1836&idInv=302810')
]

for name, u in urls:
    req = urllib.request.Request(u, headers={'Cookie': cookie_header, 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            data = r.read()
            ct = r.headers.get('Content-Type')
            disp = r.headers.get('Content-Disposition')
            is_pdf = data.startswith(b'%PDF')
            print(f"{name}: len={len(data)}, type={ct}, disp={disp}, is_pdf={is_pdf}")
            with open(f"scratch/{name}_test.pdf", "wb") as f:
                f.write(data)
    except Exception as e:
        print(f"{name}: ERROR {e}")
