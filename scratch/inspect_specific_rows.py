import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("SELECT DISTINCT folio_documento FROM entradas_movimientos WHERE folio_documento IS NOT NULL AND folio_documento != ''")
folios = [r[0] for r in c.fetchall()]
print(f'Total distinct folios in entradas ({len(folios)}):')
print(folios[:30])

c.execute("SELECT DISTINCT folio_pedido FROM salidas_pdf_movimientos WHERE folio_pedido IS NOT NULL AND folio_pedido != ''")
pedidos = [r[0] for r in c.fetchall()]
print(f'Total distinct folios in salidas ({len(pedidos)}):')
print(pedidos[:30])

conn.close()
