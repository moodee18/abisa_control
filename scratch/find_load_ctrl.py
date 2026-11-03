with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'function loadControlMovimientos' in l:
        print(f"Found loadControlMovimientos at line {i+1}")
        for j in range(i, min(i+60, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")
        break

