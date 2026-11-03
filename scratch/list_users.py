import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT id, username, nombre_completo, rol, activo FROM usuarios_sistema")
for r in c.fetchall():
    print(r)
