import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for j in range(7450, 7500):
    if j < len(lines):
        print(f"{j+1}: {lines[j]}", end="")

