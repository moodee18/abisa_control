with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert Iniciar Nuevo Mes Button
btn_target = '<button type="button" class="btn btn-success" onclick="exportControlMovimientosExcel()"'
btn_replacement = '''<button type="button" class="btn btn-outline-primary" data-perm="gestionar_control_movimientos" onclick="iniciarNuevoMesControlPrompt()" title="Iniciar mes trasladando el Inventario Disponible final del mes anterior" style="padding: 0.45rem 0.85rem; font-size: 0.82rem; border: 1px solid #2563eb; color: #2563eb; background: rgba(37,99,235,0.08); font-weight: 600; display: inline-flex; align-items: center; gap: 0.4rem;">
                            <i class="fa-solid fa-calendar-plus"></i> Iniciar Nuevo Mes
                        </button>
                        <button type="button" class="btn btn-success" onclick="exportControlMovimientosExcel()"'''

assert btn_target in content, "btn_target not found in content"
content = content.replace(btn_target, btn_replacement, 1)

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

assert entradas_old in content, "entradas_old not found in content"
content = content.replace(entradas_old, entradas_new, 1)

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

assert apoyos_old in content, "apoyos_old not found in content"
content = content.replace(apoyos_old, apoyos_new, 1)

# 4. Add iniciarNuevoMesControlPrompt JS function
iniciar_mes_js = '''
        async function iniciarNuevoMesControlPrompt() {
            const curMes = document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const curAno = parseInt(document.getElementById('ctrlYearSelect')?.value || '2026', 10);

            const meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'];
            const curIdx = meses.indexOf(curMes.toUpperCase());
            const nextIdx = (curIdx >= 0 && curIdx < 11) ? curIdx + 1 : 0;
            const nextAno = (curIdx === 11) ? curAno + 1 : curAno;
            const defaultNextMes = meses[nextIdx];

            const mesDestino = prompt(`Iniciar Nuevo Mes a partir de ${curMes} ${curAno}.\\n\\nEscriba el nombre del mes a crear (el inventario disponible final de ${curMes} se convertirá en el inventario inicial del nuevo mes):`, defaultNextMes);
            if (!mesDestino || !mesDestino.trim()) return;

            const targetMes = mesDestino.trim().toUpperCase();
            if (!confirm(`¿Confirmas inicializar el mes "${targetMes} ${nextAno}" tomando como inventario inicial el disponible final de "${curMes} ${curAno}"?`)) {
                return;
            }

            try {
                showToast(`Inicializando mes ${targetMes} ${nextAno}...`, 'info');
                const res = await fetch('/api/control-movimientos/iniciar-mes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        mes_origen: curMes,
                        ano_origen: curAno,
                        mes_destino: targetMes,
                        ano_destino: nextAno
                    })
                });
                const data = await res.json();
                if (!res.ok) {
                    showToast(data.detail || 'Error al iniciar nuevo mes', 'error');
                    return;
                }

                showToast(`¡Mes ${targetMes} inicializado con éxito! (${data.total_partidas_creadas || 0} partidas)`, 'success');
                const monthSel = document.getElementById('ctrlMonthSelect');
                if (monthSel) {
                    monthSel.value = targetMes;
                }
                const yearSel = document.getElementById('ctrlYearSelect');
                if (yearSel) {
                    yearSel.value = String(nextAno);
                }
                await loadControlMovimientos();
            } catch (err) {
                console.error("Error en iniciarNuevoMesControlPrompt:", err);
                showToast(`Error al iniciar nuevo mes: ${err.message}`, 'error');
            }
        }
'''

export_fn_target = '''        function exportControlMovimientosExcel() {
            const mes = document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const ano = document.getElementById('ctrlYearSelect')?.value || '2026';
            showToast(`Generando libro Excel de 5 hojas para ${mes} ${ano}...`, 'info');
            window.location.href = `/api/control-movimientos/export-excel?mes=${encodeURIComponent(mes)}&ano=${encodeURIComponent(ano)}`;
        }'''

assert export_fn_target in content, "export_fn_target not found in content"
content = content.replace(export_fn_target, export_fn_target + '\n' + iniciar_mes_js, 1)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully applied frontend patches to templates/index.html!")

