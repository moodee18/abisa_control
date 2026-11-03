import os
import sys
import openpyxl
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from database import DatabaseManager

client = TestClient(app)

def test_full_workflow():
    print("=== INICIANDO VALIDACIÓN INTEGRAL DE LA BASE DE INVENTARIO Y REGLA FEFO ===")
    
    # 1. Probar endpoint de importación de base
    print("\n[1] Probando POST /api/control-movimientos/import-base-excel...")
    r = client.post("/api/control-movimientos/import-base-excel", data={"mes": "OCTUBRE", "ano": 2026})
    print("Status:", r.status_code)
    data = r.json()
    print("Respuesta:", data)
    assert r.status_code == 200
    assert data["total_entradas"] == 1999
    assert data["total_salidas"] == 823
    assert data["total_apoyos"] == 50

    # 2. Probar Matriz Consolidada
    print("\n[2] Probando GET /api/control-movimientos/matriz?mes=OCTUBRE&ano=2026...")
    r_matriz = client.get("/api/control-movimientos/matriz?mes=OCTUBRE&ano=2026")
    assert r_matriz.status_code == 200
    m_data = r_matriz.json()
    kpis = m_data["kpis"]
    print("KPIs Matriz:")
    print(f"  Claves únicas:          {kpis['total_claves']}")
    print(f"  Total Lotes:            {kpis['total_lotes']}")
    print(f"  Inventario Inicial:     {kpis['total_inventario_inicial']:,.2f}")
    print(f"  Entrada Ajuste:         {kpis['total_entrada_ajuste']:,.2f}")
    print(f"  Cantidad Recibida:      {kpis['total_cantidad_recibida']:,.2f}")
    print(f"  Inventario Total:       {kpis['total_inventario_mensual']:,.2f}")
    print(f"  Total Surtido:          {kpis['total_surtido_mensual']:,.2f}")
    print(f"  Inventario Disponible:  {kpis['total_inventario_disponible']:,.2f}")

    assert kpis['total_inventario_mensual'] == 987343.0
    assert kpis['total_surtido_mensual'] == 76527.0
    assert kpis['total_inventario_disponible'] == 910816.0
    print(">>> KPIs coinciden exactamente con el archivo original de OneDrive!")

    # 3. Probar Salidas PDF y FEFO
    print("\n[3] Probando GET /api/control-movimientos/salidas-pdf...")
    r_sal = client.get("/api/control-movimientos/salidas-pdf?mes=OCTUBRE&ano=2026")
    assert r_sal.status_code == 200
    salidas = r_sal.json()
    print(f"Total salidas recuperadas: {len(salidas)}")
    assert len(salidas) == 823
    
    # Contar alertas FEFO
    fefo_avisos = [s for s in salidas if "AVISO FEFO" in s.get("aviso_fefo", "")]
    fefo_optimos = [s for s in salidas if "Cumple FEFO" in s.get("aviso_fefo", "")]
    print(f"  Salidas con AVISO FEFO: {len(fefo_avisos)}")
    print(f"  Salidas FEFO OPTIMO:    {len(fefo_optimos)}")
    print(f"  Ejemplo Aviso FEFO: '{fefo_avisos[0]['aviso_fefo'].encode('ascii', 'replace').decode()}'")
    assert len(fefo_avisos) == 169

    # 4. Probar Apoyos Institucionales
    print("\n[4] Probando GET /api/control-movimientos/apoyo-institucional...")
    r_apoyos = client.get("/api/control-movimientos/apoyo-institucional?mes=OCTUBRE&ano=2026")
    assert r_apoyos.status_code == 200
    apoyos = r_apoyos.json()
    print(f"Total apoyos institucionales: {len(apoyos)}")
    assert len(apoyos) == 50

    # 5. Probar Exportación de Excel de 5 Hojas
    print("\n[5] Probando GET /api/control-movimientos/export-excel?mes=OCTUBRE&ano=2026...")
    r_exp = client.get("/api/control-movimientos/export-excel?mes=OCTUBRE&ano=2026")
    assert r_exp.status_code == 200
    import io
    wb = openpyxl.load_workbook(io.BytesIO(r_exp.content))
    print(f"Hojas exportadas en el libro: {wb.sheetnames}")
    assert set(wb.sheetnames) == {"Reporte Diario", "Entradas", "Salidas PDF", "Apoyo Institucional", "Catálogos"}
    
    ws_salidas = wb["Salidas PDF"]
    assert "AVISO REGLA FEFO" in [ws_salidas.cell(1, c).value for c in range(1, ws_salidas.max_column + 1)]
    print("Columna 'AVISO REGLA FEFO' presente y validada en hoja Salidas PDF.")

    print("\n=======================================================")
    print(">>> ¡TODAS LAS VALIDACIONES PASARON SATISFACTORIAMENTE! <<<")
    print("=======================================================")

if __name__ == "__main__":
    test_full_workflow()
