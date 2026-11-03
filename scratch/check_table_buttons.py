import re

with open('templates/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

funcs = ['renderControlEntradasTable', 'renderControlApoyosTable', 'renderControlCatalogosTable', 'renderControlSalidasPdfTable']
for fn in funcs:
    idx = text.find('function ' + fn)
    if idx != -1:
        print(f'=== {fn} ===')
        snippet = text[idx:idx+2000]
        # find buttons inside snippet
        btns = re.findall(r'<button[^>]*>.*?</button>', snippet)
        for b in btns:
            print("  BTN:", b.replace('\n', ' '))
