with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(7490, 7515):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")

