import sys
sys.path.insert(0, '.')
from database import DatabaseManager, SalidaPdfMov
from sqlalchemy import func

db = DatabaseManager('sqlite:///data/abisalud.db')

# Test reading existing pedidos in Noviembre
session = db.get_session()
items = session.query(SalidaPdfMov).filter_by(mes='NOVIEMBRE').all()
print(f"Noviembre items count: {len(items)}")
for it in items:
    print(it.folio_pedido, it.clave, it.lote_asignado, it.cantidad)
session.close()

