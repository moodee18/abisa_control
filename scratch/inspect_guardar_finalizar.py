with open('scratch/seguimiento_inventario_full.js', encoding='utf-8') as f:
    txt = f.read()

idx = txt.find('function guardar_finalizar')
if idx != -1:
    print('=== GUARDAR_FINALIZAR FULL ===')
    print(txt[idx:idx+2000])

