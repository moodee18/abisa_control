with open('scratch/seguimiento_inventario_full.js', encoding='utf-8') as f:
    txt = f.read()

idx = txt.find('if(cadena != \'\' && error == 0){')
if idx != -1:
    print('=== REST OF GUARDAR_FINALIZAR ===')
    print(txt[idx:idx+1500])

