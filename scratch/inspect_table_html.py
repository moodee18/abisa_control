with open('scratch/iframe_abastecedor.html', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="tbl_productos"')
if idx != -1:
    print(html[idx:idx+2500])

