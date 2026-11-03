import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app import app
from database import DatabaseManager, EntradaMov

def test_api_unify():
    client = TestClient(app)
    db = DatabaseManager()
    session = db.get_session()
    test_clave = "API.TEST.001"
    
    try:
        # Limpiar
        session.query(EntradaMov).filter(EntradaMov.clave == test_clave).delete()
        session.commit()

        # 1. POST primer registro
        res1 = client.post("/api/control-movimientos/entradas", json={
            "clave": test_clave,
            "lote": "LOTE-API-1",
            "fecha_caducidad": "2027-05-15",
            "orden_suministro": "OS-API-100",
            "inventario_inicial": 10.0,
            "cantidad_recibida": 20.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        assert res1.status_code == 200, f"Error en POST 1: {res1.text}"
        d1 = res1.json()
        print("API 1:", d1.get("id"), "unified:", d1.get("unified"), "message:", d1.get("message"))
        assert d1.get("unified") is False

        # 2. POST segundo registro con MISMA clave, lote, caducidad pero DIFERENTE orden
        res2 = client.post("/api/control-movimientos/entradas", json={
            "clave": test_clave,
            "lote": "LOTE-API-1",
            "fecha_caducidad": "2027-05-15",
            "orden_suministro": "OS-API-200",  # Diferente orden!
            "inventario_inicial": 5.0,
            "cantidad_recibida": 15.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        assert res2.status_code == 200, f"Error en POST 2: {res2.text}"
        d2 = res2.json()
        print("API 2 (Diferente orden):", d2.get("id"), "unified:", d2.get("unified"), "message:", d2.get("message"))
        assert d2.get("unified") is False
        assert d2.get("id") != d1.get("id")

        # 3. POST tercer registro con COINCIDENCIA EXACTA en los 4 criterios (con el primer registro)
        res3 = client.post("/api/control-movimientos/entradas", json={
            "clave": test_clave,
            "lote": "LOTE-API-1",
            "fecha_caducidad": "2027-05-15",
            "orden_suministro": "OS-API-100",  # Coincide exactamente con el primer registro!
            "inventario_inicial": 0.0,
            "cantidad_recibida": 30.0,
            "mes": "OCTUBRE",
            "ano": 2026
        })
        assert res3.status_code == 200, f"Error en POST 3: {res3.text}"
        d3 = res3.json()
        print("API 3 (Coincidencia exacta 4 criterios):", d3.get("id"), "unified:", d3.get("unified"), "message:", d3.get("message"))
        assert d3.get("unified") is True
        assert d3.get("id") == d1.get("id")
        assert d3.get("cantidad_recibida") == 50.0  # 20 + 30

        print("\n>>> TEST DE ENDPOINT API PASÓ SATISFACTORIAMENTE! <<<")
    finally:
        session.query(EntradaMov).filter(EntradaMov.clave == test_clave).delete()
        session.commit()
        session.close()

if __name__ == "__main__":
    test_api_unify()
