import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def get_entradas_movimientos' in l:
        print(f"Found get_entradas_movimientos at line {i+1}")
        for j in range(i, min(i+60, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")
        break

