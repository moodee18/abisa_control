import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("DELETE FROM movimientos_entradas_salidas WHERE tipo IN ('ENTRADAS', 'SALIDAS')")
conn.commit()
print('Remaining records by report_source and tipo:')
c.execute('SELECT report_source, tipo, count(*), sum(cantidad) FROM movimientos_entradas_salidas GROUP BY report_source, tipo')
for r in c.fetchall():
    print(r)
conn.close()
