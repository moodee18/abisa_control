import os
import sys
from pathlib import Path
import pandas as pd
import json

# Agregar raíz al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database import DatabaseManager
from processor import DataProcessor

def run_tests():
    print("=== INICIANDO PRUEBAS DE ETL Y BASE DE DATOS ===")
    
    # 1. Crear carpeta de pruebas temporales
    test_dir = BASE_DIR / "downloads"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = test_dir / "test_reporte_insumos.csv"
    excel_file = test_dir / "test_reporte_inventario.xlsx"
    json_file = test_dir / "test_reporte_movimientos.json"

    # Datos de prueba
    sample_data = [
        {
            "clave": "010.000.1234.00",
            "descripcion": "PARACETAMOL TABLETAS 500 MG",
            "presentacion": "CAJA CON 20 TABLETAS",
            "lote": "LOT2026A",
            "caducidad": "2028-12-31",
            "cantidad": 1500,
            "unidad": "PZA",
            "precio": 12.50,
            "importe": 18750.00,
            "proveedor": "LABORATORIOS EJEMPLO SA DE CV",
            "folio": "F-98231",
            "almacen": "ALMACEN CENTRAL GUADALAJARA"
        },
        {
            "clave": "010.000.5678.00",
            "descripcion": "AMOXICILINA CAPSULAS 500 MG",
            "presentacion": "FRASCO CON 12 CAPSULAS",
            "lote": "LOT2026B",
            "caducidad": "2027-06-30",
            "cantidad": 800,
            "unidad": "FCO",
            "precio": 45.00,
            "importe": 36000.00,
            "proveedor": "FARMACEUTICA NACIONAL SA",
            "folio": "F-98232",
            "almacen": "ALMACEN REGIONAL"
        }
    ]

    # Guardar CSV
    pd.DataFrame(sample_data).to_csv(csv_file, index=False, encoding="utf-8")
    print(f"[OK] Creado archivo de prueba CSV: {csv_file.name}")

    # Guardar Excel
    pd.DataFrame(sample_data).to_excel(excel_file, index=False)
    print(f"[OK] Creado archivo de prueba Excel: {excel_file.name}")

    # Guardar JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Creado archivo de prueba JSON: {json_file.name}")

    # 2. Probar Procesamiento y Base de Datos
    db = DatabaseManager()
    
    total_processed = 0
    for f in [csv_file, excel_file, json_file]:
        df, f_type = DataProcessor.process_file(f)
        assert not df.empty, f"Error: DataFrame vacío para {f.name}"
        assert len(df) == 2, f"Error: se esperaban 2 filas en {f.name}, se obtuvieron {len(df)}"
        inserted = db.insert_dataframe(df, source_filename=f.name)
        assert inserted == 2, f"Error: se esperaban 2 filas insertadas para {f.name}"
        total_processed += inserted
        print(f"[OK] {f.name} ({f_type}) procesado e insertado exitosamente ({inserted} filas).")

    # 3. Validar Resumen de la Base de Datos
    summary = db.get_summary()
    print(f"\n[RESUMEN BD] Total registros: {summary['total_records']}, Total archivos: {summary['total_source_files']}")
    assert summary["total_records"] >= total_processed, "Error en conteo total de registros en la BD."

    print("\n=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE ===")

if __name__ == "__main__":
    run_tests()
