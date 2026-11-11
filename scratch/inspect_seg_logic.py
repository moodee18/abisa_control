with open('scratch/seguimiento_inventario_full.js', encoding='utf-8') as f:
    txt = f.read()

idx = txt.find('jQuery("#almacen").live("change"')
if idx != -1:
    print('=== ALMACEN CHANGE ===')
    print(txt[idx:idx+1200])

idx_final = txt.find('finalizado')
while idx_final != -1:
    print('=== FINALIZADO OCCURRENCE ===')
    print(txt[max(0, idx_final-100):min(len(txt), idx_final+250)])
    idx_final = txt.find('finalizado', idx_final+1)

