with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add models
models_target = 'class IniciarMesRequest(BaseModel):'
models_code = '''class PedidoItemUpdateRequest(BaseModel):
    id: Optional[int] = None
    clave: str
    descripcion: Optional[str] = ""
    cantidad: float = 0.0
    lote_asignado: Optional[str] = ""
    lote: Optional[str] = ""
    fecha_caducidad: Optional[str] = ""

class PedidoCompletoUpdateRequest(BaseModel):
    folio_actual: str
    archivo_actual: Optional[str] = ""
    mes_actual: Optional[str] = "OCTUBRE"
    ano_actual: Optional[int] = 2026
    nuevo_folio: Optional[str] = None
    nueva_fecha: Optional[str] = None
    nuevo_dia: Optional[int] = None
    nuevo_mes: Optional[str] = None
    nuevo_ano: Optional[int] = None
    nuevo_archivo: Optional[str] = None
    items: Optional[List[PedidoItemUpdateRequest]] = None

'''

assert models_target in content, "models_target not found in app.py"
content = content.replace(models_target, models_code + models_target, 1)

# 2. Add endpoints after clear_control_salidas_pdf
ep_target = '''@app.post("/api/control-movimientos/salidas-pdf/clear")
async def clear_control_salidas_pdf(
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        count = db.clear_salidas_pdf_mov(mes=mes, ano=ano)
        period_str = f" del periodo {mes} {ano}" if mes else " de todos los periodos"
        return {"status": "success", "message": f"Se eliminaron {count} salidas PDF{period_str}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''

ep_code = '''

# --- GESTIÓN DE PEDIDOS COMPLETOS (MODIFICAR O ELIMINAR PEDIDO ENTERO) ---
@app.get("/api/control-movimientos/pedidos")
async def get_control_pedidos(
    mes: Optional[str] = Query("OCTUBRE"),
    ano: Optional[int] = Query(2026),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        return db.get_pedidos_resumen(mes=mes, ano=ano, search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/control-movimientos/pedido")
async def get_control_pedido_detalle(
    folio: str = Query(...),
    archivo: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("ver_control_movimientos", "gestionar_control_movimientos")),
):
    try:
        detalle = db.get_pedido_detalle(folio_pedido=folio, archivo_pdf=archivo, mes=mes, ano=ano)
        if not detalle:
            raise HTTPException(status_code=404, detail=f"Pedido '{folio}' no encontrado.")
        return detalle
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/control-movimientos/pedido")
async def update_control_pedido(
    req: PedidoCompletoUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.update_pedido_completo(req.dict())
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/control-movimientos/pedido")
async def delete_control_pedido(
    folio: str = Query(...),
    archivo: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(require_any_permission("gestionar_control_movimientos")),
):
    try:
        return db.delete_pedido_completo(folio_pedido=folio, archivo_pdf=archivo, mes=mes, ano=ano)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''

assert ep_target in content, "ep_target not found in app.py"
content = content.replace(ep_target, ep_target + ep_code, 1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added pedido endpoints to app.py successfully!")

