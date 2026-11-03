with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(4220, 4325):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")

