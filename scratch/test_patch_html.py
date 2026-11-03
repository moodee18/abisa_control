with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Iniciar Nuevo Mes button
btn_old = '''                        <button type="button" class="btn btn-success" onclick="exportControlMovimientosExcel()" title="Descargar Libro de Excel con 5 bases separadas y fórmulas vivas" style="padding: 0.45rem 0.85rem; font-size: 0.82rem;">
                            <i class="fa-solid fa-file-excel"></i> Descargar Excel (5 Hojas)
                        </button>
                        <button type="button" class="btn" data-perm="gestionar_control_movimientos" onclick="openClearDataModal('control')" title="Vaciar datos del Control de Movimientos o de todo el sistema" style="padding: 0.45rem 0.85rem; font-size: 0.82rem; background: rgba(239, 68, 68, 0.12); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.25); font-weight: 600;">
                            <i class="fa-solid fa-trash-can"></i> Vaciar Datos
                        </button>'''

# Let's check how the text is encoded in the file
import re
btn_match = re.search(r'<button type="button" class="btn btn-success" onclick="exportControlMovimientosExcel\(\)".*?</button>\s*<button type="button" class="btn" data-perm="gestionar_control_movimientos" onclick="openClearDataModal\(\'control\'\)"', content, re.DOTALL)
if not btn_match:
    print("Could not find button block by regex")
else:
    print("Found button block match!")

# 2. Update loadControlEntradas
entradas_old = '''        // 5. Cargar Entradas Manuales
        async function loadControlEntradas() {
            const tbody = document.getElementById('ctrlEntradasTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="17" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando entradas...</td></tr>';

            try {
                const res = await fetch('/api/control-movimientos/entradas');'''

entradas_new = '''        // 5. Cargar Entradas Manuales
        async function loadControlEntradas() {
            const tbody = document.getElementById('ctrlEntradasTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="17" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando entradas...</td></tr>';

            const mes = document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const ano = document.getElementById('ctrlYearSelect')?.value || '2026';

            try {
                const res = await fetch(`/api/control-movimientos/entradas?mes=${encodeURIComponent(mes)}&ano=${encodeURIComponent(ano)}`);'''

# 3. Update loadControlApoyos
apoyos_old = '''        // 7. Cargar Apoyo Institucional
        async function loadControlApoyos() {
            const tbody = document.getElementById('ctrlApoyosTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando apoyos...</td></tr>';

            try {
                const res = await fetch('/api/control-movimientos/apoyo-institucional');'''

apoyos_new = '''        // 7. Cargar Apoyo Institucional
        async function loadControlApoyos() {
            const tbody = document.getElementById('ctrlApoyosTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando apoyos...</td></tr>';

            const mes = document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const ano = document.getElementById('ctrlYearSelect')?.value || '2026';

            try {
                const res = await fetch(`/api/control-movimientos/apoyo-institucional?mes=${encodeURIComponent(mes)}&ano=${encodeURIComponent(ano)}`);'''

print("entradas_old in content:", entradas_old in content)
print("apoyos_old in content:", apoyos_old in content)

