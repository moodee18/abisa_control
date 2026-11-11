import openpyxl

wb = openpyxl.load_workbook('data/INV_OCTUBRE_11.xlsx', data_only=True)
ws = wb['Hoja2']

rows = []
for r in ws.iter_rows(min_row=2, values_only=True):
    if not any(r):
        continue
    cod, clave, desc, lote, alm, cant, cad = r[:7]
    if alm:
        rows.append({
            'alm': str(alm).strip().upper(),
            'lote': str(lote).strip(),
            'cod': str(cod).strip(),
            'clave': str(clave).strip(),
            'cad': str(cad).strip()[:10],
            'cant': cant
        })

print(f"Total rows: {len(rows)}")

# Check duplicates by (alm, lote)
keys_alm_lote = [(r['alm'], r['lote']) for r in rows]
print(f"Unique (alm, lote): {len(set(keys_alm_lote))} / {len(rows)}")

# Check duplicates by (alm, lote, cod)
keys_alm_lote_cod = [(r['alm'], r['lote'], r['cod']) for r in rows]
print(f"Unique (alm, lote, cod): {len(set(keys_alm_lote_cod))} / {len(rows)}")

# Check duplicates by (alm, lote, cad)
keys_alm_lote_cad = [(r['alm'], r['lote'], r['cad']) for r in rows]
print(f"Unique (alm, lote, cad): {len(set(keys_alm_lote_cad))} / {len(rows)}")

if len(set(keys_alm_lote)) != len(rows):
    from collections import Counter
    c = Counter(keys_alm_lote)
    dups = [k for k, count in c.items() if count > 1]
    print(f"Number of duplicate (alm, lote): {len(dups)}")
    for d in dups[:5]:
        matches = [r for r in rows if (r['alm'], r['lote']) == d]
        print("Dup:", d, "->", matches)

