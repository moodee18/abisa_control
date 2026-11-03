import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="ctrlViewSalidas"')
if idx != -1:
    print(text[idx:idx+2500])

