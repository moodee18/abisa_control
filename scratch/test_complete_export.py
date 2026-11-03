import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from database import (
    Base, DatabaseManager, InsumoRecord, MovimientoRecord,
    CatalogoInsumoMov, ProveedorMov, UnidadMedidaMov, EntradaMov, SalidaPdfMov, ApoyoInstitucionalMov
)
from sqlalchemy import func, or_
import io
import datetime
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Test adding all these methods to a subclass and invoking them
class CompleteTestManager(DatabaseManager):
    pass

# We can dynamically bind the methods to test
mgr = CompleteTestManager()
session = mgr.get_session()
print("Catalog count:", session.query(CatalogoInsumoMov).count())
print("Entradas count:", session.query(EntradaMov).count())
session.close()
