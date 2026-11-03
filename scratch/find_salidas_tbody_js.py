import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 0
matches = []
while True:
    idx = text.find('ctrlSalidasTableBody', pos)
    if idx == -1:
        break
    matches.append(idx)
    pos = idx + 1

for m in matches:
    print(f"Match at {m}:")
    print(text[m-100:m+500])
    print("="*40)

