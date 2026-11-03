import urllib.request
import json

base_url = 'http://localhost:8000'

try:
    # 1. Test Matriz
    req = urllib.request.urlopen(f'{base_url}/api/control-movimientos/matriz?mes=OCTUBRE&ano=2026')
    print('Matriz status:', req.status)
    if req.status == 200:
        data = json.loads(req.read().decode('utf-8'))
        items = data.get('items', [])
        print(f'Total matriz items: {len(items)}')
        sample = [it for it in items if it.get('procedimiento') or it.get('contrato')]
        print(f'Matriz items with proc/contrato: {len(sample)} / {len(items)}')
        for s in sample[:5]:
            print(f"  OS: {s.get('orden_suministro')} | Proc: {s.get('procedimiento')} | Cont: {s.get('contrato')} | Cve: {s.get('clave')}")

    # 2. Test Entradas
    req_ent = urllib.request.urlopen(f'{base_url}/api/control-movimientos/entradas?mes=OCTUBRE&ano=2026')
    print('Entradas status:', req_ent.status)
    if req_ent.status == 200:
        data_ent = json.loads(req_ent.read().decode('utf-8'))
        items_ent = data_ent.get('items', []) if isinstance(data_ent, dict) else data_ent
        print(f'Total entradas items: {len(items_ent)}')
        sample_ent = [it for it in items_ent if it.get('procedimiento') or it.get('contrato')]
        print(f'Entradas items with proc/contrato: {len(sample_ent)} / {len(items_ent)}')
        for s in sample_ent[:5]:
            print(f"  OS: {s.get('orden_suministro') or s.get('folio_documento')} | Proc: {s.get('procedimiento')} | Cont: {s.get('contrato')} | Cve: {s.get('clave')}")

    # 3. Test Export Excel
    req_excel = urllib.request.urlopen(f'{base_url}/api/control-movimientos/export-excel?mes=OCTUBRE&ano=2026')
    content = req_excel.read()
    print('Export Excel status:', req_excel.status, 'Content length:', len(content))
except Exception as e:
    import traceback
    traceback.print_exc()
