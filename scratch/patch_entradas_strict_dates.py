import sys

def patch():
    # 1. Update database.py
    with open("database.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Find get_entradas_movimientos
    old_fn = """    # --- ENTRADAS MANUALES ---
    def get_entradas_movimientos(
        self,
        mes: Optional[str] = None,
        ano: Optional[int] = None,
        search: Optional[str] = None,
        classify_initial: bool = False
    ) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            q = session.query(EntradaMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(EntradaMov.mes == mes.upper())
            if ano and (not mes or mes.upper() != "TODOS"):
                q = q.filter(EntradaMov.ano == ano)
            if search:
                raw_s = search.strip()
                term = f"%{raw_s.lower()}%"
                filters = [
                    func.lower(EntradaMov.clave).like(term),
                    func.lower(EntradaMov.lote).like(term),
                    func.lower(EntradaMov.descripcion).like(term),
                    func.lower(EntradaMov.proveedor).like(term),
                    func.lower(EntradaMov.folio_documento).like(term),
                    func.lower(EntradaMov.procedimiento).like(term),
                    func.lower(EntradaMov.contrato).like(term),
                    func.lower(EntradaMov.registro_sanitario).like(term),
                    func.lower(EntradaMov.fecha_caducidad).like(term),
                    func.lower(EntradaMov.fecha_fabricacion).like(term),
                    func.lower(EntradaMov.fecha_entrada).like(term),
                    func.lower(EntradaMov.fecha_ajuste).like(term),
                    func.lower(EntradaMov.fecha_apoyo).like(term),
                    func.lower(EntradaMov.unidad_medida).like(term),
                    func.lower(EntradaMov.almacen).like(term),
                    func.lower(EntradaMov.observaciones).like(term),
                ]
                if raw_s.isdigit():
                    num_val = int(raw_s)
                    filters.append(EntradaMov.id == num_val)
                    filters.append(EntradaMov.row_index == num_val)
                q = q.filter(or_(*filters))
            items = q.order_by(EntradaMov.id.desc()).all()
            if not classify_initial:
                return [it.to_dict() for it in items]

            meses_map = {
                "ENERO": "01", "FEBRERO": "02", "MARZO": "03", "ABRIL": "04",
                "MAYO": "05", "JUNIO": "06", "JULIO": "07", "AGOSTO": "08",
                "SEPTIEMBRE": "09", "OCTUBRE": "10", "NOVIEMBRE": "11", "DICIEMBRE": "12"
            }
            res = []
            for it in items:
                d = it.to_dict()
                rec = float(d.get("cantidad_recibida", 0.0) or 0.0)
                aju = float(d.get("entrada_por_ajuste") if d.get("entrada_por_ajuste") is not None else (d.get("entrada_ajuste", 0.0) or 0.0))
                ini = float(d.get("inventario_inicial", 0.0) or 0.0)
                f_ent = str(d.get("fecha_entrada") or "").strip()
                f_aju = str(d.get("fecha_ajuste") or "").strip()
                m_str = str(d.get("mes") or "OCTUBRE").strip().upper()
                a_int = d.get("ano") or 2026
                def_date = f"{a_int}-{meses_map.get(m_str, '10')}-01"
                obs = str(d.get("observaciones") or "").strip().lower()
                fol = str(d.get("orden_suministro") or d.get("folio_documento") or "").strip().lower()

                if rec > 0:
                    if not d.get("fecha_entrada"):
                        d["fecha_entrada"] = def_date
                elif aju > 0:
                    if not d.get("fecha_ajuste"):
                        d["fecha_ajuste"] = def_date
                elif ini > 0:
                    is_aj = bool(f_aju) or ("ajuste" in obs) or ("ajuste" in fol) or ("correccion" in obs)
                    if is_aj:
                        d["entrada_por_ajuste"] = ini
                        d["entrada_ajuste"] = ini
                        d["fecha_ajuste"] = f_aju or f_ent or def_date
                    else:
                        d["cantidad_recibida"] = ini
                        d["fecha_entrada"] = f_ent or def_date
                res.append(d)
            return res"""

    new_fn = """    # --- ENTRADAS MANUALES ---
    def get_entradas_movimientos(
        self,
        mes: Optional[str] = None,
        ano: Optional[int] = None,
        search: Optional[str] = None,
        only_ingresos: bool = False
    ) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            q = session.query(EntradaMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(EntradaMov.mes == mes.upper())
            if ano and (not mes or mes.upper() != "TODOS"):
                q = q.filter(EntradaMov.ano == ano)
            if only_ingresos:
                # Sólo lo que realmente entró con fecha de entrada o ajuste registrada en el sistema
                q = q.filter(
                    or_(
                        and_(EntradaMov.fecha_entrada != None, EntradaMov.fecha_entrada != ""),
                        and_(EntradaMov.fecha_ajuste != None, EntradaMov.fecha_ajuste != ""),
                        EntradaMov.cantidad_recibida > 0,
                        EntradaMov.entrada_ajuste > 0
                    )
                )
            if search:
                raw_s = search.strip()
                term = f"%{raw_s.lower()}%"
                filters = [
                    func.lower(EntradaMov.clave).like(term),
                    func.lower(EntradaMov.lote).like(term),
                    func.lower(EntradaMov.descripcion).like(term),
                    func.lower(EntradaMov.proveedor).like(term),
                    func.lower(EntradaMov.folio_documento).like(term),
                    func.lower(EntradaMov.procedimiento).like(term),
                    func.lower(EntradaMov.contrato).like(term),
                    func.lower(EntradaMov.registro_sanitario).like(term),
                    func.lower(EntradaMov.fecha_caducidad).like(term),
                    func.lower(EntradaMov.fecha_fabricacion).like(term),
                    func.lower(EntradaMov.fecha_entrada).like(term),
                    func.lower(EntradaMov.fecha_ajuste).like(term),
                    func.lower(EntradaMov.fecha_apoyo).like(term),
                    func.lower(EntradaMov.unidad_medida).like(term),
                    func.lower(EntradaMov.almacen).like(term),
                    func.lower(EntradaMov.observaciones).like(term),
                ]
                if raw_s.isdigit():
                    num_val = int(raw_s)
                    filters.append(EntradaMov.id == num_val)
                    filters.append(EntradaMov.row_index == num_val)
                q = q.filter(or_(*filters))
            items = q.order_by(EntradaMov.id.desc()).all()
            return [it.to_dict() for it in items]"""

    content_norm = content.replace("\r\n", "\n")
    old_fn_norm = old_fn.replace("\r\n", "\n")
    new_fn_norm = new_fn.replace("\r\n", "\n")

    if old_fn_norm in content_norm:
        content_norm = content_norm.replace(old_fn_norm, new_fn_norm, 1)
        print("Updated get_entradas_movimientos in database.py")
    else:
        print("ERROR: old_fn_norm not found")

    # Update export_reporte_movimientos_excel Hoja 2
    old_export_h2 = """        # ----------------------------------------------------
        # HOJA 2: Entradas (Histórico Completo con Clasificación de Ingresos)
        # ----------------------------------------------------
        ws2 = wb.create_sheet(title="Entradas")
        entradas_data = sorted(
            self.get_entradas_movimientos(mes="TODOS", ano=None),
            key=lambda x: (
                x.get("ano") or 2026,
                ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"].index(str(x.get("mes", "OCTUBRE")).upper()) if str(x.get("mes", "OCTUBRE")).upper() in ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"] else 99,
                x.get("row_index") if x.get("row_index") else 999999,
                x.get("id") or 0
            )
        )
        ent_headers = [
            "PROCEDIMIENTO",
            "CONTRATO",
            "ORDEN DE SUMINISTRO/INSTITUCION",
            "REGISTRO SANITARIO",
            "PROVEEDOR",
            "DESCRIPCION",
            "CLAVE",
            "LOTE",
            "UNIDAD DE MEDIDA",
            "FECHA DE AJUSTE",
            "ENTRADA POR AJUSTE",
            "FECHA DE ENTRADA",
            "CANTIDAD RECIBIDA",
            "INVENTARIO ",
            "INVENTARIO TOTAL MENSUAL",
            "APOYO INSTITUCIONAL",
            "FECHA DE CADUCIDAD",
            "FECHA DE FABRICACION",
            "APOYO INSTITUCIONAL / FECHA",
        ]
        ws2.row_dimensions[1].height = 27.2
        for idx, h in enumerate(ent_headers, 1):
            c = ws2.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        meses_map = {
            "ENERO": "01", "FEBRERO": "02", "MARZO": "03", "ABRIL": "04",
            "MAYO": "05", "JUNIO": "06", "JULIO": "07", "AGOSTO": "08",
            "SEPTIEMBRE": "09", "OCTUBRE": "10", "NOVIEMBRE": "11", "DICIEMBRE": "12"
        }

        for r_idx, e in enumerate(entradas_data, 2):
            e_rec = float(e.get("cantidad_recibida", 0.0) or 0.0)
            e_aju = float(e.get("entrada_por_ajuste") if e.get("entrada_por_ajuste") is not None else (e.get("entrada_ajuste", 0.0) or 0.0))
            e_ini = float(e.get("inventario_inicial", 0.0) or 0.0)

            f_ent = str(e.get("fecha_entrada") or "").strip()
            f_aju = str(e.get("fecha_ajuste") or "").strip()
            obs = str(e.get("observaciones") or "").strip().lower()
            folio = str(e.get("orden_suministro") or e.get("folio_documento") or "").strip().lower()
            mes_row = str(e.get("mes") or "OCTUBRE").strip().upper()
            ano_row = e.get("ano") or 2026
            mes_num = meses_map.get(mes_row, "10")
            default_period_date = f"{ano_row}-{mes_num}-01"

            # Clasificación de ingreso para auditoría y trazabilidad
            val_f_aju = ""
            val_c_aju = None
            val_f_ent = ""
            val_c_rec = None
            val_c_ini = None

            if e_rec > 0:
                val_f_ent = f_ent or default_period_date
                val_c_rec = e_rec
                if e_aju > 0:
                    val_f_aju = f_aju or default_period_date
                    val_c_aju = e_aju
                if e_ini > 0:
                    val_c_ini = e_ini
            elif e_aju > 0:
                val_f_aju = f_aju or default_period_date
                val_c_aju = e_aju
                if e_ini > 0:
                    val_c_ini = e_ini
            elif e_ini > 0:
                # Traslados / Saldos Iniciales / Cargas de Inicio
                is_ajuste = bool(f_aju) or ("ajuste" in obs) or ("ajuste" in folio) or ("correccion" in obs)
                if is_ajuste:
                    val_f_aju = f_aju or f_ent or default_period_date
                    val_c_aju = e_ini
                    val_c_ini = None
                else:
                    val_f_ent = f_ent or default_period_date
                    val_c_rec = e_ini
                    val_c_ini = None
            else:
                val_c_ini = 0.0

            ws2.cell(r_idx, 1, e.get("procedimiento") or e.get("no_procedimiento", ""))
            ws2.cell(r_idx, 2, e.get("contrato") or e.get("no_contrato", ""))
            ws2.cell(r_idx, 3, e.get("orden_suministro") or e.get("folio_documento", ""))
            ws2.cell(r_idx, 4, e.get("registro_sanitario", ""))
            ws2.cell(r_idx, 5, e.get("proveedor", ""))
            ws2.cell(r_idx, 6, e.get("descripcion", ""))
            ws2.cell(r_idx, 7, e.get("clave", ""))
            ws2.cell(r_idx, 8, e.get("lote", ""))
            ws2.cell(r_idx, 9, e.get("unidad_medida", "PZA"))

            # Columnas J, K, L, M, N, O
            ws2.cell(r_idx, 10, val_f_aju)
            ws2.cell(r_idx, 11, val_c_aju if val_c_aju is not None else None).number_format = "#,##0"
            ws2.cell(r_idx, 12, val_f_ent)
            ws2.cell(r_idx, 13, val_c_rec if val_c_rec is not None else None).number_format = "#,##0"
            ws2.cell(r_idx, 14, val_c_ini if val_c_ini is not None else None).number_format = "#,##0"
            ws2.cell(r_idx, 15, f"=M{r_idx}+N{r_idx}+K{r_idx}").number_format = "#,##0"

            e_apo = float(e.get("apoyo_institucional", 0.0) or 0.0)
            ws2.cell(r_idx, 16, e_apo if e_apo != 0.0 else None).number_format = "#,##0"
            ws2.cell(r_idx, 17, e.get("fecha_caducidad", ""))
            ws2.cell(r_idx, 18, e.get("fecha_fabricacion", ""))
            ws2.cell(r_idx, 19, e.get("fecha_apoyo", "") or e.get("observaciones", ""))

            for c in range(1, 20):
                cell = ws2.cell(r_idx, c)
                cell.font = data_font
                cell.border = data_border

        ent_widths = [25.4, 14.6, 23.1, 23.1, 31.9, 29.6, 12.9, 15.3, 17.0, 10.3, 10.0, 13.0, 13.0, 10.0, 12.3, 11.5, 13.7, 13.7, 25.3]
        for idx, w in enumerate(ent_widths, 1):
            ws2.column_dimensions[get_column_letter(idx)].width = w"""

    new_export_h2 = """        # ----------------------------------------------------
        # HOJA 2: Entradas (SOLAMENTE LO QUE ENTRÓ CON FECHA REGISTRADA)
        # ----------------------------------------------------
        ws2 = wb.create_sheet(title="Entradas")
        raw_entradas = self.get_entradas_movimientos(mes="TODOS", ano=None, only_ingresos=True)
        # Si no tiene una fecha de entrada o ajuste registrada en el sistema, no debe aparecer en la hoja Entradas
        entradas_data = [
            e for e in raw_entradas
            if str(e.get("fecha_entrada") or "").strip() or str(e.get("fecha_ajuste") or "").strip()
        ]
        entradas_data.sort(
            key=lambda x: (
                x.get("fecha_entrada") or x.get("fecha_ajuste") or "",
                x.get("row_index") if x.get("row_index") else 999999,
                x.get("id") or 0
            )
        )
        ent_headers = [
            "PROCEDIMIENTO",
            "CONTRATO",
            "ORDEN DE SUMINISTRO/INSTITUCION",
            "REGISTRO SANITARIO",
            "PROVEEDOR",
            "DESCRIPCION",
            "CLAVE",
            "LOTE",
            "UNIDAD DE MEDIDA",
            "FECHA DE AJUSTE",
            "ENTRADA POR AJUSTE",
            "FECHA DE ENTRADA",
            "CANTIDAD RECIBIDA",
            "INVENTARIO ",
            "INVENTARIO TOTAL MENSUAL",
            "APOYO INSTITUCIONAL",
            "FECHA DE CADUCIDAD",
            "FECHA DE FABRICACION",
            "APOYO INSTITUCIONAL / FECHA",
        ]
        ws2.row_dimensions[1].height = 27.2
        for idx, h in enumerate(ent_headers, 1):
            c = ws2.cell(1, idx, h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        for r_idx, e in enumerate(entradas_data, 2):
            f_ent = str(e.get("fecha_entrada") or "").strip()
            f_aju = str(e.get("fecha_ajuste") or "").strip()
            e_rec = float(e.get("cantidad_recibida", 0.0) or 0.0)
            e_aju = float(e.get("entrada_por_ajuste") if e.get("entrada_por_ajuste") is not None else (e.get("entrada_ajuste", 0.0) or 0.0))

            val_f_ent = f_ent if f_ent else ""
            val_c_rec = e_rec if e_rec > 0 else (float(e.get("inventario_inicial", 0.0) or 0.0) if float(e.get("inventario_inicial", 0.0) or 0.0) > 0 and f_ent else None)

            val_f_aju = f_aju if f_aju else ""
            val_c_aju = e_aju if e_aju > 0 else (float(e.get("inventario_inicial", 0.0) or 0.0) if float(e.get("inventario_inicial", 0.0) or 0.0) > 0 and f_aju and not f_ent else None)

            ws2.cell(r_idx, 1, e.get("procedimiento") or e.get("no_procedimiento", ""))
            ws2.cell(r_idx, 2, e.get("contrato") or e.get("no_contrato", ""))
            ws2.cell(r_idx, 3, e.get("orden_suministro") or e.get("folio_documento", ""))
            ws2.cell(r_idx, 4, e.get("registro_sanitario", ""))
            ws2.cell(r_idx, 5, e.get("proveedor", ""))
            ws2.cell(r_idx, 6, e.get("descripcion", ""))
            ws2.cell(r_idx, 7, e.get("clave", ""))
            ws2.cell(r_idx, 8, e.get("lote", ""))
            ws2.cell(r_idx, 9, e.get("unidad_medida", "PZA"))

            # Columnas J, K, L, M, N, O
            ws2.cell(r_idx, 10, val_f_aju)
            ws2.cell(r_idx, 11, val_c_aju if val_c_aju is not None else None).number_format = "#,##0"
            ws2.cell(r_idx, 12, val_f_ent)
            ws2.cell(r_idx, 13, val_c_rec if val_c_rec is not None else None).number_format = "#,##0"
            ws2.cell(r_idx, 14, None).number_format = "#,##0"
            ws2.cell(r_idx, 15, f"=M{r_idx}+N{r_idx}+K{r_idx}").number_format = "#,##0"

            e_apo = float(e.get("apoyo_institucional", 0.0) or 0.0)
            ws2.cell(r_idx, 16, e_apo if e_apo != 0.0 else None).number_format = "#,##0"
            ws2.cell(r_idx, 17, e.get("fecha_caducidad", ""))
            ws2.cell(r_idx, 18, e.get("fecha_fabricacion", ""))
            ws2.cell(r_idx, 19, e.get("fecha_apoyo", "") or e.get("observaciones", ""))

            for c in range(1, 20):
                cell = ws2.cell(r_idx, c)
                cell.font = data_font
                cell.border = data_border

        # Fila de Totales en Hoja 2 Entradas
        last_ent_row = len(entradas_data) + 1 if len(entradas_data) > 0 else 1
        tot_ent_row = last_ent_row + 1
        ws2.row_dimensions[tot_ent_row].height = 22
        ws2.cell(tot_ent_row, 1, "TOTALES GENERALES").alignment = Alignment(horizontal="center")
        for col_idx in range(2, 10):
            ws2.cell(tot_ent_row, col_idx, "").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 10, "").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 11, f"=SUM(K2:K{last_ent_row})").number_format = "#,##0"
        ws2.cell(tot_ent_row, 12, "").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 13, f"=SUM(M2:M{last_ent_row})").number_format = "#,##0"
        ws2.cell(tot_ent_row, 14, "-").alignment = Alignment(horizontal="center")
        ws2.cell(tot_ent_row, 15, f"=SUM(O2:O{last_ent_row})").number_format = "#,##0"
        ws2.cell(tot_ent_row, 16, f"=SUM(P2:P{last_ent_row})").number_format = "#,##0"
        for col_idx in range(17, 20):
            ws2.cell(tot_ent_row, col_idx, "-").alignment = Alignment(horizontal="center")

        tot_ent_fill = PatternFill(start_color="E2F0D9", end_color="E2F0D9", fill_type="solid")
        tot_ent_font = Font(name="Aptos Narrow", size=10, bold=True, color="1E7145")
        tot_ent_border = Border(
            left=Side(style="thin", color="1E7145"),
            right=Side(style="thin", color="1E7145"),
            top=Side(style="thin", color="1E7145"),
            bottom=Side(style="double", color="1E7145")
        )
        for col in range(1, 20):
            c_tot = ws2.cell(tot_ent_row, col)
            c_tot.fill = tot_ent_fill
            c_tot.font = tot_ent_font
            c_tot.border = tot_ent_border

        ent_widths = [25.4, 14.6, 23.1, 23.1, 31.9, 29.6, 12.9, 15.3, 17.0, 10.3, 10.0, 13.0, 13.0, 10.0, 12.3, 11.5, 13.7, 13.7, 25.3]
        for idx, w in enumerate(ent_widths, 1):
            ws2.column_dimensions[get_column_letter(idx)].width = w"""

    old_export_norm = old_export_h2.replace("\r\n", "\n")
    new_export_norm = new_export_h2.replace("\r\n", "\n")

    if old_export_norm in content_norm:
        content_norm = content_norm.replace(old_export_norm, new_export_norm, 1)
        print("Updated export_reporte_movimientos_excel Hoja 2 in database.py")
    else:
        print("ERROR: old_export_norm not found")

    with open("database.py", "w", encoding="utf-8") as f:
        f.write(content_norm)

    # 2. Update app.py get_control_entradas route
    with open("app.py", "r", encoding="utf-8") as f:
        app_content = f.read()
    app_norm = app_content.replace("\r\n", "\n")

    old_app_ent = """@app.get("/api/control-movimientos/entradas")
async def get_control_entradas(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_entradas_movimientos(mes=mes, ano=target_ano, search=search, classify_initial=True)"""

    new_app_ent = """@app.get("/api/control-movimientos/entradas")
async def get_control_entradas(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    only_ingresos: Optional[bool] = Query(True),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_entradas_movimientos(mes=mes, ano=target_ano, search=search, only_ingresos=only_ingresos)"""

    if old_app_ent in app_norm:
        app_norm = app_norm.replace(old_app_ent, new_app_ent, 1)
        print("Updated app.py get_control_entradas")
    else:
        print("ERROR: old_app_ent not found in app.py")

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_norm)

    # 3. Update templates/index.html loadCtrlModificarRecords to pass only_ingresos=false
    with open("templates/index.html", "r", encoding="utf-8") as f:
        tpl_content = f.read()
    tpl_norm = tpl_content.replace("\r\n", "\n")

    old_mod_fetch = "fetch(`/api/control-movimientos/entradas?${periodQs}`)"
    new_mod_fetch = "fetch(`/api/control-movimientos/entradas?${periodQs}&only_ingresos=false`)"

    if old_mod_fetch in tpl_norm:
        tpl_norm = tpl_norm.replace(old_mod_fetch, new_mod_fetch, 1)
        print("Updated templates/index.html loadCtrlModificarRecords fetch")

    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(tpl_norm)

if __name__ == "__main__":
    patch()

