import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'class SalidaPdfMov' in l:
        for j in range(i, min(i+45, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")
        break

