import openpyxl
import urllib.request
import urllib.parse
import json
import io
import mimetypes
import uuid

BASE_URL = "http://localhost:8000"

def http_get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

def http_post_form(url, fields):
    data = urllib.parse.urlencode(fields).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

def http_post_multipart(url, fields, files):
    boundary = uuid.uuid4().hex
    body = bytearray()
    for k, v in fields.items():
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode('utf-8'))
        body.extend(f'{v}\r\n'.encode('utf-8'))
    for k, (filename, filedata) in files.items():
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{k}"; filename="{filename}"\r\n'.encode('utf-8'))
        body.extend(b'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n')
        body.extend(filedata)
        body.extend(b'\r\n')
    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

    req = urllib.request.Request(url, data=bytes(body), headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

def test_default_import():
    print("--- 1. Testing Default Base Excel Import ---")
    status, raw = http_post_form(f"{BASE_URL}/api/control-movimientos/import-base-excel", {'mes': 'OCTUBRE', 'ano': '2026'})
    assert status == 200
    json_data = json.loads(raw.decode('utf-8'))
    print("Status:", status)
    print("Response message:", json_data.get('message'))

def test_matriz_query():
    print("\n--- 2. Testing Matriz Query ---")
    status, raw = http_get(f"{BASE_URL}/api/control-movimientos/matriz?mes=OCTUBRE&ano=2026")
    assert status == 200
    data = json.loads(raw.decode('utf-8'))
    items = data.get('items', [])
    kpis = data.get('kpis', {})
    print(f"Total rows: {len(items)}")
    print(f"KPI Partidas/Lotes: {kpis.get('total_partidas')}, Claves: {kpis.get('total_claves')}")
    print(f"KPI Inv Total Mensual: {kpis.get('total_inventario_mensual')}")
    print(f"KPI Total Surtido: {kpis.get('total_surtido_mes')}")
    print(f"KPI Inv Disponible: {kpis.get('total_inventario_disponible')}")

    if items:
        first = items[0]
        print("\nFirst row sample:")
        print("  Procedimiento:", first.get('procedimiento'))
        print("  Contrato:", first.get('contrato'))
        print("  Orden:", first.get('orden_suministro'))
        print("  Reg. Sanitario:", first.get('registro_sanitario'))
        print("  Proveedor:", first.get('proveedor'))
        print("  Clave:", first.get('clave'))
        print("  Lote:", first.get('lote'))
        print("  Caducidad:", first.get('fecha_caducidad'))
        print("  Inv Inicial:", first.get('inventario_inicial'))
        print("  Ajuste:", first.get('entrada_por_ajuste'))
        print("  Recibida:", first.get('cantidad_recibida'))
        print("  Total Mensual:", first.get('inventario_total_mensual'))
        print("  Total Surtido:", first.get('total_surtido'))
        print("  Disponible:", first.get('inventario_disponible'))

def test_new_excel_upload():
    print("\n--- 3. Testing Upload of New 52-Column Excel ---")
    status, excel_bytes = http_get(f"{BASE_URL}/api/control-movimientos/export-excel?mes=OCTUBRE&ano=2026")
    assert status == 200

    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes), data_only=False)
    sheet1 = wb.worksheets[0]
    print("Sheet 1 Title:", sheet1.title)
    headers = [sheet1.cell(row=2, column=c).value for c in range(1, 53)]
    print(f"Headers count: {len(headers)}")
    print(f"Col 1..5: {headers[:5]}")
    print(f"Col 6..10: {headers[5:10]}")
    print(f"Col 11..15: {headers[10:15]}")
    print(f"Col 47..52: {headers[46:52]}")

    status, raw = http_post_multipart(
        f"{BASE_URL}/api/control-movimientos/import-base-excel",
        {'mes': 'OCTUBRE', 'ano': '2026'},
        {'file': ('NUEVO_INVENTARIO_GENERAL_OCT.xlsx', excel_bytes)}
    )
    print("Upload status:", status)
    upload_json = json.loads(raw.decode('utf-8'))
    print("Upload message:", upload_json.get('message'))
    assert status == 200

if __name__ == "__main__":
    test_default_import()
    test_matriz_query()
    test_new_excel_upload()
    test_matriz_query()
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
