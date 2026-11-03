import sys
sys.path.insert(0, '.')
from database import DatabaseManager, SalidaPdfMov
from collections import defaultdict

db = DatabaseManager('sqlite:///data/abisalud.db')
session = db.get_session()

# Test grouping for NOVIEMBRE
q = session.query(SalidaPdfMov).filter(SalidaPdfMov.mes == 'NOVIEMBRE', SalidaPdfMov.ano == 2026)
nov_items = q.all()
print(f"Noviembre items: {len(nov_items)}")
for it in nov_items:
    print(f"  ID={it.id}, Clave={it.clave}, Lote={it.lote_asignado}, Cant={it.cantidad}, Folio={it.folio_pedido}, Archivo={it.archivo_pdf}")

# Test grouping for OCTUBRE
q_oct = session.query(SalidaPdfMov).filter(SalidaPdfMov.mes == 'OCTUBRE', SalidaPdfMov.ano == 2026)
oct_items = q_oct.all()
print(f"Octubre items: {len(oct_items)}")
pedidos_oct = defaultdict(list)
for it in oct_items:
    key = (it.folio_pedido or "SIN_FOLIO", it.archivo_pdf or "SIN_ARCHIVO")
    pedidos_oct[key].append(it)

print(f"Octubre distinct pedidos: {len(pedidos_oct)}")
for (fol, arch), items in sorted(pedidos_oct.items(), key=lambda x: len(x[1])):
    print(f"  Pedido: {fol} | Archivo: {arch} | Partidas: {len(items)} | Total Piezas: {sum(i.cantidad for i in items)}")

session.close()

