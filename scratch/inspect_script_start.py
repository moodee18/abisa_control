with open('templates/index.html', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(3850, min(len(lines), 4100)):
    if '</div' in lines[i] or '<script' in lines[i] or 'id="tab-' in lines[i]:
        print(f"{i+1}: {lines[i].strip()[:100]}")

