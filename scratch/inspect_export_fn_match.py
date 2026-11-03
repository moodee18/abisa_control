with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
fn_match = re.search(r'(function exportControlMovimientosExcel\(\)\s*\{[^}]+\})', content)
if fn_match:
    print("Found exportControlMovimientosExcel match:")
    print(fn_match.group(1))

