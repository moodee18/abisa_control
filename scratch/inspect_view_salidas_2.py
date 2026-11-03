import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="ctrlViewSalidas"')
if idx != -1:
    print(text[idx+3600:idx+5500])
