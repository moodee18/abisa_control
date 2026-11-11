with open('scratch/seguimiento_inventario_full.js', encoding='utf-8') as f:
    txt = f.read()

idx = txt.find('function limpiar(')
if idx != -1:
    print('=== LIMPIAR FULL ===')
    print(txt[idx:idx+1000])

