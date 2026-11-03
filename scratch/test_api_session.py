import json
import urllib.request

token = "FnRey7StNwab1s95PEHYYGkWD_vr_umOEGibNEQvRkejhEhXqZD3IFZIq4frOtsu"
headers = {"Authorization": f"Bearer {token}"}

# Test Octubre
req = urllib.request.Request("http://127.0.0.1:8000/api/control-movimientos/matriz?mes=OCTUBRE&ano=2026", headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("OCTUBRE KPI total_surtido:", data.get('kpis', {}).get('total_surtido'))
    print("OCTUBRE KPI total_disponible:", data.get('kpis', {}).get('total_inventario_disponible'))
    rows = data.get('items', [])
    rows_fa = [r for r in rows if r.get('fecha_ajuste')]
    print(f"OCTUBRE rows with fecha_ajuste: {len(rows_fa)}")

# Test Noviembre
req2 = urllib.request.Request("http://127.0.0.1:8000/api/control-movimientos/matriz?mes=NOVIEMBRE&ano=2026", headers=headers)
with urllib.request.urlopen(req2) as resp:
    data2 = json.loads(resp.read().decode('utf-8'))
    print("NOVIEMBRE KPI total_surtido:", data2.get('kpis', {}).get('total_surtido'))
    print("NOVIEMBRE KPI total_disponible:", data2.get('kpis', {}).get('total_inventario_disponible'))
    print("NOVIEMBRE KPI total_inicial:", data2.get('kpis', {}).get('total_inventario_inicial'))
