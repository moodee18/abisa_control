import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(4068, min(4068+250, len(lines))):
    print(f"{i+1}: {lines[i]}", end="")

