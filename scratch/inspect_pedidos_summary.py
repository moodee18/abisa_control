import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()
c.execute("""
    SELECT mes, ano, folio_pedido, archivo_pdf, COUNT(*), SUM(cantidad), MIN(fecha)
    FROM salidas_pdf_movimientos
    GROUP BY mes, ano, folio_pedido, archivo_pdf
    ORDER BY mes, ano, id DESC
""")
print(f"{'MES':<10} {'AÑO':<6} {'FOLIO':<18} {'ARCHIVO':<25} {'ITEMS':<6} {'PIEZAS':<8} {'FECHA'}")
print("-" * 85)
for r in c.fetchall():
    print(f"{str(r[0]):<10} {str(r[1]):<6} {str(r[2]):<18} {str(r[3]):<25} {str(r[4]):<6} {str(r[5]):<8} {str(r[6])}")

