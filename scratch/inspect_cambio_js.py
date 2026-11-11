with open('scratch/seguimiento_inventario_full.js', encoding='utf-8') as f:
    txt = f.read()

idx = 0
while True:
    idx = txt.find('.cells[10]', idx)
    if idx == -1:
        break
    print('=== CELLS[10] ===')
    print(txt[max(0, idx-100):min(len(txt), idx+200)])
    idx += 10

idx = 0
while True:
    idx = txt.find('id="cambio"', idx)
    if idx == -1:
        break
    print('=== ID CAMBIO ===')
    print(txt[max(0, idx-100):min(len(txt), idx+200)])
    idx += 11

