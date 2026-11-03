import sys

with open("database.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """        # Si no tiene una fecha de entrada o ajuste registrada en el sistema, no debe aparecer en la hoja Entradas
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
        )"""

replacement = """        # Si no tiene una fecha de entrada o ajuste registrada en el sistema, no debe aparecer en la hoja Entradas
        raw_filtered = [
            e for e in raw_entradas
            if str(e.get("fecha_entrada") or "").strip() or str(e.get("fecha_ajuste") or "").strip()
        ]

        def _normalize_date_for_sort(d_str: str) -> str:
            d_str = str(d_str or "").strip()
            if not d_str:
                return "9999-99-99"
            m = re.match(r"^(\\d{2})/(\\d{2})/(\\d{4})", d_str)
            if m:
                return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
            m2 = re.match(r"^(\\d{4})-(\\d{2})-(\\d{2})", d_str)
            if m2:
                return f"{m2.group(1)}-{m2.group(2)}-{m2.group(3)}"
            return d_str

        # Desglosar dinámicamente si cualquier registro contuviera múltiples fechas separadas por espacios
        expanded_entradas = []
        for e in raw_filtered:
            f_ent = str(e.get("fecha_entrada") or "").strip()
            f_aju = str(e.get("fecha_ajuste") or "").strip()
            dates_ent = re.findall(r"\\b\\d{2,4}[/-]\\d{2}[/-]\\d{2,4}\\b", f_ent)
            dates_aju = re.findall(r"\\b\\d{2,4}[/-]\\d{2}[/-]\\d{2,4}\\b", f_aju)

            if len(dates_ent) > 1:
                qty_tot = float(e.get("cantidad_recibida", 0.0) or 0.0)
                split_qty = round(qty_tot / len(dates_ent), 2)
                for d in dates_ent:
                    ec = dict(e)
                    ec["fecha_entrada"] = _normalize_date_for_sort(d)
                    ec["cantidad_recibida"] = split_qty
                    expanded_entradas.append(ec)
            elif len(dates_aju) > 1:
                qty_tot = float(e.get("entrada_por_ajuste") if e.get("entrada_por_ajuste") is not None else (e.get("entrada_ajuste", 0.0) or 0.0))
                split_qty = round(qty_tot / len(dates_aju), 2)
                for d in dates_aju:
                    ec = dict(e)
                    ec["fecha_ajuste"] = _normalize_date_for_sort(d)
                    ec["entrada_ajuste"] = split_qty
                    ec["entrada_por_ajuste"] = split_qty
                    expanded_entradas.append(ec)
            else:
                expanded_entradas.append(e)

        entradas_data = expanded_entradas
        entradas_data.sort(
            key=lambda x: (
                _normalize_date_for_sort(x.get("fecha_entrada") or x.get("fecha_ajuste") or ""),
                x.get("row_index") if x.get("row_index") else 999999,
                x.get("id") or 0
            )
        )"""

# Handle both CRLF and LF
if target in content:
    content = content.replace(target, replacement, 1)
    print("Replaced with LF match")
elif target.replace("\n", "\r\n") in content:
    content = content.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"), 1)
    print("Replaced with CRLF match")
else:
    print("Target not found directly, checking snippet...")
    idx = content.find("Si no tiene una fecha de entrada")
    print("Snippet near target:", repr(content[idx:idx+200]))
    sys.exit(1)

with open("database.py", "w", encoding="utf-8") as f:
    f.write(content)

print("database.py updated successfully!")

