import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(10030, 10090):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")

