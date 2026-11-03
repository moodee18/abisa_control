with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
btn_match = re.search(r'(<button type="button" class="btn btn-success" onclick="exportControlMovimientosExcel\(\)".*?</button>\s*)(<button type="button" class="btn" data-perm="gestionar_control_movimientos" onclick="openClearDataModal\(\'control\'\)")', content, re.DOTALL)
if btn_match:
    print("Found match:")
    print(repr(btn_match.group(1)))
    print("---")
    print(repr(btn_match.group(2)))

