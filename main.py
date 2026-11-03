import argparse
import sys
import shutil
import webbrowser
import threading
import time
from pathlib import Path
import pandas as pd
from tabulate import tabulate

import config
from database import DatabaseManager
from processor import DataProcessor

def process_all_downloads(move_after_process: bool = True):
    """Lee todos los archivos en la carpeta de descargas, los procesa y los guarda en la base de datos."""
    db = DatabaseManager()
    download_dir = config.DOWNLOAD_DIR
    processed_dir = config.PROCESSED_DIR

    files = [
        f for f in download_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in [".csv", ".xlsx", ".xls", ".json", ".pdf"]
        and not f.name.startswith("test_") and not f.name.startswith("test-")
    ]

    if not files:
        print(f"[INFO] No se encontraron archivos nuevos para procesar en: {download_dir}")
        return

    print(f"\n[PROCESADOR] Se encontraron {len(files)} archivo(s) para procesar.")

    results = []
    for file_path in files:
        print(f"\n--> Procesando: {file_path.name}...")
        try:
            # 1. Detectar si es archivo de Entradas y Salidas de SIIA
            is_ent_sal = False
            if file_path.suffix.lower() in [".xlsx", ".xls"]:
                if any(w in file_path.name.lower() for w in ["entrada", "salida"]):
                    is_ent_sal = True
                else:
                    try:
                        import openpyxl
                        clean_buf = DataProcessor.get_clean_excel_file(file_path)
                        wb = openpyxl.load_workbook(clean_buf, read_only=True)
                        s_lower = [s.lower() for s in wb.sheetnames]
                        wb.close()
                        if any("entrada" in s or "salida" in s for s in s_lower):
                            is_ent_sal = True
                    except Exception:
                        pass

            if is_ent_sal:
                res = DataProcessor.read_entradas_salidas_excel(file_path)
                df_ent = res.get("entradas", pd.DataFrame())
                df_sal = res.get("salidas", pd.DataFrame())
                c_ent = db.insert_movimientos(df_ent, "ENTRADA", file_path.name) if not df_ent.empty else 0
                c_sal = db.insert_movimientos(df_sal, "SALIDA", file_path.name) if not df_sal.empty else 0
                total_c = c_ent + c_sal
                print(f"    [ÉXITO] Archivo de Entradas y Salidas: {c_ent} entradas, {c_sal} salidas importadas.")
                results.append((file_path.name, "Excel (Entradas/Salidas)", total_c, f"{c_ent} ent, {c_sal} sal"))

            # 2. Detectar si es PDF de Hoja de Entrega de Pedido
            elif file_path.suffix.lower() == ".pdf":
                doc_info, items = DataProcessor.read_hoja_pedido_pdf(file_path)
                if items:
                    df_pdf = pd.DataFrame(items)
                    c = db.insert_movimientos(df_pdf, "SALIDA", file_path.name)
                    print(f"    [ÉXITO] Hoja de Pedido {doc_info.get('pedido', 'S/N')}: {c} salidas registradas.")
                    results.append((file_path.name, "PDF (Pedido)", c, f"Pedido {doc_info.get('pedido', '')}"))
                else:
                    print(f"    [INFO] PDF sin partidas de pedido detectadas.")
                    results.append((file_path.name, "PDF", 0, "Sin partidas"))

            # 3. Reporte estándar de Inventario por Lotes / Catálogo
            else:
                df, file_type = DataProcessor.process_file(file_path)
                if df.empty:
                    print(f"    [ADVERTENCIA] El archivo {file_path.name} no contiene registros o no se pudieron extraer tablas.")
                    db.log_execution("IMPORT", "WARNING", file_name=file_path.name, records_count=0, details="Archivo vacío o sin tablas")
                    results.append((file_path.name, file_type, 0, "Vacío / Sin datos"))
                    continue

                # Insertar en base de datos de inventario
                inserted = db.insert_dataframe(df, source_filename=file_path.name)
                print(f"    [ÉXITO] Se insertaron {inserted} filas en el inventario.")
                results.append((file_path.name, file_type, inserted, "Completado"))

            # Mover archivo procesado para evitar duplicados en la siguiente ejecución
            if move_after_process:
                dest = processed_dir / file_path.name
                shutil.move(str(file_path), str(dest))
                print(f"    [INFO] Archivo archivado en: {dest}")

        except Exception as e:
            print(f"    [ERROR] Falló el procesamiento de {file_path.name}: {e}")
            db.log_execution("IMPORT", "FAILED", file_name=file_path.name, records_count=0, details=str(e))
            results.append((file_path.name, "N/A", 0, f"Error: {e}"))

    print("\n" + "="*70)
    print(" RESUMEN DE PROCESAMIENTO ETL")
    print("="*70)
    try:
        print(tabulate(results, headers=["Archivo", "Tipo", "Registros", "Estado"], tablefmt="grid"))
    except UnicodeEncodeError:
        safe_results = [[str(cell).encode('ascii', 'replace').decode('ascii') for cell in row] for row in results]
        print(tabulate(safe_results, headers=["Archivo", "Tipo", "Registros", "Estado"], tablefmt="grid"))

