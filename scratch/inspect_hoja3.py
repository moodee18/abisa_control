import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(4415, 4475):
    print(f"{i+1}: {lines[i]}", end="")

