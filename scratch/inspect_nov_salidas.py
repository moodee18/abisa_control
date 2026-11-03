import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT folio_pedido, archivo_pdf, COUNT(*), SUM(cantidad) FROM salidas_pdf_movimientos WHERE mes='NOVIEMBRE' GROUP BY folio_pedido, archivo_pdf")
for r in c.fetchall():
    print(r)

