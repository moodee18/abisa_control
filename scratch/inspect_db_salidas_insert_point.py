with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(3055, 3095):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")

