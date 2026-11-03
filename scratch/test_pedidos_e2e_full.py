import json
import urllib.request

token = "FnRey7StNwab1s95PEHYYGkWD_vr_umOEGibNEQvRkejhEhXqZD3IFZIq4frOtsu"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 1. Insert a test order in NOVIEMBRE
insert_payload = json.dumps({
    "folio_actual": "TEST-PEDIDO-999",
    "archivo_actual": "TEST_PEDIDO_999.pdf",
    "mes_actual": "NOVIEMBRE",
    "ano_actual": 2026,
    "nuevo_folio": "TEST-PEDIDO-999",
    "nueva_fecha": "2026-11-05 12:00:00",
    "nuevo_dia": 5,
    "nuevo_mes": "NOVIEMBRE",
    "nuevo_ano": 2026,
    "nuevo_archivo": "TEST_PEDIDO_999.pdf",
    "items": [
        {
            "clave": "010.000.3675.00",
            "descripcion": "SOLUCION TEST",
            "cantidad": 10.0,
            "lote_asignado": "TESTLOT1",
            "fecha_caducidad": "2028-12-31"
        },
        {
            "clave": "010.000.3627.00",
            "descripcion": "SOLUCION TEST 2",
            "cantidad": 20.0,
            "lote_asignado": "TESTLOT2",
            "fecha_caducidad": "2028-12-31"
        }
    ]
}).encode('utf-8')

# We can insert via direct db or test update_pedido_completo
import sys
sys.path.insert(0, '.')
from database import DatabaseManager, SalidaPdfMov

db = DatabaseManager('sqlite:///data/abisalud.db')
sess = db.get_session()
item1 = SalidaPdfMov(archivo_pdf="TEST_PEDIDO_999.pdf", folio_pedido="TEST-PEDIDO-999", fecha="2026-11-05 12:00:00", dia=5, mes="NOVIEMBRE", ano=2026, clave="010.000.3675.00", descripcion="TEST 1", cantidad=10.0, lote_asignado="TESTLOT1", fecha_caducidad="2028-12-31")
item2 = SalidaPdfMov(archivo_pdf="TEST_PEDIDO_999.pdf", folio_pedido="TEST-PEDIDO-999", fecha="2026-11-05 12:00:00", dia=5, mes="NOVIEMBRE", ano=2026, clave="010.000.3627.00", descripcion="TEST 2", cantidad=20.0, lote_asignado="TESTLOT2", fecha_caducidad="2028-12-31")
sess.add(item1)
sess.add(item2)
sess.commit()
sess.close()

print("Inserted temporary TEST-PEDIDO-999 with 2 items (30 piezas)")

# 2. Test modifying the entire order via PUT /api/control-movimientos/pedido
modify_payload = json.dumps({
    "folio_actual": "TEST-PEDIDO-999",
    "archivo_actual": "TEST_PEDIDO_999.pdf",
    "mes_actual": "NOVIEMBRE",
    "ano_actual": 2026,
    "nuevo_folio": "TEST-PEDIDO-MODIFICADO",
    "nueva_fecha": "2026-11-05 14:30:00",
    "nuevo_dia": 5,
    "nuevo_mes": "NOVIEMBRE",
    "nuevo_ano": 2026,
    "nuevo_archivo": "TEST_MODIFICADO.pdf",
    "items": [
        {
            "clave": "010.000.3675.00",
            "descripcion": "SOLUCION TEST MOD",
            "cantidad": 50.0,
            "lote_asignado": "TESTLOT1_MOD",
            "fecha_caducidad": "2029-01-01"
        }
    ]
}).encode('utf-8')

req_put = urllib.request.Request("http://127.0.0.1:8000/api/control-movimientos/pedido", data=modify_payload, headers=headers, method="PUT")
with urllib.request.urlopen(req_put) as resp:
    put_data = json.loads(resp.read().decode('utf-8'))
    print("PUT response:", put_data)

# Check detail after modification
req_det = urllib.request.Request("http://127.0.0.1:8000/api/control-movimientos/pedido?folio=TEST-PEDIDO-MODIFICADO&mes=NOVIEMBRE&ano=2026", headers=headers)
with urllib.request.urlopen(req_det) as resp:
    det_data = json.loads(resp.read().decode('utf-8'))
    print("Modified order detail:", det_data.get('folio_pedido'), det_data.get('total_partidas'), det_data.get('total_piezas'))
    assert det_data.get('folio_pedido') == "TEST-PEDIDO-MODIFICADO"
    assert det_data.get('total_partidas') == 1
    assert det_data.get('total_piezas') == 50.0

# 3. Test deleting the entire order via DELETE /api/control-movimientos/pedido
req_del = urllib.request.Request("http://127.0.0.1:8000/api/control-movimientos/pedido?folio=TEST-PEDIDO-MODIFICADO&mes=NOVIEMBRE&ano=2026", headers=headers, method="DELETE")
with urllib.request.urlopen(req_del) as resp:
    del_data = json.loads(resp.read().decode('utf-8'))
    print("DELETE response:", del_data)
    assert del_data.get('deleted_items') == 1
    assert del_data.get('deleted_piezas') == 50.0

# Verify it no longer exists
sess = db.get_session()
rem = sess.query(SalidaPdfMov).filter_by(folio_pedido="TEST-PEDIDO-MODIFICADO").count()
sess.close()
print("Remaining rows for TEST-PEDIDO-MODIFICADO:", rem)
assert rem == 0
print("ALL END-TO-END TESTS PASSED!")

