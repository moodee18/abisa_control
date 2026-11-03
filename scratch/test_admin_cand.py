import sys
sys.path.insert(0, '.')
from database import verify_password
import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT password_hash FROM usuarios_sistema WHERE username='admin'")
h = c.fetchone()[0]

candidates = ['admin', 'admin123', 'admin2026', 'abisalud', 'abisalud2026', '123456', '1234', 'superadmin', 'superadmin123', 'admin@abisalud', 'password', 'Admin123', 'Admin123*', 'admin123!']
for cand in candidates:
    if verify_password(cand, h):
        print("MATCH FOUND FOR ADMIN:", cand)
        break
else:
    print("No match among candidates")