def show_db_summary():
    """Muestra el estado actual y KPIs de la base de datos."""
    db = DatabaseManager()
    kpis = db.get_inventory_kpis()
    summary = db.get_summary()

    print("\n" + "="*65)
    print(" ESTADO Y MÉTRICAS DEL INVENTARIO (SIIA ABISALUD)")
    print("="*65)
    print(f" Claves únicas registradas:       {kpis['total_claves']}")
    print(f" Total piezas en existencia:      {kpis['total_piezas']:,.2f}")
    print(f" Valor monetario del inventario:  ${kpis['total_valor']:,.2f} MXN")
    print(f" Total de lotes registrados:      {kpis['total_lotes']}")
    print(f" Total de registros almacenados:  {kpis['total_records']}")
    print(f" Ubicación de la BD:              {config.DATABASE_URL}")
    print("\n Registros de actividad recientes:")
    if summary["recent_logs"]:
        logs_table = [[l["created_at"], l["operation"], l["file_name"] or "-", l["status"], l["records_count"]] for l in summary["recent_logs"]]
        print(tabulate(logs_table, headers=["Fecha", "Operación", "Archivo/Fuente", "Estado", "Filas"], tablefmt="simple"))
    else:
        print(" (No hay registros de actividad aún)")
    print("="*65 + "\n")

def show_inventory_table(search: str = None):
    """Muestra el catálogo de claves y existencias en consola."""
    db = DatabaseManager()
    catalog = db.get_catalog_by_clave(search=search)

    if not catalog:
        print("\n[INFO] No hay claves registradas en el inventario.")
        return

    table_data = []
    for item in catalog:
        table_data.append([
            item["clave"],
            item["descripcion"][:40] + ("..." if len(item["descripcion"]) > 40 else ""),
            f"{item['total_existencia']:,.2f}",
            item["unidad_medida"],
            f"${item['precio_promedio']:,.2f}",
            f"${item['total_valor']:,.2f}",
            item["total_lotes_registrados"]
        ])

    print("\n" + "="*85)
    print(" CATÁLOGO DE CLAVES Y EXISTENCIAS CONSOLIDADAS")
    print("="*85)
    print(tabulate(
        table_data, 
        headers=["Clave", "Descripción", "Existencia", "U.M.", "Precio Prom.", "Importe Total", "Lotes"], 
        tablefmt="fancy_grid"
    ))
    print(f" Total: {len(catalog)} clave(s) listadas.\n")

def add_record_interactive():
    """Asistente en consola para registrar un insumo manualmente."""
    db = DatabaseManager()
    print("\n" + "="*50)
    print(" ALTA MANUAL DE INSUMO / LOTE")
    print("="*50)

    clave = input("1. Clave / Código (ej. 010.000.1234.00): ").strip()
    if not clave:
        print("[ERROR] La clave es obligatoria.")
        return

    descripcion = input("2. Descripción (ej. PARACETAMOL 500MG): ").strip()
    presentacion = input("3. Presentación (ej. CAJA C/20 TAB): ").strip()
    lote = input("4. Lote (ej. L2026A): ").strip()
    caducidad = input("5. Caducidad (ej. 2027-12-31): ").strip()

    try:
        cant_str = input("6. Cantidad [1]: ").strip()
        cantidad = float(cant_str) if cant_str else 1.0
    except ValueError:
        cantidad = 1.0

    unidad_medida = input("7. Unidad de Medida [PZA]: ").strip() or "PZA"

    try:
        precio_str = input("8. Precio Unitario [$0.00]: ").strip()
        precio_unitario = float(precio_str) if precio_str else 0.0
    except ValueError:
        precio_unitario = 0.0

    almacen_origen = input("9. Almacén (ej. ALMACEN CENTRAL): ").strip()
    proveedor = input("10. Proveedor: ").strip()

    data = {
        "clave": clave,
        "descripcion": descripcion,
        "presentacion": presentacion,
        "lote": lote,
        "caducidad": caducidad,
        "cantidad": cantidad,
        "unidad_medida": unidad_medida,
        "precio_unitario": precio_unitario,
        "importe_total": round(cantidad * precio_unitario, 2),
        "almacen_origen": almacen_origen,
        "proveedor": proveedor,
        "report_source": "CLI_MANUAL"
    }

    try:
        result = db.create_record(data)
        print(f"\n[ÉXITO] Insumo registrado con ID #{result['id']} (Clave: {result['clave']}, Cantidad: {result['cantidad']})")
    except Exception as e:
        print(f"\n[ERROR] No se pudo registrar el insumo: {e}")

