import re

with open('templates/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

ctrl_start = text.find('id="tab-control-movimientos"')
ctrl_end = text.find('<!-- Modal 1:', ctrl_start)
ctrl_html = text[ctrl_start:ctrl_end]

buttons = re.findall(r'<button[^>]*>.*?</button>', ctrl_html, re.DOTALL)
print(f"Total buttons in tab-control-movimientos: {len(buttons)}\n")
for i, b in enumerate(buttons):
    b_clean = ' '.join(b.split())
    # find onclick
    onclick = re.search(r'onclick="([^"]+)"', b)
    oc_val = onclick.group(1) if onclick else "NO ONCLICK"
    # find text
    text_content = re.sub(r'<[^>]+>', '', b).strip()
    print(f"[{i+1}] Text: '{text_content}' | Onclick: {oc_val}")
