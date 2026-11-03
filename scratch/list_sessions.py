import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT token, user_id, expires_at FROM sesiones_usuarios ORDER BY id DESC LIMIT 5")
for r in c.fetchall():
    print(r)