def export_database(output_format: str = "excel", filename: str = "reporte_consolidado.xlsx"):
    """Exporta todos los registros consolidados de la BD a un archivo."""
    db = DatabaseManager()
    session = db.get_session()
    try:
        query = "SELECT * FROM insumos_report ORDER BY id DESC"
        df = pd.read_sql(query, con=db.engine)
        if df.empty:
            print("[INFO] No hay datos en la base de datos para exportar.")
            return

        if "raw_json" in df.columns:
            df = df.drop(columns=["raw_json"])

        out_path = config.BASE_DIR / filename
        if output_format.lower() in ["excel", "xlsx"]:
            df.to_excel(out_path, index=False)
        else:
            df.to_csv(out_path, index=False, encoding="utf-8-sig")

        print(f"[ÉXITO] Base de datos exportada ({len(df)} filas) a: {out_path}")
    finally:
        session.close()

def run_web_server():
    """Inicia el servidor web FastAPI y abre el navegador."""
    import uvicorn
    import socket

    # Obtener IP local para compartir con otros equipos de la red
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    local_url = f"http://localhost:{config.APP_PORT}"
    network_url = f"http://{local_ip}:{config.APP_PORT}"

    print("\n" + "="*65)
    print("  PANEL WEB DE INVENTARIO SIIA ABISALUD")
    print("="*65)
    print(f"  --> Acceso en este equipo:      {local_url}")
    print(f"  --> Acceso desde otros equipos: {network_url}")
    print("="*65)
    print("  Presione CTRL+C para detener el servidor.\n")

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(local_url)

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app:app", host="0.0.0.0", port=config.APP_PORT, reload=True)

def main():
    parser = argparse.ArgumentParser(description="Sistema de Inventario, Catálogo y Automatización SIIA Abisalud")
    parser.add_argument("--web", "--ui", action="store_true", help="Inicia el panel web interactivo en el navegador")
    parser.add_argument("--inventory", action="store_true", help="Muestra el catálogo de claves y stock en la consola")
    parser.add_argument("--add", action="store_true", help="Asistente interactivo en consola para agregar un nuevo insumo")
    parser.add_argument("--download", action="store_true", help="Inicia el navegador para login y descarga de reportes")
    parser.add_argument("--process", action="store_true", help="Procesa archivos existentes en downloads/ y los guarda en la BD")
    parser.add_argument("--summary", action="store_true", help="Muestra resumen y estadísticas de la base de datos")
    parser.add_argument("--export", action="store_true", help="Exporta la base de datos a un archivo consolidado Excel")
    parser.add_argument("--clear", action="store_true", help="Vacía todos los registros de la base de datos para cargar datos nuevos")
    parser.add_argument("--all", action="store_true", help="Ejecuta descarga y posterior procesamiento completo")

    args = parser.parse_args()

    # Si no se pasa ningún argumento, mostrar menú interactivo y resumen
    if not any([args.web, args.inventory, args.add, args.download, args.process, args.summary, args.export, args.clear, args.all]):
        print("\n--- Sistema de Inventario y Automatización SIIA Abisalud ---")
        print("Comandos disponibles:")
        print("  python main.py --web         (Abrir Panel Web Interactivo con Catálogo, Altas y Ediciones)")
        print("  python main.py --inventory   (Ver tabla de claves y existencias en consola)")
        print("  python main.py --add         (Agregar nuevo insumo manualmente por consola)")
        print("  python main.py --download    (Iniciar navegador RPA para descargar reportes)")
        print("  python main.py --process     (Procesar archivos CSV/Excel/PDF/JSON a la BD)")
        print("  python main.py --export      (Exportar inventario a Excel consolidado)")
        print("  python main.py --clear       (Vaciar base de datos para cargar datos nuevos)")
        print("  python main.py --summary     (Ver estadísticas generales)")
        show_db_summary()
        return

    if args.clear:
        db = DatabaseManager()
        deleted = db.clear_all_records()
        print(f"\n[ÉXITO] Base de datos vaciada. Se eliminaron {deleted} registro(s). Lista para datos nuevos.\n")
        return

    if args.web:
        run_web_server()

    if args.inventory:
        show_inventory_table()

    if args.add:
        add_record_interactive()

    if args.download or args.all:
        try:
            from downloader import SiiaDownloader
            downloader = SiiaDownloader()
            downloader.run_interactive_session()
        except ImportError as e:
            print(f"\n[ERROR] No se pudo cargar el módulo de automatización SIIA: {e}")
            print("Si Windows bloqueó el archivo (_greenlet / playwright), desactive el 'Control inteligente de aplicaciones' en Seguridad de Windows o desbloquee los archivos.\n")

    if args.process or args.all:
        process_all_downloads()

    if args.summary:
        show_db_summary()

    if args.export:
        export_database()

if __name__ == "__main__":
    main()
