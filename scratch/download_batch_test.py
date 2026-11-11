import sys
sys.path.insert(0, '.')
import urllib.request
import ssl
import json
from downloader import SiiaDownloader

dl = SiiaDownloader()
cookies = dl.get_authenticated_session_cookies()
cookie_header = '; '.join([f'{k}={v}' for k, v in cookies.items()])

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

seg = {}
with open('scratch/seguimiento_almacenes.txt', encoding='utf-8') as f:
    for line in f:
        if '|' in line:
            v, n = line.strip().split('|', 1)
            seg[n.strip().upper()] = v.strip()

with open('scratch/results_altas.json', encoding='utf-8') as f:
    altas = json.load(f)

for item in altas[:5]:
    nom = item['nombre'].upper()
    almacen_id = item['id']
    inv_id = seg[nom]
    u = f'https://siia.abisalud.com/almacen/inventarios/inventario_periodico/pdf.php?localidad=1836&almacen={almacen_id}&idInv={inv_id}'
    req = urllib.request.Request(u, headers={'Cookie': cookie_header, 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as r:
        data = r.read()
        print(f"Num {item['num']}: {nom[:35]} (Alm: {almacen_id}, Inv: {inv_id}) -> {len(data)} bytes, PDF: {data.startswith(b'%PDF')}")

