import json
import urllib.request

token = "FnRey7StNwab1s95PEHYYGkWD_vr_umOEGibNEQvRkejhEhXqZD3IFZIq4frOtsu"
headers = {"Authorization": f"Bearer {token}"}

# Test GET /api/control-movimientos/pedidos
req = urllib.request.Request("http://127.0.0.1:8000/api/control-movimientos/pedidos?mes=NOVIEMBRE&ano=2026", headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("NOVIEMBRE pedidos count:", len(data))
    print("First pedido:", data[0] if data else None)

# Test GET /api/control-movimientos/pedido?folio=N-197283
req2 = urllib.request.Request("http://127.0.0.1:8000/api/control-movimientos/pedido?folio=N-197283&mes=NOVIEMBRE&ano=2026", headers=headers)
with urllib.request.urlopen(req2) as resp:
    data2 = json.loads(resp.read().decode('utf-8'))
    print("Detalle N-197283:")
    print("  Folio:", data2.get('folio_pedido'))
    print("  Partidas:", data2.get('total_partidas'))
    print("  Piezas:", data2.get('total_piezas'))

