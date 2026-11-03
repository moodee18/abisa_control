import sys
sys.path.insert(0, '.')
from database import DatabaseManager

db = DatabaseManager('sqlite:///data/abisalud.db')

# 1. Test get_pedidos_resumen for Noviembre
pedidos_nov = db.get_pedidos_resumen(mes='NOVIEMBRE', ano=2026)
print(f"Pedidos en Noviembre: {len(pedidos_nov)}")
for p in pedidos_nov:
    print(p)

# 2. Test get_pedido_detalle
detalle = db.get_pedido_detalle(folio_pedido='N-197283', mes='NOVIEMBRE', ano=2026)
print("Detalle N-197283:")
print("  Folio:", detalle.get('folio_pedido'))
print("  Partidas:", detalle.get('total_partidas'))
print("  Piezas:", detalle.get('total_piezas'))
print("  Items count:", len(detalle.get('items', [])))

# 3. Test get_pedidos_resumen for Octubre
pedidos_oct = db.get_pedidos_resumen(mes='OCTUBRE', ano=2026)
print(f"Pedidos en Octubre: {len(pedidos_oct)}")
for p in pedidos_oct[:5]:
    print(" ", p.get('folio_pedido'), p.get('archivo_pdf'), p.get('dia'), p.get('total_partidas'), p.get('total_piezas'))

