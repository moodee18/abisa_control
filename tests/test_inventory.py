import sys
import unittest
from pathlib import Path

# Añadir el directorio raíz
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import DatabaseManager
from fastapi.testclient import TestClient
from app import app

class TestInventorySystem(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.client = TestClient(app)

    def test_01_crud_database_operations(self):
        # 1. Crear insumo
        item_data = {
            "clave": "010.000.TEST.01",
            "descripcion": "INSUMO DE PRUEBA UNITARIA 500MG",
            "presentacion": "CAJA C/10",
            "lote": "LOTE-UNIT-01",
            "caducidad": "2028-12-31",
            "cantidad": 50.0,
            "unidad_medida": "CAJA",
            "precio_unitario": 25.50,
            "almacen_origen": "ALMACEN TEST",
            "proveedor": "PROVEEDOR TEST"
        }
        created = self.db.create_record(item_data)
        self.assertIsNotNone(created["id"])
        self.assertEqual(created["clave"], "010.000.TEST.01")
        self.assertEqual(created["importe_total"], 50.0 * 25.50)
        record_id = created["id"]

        # 2. Consultar catálogo
        catalog = self.db.get_catalog_by_clave(search="TEST.01")
        self.assertTrue(len(catalog) >= 1)
        self.assertEqual(catalog[0]["clave"], "010.000.TEST.01")
        self.assertEqual(catalog[0]["total_existencia"], 50.0)

        # 3. Actualizar insumo
        updated = self.db.update_record(record_id, {"cantidad": 100.0, "precio_unitario": 30.0})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["cantidad"], 100.0)
        self.assertEqual(updated["importe_total"], 3000.0)

        # 4. Eliminar insumo
        deleted = self.db.delete_record(record_id)
        self.assertTrue(deleted)

        # 5. Verificar que ya no existe
        record = self.db.get_record_by_id(record_id)
        self.assertIsNone(record)

    def test_02_fastapi_endpoints(self):
        # Test KPIs
        res = self.client.get("/api/kpis")
        self.assertEqual(res.status_code, 200)
        kpis = res.json()
        self.assertIn("total_claves", kpis)
        self.assertIn("total_piezas", kpis)

        # Test POST create via API
        payload = {
            "clave": "010.000.API.99",
            "descripcion": "INSUMO CREADO POR API",
            "presentacion": "FRASCO 100ML",
            "lote": "LOTE-API-99",
            "caducidad": "2027-06-30",
            "cantidad": 20.0,
            "unidad_medida": "FRASCO",
            "precio_unitario": 45.0,
            "almacen_origen": "ALMACEN API"
        }
        res_post = self.client.post("/api/inventory", json=payload)
        self.assertEqual(res_post.status_code, 200)
        data = res_post.json()
        self.assertEqual(data["status"], "success")
        rec_id = data["data"]["id"]

        # Test GET catalog
        res_cat = self.client.get("/api/catalog?search=API.99")
        self.assertEqual(res_cat.status_code, 200)
        self.assertTrue(len(res_cat.json()) >= 1)

        # Test PUT update via API
        res_put = self.client.put(f"/api/inventory/{rec_id}", json={"cantidad": 35.0})
        self.assertEqual(res_put.status_code, 200)
        self.assertEqual(res_put.json()["data"]["cantidad"], 35.0)

        # Test DELETE via API
        res_del = self.client.delete(f"/api/inventory/{rec_id}")
        self.assertEqual(res_del.status_code, 200)

        # Test POST /api/clear
        res_clear = self.client.post("/api/clear")
        self.assertEqual(res_clear.status_code, 200)
        self.assertEqual(res_clear.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
