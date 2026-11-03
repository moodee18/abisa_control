import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
endpoints = re.findall(r'@app\.get\(["\']/api/control-movimientos/[^"\']*["\']\)\s*def\s+[^(]+\([^)]*\)', text)
for ep in endpoints:
    print(ep)

