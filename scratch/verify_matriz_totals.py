import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import DatabaseManager

db = DatabaseManager()
matriz = db.get_reporte_movimientos_matriz(mes="OCTUBRE", ano=2026)

kpis = matriz.get("kpis", {})
print("=== KPIS OBTENIDOS DE LA MATRIZ CONSOLIDADA ===")
for k, v in kpis.items():
    if isinstance(v, float):
        print(f"  {k}: {v:,.2f}")
    else:
        print(f"  {k}: {v}")

items = matriz.get("items", [])
print(f"\nTotal registros en matriz: {len(items)}")

# Comparar con Excel original:
# Total Inventario Mensual esperado: 987,343.00
# Total Surtido esperado: 76,527.00
# Total Inventario Disponible esperado: 910,816.00
tot_inv_mensual = kpis.get("total_inventario_mensual", 0.0)
tot_surtido = kpis.get("total_surtido_mensual", 0.0)
tot_disp = kpis.get("total_inventario_disponible", 0.0)

print(f"\nComparativa con Excel Original:")
print(f"  Inventario Total Mensual: {tot_inv_mensual:,.2f} (Esperado: 987,343.00) -> Diferencia: {tot_inv_mensual - 987343:.2f}")
print(f"  Total Surtido:            {tot_surtido:,.2f} (Esperado: 76,527.00)  -> Diferencia: {tot_surtido - 76527:.2f}")
print(f"  Inventario Disponible:    {tot_disp:,.2f} (Esperado: 910,816.00) -> Diferencia: {tot_disp - 910816:.2f}")

assert abs(tot_inv_mensual - 987343.0) < 0.01, "Discrepancia en Inventario Total Mensual"
assert abs(tot_surtido - 76527.0) < 0.01, "Discrepancia en Total Surtido"
assert abs(tot_disp - 910816.0) < 0.01, "Discrepancia en Inventario Disponible"
print("\n>>> ¡VERIFICACIÓN MATEMÁTICA 100% PERFECTA Y EXACTA!")
