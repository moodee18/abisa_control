import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://siia.abisalud.com/js/almacen/inventarios/seguimiento_inventario.js', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as r:
    txt = r.read().decode('utf-8', errors='ignore')

with open('scratch/seguimiento_inventario_full.js', 'w', encoding='utf-8') as f:
    f.write(txt)

print("Saved scratch/seguimiento_inventario_full.js, len:", len(txt))

