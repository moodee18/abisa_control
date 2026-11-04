import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import pandas as pd
import json
import datetime

class DataProcessor:
    """Procesador y normalizador de archivos CSV, Excel, PDF y JSON."""

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y estandariza los nombres de las columnas a minúsculas sin acentos ni espacios extra."""
        clean_cols = {}
        for col in df.columns:
            c = str(col).strip().lower()
            # Reemplazo de caracteres especiales
            c = c.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            c = c.replace("ñ", "n").replace(" ", "_").replace(".", "").replace("#", "no")
            clean_cols[col] = c
        return df.rename(columns=clean_cols)

    @classmethod
    def read_csv(cls, file_path: Path) -> pd.DataFrame:
        """Lee archivos CSV intentando diferentes delimitadores y codificaciones."""
        encodings = ["utf-8", "latin-1", "cp1252"]
        delimiters = [",", ";", "\t", "|"]

        for enc in encodings:
            for sep in delimiters:
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding=enc)
                    if len(df.columns) > 1: # Si separó correctamente en más de 1 columna
                        return cls.clean_column_names(df)
                except Exception:
                    continue
        
        # Fallback estándar
        df = pd.read_csv(file_path, encoding="latin-1")
        return cls.clean_column_names(df)

    @classmethod
    def _read_sheet_with_dynamic_header(cls, excel_file: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """Lee una hoja de cálculo buscando la fila real donde inician los encabezados."""
        df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        if df_raw.empty:
            return pd.DataFrame()

        header_idx = 0
        for i, row in df_raw.iterrows():
            row_str = ' '.join([str(val).lower() for val in row if pd.notna(val)])
            if any(k in row_str for k in ['clave', 'descripcion', 'lote', 'existencia', 'codigo', 'concepto']):
                header_idx = i
                break

        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_idx)
        df = df.dropna(how="all")
        return cls.clean_column_names(df)

    @classmethod
    def get_clean_excel_file(cls, file_path_or_buf: Any) -> Any:
        """
        Repara archivos Excel (.xlsx) generados por SIIA Abisalud (PHP)
        que contienen etiquetas de estilo con valores de color hexadecimal inválidos (ej. rgb="FFFFFFFFF"),
        haciendo que openpyxl falle con ValueError: Colors must be aRGB hex values.
        """
        import zipfile
        import io
        import re

        try:
            raw_data = None
            if isinstance(file_path_or_buf, (str, Path)):
                p = Path(file_path_or_buf)
                if not p.is_file() or p.suffix.lower() not in [".xlsx", ".xlsm"]:
                    return file_path_or_buf
                with open(p, "rb") as f:
                    raw_data = f.read()
            elif isinstance(file_path_or_buf, io.BytesIO):
                file_path_or_buf.seek(0)
                raw_data = file_path_or_buf.read()
                file_path_or_buf.seek(0)
            elif isinstance(file_path_or_buf, bytes):
                raw_data = file_path_or_buf

            if raw_data and zipfile.is_zipfile(io.BytesIO(raw_data)):
                mem_zip = io.BytesIO()
                has_repair = False
                with zipfile.ZipFile(io.BytesIO(raw_data), "r") as zin, zipfile.ZipFile(mem_zip, "w") as zout:
                    for item in zin.infolist():
                        content = zin.read(item.filename)
                        if item.filename.endswith(".xml"):
                            if b"FFFFFFFFF" in content or re.search(rb'rgb="[0-9a-fA-F]{9,}"', content):
                                has_repair = True
                                content = content.replace(b"FFFFFFFFF", b"FFFFFFFF")
                                content = re.sub(rb'rgb="([0-9a-fA-F]{8})[0-9a-fA-F]+"', rb'rgb="\1"', content)
                        zout.writestr(item, content)
                if has_repair:
                    mem_zip.seek(0)
                    return mem_zip
        except Exception as e:
            print(f"[REPAIR EXCEL] Aviso: {e}")

        return file_path_or_buf

    @classmethod
    def read_excel(cls, file_path: Path) -> pd.DataFrame:
        """Lee archivos de Excel (.xlsx, .xls) reparando XMLs defectuosos de PHP y detectando encabezados dinámicamente."""
        try:
            file_buffer = cls.get_clean_excel_file(file_path)
            excel_file = pd.ExcelFile(file_buffer, engine='openpyxl' if file_path.suffix.lower() == '.xlsx' else None)
            sheet_names = excel_file.sheet_names

            # Caso especial SIIA Abisalud: 'Existencias_x_Localidad' contiene el detalle completo de lotes.
            # No concatenar con 'Por Clave Cliente' para no duplicar existencias.
            existencias_sheet = next((s for s in sheet_names if s.strip().lower() == 'existencias_x_localidad'), None)
            if existencias_sheet:
                df_main = cls._read_sheet_with_dynamic_header(excel_file, existencias_sheet)
                df_main['hoja_origen'] = 'Existencias_x_Localidad'
                
                # Rescatar 'Unidad de Medida' de la hoja resumen 'Por Clave Cliente' si existe
                resumen_sheet = next((s for s in sheet_names if 'clave cliente' in s.strip().lower()), None)
                if resumen_sheet:
                    try:
                        df_summary = cls._read_sheet_with_dynamic_header(excel_file, resumen_sheet)
                        if 'clave_cliente' in df_summary.columns and 'unidad_de_medida' in df_summary.columns:
                            um_map = df_summary.set_index('clave_cliente')['unidad_de_medida'].dropna().to_dict()
                            if 'clave_cliente' in df_main.columns:
                                df_main['unidad_de_medida'] = df_main['clave_cliente'].map(um_map).fillna(df_main.get('presentacion_venta', 'PZA'))
                    except Exception as e_map:
                        print(f"[MAPEO UNIDAD] Aviso: {e_map}")

                return df_main

            # Flujo estándar para otros archivos de Excel
            frames = []
            for sheet in sheet_names:
                df = cls._read_sheet_with_dynamic_header(excel_file, sheet)
                if not df.empty and any(k in df.columns for k in ['clave', 'codigo', 'descripcion', 'lote']):
                    frames.append(df)

            if frames:
                return pd.concat(frames, ignore_index=True)
            elif sheet_names:
                return cls._read_sheet_with_dynamic_header(excel_file, sheet_names[0])
            return pd.DataFrame()
        except Exception as e:
            print(f"[ERROR EXCEL] No se pudo leer {file_path.name}: {e}")
            raise e

    @classmethod
    def read_json(cls, file_path: Path) -> pd.DataFrame:
        """Lee archivos JSON con estructuras de lista o diccionario."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Si tiene una clave que contiene una lista (ej. 'data', 'items', 'rows')
            for key in ["data", "items", "results", "rows", "registros"]:
                if key in data and isinstance(data[key], list):
                    df = pd.DataFrame(data[key])
                    return cls.clean_column_names(df)
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame()
        
        return cls.clean_column_names(df)

    @classmethod
    def read_pdf(cls, file_path: Path) -> pd.DataFrame:
        """Extrae tablas de un archivo PDF usando pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            print("[ADVERTENCIA] pdfplumber no está instalado. Ejecute 'pip install pdfplumber'.")
            return pd.DataFrame()

        all_rows = []
        headers = None

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    if headers is None:
                        # La primera fila se toma como encabezado
                        headers = [str(cell).strip() if cell else f"col_{i}" for i, cell in enumerate(table[0])]
                        data_rows = table[1:]
                    else:
                        data_rows = table
                    
                    for row in data_rows:
                        # Asegurar que coincida con la longitud de headers
                        if len(row) == len(headers):
                            all_rows.append(row)
                        elif len(row) < len(headers):
                            all_rows.append(row + [None] * (len(headers) - len(row)))
                        else:
                            all_rows.append(row[:len(headers)])

        if headers and all_rows:
            df = pd.DataFrame(all_rows, columns=headers)
            # Limpiar filas completamente vacías
            df.dropna(how="all", inplace=True)
            return cls.clean_column_names(df)
        
        return pd.DataFrame()

    @classmethod
    def read_entradas_salidas_excel(cls, file_path: Path) -> Dict[str, pd.DataFrame]:
        """
        Lee el archivo de Entradas y Salidas descargado del SIIA (con hojas 'Entradas' y 'Salidas')
        detectando dinámicamente las cabeceras y normalizando los campos.
        """
        import openpyxl
        clean_file = cls.get_clean_excel_file(file_path)
        wb = openpyxl.load_workbook(clean_file, data_only=True)
        results = {"entradas": pd.DataFrame(), "salidas": pd.DataFrame()}

        for sheet in wb.sheetnames:
            s_lower = sheet.lower()
            if "entrada" in s_lower:
                tipo = "entradas"
            elif "salida" in s_lower:
                tipo = "salidas"
            else:
                continue

            ws = wb[sheet]
            header_row = None
            for r in range(1, 15):
                vals = [str(ws.cell(r, c).value or "").strip() for c in range(1, ws.max_column + 1)]
                if any(v.lower() in ["clave", "clave cliente", "codigo barras"] for v in vals):
                    next_vals = [str(ws.cell(r + 1, c).value or "").strip() for c in range(1, ws.max_column + 1)]
                    if any(nv.lower() in ["clave", "clave cliente", "codigo barras"] for nv in next_vals):
                        header_row = r + 1
                    else:
                        header_row = r
                    break

            if header_row is None:
                continue

            headers = [str(ws.cell(header_row, c).value or "").strip() for c in range(1, ws.max_column + 1)]
            clean_headers = []
            for i, h in enumerate(headers):
                if not h:
                    clean_headers.append(f"col_{i}")
                else:
                    ch = h.lower().replace(" ", "_").replace(".", "").replace("/", "_").replace("(", "").replace(")", "")
                    ch = ch.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
                    clean_headers.append(ch)

            rows = []
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
                if not any(v is not None and str(v).strip() != "" for v in row_vals):
                    continue
                if str(row_vals[0]).strip().lower() == "clave":
                    continue
                rows.append(row_vals)

            df = pd.DataFrame(rows, columns=clean_headers)
            results[tipo] = df

        wb.close()
        return results

    @classmethod
    def read_hoja_pedido_pdf(cls, file_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extrae datos de 'Hoja De Entrega De Pedido' en PDF:
        - Metadatos: pedido (ej. N-197105), folio_salida, fecha_surtido, localidad.
        - Partidas: codigo_barras, clave_cliente, descripcion, c_pedida, c_surtida, lote, caducidad.
        """
        import pdfplumber
        import re

        all_items = []
        doc_info = {}

        with pdfplumber.open(file_path) as pdf:
            for p_no, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if not doc_info.get("pedido"):
                    ped_m = re.search(r'\(T\s+([A-Za-z0-9\-]+)', text) or re.search(r'\b(N-\d+)\b', text)
                    if ped_m:
                        doc_info["pedido"] = ped_m.group(1)

                if not doc_info.get("folio_salida"):
                    fol_m = re.search(r'Folio\s+de\s+Salida\s*[\r\n\:]*\s*(\d+)', text, re.IGNORECASE)
                    if fol_m:
                        doc_info["folio_salida"] = fol_m.group(1)

                if not doc_info.get("fecha_surtido"):
                    fech_m = re.search(
                        r'Fecha\s+(?:de\s+)?(?:Surtido|Salida|Entrega)\s*:\s*([0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}(?:\s+[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})?|[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{4}(?:\s+[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})?)',
                        text,
                        re.IGNORECASE
                    )
                    if not fech_m:
                        fech_m = re.search(r'el\s+d[ií]a\s+([0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}(?:\s+[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})?|[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{4})', text, re.IGNORECASE)
                    if fech_m:
                        doc_info["fecha_surtido"] = fech_m.group(1).strip()

                if not doc_info.get("localidad"):
                    loc_m = re.search(r'Localidad:\s*([^\r\n]+)', text)
                    if loc_m:
                        doc_info["localidad"] = loc_m.group(1).strip()

                lines = text.splitlines()
                # Patrón robusto para detectar inicio de partida:
                # 1. Con código de barras (6 a 18 dígitos) seguido de clave (formato CNIS con puntos o alfanumérico como HCDTF001)
                item_pattern = re.compile(r'^(\d{6,18})\s+([A-Za-z0-9\.\-_/]{3,35})\s+(.*)$')
                # 2. Sin código de barras (inicia directamente con la clave)
                item_pattern_direct = re.compile(r'^(?:([0-9]{3}\.[0-9]{3}\.[0-9]{3,5}(?:\.[0-9]{2})?)|([A-Za-z]{2,8}[0-9]{2,10}[A-Za-z0-9\-_/]*))\s+(.*)$')
                
                # Patrón para extraer cantidades, lote y caducidad al final de la línea o bloque
                tail_pattern = re.compile(
                    r'([\d,]+(?:\.\d+)?)\s+'
                    r'([\d,]+(?:\.\d+)?)(?:\s+[\d,]+(?:\.\d+)?)?\s+'
                    r'([A-Za-z0-9\-_\./]+)\s+'
                    r'(20[2-3][0-9][-/.][0-1]?[0-9][-/.][0-3]?[0-9]|[0-3]?[0-9][-/.][0-1]?[0-9][-/.](?:20)?[2-3][0-9])'
                    r'(?:\s+(.*))?$'
                )

                current = None
                in_table = False
                for line in lines:
                    l_str = line.strip()
                    if "Codigo Barras" in l_str and "Clave Cliente" in l_str:
                        in_table = True
                        continue
                    if in_table:
                        if "Observaciones:" in l_str or "Cant. Pedida:" in l_str or "PSAI-" in l_str or "Hoja " in l_str:
                            if current:
                                all_items.append(current)
                                current = None
                            break

                        m_start = item_pattern.match(l_str)
                        if m_start:
                            if current:
                                all_items.append(current)
                            current = {
                                "codigo_barras": m_start.group(1),
                                "clave_cliente": m_start.group(2).strip(),
                                "raw_parts": [m_start.group(3)]
                            }
                        else:
                            m_dir = item_pattern_direct.match(l_str)
                            if m_dir:
                                if current:
                                    all_items.append(current)
                                current = {
                                    "codigo_barras": "",
                                    "clave_cliente": (m_dir.group(1) or m_dir.group(2)).strip(),
                                    "raw_parts": [m_dir.group(3)]
                                }
                            elif current:
                                current["raw_parts"].append(l_str)

                if current:
                    all_items.append(current)

        parsed_items = []
        for it in all_items:
            combined = " ".join(it["raw_parts"])
            tm = tail_pattern.search(combined)
            if tm:
                c_pedida = float(str(tm.group(1)).replace(",", ""))
                c_surtida = float(str(tm.group(2)).replace(",", ""))
                lote = str(tm.group(3)).strip()
                raw_cad = str(tm.group(4)).strip()
                caducidad = raw_cad
                if "/" in raw_cad or (len(raw_cad.split("-")[0]) <= 2 if "-" in raw_cad else False):
                    parts = re.split(r'[-/.]', raw_cad)
                    if len(parts) == 3:
                        if len(parts[0]) == 4:
                            caducidad = f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
                        elif len(parts[2]) == 4:
                            caducidad = f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
                desc = combined[:tm.start()].strip()
                rest = tm.group(5).strip() if tm.group(5) else ""
            else:
                c_pedida = 0.0
                c_surtida = 0.0
                lote = ""
                caducidad = ""
                desc = combined
                rest = ""

            # Regla de Fecha de Salida:
            # Asignar estrictamente el día de acuerdo con la Fecha de Surtido / Salida que viene en el PDF
            fecha_doc = doc_info.get("fecha_surtido", "")
            dia = None
            if fecha_doc:
                # Formato YYYY-MM-DD o YYYY/MM/DD
                m_d = re.search(r'\b20[2-3][0-9][-/.][0-1]?[0-9][-/.]([0-3]?[0-9])\b', fecha_doc)
                if m_d:
                    dia = int(m_d.group(1))
                else:
                    # Formato DD/MM/YYYY o DD-MM-YYYY
                    m_d2 = re.search(r'\b([0-3]?[0-9])[-/.][0-1]?[0-9][-/.](?:20)?[2-3][0-9]\b', fecha_doc)
                    if m_d2:
                        dia = int(m_d2.group(1))

            if dia is None:
                dia = datetime.date.today().day

            fecha_final = fecha_doc if fecha_doc else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            parsed_items.append({
                "pedido": doc_info.get("pedido", ""),
                "documento": doc_info.get("pedido", ""),
                "folio_salida": doc_info.get("folio_salida", ""),
                "fecha": fecha_final,
                "fecha_documento": fecha_doc,
                "dia": dia,
                "codigo_barras": it["codigo_barras"],
                "clave_cliente": it["clave_cliente"],
                "clave": it["clave_cliente"],
                "descripcion": desc,
                "c_pedida": c_pedida,
                "cantidad": c_surtida,
                "c_surtida": c_surtida,
                "lote": lote,
                "caducidad": caducidad,
                "localidad": doc_info.get("localidad", ""),
                "tipo": "SALIDA"
            })

        return doc_info, parsed_items

    @classmethod
    def process_file(cls, file_path: Path) -> Tuple[pd.DataFrame, str]:
        """Identifica la extensión del archivo y lo convierte a un DataFrame estandarizado."""
        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            return cls.read_csv(file_path), "CSV"
        elif suffix in [".xlsx", ".xls"]:
            return cls.read_excel(file_path), "EXCEL"
        elif suffix == ".json":
            return cls.read_json(file_path), "JSON"
        elif suffix == ".pdf":
            return cls.read_pdf(file_path), "PDF"
        else:
            raise ValueError(f"Formato no soportado: {suffix}")

