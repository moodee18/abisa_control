with open('scratch/seguimiento_inventario_full.js', encoding='utf-8') as f:
    txt = f.read()

idx = txt.find('function cambio_pagina(')
if idx != -1:
    print('=== CAMBIO_PAGINA FULL ===')
    print(txt[idx:idx+2500])

