import json
from collections import Counter
import openpyxl

# 1. Read seguimiento_almacenes.txt
seg = {}
with open('scratch/seguimiento_almacenes.txt', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or '|' not in line:
            continue
        v, n = line.split('|', 1)
        v = v.strip()
        n = n.strip()
        if v != '-1':
            seg[n.upper()] = v

# 2. Read unique almacenes from Excel
wb = openpyxl.load_workbook('data/INV_OCTUBRE_11.xlsx', data_only=True)
ws = wb['Hoja2']

almacenes_excel = set()
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[4]:
        almacenes_excel.add(str(r[4]).strip().upper())

print(f"Total almacenes in Excel: {len(almacenes_excel)}")
print(f"Total almacenes in SIIA seguimiento: {len(seg)}")

matched = {}
unmatched = []

for a in sorted(almacenes_excel):
    if a in seg:
        matched[a] = seg[a]
    else:
        # try fuzzy match
        found = None
        for s_name, s_id in seg.items():
            if a == s_name or a in s_name or s_name in a:
                found = (s_name, s_id)
                break
        if found:
            matched[a] = found[1]
            print(f"Fuzzy matched: '{a}' -> '{found[0]}' (ID: {found[1]})")
        else:
            unmatched.append(a)

print(f"\nMatched: {len(matched)} / {len(almacenes_excel)}")
if unmatched:
    print("\nUnmatched almacenes:", unmatched)

