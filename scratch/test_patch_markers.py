import re

# Test loading index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Check toolbar in ctrlViewSalidas
toolbar_pattern = r'<button type="button" class="btn btn-primary" data-perm="gestionar_control_movimientos" onclick="openModalControlPdf\(\)">\s*<i class="fa-solid fa-cloud-arrow-up"></i> Cargar PDFs de Salidas\s*</button>'
m_toolbar = re.search(toolbar_pattern, text)
print("Toolbar match:", bool(m_toolbar))

# 2. Check modalControlPdf end
modal_pdf_end = '<!-- Modal 4: Cat'
print("Modal pdf end match:", modal_pdf_end in text)

# 3. Check renderControlSalidasPdfTable
render_pattern = r'<td style="font-weight: 600;">\$\{s\.pedido_folio \|\| s\.folio_pedido \|\| \'-\'\}</td>'
m_render = re.search(render_pattern, text)
print("Render folio match:", bool(m_render))

