# -*- coding: utf-8 -*-
with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('CSS in text:', '/* ESTILOS CONTROL DE INVENTARIO POR MOVIMIENTOS */' in text)
print('Toolbar button in text:', 'tab-control-movimientos' in text)
print('Tab content in text:', 'id="tab-control-movimientos"' in text)
print('Modals in text:', 'id="modalControlEntrada"' in text)
print('JS functions in text:', 'async function loadControlMovimientos' in text)
print('switchTab hook in text:', "if (tabId === 'tab-control-movimientos')" in text)
