import sys

def patch_all():
    # 1. Update database.py line 3151
    with open("database.py", "r", encoding="utf-8") as f:
        db_content = f.read()

    old_ped_filter = """            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.upper())
            if ano:
                q = q.filter(SalidaPdfMov.ano == int(ano))"""
    new_ped_filter = """            if mes and mes.upper() != "TODOS":
                q = q.filter(SalidaPdfMov.mes == mes.upper())
            if ano and (not mes or mes.upper() != "TODOS"):
                q = q.filter(SalidaPdfMov.ano == int(ano))"""

    db_norm = db_content.replace("\r\n", "\n")
    if old_ped_filter in db_norm:
        db_norm = db_norm.replace(old_ped_filter, new_ped_filter, 1)
        with open("database.py", "w", encoding="utf-8") as f:
            f.write(db_norm)
        print("Updated database.py get_pedidos_resumen filter")
    else:
        print("Notice: old_ped_filter already updated or not found")

    # 2. Update app.py routes
    with open("app.py", "r", encoding="utf-8") as f:
        app_content = f.read()
    app_norm = app_content.replace("\r\n", "\n")

    # entradas route
    old_ent_route = """@app.get("/api/control-movimientos/entradas")
async def get_control_entradas(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_entradas_movimientos(mes=mes, ano=ano, search=search)"""

    new_ent_route = """@app.get("/api/control-movimientos/entradas")
async def get_control_entradas(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_entradas_movimientos(mes=mes, ano=target_ano, search=search, classify_initial=True)"""

    if old_ent_route in app_norm:
        app_norm = app_norm.replace(old_ent_route, new_ent_route, 1)
        print("Updated app.py get_control_entradas")

    # salidas route
    old_sal_route = """@app.get("/api/control-movimientos/salidas-pdf")
async def get_control_salidas_pdf(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_salidas_pdf_movimientos(mes=mes, ano=ano, search=search)"""

    new_sal_route = """@app.get("/api/control-movimientos/salidas-pdf")
async def get_control_salidas_pdf(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_salidas_pdf_movimientos(mes=mes, ano=target_ano, search=search)"""

    if old_sal_route in app_norm:
        app_norm = app_norm.replace(old_sal_route, new_sal_route, 1)
        print("Updated app.py get_control_salidas_pdf")

    # pedidos route
    old_ped_route = """@app.get("/api/control-movimientos/pedidos")
async def get_control_pedidos(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_pedidos_resumen(mes=mes, ano=ano, search=search)"""

    new_ped_route = """@app.get("/api/control-movimientos/pedidos")
async def get_control_pedidos(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_pedidos_resumen(mes=mes, ano=target_ano, search=search)"""

    if old_ped_route in app_norm:
        app_norm = app_norm.replace(old_ped_route, new_ped_route, 1)
        print("Updated app.py get_control_pedidos")

    # apoyos route
    old_apo_route = """@app.get("/api/control-movimientos/apoyo-institucional")
async def get_control_apoyos(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_apoyos_institucionales(mes=mes, ano=ano, search=search)"""

    new_apo_route = """@app.get("/api/control-movimientos/apoyo-institucional")
async def get_control_apoyos(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        target_ano = None if (mes and mes.upper() == "TODOS") else ano
        return db.get_apoyos_institucionales(mes=mes, ano=target_ano, search=search)"""

    if old_apo_route in app_norm:
        app_norm = app_norm.replace(old_apo_route, new_apo_route, 1)
        print("Updated app.py get_control_apoyos")

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_norm)

    # 3. Update templates/index.html dropdown
    with open("templates/index.html", "r", encoding="utf-8") as f:
        tpl_content = f.read()
    tpl_norm = tpl_content.replace("\r\n", "\n")

    old_select = """                        <select id="ctrlMonthSelect" class="form-control" style="width: auto; padding: 0.4rem 0.65rem; font-size: 0.82rem; font-weight: 600;" onchange="loadControlMovimientos()">
                            <option value="ENERO">Enero</option>"""
    new_select = """                        <select id="ctrlMonthSelect" class="form-control" style="width: auto; padding: 0.4rem 0.65rem; font-size: 0.82rem; font-weight: 600;" onchange="loadControlMovimientos()">
                            <option value="TODOS">Todos los Meses (Histórico)</option>
                            <option value="ENERO">Enero</option>"""

    if old_select in tpl_norm:
        tpl_norm = tpl_norm.replace(old_select, new_select, 1)
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(tpl_norm)
        print("Updated templates/index.html ctrlMonthSelect")
    else:
        print("Notice: old_select already updated or not found")

if __name__ == "__main__":
    patch_all()

