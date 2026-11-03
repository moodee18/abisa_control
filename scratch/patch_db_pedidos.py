with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

target_str = '''    def clear_salidas_pdf_mov(self, mes: Optional[str] = None, ano: Optional[int] = None) -> int:
        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == ano)
            count = q.delete()
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()'''

new_methods = '''

    def get_pedidos_resumen(
        self,
        mes: Optional[str] = None,
        ano: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Agrupa las salidas registradas en SalidaPdfMov por Pedido (folio_pedido + archivo_pdf + mes + ano).
        Retorna la lista de pedidos consolidados con el total de partidas, piezas surtidas y estado FEFO.
        """
        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == int(ano))

            items = q.order_by(SalidaPdfMov.dia.desc(), SalidaPdfMov.id.desc()).all()

            grouped = {}
            for it in items:
                f_ped = (it.folio_pedido or "").strip()
                f_arch = (it.archivo_pdf or "").strip()
                m_val = (it.mes or "").strip().upper()
                a_val = int(it.ano or 2026)

                group_key = (f_ped, f_arch, m_val, a_val)
                if group_key not in grouped:
                    grouped[group_key] = {
                        "folio_pedido": f_ped or "SIN_FOLIO",
                        "archivo_pdf": f_arch or "SIN_ARCHIVO",
                        "mes": m_val or "OCTUBRE",
                        "ano": a_val,
                        "dia": int(it.dia or 1),
                        "fecha": it.fecha or "",
                        "cliente_destino": it.cliente_destino or "",
                        "total_partidas": 0,
                        "total_piezas": 0.0,
                        "claves": set(),
                        "lotes": set(),
                        "has_fefo_alert": False,
                        "items_ids": [],
                    }

                g = grouped[group_key]
                g["total_partidas"] += 1
                g["total_piezas"] += float(it.cantidad or 0.0)
                if it.clave:
                    g["claves"].add(it.clave)
                if it.lote_asignado:
                    g["lotes"].add(it.lote_asignado)
                if it.aviso_fefo and ("AVISO FEFO" in it.aviso_fefo or "⚠️" in it.aviso_fefo):
                    g["has_fefo_alert"] = True
                g["items_ids"].append(it.id)

            res = []
            search_t = search.strip().lower() if search else None

            for g in grouped.values():
                g["total_piezas"] = round(g["total_piezas"], 2)
                g["total_claves"] = len(g["claves"])
                claves_str = ", ".join(sorted(list(g["claves"])))
                lotes_str = ", ".join(sorted(list(g["lotes"])))
                del g["claves"]
                del g["lotes"]

                if search_t:
                    match = (
                        search_t in g["folio_pedido"].lower() or
                        search_t in g["archivo_pdf"].lower() or
                        search_t in claves_str.lower() or
                        search_t in lotes_str.lower() or
                        search_t in str(g["dia"]).lower() or
                        search_t in g["fecha"].lower()
                    )
                    if not match:
                        continue

                res.append(g)

            res.sort(key=lambda x: (x.get("dia", 0), x.get("total_piezas", 0)), reverse=True)
            return res
        finally:
            session.close()

    def get_pedido_detalle(
        self,
        folio_pedido: str,
        archivo_pdf: Optional[str] = None,
        mes: Optional[str] = None,
        ano: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna la cabecera consolidada de un pedido y todas las partidas individuales que lo componen.
        """
        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            target_fol = (folio_pedido or "").strip()
            if target_fol:
                q = q.filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower())
            if archivo_pdf and archivo_pdf.strip():
                q = q.filter(func.lower(SalidaPdfMov.archivo_pdf) == archivo_pdf.strip().lower())
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.strip().upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == int(ano))

            items = q.order_by(SalidaPdfMov.id.asc()).all()
            if not items:
                if target_fol:
                    items = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower()).all()

            if not items:
                return None

            first = items[0]
            items_dicts = [it.to_dict() for it in items]

            total_piezas = round(sum(float(it.cantidad or 0.0) for it in items), 2)
            has_alert = any("AVISO FEFO" in (it.aviso_fefo or "") or "⚠️" in (it.aviso_fefo or "") for it in items)

            return {
                "folio_pedido": first.folio_pedido or "",
                "archivo_pdf": first.archivo_pdf or "",
                "fecha": first.fecha or "",
                "dia": int(first.dia or 1),
                "mes": first.mes or "OCTUBRE",
                "ano": int(first.ano or 2026),
                "cliente_destino": first.cliente_destino or "",
                "total_partidas": len(items),
                "total_piezas": total_piezas,
                "has_fefo_alert": has_alert,
                "items": items_dicts
            }
        finally:
            session.close()

    def update_pedido_completo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifica un pedido completo:
        - Actualiza campos a nivel de pedido (folio, fecha, día, mes, año, archivo) aplicándolos a todas sus partidas.
        - Actualiza cantidades, claves, lotes y caducidades de las partidas existentes.
        - Elimina partidas que hayan sido retiradas del pedido.
        - Crea nuevas partidas si se agregaron filas al pedido.
        - Recalcula auditoría FEFO y actualiza el impacto en inventario.
        """
        folio_actual = str(data.get("folio_actual") or "").strip()
        archivo_actual = str(data.get("archivo_actual") or "").strip()
        mes_actual = str(data.get("mes_actual") or "").strip().upper()
        ano_actual = int(data.get("ano_actual") or 2026)

        nuevo_folio = str(data.get("nuevo_folio") or folio_actual).strip()
        nueva_fecha = str(data.get("nueva_fecha") or "").strip()
        nuevo_dia = int(data.get("nuevo_dia") or 1)
        nuevo_mes = str(data.get("nuevo_mes") or mes_actual).strip().upper()
        nuevo_ano = int(data.get("nuevo_ano") or ano_actual)
        nuevo_archivo = str(data.get("nuevo_archivo") or archivo_actual).strip()

        if not nuevo_folio:
            raise ValueError("El folio del pedido no puede estar vacío.")

        items_input = data.get("items", [])

        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov)
            if folio_actual:
                q = q.filter(func.lower(SalidaPdfMov.folio_pedido) == folio_actual.lower())
            if archivo_actual:
                q = q.filter(func.lower(SalidaPdfMov.archivo_pdf) == archivo_actual.lower())
            if mes_actual and mes_actual != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes_actual)
            if ano_actual:
                q = q.filter(SalidaPdfMov.ano == ano_actual)

            existing_items = q.all()
            if not existing_items and folio_actual:
                existing_items = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == folio_actual.lower()).all()

            if not existing_items:
                raise ValueError(f"No se encontró el pedido '{folio_actual}' en el sistema.")

            existing_map = {it.id: it for it in existing_items}
            submitted_ids = set()

            for item_data in items_input:
                item_id = item_data.get("id")
                cve = str(item_data.get("clave") or "").strip()
                if not cve:
                    continue

                lote_val = str(item_data.get("lote_asignado") or item_data.get("lote") or "").strip()
                cant_val = float(item_data.get("cantidad") or 0.0)
                cad_val = str(item_data.get("fecha_caducidad") or item_data.get("fecha_caducidad_lote") or "").strip()
                desc_val = str(item_data.get("descripcion") or "").strip()

                if item_id and int(item_id) in existing_map:
                    it_obj = existing_map[int(item_id)]
                    submitted_ids.add(int(item_id))
                    it_obj.folio_pedido = nuevo_folio
                    if nueva_fecha:
                        it_obj.fecha = nueva_fecha
                    it_obj.dia = max(1, min(31, nuevo_dia))
                    it_obj.mes = nuevo_mes
                    it_obj.ano = nuevo_ano
                    if nuevo_archivo:
                        it_obj.archivo_pdf = nuevo_archivo
                    it_obj.clave = cve
                    it_obj.lote_asignado = lote_val
                    it_obj.cantidad = cant_val
                    it_obj.fecha_caducidad = cad_val
                    if desc_val:
                        it_obj.descripcion = desc_val
                else:
                    new_salida = SalidaPdfMov(
                        archivo_pdf=nuevo_archivo or "PEDIDO_MANUAL.pdf",
                        folio_pedido=nuevo_folio,
                        fecha=nueva_fecha or f"{nuevo_ano}-{nuevo_mes[:3]}-{nuevo_dia:02d}",
                        dia=max(1, min(31, nuevo_dia)),
                        mes=nuevo_mes,
                        ano=nuevo_ano,
                        clave=cve,
                        descripcion=desc_val,
                        cantidad=cant_val,
                        lote_asignado=lote_val,
                        fecha_caducidad=cad_val,
                        estado_validacion="VALIDADO"
                    )
                    session.add(new_salida)

            if items_input:
                for eid, eit in existing_map.items():
                    if eid not in submitted_ids:
                        session.delete(eit)
            else:
                for it_obj in existing_items:
                    it_obj.folio_pedido = nuevo_folio
                    if nueva_fecha:
                        it_obj.fecha = nueva_fecha
                    it_obj.dia = max(1, min(31, nuevo_dia))
                    it_obj.mes = nuevo_mes
                    it_obj.ano = nuevo_ano
                    if nuevo_archivo:
                        it_obj.archivo_pdf = nuevo_archivo

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        for m, a in {(mes_actual, ano_actual), (nuevo_mes, nuevo_ano)}:
            if m and a:
                try:
                    self.refresh_fefo_salidas_existentes(mes=m, ano=a)
                except Exception:
                    pass

        return {
            "success": True,
            "message": f"Pedido '{nuevo_folio}' actualizado correctamente.",
            "folio_pedido": nuevo_folio,
            "mes": nuevo_mes,
            "ano": nuevo_ano
        }

    def delete_pedido_completo(
        self,
        folio_pedido: str,
        archivo_pdf: Optional[str] = None,
        mes: Optional[str] = None,
        ano: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Elimina todas las partidas de un pedido completo.
        """
        target_fol = (folio_pedido or "").strip()
        if not target_fol:
            raise ValueError("Debe especificar el folio del pedido a eliminar.")

        session = self.get_session()
        try:
            q = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower())
            if archivo_pdf and archivo_pdf.strip():
                q = q.filter(func.lower(SalidaPdfMov.archivo_pdf) == archivo_pdf.strip().lower())
            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.strip().upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == int(ano))

            items = q.all()
            if not items:
                items = session.query(SalidaPdfMov).filter(func.lower(SalidaPdfMov.folio_pedido) == target_fol.lower()).all()

            if not items:
                raise ValueError(f"No se encontraron partidas para el pedido '{target_fol}'.")

            count = len(items)
            total_piezas = round(sum(float(it.cantidad or 0.0) for it in items), 2)
            affected_mes = items[0].mes
            affected_ano = items[0].ano

            for it in items:
                session.delete(it)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        if affected_mes and affected_ano:
            try:
                self.refresh_fefo_salidas_existentes(mes=affected_mes, ano=affected_ano)
            except Exception:
                pass

        return {
            "success": True,
            "message": f"Pedido '{target_fol}' eliminado exitosamente ({count} partidas, {total_piezas:,.0f} piezas eliminadas).",
            "folio_pedido": target_fol,
            "deleted_items": count,
            "deleted_piezas": total_piezas
        }'''

assert target_str in content, "target_str not found in database.py"
content = content.replace(target_str, target_str + new_methods, 1)

with open('database.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added pedido methods to database.py successfully!")

