with open("database.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """        # HOJA 4: Apoyo Institucional (Histórico Completo)
        # ----------------------------------------------------
        ws4 = wb.create_sheet(title="Apoyo Institucional")
        apoyos_data = sorted(
            self.get_apoyos_institucionales(mes="TODOS", ano=None),
            key=lambda x: (x.get("fecha", ""), x.get("id") or 0)
        )
        apoyo_headers = [
            "FOLIO / OFICIO", "FECHA", "DÍA MES", "INSTITUCIÓN RECEPTORA",
            "CLAVE", "LOTE", "DESCRIPCIóN", "CANTIDAD DONADA / ENTREGADA", "OBSERVACIONES"
        ]
        ws4.row_dimensions[1].height = 24
        for idx, h in enumerate(apoyo_headers, 1):
            c = ws4.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        for r_idx, a in enumerate(apoyos_data, 2):
            ws4.cell(r_idx, 1, a.get("folio_documento", ""))
            ws4.cell(r_idx, 2, a.get("fecha", ""))
            ws4.cell(r_idx, 3, int(a.get("dia", 1)))
            ws4.cell(r_idx, 4, a.get("institucion", ""))
            ws4.cell(r_idx, 5, a.get("clave", ""))
            ws4.cell(r_idx, 6, a.get("lote", ""))
            ws4.cell(r_idx, 7, a.get("descripcion", ""))
            ws4.cell(r_idx, 8, float(a.get("cantidad", 0.0))).number_format = "#,##0"
            ws4.cell(r_idx, 9, a.get("observaciones", ""))

            for c in range(1, 10):
                cell = ws4.cell(r_idx, c)
                cell.font = data_font
                cell.border = data_border

        for col in range(1, 10):
            ws4.column_dimensions[get_column_letter(col)].width = 18"""

replacement = """        # HOJA 4: Apoyo Institucional (Histórico Completo)
        # ----------------------------------------------------
        ws4 = wb.create_sheet(title="Apoyo Institucional")
        raw_apoyos = self.get_apoyos_institucionales(mes="TODOS", ano=None)

        # Desglosar dinámicamente si cualquier fila contuviera múltiples fechas separadas por espacios
        expanded_apoyos = []
        for a in raw_apoyos:
            f_apo = str(a.get("fecha") or "").strip()
            dates_apo = re.findall(r"\\b\\d{2,4}[/-]\\d{2}[/-]\\d{2,4}\\b", f_apo)
            if len(dates_apo) > 1:
                tot_qty = float(a.get("cantidad", 0.0) or 0.0)
                split_qty = round(tot_qty / len(dates_apo), 2)
                for d in dates_apo:
                    ac = dict(a)
                    norm_d = _normalize_date_for_sort(d)
                    ac["fecha"] = norm_d
                    try:
                        ac["dia"] = int(norm_d.split("-")[2])
                    except Exception:
                        pass
                    ac["cantidad"] = split_qty
                    expanded_apoyos.append(ac)
            else:
                ac = dict(a)
                ac["fecha"] = _normalize_date_for_sort(f_apo)
                try:
                    ac["dia"] = int(ac["fecha"].split("-")[2])
                except Exception:
                    pass
                expanded_apoyos.append(ac)

        apoyos_data = sorted(
            expanded_apoyos,
            key=lambda x: (_normalize_date_for_sort(x.get("fecha", "")), x.get("id") or 0)
        )
        apoyo_headers = [
            "FOLIO / OFICIO", "FECHA", "DÍA MES", "INSTITUCIÓN RECEPTORA",
            "CLAVE", "LOTE", "DESCRIPCIÓN", "CANTIDAD DONADA / ENTREGADA", "OBSERVACIONES"
        ]
        ws4.row_dimensions[1].height = 24
        for idx, h in enumerate(apoyo_headers, 1):
            c = ws4.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        for r_idx, a in enumerate(apoyos_data, 2):
            ws4.cell(r_idx, 1, a.get("folio_documento", ""))
            ws4.cell(r_idx, 2, a.get("fecha", ""))
            ws4.cell(r_idx, 3, int(a.get("dia", 1)))
            ws4.cell(r_idx, 4, a.get("institucion", ""))
            ws4.cell(r_idx, 5, a.get("clave", ""))
            ws4.cell(r_idx, 6, a.get("lote", ""))
            ws4.cell(r_idx, 7, a.get("descripcion", ""))
            ws4.cell(r_idx, 8, float(a.get("cantidad", 0.0))).number_format = "#,##0"
            ws4.cell(r_idx, 9, a.get("observaciones", ""))

            for c in range(1, 10):
                cell = ws4.cell(r_idx, c)
                cell.font = data_font
                cell.border = data_border

        last_apo_row = len(apoyos_data) + 1 if len(apoyos_data) > 0 else 1
        tot_apo_row = last_apo_row + 1
        ws4.row_dimensions[tot_apo_row].height = 22
        ws4.cell(tot_apo_row, 1, "TOTALES GENERALES").alignment = Alignment(horizontal="center")
        for col_idx in range(2, 8):
            ws4.cell(tot_apo_row, col_idx, "").alignment = Alignment(horizontal="center")
        ws4.cell(tot_apo_row, 8, f"=SUM(H2:H{last_apo_row})").number_format = "#,##0"
        ws4.cell(tot_apo_row, 9, "").alignment = Alignment(horizontal="center")
        for c in range(1, 10):
            cell = ws4.cell(tot_apo_row, c)
            cell.font = Font(name="Aptos Narrow", size=9, bold=True)
            cell.border = data_border

        for col in range(1, 10):
            ws4.column_dimensions[get_column_letter(col)].width = 18"""

# Try both direct and normalized match
idx = content.find("HOJA 4: Apoyo Institucional")
end_idx = content.find("HOJA 5: Cat", idx)

if idx != -1 and end_idx != -1:
    # replace block from idx to end_idx
    old_block = content[idx:end_idx]
    # indent replacement
    content = content[:idx] + replacement.strip() + "\n\n        # ----------------------------------------------------\n        # " + content[end_idx:]
    with open("database.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched HOJA 4 in database.py!")
else:
    print("Could not find delimiters for HOJA 4 block.")

