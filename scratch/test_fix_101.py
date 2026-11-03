import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import openpyxl
import json
from database import DatabaseManager, EntradaMov

db = DatabaseManager()
session = db.get_session()

entradas = session.query(EntradaMov).filter(EntradaMov.mes == 'OCTUBRE', EntradaMov.ano == 2026).all()
print(f"Total EntradaMov in database: {len(entradas)}")

ordenes = [e for e in entradas if e.folio_documento and str(e.folio_documento).strip() and str(e.folio_documento).strip() != '-']
print(f"Total EntradaMov with folio_documento (orden): {len(ordenes)}")

print("First 5 ordenes:")
for e in ordenes[:5]:
    print(f"   ID {e.id}: {e.folio_documento} | {e.clave} | {e.lote}")

print("Last 5 ordenes:")
for e in ordenes[-5:]:
    print(f"   ID {e.id}: {e.folio_documento} | {e.clave} | {e.lote}")

session.close()
