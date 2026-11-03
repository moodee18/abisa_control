import sys
import os
import openpyxl
from fastapi.testclient import TestClient

# Añadir directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import DatabaseManager

db = DatabaseManager()
client = TestClient(app)

def test_fefo_pdf_rules():
    print("=== INICIANDO PRUEBAS DE REGLA FEFO Y ASIGNACIÓN EXACTA POR PDF ===")
    
    # Limpiar salidas previas de prueba
    db.clear_salidas_pdf_mov(mes="OCTUBRE", ano=2026)

    # 1. Crear / Asegurar Clave en Catálogo
    db.create_catalogo_insumo_mov({
        "clave": "010.000.FEFO.01",
        "descripcion": "MEDICAMENTO TEST PARA AUDITORIA FEFO",
        "unidad_medida": "ENV",
        "proveedor_predeterminado": "LABORATORIO FEFO SA"
    })
    print("[1] Clave de catálogo asegurada: 010.000.FEFO.01")

    # 2. Registrar dos entradas:
    # Lote A (Vence pronto: 2026-11-15)
    # Lote B (Vence tarde: 2027-08-30)
    ent_a = db.create_entrada_mov({
        "clave": "010.000.FEFO.01",
        "lote": "LOTE-PRONTO-2026",
        "descripcion": "MEDICAMENTO TEST PARA AUDITORIA FEFO",
        "unidad_medida": "ENV",
        "proveedor": "LABORATORIO FEFO SA",
        "fecha_caducidad": "2026-11-15",
        "inventario_inicial": 200.0,
        "mes": "OCTUBRE",
        "ano": 2026
    })
    ent_b = db.create_entrada_mov({
        "clave": "010.000.FEFO.01",
        "lote": "LOTE-TARDE-2027",
        "descripcion": "MEDICAMENTO TEST PARA AUDITORIA FEFO",
        "unidad_medida": "ENV",
        "proveedor": "LABORATORIO FEFO SA",
        "fecha_caducidad": "2027-08-30",
        "inventario_inicial": 500.0,
        "mes": "OCTUBRE",
        "ano": 2026
    })
    print(f"[2] Entradas creadas: Lote Pronto ({ent_a.id}), Lote Tarde ({ent_b.id})")

    # 3. Caso 1: El PDF surte LOTE-TARDE-2027
    # Debe respetarse exactamente LOTE-TARDE-2027, pero EMITIR AVISO FEFO
    items_pdf_caso1 = [
        {
            "pedido": "N-TEST-001",
            "folio_salida": "99001",
            "fecha": "2026-10-14",
            "dia": 14,
            "clave": "010.000.FEFO.01",
            "descripcion": "MEDICAMENTO TEST PARA AUDITORIA FEFO",
            "cantidad": 50.0,
            "lote": "LOTE-TARDE-2027",
            "caducidad": "2027-08-30",
            "localidad": "HOSPITAL GENERAL GUADALAJARA"
        }
    ]
    res1 = db.process_salidas_pdf_items(items_pdf_caso1, "hoja_entrega_caso1.pdf", mes="OCTUBRE", ano=2026)
    print("\n--- CASO 1: PDF con lote que vence más tarde ---")
    print("Resultado:", res1)
    assert res1["total_procesados"] == 1
    assert res1["total_avisos_fefo"] == 1
    assert len(res1["avisos_fefo"]) == 1

    salidas = db.get_salidas_pdf_movimientos(mes="OCTUBRE", ano=2026)
    s1 = next(s for s in salidas if s["folio_pedido"] == "N-TEST-001")
    print(f"Salida 1 Lote asignado: '{s1['lote_asignado']}' (Esperado: 'LOTE-TARDE-2027')")
    print(f"Salida 1 Estado: '{s1['estado_validacion']}'")
    print(f"Salida 1 Aviso FEFO: '{s1['aviso_fefo']}'")
    assert s1["lote_asignado"] == "LOTE-TARDE-2027", "ERROR: No respetó el lote exacto del PDF!"
    assert "AVISO FEFO" in s1["aviso_fefo"], "ERROR: No generó el aviso FEFO!"
    assert "LOTE-PRONTO-2026" in s1["aviso_fefo"], "ERROR: No mencionó el lote de almacén con caducidad más próxima!"
    assert s1["estado_validacion"] == "AVISO_FEFO"
    print(">>> CASO 1 EXITOSO: Respetó lote del PDF y emitió alerta FEFO.")

    # 4. Caso 2: El PDF surte LOTE-PRONTO-2026
    # Debe respetarse LOTE-PRONTO-2026 y marcar FEFO_OPTIMO
    items_pdf_caso2 = [
        {
            "pedido": "N-TEST-002",
            "folio_salida": "99002",
            "fecha": "2026-10-15",
            "dia": 15,
            "clave": "010.000.FEFO.01",
            "descripcion": "MEDICAMENTO TEST PARA AUDITORIA FEFO",
            "cantidad": 30.0,
            "lote": "LOTE-PRONTO-2026",
            "caducidad": "2026-11-15",
            "localidad": "CENTRO DE SALUD TONALA"
        }
    ]
    res2 = db.process_salidas_pdf_items(items_pdf_caso2, "hoja_entrega_caso2.pdf", mes="OCTUBRE", ano=2026)
    print("\n--- CASO 2: PDF con lote óptimo (vence más pronto) ---")
    print("Resultado:", res2)
    assert res2["total_fefo_optimo"] == 1

    salidas2 = db.get_salidas_pdf_movimientos(mes="OCTUBRE", ano=2026)
    s2 = next(s for s in salidas2 if s["folio_pedido"] == "N-TEST-002")
    print(f"Salida 2 Lote asignado: '{s2['lote_asignado']}' (Esperado: 'LOTE-PRONTO-2026')")
    print(f"Salida 2 Estado: '{s2['estado_validacion']}'")
    print(f"Salida 2 Aviso FEFO: '{s2['aviso_fefo']}'")
    assert s2["lote_asignado"] == "LOTE-PRONTO-2026"
    assert "Cumple FEFO" in s2["aviso_fefo"]
    assert s2["estado_validacion"] == "FEFO_OPTIMO"
    print(">>> CASO 2 EXITOSO: Respetó lote del PDF y validó cumplimiento FEFO.")

    # 5. Caso 3: Verificar Reporte Diario (Matriz)
    print("\n--- CASO 3: Verificación en Matriz Consolidada ---")
    matriz = db.get_reporte_movimientos_matriz(mes="OCTUBRE", ano=2026, search="010.000.FEFO.01")
    items_matriz = matriz["items"]
    print(f"Filas encontradas en matriz para la clave: {len(items_matriz)}")
    assert len(items_matriz) == 2, f"Se esperaban 2 filas (una por lote), encontradas: {len(items_matriz)}"
    
    fila_tarde = next(f for f in items_matriz if f["lote"] == "LOTE-TARDE-2027")
    fila_pronto = next(f for f in items_matriz if f["lote"] == "LOTE-PRONTO-2026")
    
    # Verificar salidas en días 14 y 15
    print(f"LOTE-TARDE-2027: Día 14 = {fila_tarde['dias']['14']} (Esperado: 50.0), Total Surtido = {fila_tarde['total_surtido']}, Aviso: '{fila_tarde.get('aviso_fefo')}'")
    print(f"LOTE-PRONTO-2026: Día 15 = {fila_pronto['dias']['15']} (Esperado: 30.0), Total Surtido = {fila_pronto['total_surtido']}")
    assert fila_tarde["dias"]["14"] == 50.0
    assert fila_pronto["dias"]["15"] == 30.0
    assert "AVISO FEFO" in fila_tarde.get("aviso_fefo", "")
    print(">>> CASO 3 EXITOSO: Ambos lotes se reflejan con sus salidas exactas en la matriz.")

    # 6. Caso 4: Verificación en Exportación Excel
    print("\n--- CASO 4: Verificación en Exportación Excel ---")
    excel_stream = db.export_reporte_movimientos_excel(mes="OCTUBRE", ano=2026)
    wb = openpyxl.load_workbook(excel_stream)
    assert "Salidas PDF" in wb.sheetnames
    ws3 = wb["Salidas PDF"]
    headers = [ws3.cell(1, col).value for col in range(1, ws3.max_column + 1)]
    print(f"Cabeceras de 'Salidas PDF': {headers}")
    assert "AVISO REGLA FEFO" in headers, "ERROR: La columna AVISO REGLA FEFO no está en la hoja de Excel!"
    
    col_idx = headers.index("AVISO REGLA FEFO") + 1
    # Buscar fila con caso 1
    fefo_aviso_encontrado = False
    for r in range(2, ws3.max_row + 1):
        cell_val = ws3.cell(r, col_idx).value or ""
        if "AVISO FEFO" in cell_val:
            fefo_aviso_encontrado = True
            print(f"Fila {r} Excel tiene Aviso FEFO: '{cell_val}'")
            # Verificar color de fondo
            fill_color = ws3.cell(r, col_idx).fill.start_color.rgb
            print(f"Color de relleno de celda: {fill_color}")
            break
            
    assert fefo_aviso_encontrado, "ERROR: No se encontró el aviso FEFO en los datos de Excel!"
    print(">>> CASO 4 EXITOSO: Columna 'AVISO REGLA FEFO' verificada con éxito en Excel.")

    # Limpieza de registros de prueba
    db.delete_entrada_mov(ent_a.id)
    db.delete_entrada_mov(ent_b.id)
    db.clear_salidas_pdf_mov(mes="OCTUBRE", ano=2026)
    print("\n=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE ===")

if __name__ == "__main__":
    test_fefo_pdf_rules()
