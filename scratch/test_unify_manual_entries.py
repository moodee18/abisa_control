import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import DatabaseManager, EntradaMov

def test_unify_criteria():
    db = DatabaseManager()
    session = db.get_session()
    test_clave_1 = "TEST.001.0001"
    test_clave_2 = "TEST.002.0002"
    
    try:
        # Limpiar cualquier prueba previa
        session.query(EntradaMov).filter(EntradaMov.clave.in_([test_clave_1, test_clave_2])).delete()
        session.commit()

        print("=== TEST 1: Primera entrada manual (OS-AAA-01) ===")
        e1 = db.create_entrada_mov({
            "clave": test_clave_1,
            "lote": "LOT-ALPHA",
            "fecha_caducidad": "2027-08-30",
            "orden_suministro": "OS-AAA-01",
            "inventario_inicial": 100.0,
            "cantidad_recibida": 50.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        print(f"  Resultado: ID={e1['id']}, row_index={e1.get('row_index')}, unified={e1.get('unified')}")
        assert e1.get("unified") is False, "TEST 1 FALLÓ: No debió unificarse porque es la primera entrada."

        print("\n=== TEST 2: Misma clave, lote y caducidad pero DIFERENTE orden (OS-BBB-02) ===")
        e2 = db.create_entrada_mov({
            "clave": test_clave_1,
            "lote": "LOT-ALPHA",
            "fecha_caducidad": "2027-08-30",
            "orden_suministro": "OS-BBB-02",  # Diferente orden
            "inventario_inicial": 0.0,
            "cantidad_recibida": 30.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        print(f"  Resultado: ID={e2['id']}, row_index={e2.get('row_index')}, unified={e2.get('unified')}")
        assert e2.get("unified") is False, "TEST 2 FALLÓ: Debió agregarse como fila independiente al tener diferente orden."
        assert e2["id"] != e1["id"], "TEST 2 FALLÓ: Debe tener un ID diferente."
        assert e2.get("row_index") != e1.get("row_index"), "TEST 2 FALLÓ: Debe tener un row_index diferente."

        print("\n=== TEST 3: Coincidencia EXACTA en los 4 criterios (Clave, Lote, Caducidad y Orden OS-AAA-01) ===")
        e3 = db.create_entrada_mov({
            "clave": test_clave_1,
            "lote": "LOT-ALPHA",
            "fecha_caducidad": "2027-08-30",
            "orden_suministro": "OS-AAA-01",  # Coincide exactamente con e1
            "proveedor": "PROVEEDOR_NUEVO_IGNORAR",
            "contrato": "CONTRATO_NUEVO_IGNORAR",
            "procedimiento": "PROCEDIMIENTO_NUEVO_IGNORAR",
            "inventario_inicial": 0.0,
            "cantidad_recibida": 25.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        print(f"  Resultado: ID={e3['id']}, row_index={e3.get('row_index')}, unified={e3.get('unified')}")
        assert e3.get("unified") is True, "TEST 3 FALLÓ: Debió unificarse al coincidir los 4 criterios."
        assert e3["id"] == e1["id"], "TEST 3 FALLÓ: El ID unificado debe coincidir con el registro e1."
        assert e3["cantidad_recibida"] == 75.0, f"TEST 3 FALLÓ: La cantidad recibida acumulada debió ser 75.0 (50+25), dio {e3['cantidad_recibida']}"
        assert e3["inventario_inicial"] == 100.0, f"TEST 3 FALLÓ: El inventario inicial debió mantenerse en 100.0, dio {e3['inventario_inicial']}"
        assert e3.get("proveedor") != "PROVEEDOR_NUEVO_IGNORAR", "TEST 3 FALLÓ: El proveedor NO debió autocompletarse ni sobreescribirse!"
        assert e3.get("contrato") != "CONTRATO_NUEVO_IGNORAR", "TEST 3 FALLÓ: El contrato NO debió autocompletarse ni sobreescribirse!"
        assert e3.get("procedimiento") != "PROCEDIMIENTO_NUEVO_IGNORAR", "TEST 3 FALLÓ: El procedimiento NO debió autocompletarse ni sobreescribirse!"

        print("\n=== TEST 4: Misma clave, lote y orden pero DIFERENTE caducidad ===")
        e4 = db.create_entrada_mov({
            "clave": test_clave_1,
            "lote": "LOT-ALPHA",
            "fecha_caducidad": "2029-12-31",  # Diferente caducidad
            "orden_suministro": "OS-AAA-01",
            "inventario_inicial": 0.0,
            "cantidad_recibida": 40.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        print(f"  Resultado: ID={e4['id']}, row_index={e4.get('row_index')}, unified={e4.get('unified')}")
        assert e4.get("unified") is False, "TEST 4 FALLÓ: No debe unificarse al tener distinta caducidad."
        assert e4["id"] not in (e1["id"], e2["id"]), "TEST 4 FALLÓ: Debe tener un nuevo ID."

        print("\n=== TEST 5: Entradas sin orden de suministro ('') vs ('-') ===")
        e5a = db.create_entrada_mov({
            "clave": test_clave_2,
            "lote": "LOT-BETA",
            "fecha_caducidad": "2026-11-15",
            "orden_suministro": "",
            "inventario_inicial": 50.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        print(f"  5a Resultado: ID={e5a['id']}, unified={e5a.get('unified')}")

        e5b = db.create_entrada_mov({
            "clave": test_clave_2,
            "lote": "LOT-BETA",
            "fecha_caducidad": "2026-11-15",
            "orden_suministro": "-",  # Ambos normalizan a sin orden
            "inventario_inicial": 20.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        print(f"  5b Resultado: ID={e5b['id']}, unified={e5b.get('unified')}, inv_ini={e5b['inventario_inicial']}")
        assert e5b.get("unified") is True, "TEST 5 FALLÓ: Ambas sin orden deben unificarse."
        assert e5b["inventario_inicial"] == 70.0, f"TEST 5 FALLÓ: Inventario acumulado debió ser 70.0, dio {e5b['inventario_inicial']}"

        print("\n>>> TODOS LOS TESTS DE UNIFICACIÓN Y FILAS INDEPENDIENTES PASARON EXITOSAMENTE! <<<")

    finally:
        # Limpieza de registros de prueba
        session.query(EntradaMov).filter(EntradaMov.clave.in_([test_clave_1, test_clave_2])).delete()
        session.commit()
        session.close()

if __name__ == "__main__":
    test_unify_criteria()
