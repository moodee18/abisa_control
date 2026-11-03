with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    l_str = line.strip()
    if 'class="tab-btn' in l_str or '<div id="tab-' in l_str or 'switchTab(' in l_str:
        print(f'{i+1}: {l_str[:120]}')
