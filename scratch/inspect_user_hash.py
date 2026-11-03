import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT id, username, password_hash FROM usuarios_sistema")
for r in c.fetchall():
    print(r[0], r[1], r[2][:30])

