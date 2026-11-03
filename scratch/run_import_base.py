import os
import sys
import openpyxl
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import DatabaseManager, normalize_caducidad, CatalogoInsumoMov, ProveedorMov, UnidadMedidaMov, EntradaMov, SalidaPdfMov, ApoyoInstitucionalMov

db = DatabaseManager()

def import_base_excel(file_path='data/INVETARIO_SIMPLIFICADO_OCT.xlsx', target_mes='OCTUBRE', target_ano=2026):
    print(f"Cargando {file_path}...")
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb['OCT'] if 'OCT' in wb.sheetnames else wb.active

    session = db.get_session()
    try:
        # Detectar columnas de días (fila 3)
        day_cols = {}
        for c in range(11, 30):
            val_header = str(ws.cell(3, c).value or '').strip()
            if val_header:
                try:
                    d_int = int(val_header)
                    day_cols[c] = d_int
                except:
                    pass
        print(f"Días detectados: {sorted(list(day_cols.values()))}")

        # Limpiar datos previos de este periodo para una importación limpia
        session.query(EntradaMov).filter(EntradaMov.mes == target_mes, EntradaMov.ano == target_ano).delete()
        session.query(SalidaPdfMov).filter(SalidaPdfMov.mes == target_mes, SalidaPdfMov.ano == target_ano).delete()
        session.query(ApoyoInstitucionalMov).filter(ApoyoInstitucionalMov.mes == target_mes, ApoyoInstitucionalMov.ano == target_ano).delete()
        session.commit()
        print("Periodo OCTUBRE 2026 limpiado.")

        # Primera pasada: Recolectar datos y ordenar lotes por clave para FEFO
        rows_data = []
        lotes_por_clave = {}
        unique_claves = {}
        unique_provs = set()
        unique_udms = set()

        for r in range(4, ws.max_row + 1):
            cve_val = ws.cell(r, 4).value
            if cve_val is None or not str(cve_val).strip():
                continue
            cve = str(cve_val).strip()
            lote = str(ws.cell(r, 5).value or '').strip()
            desc = str(ws.cell(r, 3).value or '').strip()
            prov = str(ws.cell(r, 2).value or '').strip()
            udm = str(ws.cell(r, 6).value or 'PZA').strip().upper()
            orden = str(ws.cell(r, 1).value or '').strip()
            
            # Caducidad
            cad_raw = ws.cell(r, 33).value
            if isinstance(cad_raw, (datetime.datetime, datetime.date)):
                cad_str = cad_raw.strftime("%Y-%m-%d")
            else:
                cad_str = str(cad_raw or '').strip()
                if cad_str.endswith("00:00:00"):
                    cad_str = cad_str.replace("00:00:00", "").strip()
            cad_norm = normalize_caducidad(cad_str)

            try:
                inv_ini = float(ws.cell(r, 9).value or 0.0)
            except:
                inv_ini = 0.0
            try:
                ajuste = float(ws.cell(r, 7).value or 0.0)
            except:
                ajuste = 0.0
            try:
                recibida = float(ws.cell(r, 8).value or 0.0)
            except:
                recibida = 0.0
            try:
                apoyo = float(ws.cell(r, 30).value or 0.0)
            except:
                apoyo = 0.0

            col34 = str(ws.cell(r, 34).value or '').strip()

            # Salidas diarias en este registro
            salidas_fila = {}
            for col_idx, dia_num in day_cols.items():
                v = ws.cell(r, col_idx).value
                try:
                    fv = float(v or 0.0)
                    if fv > 0:
                        salidas_fila[dia_num] = fv
                except:
                    pass

            row_obj = {
                "orden": orden,
                "prov": prov,
                "desc": desc,
                "cve": cve,
                "lote": lote,
                "udm": udm,
                "inv_ini": inv_ini,
                "ajuste": ajuste,
                "recibida": recibida,
                "cad_str": cad_str,
                "cad_norm": cad_norm,
                "apoyo": apoyo,
                "col34": col34,
                "salidas": salidas_fila
            }
            rows_data.append(row_obj)

            # Catálogos
            if cve not in unique_claves:
                unique_claves[cve] = {"desc": desc, "udm": udm, "prov": prov}
            if prov:
                unique_provs.add(prov)
            if udm:
                unique_udms.add(udm)

            if cve not in lotes_por_clave:
                lotes_por_clave[cve] = []
            lotes_por_clave[cve].append({
                "lote": lote,
                "cad_str": cad_str,
                "cad_norm": cad_norm,
                "stock": inv_ini + ajuste + recibida
            })

        # Ordenar lotes de cada clave por caducidad (FEFO)
        for cve in lotes_por_clave:
            lotes_por_clave[cve].sort(key=lambda x: x["cad_norm"])

        print(f"Total filas procesadas: {len(rows_data)}")
        print(f"Catálogos: {len(unique_claves)} claves, {len(unique_provs)} proveedores, {len(unique_udms)} UDMs.")

        # 1. Guardar / Actualizar Catálogos
        for cve, info in unique_claves.items():
            cat = session.query(CatalogoInsumoMov).filter_by(clave=cve).first()
            if not cat:
                cat = CatalogoInsumoMov(
                    clave=cve,
                    descripcion=info["desc"],
                    unidad_medida=info["udm"],
                    proveedor_predeterminado=info["prov"]
                )
                session.add(cat)
            else:
                if not cat.descripcion and info["desc"]:
                    cat.descripcion = info["desc"]
                if not cat.proveedor_predeterminado and info["prov"]:
                    cat.proveedor_predeterminado = info["prov"]

        for p_name in unique_provs:
            prov = session.query(ProveedorMov).filter_by(nombre=p_name).first()
            if not prov:
                session.add(ProveedorMov(nombre=p_name))

        for u_name in unique_udms:
            udm_rec = session.query(UnidadMedidaMov).filter_by(clave_unidad=u_name).first()
            if not udm_rec:
                session.add(UnidadMedidaMov(clave_unidad=u_name))

        session.commit()
        print("Catálogos guardados.")

        # 2. Guardar Entradas, Salidas y Apoyos
        total_entradas = 0
        total_salidas = 0
        total_apoyos = 0
        total_fefo_alertas = 0

        for it in rows_data:
            # Entrada
            entrada_rec = EntradaMov(
                folio_documento=it["orden"],
                procedimiento="",
                contrato="",
                registro_sanitario="",
                almacen="CS ALMACEN 2022",
                proveedor=it["prov"],
                clave=it["cve"],
                lote=it["lote"],
                descripcion=it["desc"],
                unidad_medida=it["udm"],
                fecha_entrada=f"{target_ano}-10-01",
                fecha_caducidad=it["cad_str"],
                inventario_inicial=it["inv_ini"],
                entrada_ajuste=it["ajuste"],
                cantidad_recibida=it["recibida"],
                mes=target_mes,
                ano=target_ano,
                observaciones="Importado de INVETARIO SIMPLIFICADO OCT.xlsx"
            )
            session.add(entrada_rec)
            total_entradas += 1

            # Salidas diarias
            cve_candidates = lotes_por_clave.get(it["cve"], [])
            fefo_candidate = cve_candidates[0] if len(cve_candidates) > 0 else None

            for dia_num, cant in it["salidas"].items():
                # Auditar Regla FEFO para este lote
                if fefo_candidate and fefo_candidate["lote"].upper() != it["lote"].upper() and fefo_candidate["cad_norm"] < it["cad_norm"]:
                    aviso_fefo = f"⚠️ AVISO FEFO: Se dio salida al lote '{it['lote']}' (cad: {it['cad_str'] or 'S/F'}), pero en almacén existe el lote '{fefo_candidate['lote']}' con caducidad más próxima ({fefo_candidate['cad_str']})."
                    estado_val = "AVISO_FEFO"
                    total_fefo_alertas += 1
                else:
                    aviso_fefo = f"✅ Cumple FEFO: El lote '{it['lote']}' es el de caducidad más próxima ({it['cad_str']})."
                    estado_val = "FEFO_OPTIMO"

                salida_rec = SalidaPdfMov(
                    archivo_pdf="INVETARIO SIMPLIFICADO OCT.xlsx",
                    folio_pedido=it["orden"] or f"SALIDA-DIA-{dia_num:02d}",
                    fecha=f"{target_ano}-10-{dia_num:02d}",
                    dia=dia_num,
                    mes=target_mes,
                    ano=target_ano,
                    clave=it["cve"],
                    descripcion=it["desc"],
                    cantidad=cant,
                    lote_asignado=it["lote"],
                    fecha_caducidad=it["cad_str"],
                    cliente_destino="DISPENSARIO / FARMACIA",
                    estado_validacion=estado_val,
                    aviso_fefo=aviso_fefo,
                    observaciones=f"Salida día {dia_num} importada de base Excel"
                )
                session.add(salida_rec)
                total_salidas += 1

            # Apoyos Institucionales
            if it["apoyo"] > 0:
                fecha_apoyo = it["col34"] or f"{target_ano}-10-15"
                # Extraer día si viene fecha
                dia_apoyo = 15
                if "16" in fecha_apoyo:
                    dia_apoyo = 16
                elif "08" in fecha_apoyo:
                    dia_apoyo = 8
                elif "06" in fecha_apoyo:
                    dia_apoyo = 6
                elif "05" in fecha_apoyo:
                    dia_apoyo = 5

                apoyo_rec = ApoyoInstitucionalMov(
                    clave=it["cve"],
                    lote=it["lote"],
                    descripcion=it["desc"],
                    cantidad=it["apoyo"],
                    institucion="SECRETARIA DE SALUD / OTRA INSTITUCION",
                    fecha=fecha_apoyo,
                    dia=dia_apoyo,
                    mes=target_mes,
                    ano=target_ano,
                    folio_documento=it["orden"],
                    observaciones=f"Apoyo importado. Fechas registradas: {it['col34']}"
                )
                session.add(apoyo_rec)
                total_apoyos += 1

        session.commit()
        print("\n=== IMPORTACIÓN COMPLETADA CON ÉXITO ===")
        print(f"Total Entradas importadas: {total_entradas}")
        print(f"Total Salidas registradas: {total_salidas} (Alertas FEFO detectadas: {total_fefo_alertas})")
        print(f"Total Apoyos Institucionales: {total_apoyos}")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    import_base_excel()
