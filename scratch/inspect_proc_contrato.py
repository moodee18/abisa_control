import sqlite3

conn = sqlite3.connect('data/abisalud.db')
c = conn.cursor()

print("--- catalogo_movimientos non-null procedimiento/contrato ---")
c.execute("SELECT clave, descripcion, procedimiento, contrato FROM catalogo_movimientos WHERE (procedimiento IS NOT NULL AND procedimiento != '') OR (contrato IS NOT NULL AND contrato != '') LIMIT 20")
rows = c.fetchall()
print(f"Count non-empty: {len(rows)}")
for r in rows:
    print(r)

print("\n--- insumos_report non-null no_procedimiento ---")
c.execute("SELECT clave, lote, folio_documento, no_procedimiento, fuente_adquisicion, proveedor FROM insumos_report WHERE no_procedimiento IS NOT NULL AND no_procedimiento != '' LIMIT 20")
rows2 = c.fetchall()
print(f"Count non-empty in insumos_report: {len(rows2)}")
for r in rows2:
    print(r)

print("\n--- entradas_movimientos non-null procedimiento/contrato ---")
c.execute("SELECT id, clave, lote, folio_documento, procedimiento, contrato FROM entradas_movimientos WHERE (procedimiento IS NOT NULL AND procedimiento != '') OR (contrato IS NOT NULL AND contrato != '')")
rows3 = c.fetchall()
print(f"Count in entradas_movimientos: {len(rows3)}")
for r in rows3:
    print(r)
