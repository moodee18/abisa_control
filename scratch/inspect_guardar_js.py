with open('scratch/seguimiento_inventario_full.js', encoding='utf-8') as f:
    txt = f.read()

idx = txt.find('function validar_guardar')
if idx != -1:
    print('=== VALIDAR_GUARDAR ===')
    print(txt[idx:idx+1200])

idx2 = txt.find('function guardar(')
if idx2 != -1:
    print('=== GUARDAR ===')
    print(txt[idx2:idx2+1200])

