with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- ENTRADAS GET ---")
for i in range(1290, 1310):
    if i < len(lines):
        print(lines[i], end="")

print("--- APOYO-INSTITUCIONAL GET ---")
for i in range(1475, 1495):
    if i < len(lines):
        print(lines[i], end="")

