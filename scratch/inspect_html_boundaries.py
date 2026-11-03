with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<div id="tab-' in line:
        print(f'{i+1}: {line.strip()[:100]}')
    if 'id="modal' in line or 'class="modal' in line:
        print(f'{i+1}: MODAL -> {line.strip()[:100]}')
    if '<script' in line:
        print(f'{i+1}: SCRIPT -> {line.strip()[:100]}')
