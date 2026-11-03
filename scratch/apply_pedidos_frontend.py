import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS for .btn-pedido-pill
css_target = '.header-actions {'
css_new = '''.btn-pedido-pill {
            background: rgba(37, 99, 235, 0.1);
            color: var(--primary);
            border: 1px solid rgba(37, 99, 235, 0.25);
            border-radius: 6px;
            padding: 2px 7px;
            font-size: 0.78rem;
            font-weight: 700;
            font-family: monospace;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s ease;
        }
        .btn-pedido-pill:hover {
            background: var(--primary);
            color: #ffffff;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25);
        }
        .header-actions {'''

assert css_target in content, "css_target not found"
content = content.replace(css_target, css_new, 1)

# 2. Add button in toolbar of ctrlViewSalidas
toolbar_target = '''<button type="button" class="btn btn-primary" data-perm="gestionar_control_movimientos" onclick="openModalControlPdf()">
                                    <i class="fa-solid fa-cloud-arrow-up"></i> Cargar PDFs de Salidas
                                </button>'''

toolbar_new = '''<button type="button" class="btn btn-primary" data-perm="gestionar_control_movimientos" onclick="openModalControlPdf()">
                                    <i class="fa-solid fa-cloud-arrow-up"></i> Cargar PDFs de Salidas
                                </button>
                                <button type="button" class="btn" data-perm="gestionar_control_movimientos" onclick="abrirModalGestionarPedidos()" style="background: rgba(37, 99, 235, 0.12); color: var(--primary); border: 1px solid rgba(37, 99, 235, 0.3); font-weight: 700; display: inline-flex; align-items: center; gap: 0.4rem;" title="Ver, modificar o eliminar pedidos completos (Hojas de Entrega)">
                                    <i class="fa-solid fa-file-invoice"></i> Modificar / Eliminar Pedido
                                </button>'''

assert toolbar_target in content, "toolbar_target not found"
content = content.replace(toolbar_target, toolbar_new, 1)

# 3. Add Modals after modalControlPdf
modals_target = '''                <button type="button" class="btn btn-primary" id="btnUploadCtrlPdf" onclick="submitControlPdf()" disabled>
                    <i class="fa-solid fa-upload"></i> Procesar Salidas PDF
                </button>
            </div>
        </div>
    </div>'''

modals_html = '''

    <!-- Modal: Modificar / Eliminar Pedido Completo -->
    <div class="modal-overlay" id="modalModificarPedidoCompleto">
        <div class="modal-container" style="max-width: 900px; width: 95vw;">
            <div class="modal-header">
                <div>
                    <h3 style="display: flex; align-items: center; gap: 0.5rem; margin: 0;">
                        <i class="fa-solid fa-file-invoice" style="color: var(--primary);"></i>
                        <span>Modificar Pedido Completo:</span>
                        <span id="modPedFolioBadge" style="background: var(--primary); color: #fff; padding: 2px 8px; border-radius: 6px; font-family: monospace; font-size: 0.95rem;"></span>
                    </h3>
                    <p id="modPedSubtitle" style="font-size: 0.8rem; color: var(--text-muted); margin: 0.25rem 0 0 0;"></p>
                </div>
                <button class="modal-close" onclick="closeModal('modalModificarPedidoCompleto')">&times;</button>
            </div>
            <div class="modal-body" style="max-height: 72vh; overflow-y: auto;">
                <input type="hidden" id="modPedOriginalFolio">
                <input type="hidden" id="modPedOriginalArchivo">
                <input type="hidden" id="modPedOriginalMes">
                <input type="hidden" id="modPedOriginalAno">

                <!-- Datos Generales del Pedido -->
                <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <h4 style="font-size: 0.88rem; margin: 0 0 0.75rem 0; color: var(--primary); display: flex; align-items: center; gap: 0.4rem;">
                        <i class="fa-solid fa-sliders"></i> Datos Generales del Pedido
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem;">
                        <div>
                            <label style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Folio del Pedido *</label>
                            <input type="text" id="modPedFolio" class="form-control" style="font-weight: 700; font-family: monospace;" required>
                        </div>
                        <div>
                            <label style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Fecha y Hora de Salida</label>
                            <input type="text" id="modPedFecha" class="form-control" placeholder="YYYY-MM-DD HH:MM:SS">
                        </div>
                        <div>
                            <label style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Día del Mes (1-31)</label>
                            <input type="number" id="modPedDia" min="1" max="31" class="form-control" style="font-weight: 700;">
                        </div>
                        <div>
                            <label style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Mes</label>
                            <select id="modPedMes" class="form-control" style="font-weight: 600;">
                                <option value="ENERO">Enero</option>
                                <option value="FEBRERO">Febrero</option>
                                <option value="MARZO">Marzo</option>
                                <option value="ABRIL">Abril</option>
                                <option value="MAYO">Mayo</option>
                                <option value="JUNIO">Junio</option>
                                <option value="JULIO">Julio</option>
                                <option value="AGOSTO">Agosto</option>
                                <option value="SEPTIEMBRE">Septiembre</option>
                                <option value="OCTUBRE">Octubre</option>
                                <option value="NOVIEMBRE">Noviembre</option>
                                <option value="DICIEMBRE">Diciembre</option>
                            </select>
                        </div>
                        <div>
                            <label style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Año</label>
                            <select id="modPedAno" class="form-control" style="font-weight: 600;">
                                <option value="2025">2025</option>
                                <option value="2026">2026</option>
                                <option value="2027">2027</option>
                            </select>
                        </div>
                        <div>
                            <label style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Archivo Origen / PDF</label>
                            <input type="text" id="modPedArchivo" class="form-control" placeholder="ej. PEDIDO 197283.pdf">
                        </div>
                    </div>
                </div>

                <!-- Partidas Incluidas -->
                <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <h4 style="font-size: 0.88rem; margin: 0; color: var(--text-main); display: flex; align-items: center; gap: 0.4rem;">
                                <i class="fa-solid fa-boxes-stacked"></i> Partidas del Pedido
                            </h4>
                            <span style="font-size: 0.8rem; background: rgba(37,99,235,0.1); color: var(--primary); padding: 2px 8px; border-radius: 12px; font-weight: 700;">
                                <span id="modPedItemCount">0</span> partidas • <span id="modPedPieceCount">0</span> piezas
                            </span>
                        </div>
                        <button type="button" class="btn btn-secondary" onclick="agregarFilaPartidaPedido()" style="padding: 0.35rem 0.75rem; font-size: 0.78rem;">
                            <i class="fa-solid fa-plus"></i> Agregar Partida
                        </button>
                    </div>

                    <div class="table-responsive" style="max-height: 280px; overflow-y: auto; border: 1px solid var(--card-border); border-radius: 6px;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem;">
                            <thead style="position: sticky; top: 0; background: var(--bg-hover); z-index: 2;">
                                <tr>
                                    <th style="padding: 0.5rem; text-align: center; width: 35px;">#</th>
                                    <th style="padding: 0.5rem; text-align: left; width: 140px;">Clave *</th>
                                    <th style="padding: 0.5rem; text-align: left;">Descripción</th>
                                    <th style="padding: 0.5rem; text-align: left; width: 120px;">Lote *</th>
                                    <th style="padding: 0.5rem; text-align: center; width: 110px;">Caducidad</th>
                                    <th style="padding: 0.5rem; text-align: right; width: 110px;">Cantidad *</th>
                                    <th style="padding: 0.5rem; text-align: center; width: 40px;"></th>
                                </tr>
                            </thead>
                            <tbody id="modPedItemsTableBody">
                                <tr><td colspan="7" class="empty-state" style="padding: 1rem;"><i class="fa-solid fa-spinner fa-spin"></i> Cargando partidas...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center;">
                <button type="button" class="btn btn-danger" onclick="eliminarPedidoActualDesdeModal()" style="display: inline-flex; align-items: center; gap: 0.4rem;">
                    <i class="fa-solid fa-trash-can"></i> Eliminar Pedido Completo
                </button>
                <div style="display: flex; gap: 0.5rem;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('modalModificarPedidoCompleto')">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="btnGuardarModPedido" onclick="guardarCambiosPedidoCompleto()" style="display: inline-flex; align-items: center; gap: 0.4rem;">
                        <i class="fa-solid fa-floppy-disk"></i> Guardar Cambios del Pedido
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal: Gestor de Pedidos de Salidas PDF (Lista Resumen) -->
    <div class="modal-overlay" id="modalGestionarPedidos">
        <div class="modal-container" style="max-width: 950px; width: 95vw;">
            <div class="modal-header">
                <div>
                    <h3 style="display: flex; align-items: center; gap: 0.5rem; margin: 0; color: var(--primary);">
                        <i class="fa-solid fa-file-invoice"></i>
                        <span>Gestor de Pedidos Completos</span>
                        <span id="gestionarPedidosMesBadge" style="background: rgba(37,99,235,0.12); color: var(--primary); padding: 2px 8px; border-radius: 6px; font-size: 0.82rem; font-weight: 700;"></span>
                    </h3>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0.25rem 0 0 0;">
                        Visualice todos los pedidos/hojas de entrega cargados en este periodo. Modifique sus datos o elimine pedidos completos de un solo clic.
                    </p>
                </div>
                <button class="modal-close" onclick="closeModal('modalGestionarPedidos')">&times;</button>
            </div>
            <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; gap: 0.75rem; flex-wrap: wrap;">
                    <div class="search-box" style="flex: 1; min-width: 250px; padding: 0.4rem 0.75rem;">
                        <i class="fa-solid fa-magnifying-glass" style="color: var(--primary);"></i>
                        <input type="text" id="gestionarPedidosSearchInput" placeholder="Buscar por Folio, Archivo, Clave..." oninput="filtrarListaPedidosModal()">
                    </div>
                    <span id="gestionarPedidosCountSummary" style="font-size: 0.82rem; font-weight: 700; color: var(--text-muted);">0 pedidos</span>
                </div>

                <div class="table-responsive" style="max-height: 420px; overflow-y: auto; border: 1px solid var(--card-border); border-radius: 8px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead style="position: sticky; top: 0; background: var(--bg-hover); z-index: 2;">
                            <tr>
                                <th style="padding: 0.65rem; text-align: left;">Folio Pedido</th>
                                <th style="padding: 0.65rem; text-align: left;">Fecha / Día</th>
                                <th style="padding: 0.65rem; text-align: left;">Archivo Fuente</th>
                                <th style="padding: 0.65rem; text-align: center;">Partidas</th>
                                <th style="padding: 0.65rem; text-align: right;">Total Piezas</th>
                                <th style="padding: 0.65rem; text-align: center;">Estado FEFO</th>
                                <th style="padding: 0.65rem; text-align: center; width: 140px;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="gestionarPedidosTableBody">
                            <tr><td colspan="7" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando lista de pedidos...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalGestionarPedidos')">Cerrar</button>
            </div>
        </div>
    </div>'''

assert modals_target in content, "modals_target not found"
content = content.replace(modals_target, modals_target + modals_html, 1)

# 4. Update renderControlSalidasPdfTable to show interactive folio and pedido actions
render_target = '''                html += `<tr>
                    <td>${s.fecha_salida || s.fecha || '-'}</td>
                    <td style="font-weight: 800; color: var(--primary);">Día ${s.dia_mes || s.dia || '-'}</td>
                    <td style="font-weight: 700; font-family: monospace;">${s.clave || ''}</td>
                    <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis;" title="${s.descripcion || ''}">${s.descripcion || ''}</td>
                    <td style="text-align: right; font-weight: 800; color: #ea580c;">${formatNumber(s.cantidad || 0)}</td>
                    <td>${loteBadge}</td>
                    <td>${s.fecha_caducidad_lote || s.fecha_caducidad || '-'}</td>
                    <td>${fefoBadge}</td>
                    <td style="font-weight: 600;">${s.pedido_folio || s.folio_pedido || '-'}</td>
                    <td style="font-size: 0.75rem; color: var(--text-muted);">${s.archivo_fuente || s.archivo_pdf || '-'}</td>
                    <td>
                        ${hasPerm('gestionar_control_movimientos') ? `
                        <div class="action-btn-group">
                            <button type="button" class="btn-action btn-edit" onclick="openCtrlModificarRecord('salidas_pdf', ${s.id})" title="Modificar registro"><i class="fa-solid fa-pen-to-square"></i></button>
                            <button type="button" class="btn-action btn-delete" onclick="deleteControlSalidaPdf(${s.id})" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
                        </div>` : '-'}
                    </td>
                </tr>`;'''

render_new = '''                const curFolio = s.pedido_folio || s.folio_pedido || '';
                const curArch = s.archivo_fuente || s.archivo_pdf || '';
                const curMes = s.mes || document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
                const curAno = parseInt(s.ano || document.getElementById('ctrlYearSelect')?.value || 2026, 10);
                const safeFolio = escapeAttr(curFolio);
                const safeArch = escapeAttr(curArch);
                const safeMes = escapeAttr(curMes);

                const folioHtml = curFolio ? 
                    `<button type="button" class="btn-pedido-pill" onclick="abrirModalModificarPedido('${safeFolio}', '${safeArch}', '${safeMes}', ${curAno})" title="Ver o modificar el pedido completo ${curFolio}">
                        <i class="fa-solid fa-file-invoice"></i> ${curFolio}
                    </button>` : '-';

                html += `<tr>
                    <td>${s.fecha_salida || s.fecha || '-'}</td>
                    <td style="font-weight: 800; color: var(--primary);">Día ${s.dia_mes || s.dia || '-'}</td>
                    <td style="font-weight: 700; font-family: monospace;">${s.clave || ''}</td>
                    <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis;" title="${s.descripcion || ''}">${s.descripcion || ''}</td>
                    <td style="text-align: right; font-weight: 800; color: #ea580c;">${formatNumber(s.cantidad || 0)}</td>
                    <td>${loteBadge}</td>
                    <td>${s.fecha_caducidad_lote || s.fecha_caducidad || '-'}</td>
                    <td>${fefoBadge}</td>
                    <td>${folioHtml}</td>
                    <td style="font-size: 0.75rem; color: var(--text-muted); max-width: 140px; overflow: hidden; text-overflow: ellipsis;" title="${curArch}">${curArch || '-'}</td>
                    <td>
                        ${hasPerm('gestionar_control_movimientos') ? `
                        <div class="action-btn-group">
                            <button type="button" class="btn-action btn-edit" onclick="openCtrlModificarRecord('salidas_pdf', ${s.id})" title="Modificar partida individual"><i class="fa-solid fa-pen-to-square"></i></button>
                            <button type="button" class="btn-action btn-delete" onclick="deleteControlSalidaPdf(${s.id})" title="Eliminar solo esta partida"><i class="fa-solid fa-trash"></i></button>
                            ${curFolio ? `
                            <span style="display:inline-block; width:1px; height:15px; background:var(--card-border); margin:0 2px;"></span>
                            <button type="button" class="btn-action" style="color: #2563eb; background: rgba(37,99,235,0.12);" onclick="abrirModalModificarPedido('${safeFolio}', '${safeArch}', '${safeMes}', ${curAno})" title="Modificar Pedido Completo (${safeFolio})"><i class="fa-solid fa-file-pen"></i></button>
                            <button type="button" class="btn-action" style="color: #dc2626; background: rgba(239,68,68,0.14);" onclick="confirmarEliminarPedidoCompleto('${safeFolio}', '${safeArch}', '${safeMes}', ${curAno})" title="Eliminar Pedido Completo (${safeFolio} - todas sus partidas)"><i class="fa-solid fa-trash-can-arrow-up"></i></button>
                            ` : ''}
                        </div>` : '-'}
                    </td>
                </tr>`;'''

assert render_target in content, "render_target not found"
content = content.replace(render_target, render_new, 1)

# 5. Add JavaScript functions for managing pedidos
js_target = 'async function vaciarSalidasPdfControl() {'
js_code = '''// =========================================================================
        // GESTIÓN DE PEDIDOS COMPLETOS (MODIFICAR Y ELIMINAR PEDIDO COMPLETO)
        // =========================================================================
        let ctrlCurrentPedidoData = null;
        let ctrlPedidosListaData = [];

        function escapeAttr(str) {
            if (!str) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/'/g, "\\'")
                .replace(/"/g, '&quot;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
        }

        async function abrirModalGestionarPedidos() {
            const mes = document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const ano = document.getElementById('ctrlYearSelect')?.value || '2026';
            const badge = document.getElementById('gestionarPedidosMesBadge');
            if (badge) badge.innerText = `${mes} ${ano}`;

            const searchInp = document.getElementById('gestionarPedidosSearchInput');
            if (searchInp) searchInp.value = '';

            const tbody = document.getElementById('gestionarPedidosTableBody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Consultando pedidos del periodo...</td></tr>';
            }

            openModal('modalGestionarPedidos');

            try {
                const res = await fetch(`/api/control-movimientos/pedidos?mes=${encodeURIComponent(mes)}&ano=${encodeURIComponent(ano)}`);
                const data = await res.json();
                ctrlPedidosListaData = Array.isArray(data) ? data : [];
                renderGestionarPedidosTable(ctrlPedidosListaData);
            } catch (err) {
                if (tbody) {
                    tbody.innerHTML = `<tr><td colspan="7" class="empty-state" style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i><br>Error al cargar pedidos: ${err.message}</td></tr>`;
                }
            }
        }

        function renderGestionarPedidosTable(pedidos) {
            const tbody = document.getElementById('gestionarPedidosTableBody');
            const summary = document.getElementById('gestionarPedidosCountSummary');
            if (!tbody) return;

            if (summary) {
                const totalPiezas = (pedidos || []).reduce((acc, p) => acc + (p.total_piezas || 0), 0);
                summary.innerText = `${(pedidos || []).length} pedidos • ${formatNumber(totalPiezas)} piezas`;
            }

            if (!pedidos || pedidos.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><i class="fa-solid fa-box-open"></i><br>No se encontraron pedidos en este periodo.</td></tr>';
                return;
            }

            let html = '';
            pedidos.forEach(p => {
                const safeFolio = escapeAttr(p.folio_pedido);
                const safeArch = escapeAttr(p.archivo_pdf);
                const safeMes = escapeAttr(p.mes);
                const pAno = p.ano || 2026;

                const fefoStatus = p.has_fefo_alert ? 
                    `<span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #b45309; border: 1px solid rgba(245, 158, 11, 0.35); font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;"><i class="fa-solid fa-triangle-exclamation"></i> Aviso FEFO</span>` :
                    `<span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #047857; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;"><i class="fa-solid fa-circle-check"></i> Óptimo</span>`;

                html += `<tr>
                    <td style="font-weight: 700; font-family: monospace; color: var(--primary);">
                        <button type="button" class="btn-pedido-pill" onclick="abrirModalModificarPedido('${safeFolio}', '${safeArch}', '${safeMes}', ${pAno})">
                            <i class="fa-solid fa-file-invoice"></i> ${p.folio_pedido}
                        </button>
                    </td>
                    <td>${p.fecha ? p.fecha.split(' ')[0] : '-'} (Día ${p.dia || '-'})</td>
                    <td style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; font-size: 0.78rem;" title="${p.archivo_pdf}">${p.archivo_pdf}</td>
                    <td style="text-align: center; font-weight: 700;">${p.total_partidas}</td>
                    <td style="text-align: right; font-weight: 800; color: #ea580c;">${formatNumber(p.total_piezas || 0)}</td>
                    <td style="text-align: center;">${fefoStatus}</td>
                    <td style="text-align: center;">
                        <div class="action-btn-group" style="justify-content: center;">
                            <button type="button" class="btn btn-secondary" onclick="abrirModalModificarPedido('${safeFolio}', '${safeArch}', '${safeMes}', ${pAno})" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;" title="Modificar este pedido">
                                <i class="fa-solid fa-pen-to-square"></i> Modificar
                            </button>
                            <button type="button" class="btn btn-danger" onclick="confirmarEliminarPedidoCompleto('${safeFolio}', '${safeArch}', '${safeMes}', ${pAno})" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;" title="Eliminar este pedido completo">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>`;
            });

            tbody.innerHTML = html;
        }

        function filtrarListaPedidosModal() {
            const raw = (document.getElementById('gestionarPedidosSearchInput')?.value || '').trim().toLowerCase();
            if (!raw) {
                renderGestionarPedidosTable(ctrlPedidosListaData);
                return;
            }
            const filtered = ctrlPedidosListaData.filter(p => {
                const fol = (p.folio_pedido || '').toLowerCase();
                const arch = (p.archivo_pdf || '').toLowerCase();
                const dia = String(p.dia || '');
                const fecha = (p.fecha || '').toLowerCase();
                return fol.includes(raw) || arch.includes(raw) || dia.includes(raw) || fecha.includes(raw);
            });
            renderGestionarPedidosTable(filtered);
        }

        async function abrirModalModificarPedido(folio, archivo, mes, ano) {
            if (!folio) {
                showToast("Folio de pedido inválido", "error");
                return;
            }

            const targetMes = mes || document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const targetAno = ano || document.getElementById('ctrlYearSelect')?.value || 2026;

            closeModal('modalGestionarPedidos');
            openModal('modalModificarPedidoCompleto');

            document.getElementById('modPedFolioBadge').innerText = folio;
            document.getElementById('modPedSubtitle').innerText = "Cargando partidas del pedido...";
            const tbody = document.getElementById('modPedItemsTableBody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="7" class="empty-state" style="padding: 1.5rem;"><i class="fa-solid fa-spinner fa-spin"></i> Consultando partidas del pedido...</td></tr>';
            }

            try {
                const url = `/api/control-movimientos/pedido?folio=${encodeURIComponent(folio)}&archivo=${encodeURIComponent(archivo || '')}&mes=${encodeURIComponent(targetMes)}&ano=${encodeURIComponent(targetAno)}`;
                const res = await fetch(url);
                if (!res.ok) {
                    const errData = await res.json();
                    throw new Error(errData.detail || "Error al consultar pedido");
                }
                const ped = await res.json();
                ctrlCurrentPedidoData = ped;

                document.getElementById('modPedOriginalFolio').value = ped.folio_pedido || folio;
                document.getElementById('modPedOriginalArchivo').value = ped.archivo_pdf || archivo || '';
                document.getElementById('modPedOriginalMes').value = ped.mes || targetMes;
                document.getElementById('modPedOriginalAno').value = ped.ano || targetAno;

                document.getElementById('modPedFolio').value = ped.folio_pedido || folio;
                document.getElementById('modPedFecha').value = ped.fecha || '';
                document.getElementById('modPedDia').value = ped.dia || 1;
                document.getElementById('modPedMes').value = (ped.mes || targetMes).toUpperCase();
                document.getElementById('modPedAno').value = String(ped.ano || targetAno);
                document.getElementById('modPedArchivo').value = ped.archivo_pdf || archivo || '';

                document.getElementById('modPedSubtitle').innerText = `${ped.total_partidas} partidas • ${formatNumber(ped.total_piezas)} piezas • Archivo: ${ped.archivo_pdf || '-'}`;

                renderModificarPedidoItemsTable(ped.items || []);
            } catch (err) {
                console.error("Error en abrirModalModificarPedido:", err);
                showToast(`Error al cargar pedido: ${err.message}`, "error");
                if (tbody) {
                    tbody.innerHTML = `<tr><td colspan="7" class="empty-state" style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i><br>${err.message}</td></tr>`;
                }
            }
        }

        function renderModificarPedidoItemsTable(items) {
            const tbody = document.getElementById('modPedItemsTableBody');
            if (!tbody) return;

            if (!items || items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="empty-state" style="padding: 1rem;"><i class="fa-solid fa-box-open"></i><br>No hay partidas en este pedido. Haga clic en "+ Agregar Partida".</td></tr>';
                updateModificarPedidoTotals();
                return;
            }

            let html = '';
            items.forEach((it, idx) => {
                const itemId = it.id || '';
                html += `<tr data-item-id="${itemId}" class="mod-ped-item-row">
                    <td style="text-align: center; font-weight: 700; color: var(--text-muted);">${idx + 1}</td>
                    <td>
                        <input type="text" class="form-control mod-ped-clave" value="${it.clave || ''}" style="font-size: 0.78rem; font-weight: 700; font-family: monospace; padding: 0.3rem 0.5rem;" required>
                    </td>
                    <td>
                        <input type="text" class="form-control mod-ped-desc" value="${escapeAttr(it.descripcion || '')}" style="font-size: 0.75rem; padding: 0.3rem 0.5rem;" placeholder="Descripción del insumo">
                    </td>
                    <td>
                        <input type="text" class="form-control mod-ped-lote" value="${it.lote_asignado || it.lote || ''}" style="font-size: 0.78rem; font-weight: 700; padding: 0.3rem 0.5rem;" required>
                    </td>
                    <td>
                        <input type="text" class="form-control mod-ped-cad" value="${it.fecha_caducidad || it.fecha_caducidad_lote || ''}" style="font-size: 0.78rem; text-align: center; padding: 0.3rem 0.4rem;" placeholder="YYYY-MM-DD">
                    </td>
                    <td>
                        <input type="number" step="any" min="0" class="form-control mod-ped-cant" value="${it.cantidad || 0}" oninput="updateModificarPedidoTotals()" style="font-size: 0.78rem; font-weight: 800; text-align: right; color: #ea580c; padding: 0.3rem 0.5rem;" required>
                    </td>
                    <td style="text-align: center;">
                        <button type="button" class="btn-action btn-delete" onclick="eliminarFilaPartidaPedido(this)" title="Quitar esta partida del pedido">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>`;
            });

            tbody.innerHTML = html;
            updateModificarPedidoTotals();
        }

        function updateModificarPedidoTotals() {
            const rows = document.querySelectorAll('.mod-ped-item-row');
            let totalPiezas = 0;
            let totalPartidas = rows.length;

            rows.forEach(r => {
                const cant = parseFloat(r.querySelector('.mod-ped-cant')?.value || 0) || 0;
                totalPiezas += cant;
            });

            const cntEl = document.getElementById('modPedItemCount');
            const pcsEl = document.getElementById('modPedPieceCount');
            if (cntEl) cntEl.innerText = totalPartidas;
            if (pcsEl) pcsEl.innerText = formatNumber(Math.round(totalPiezas * 100) / 100);
        }

        function agregarFilaPartidaPedido() {
            const tbody = document.getElementById('modPedItemsTableBody');
            if (!tbody) return;

            // Limpiar empty state si existe
            if (tbody.querySelector('.empty-state')) {
                tbody.innerHTML = '';
            }

            const rowsCount = tbody.querySelectorAll('.mod-ped-item-row').length;
            const tr = document.createElement('tr');
            tr.className = 'mod-ped-item-row';
            tr.setAttribute('data-item-id', '');

            tr.innerHTML = `
                <td style="text-align: center; font-weight: 700; color: var(--text-muted);">${rowsCount + 1}</td>
                <td>
                    <input type="text" class="form-control mod-ped-clave" value="" style="font-size: 0.78rem; font-weight: 700; font-family: monospace; padding: 0.3rem 0.5rem;" placeholder="060.000.0000" required>
                </td>
                <td>
                    <input type="text" class="form-control mod-ped-desc" value="" style="font-size: 0.75rem; padding: 0.3rem 0.5rem;" placeholder="Descripción del insumo">
                </td>
                <td>
                    <input type="text" class="form-control mod-ped-lote" value="" style="font-size: 0.78rem; font-weight: 700; padding: 0.3rem 0.5rem;" placeholder="Lote" required>
                </td>
                <td>
                    <input type="text" class="form-control mod-ped-cad" value="" style="font-size: 0.78rem; text-align: center; padding: 0.3rem 0.4rem;" placeholder="YYYY-MM-DD">
                </td>
                <td>
                    <input type="number" step="any" min="0" class="form-control mod-ped-cant" value="1" oninput="updateModificarPedidoTotals()" style="font-size: 0.78rem; font-weight: 800; text-align: right; color: #ea580c; padding: 0.3rem 0.5rem;" required>
                </td>
                <td style="text-align: center;">
                    <button type="button" class="btn-action btn-delete" onclick="eliminarFilaPartidaPedido(this)" title="Quitar esta partida">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
            updateModificarPedidoTotals();
        }

        function eliminarFilaPartidaPedido(btn) {
            const tr = btn.closest('tr');
            if (tr) {
                tr.remove();
                // Renumerar
                const rows = document.querySelectorAll('.mod-ped-item-row');
                rows.forEach((r, idx) => {
                    const firstTd = r.querySelector('td');
                    if (firstTd) firstTd.innerText = idx + 1;
                });
                if (rows.length === 0) {
                    const tbody = document.getElementById('modPedItemsTableBody');
                    if (tbody) {
                        tbody.innerHTML = '<tr><td colspan="7" class="empty-state" style="padding: 1rem;"><i class="fa-solid fa-box-open"></i><br>No hay partidas en este pedido. Haga clic en "+ Agregar Partida".</td></tr>';
                    }
                }
                updateModificarPedidoTotals();
            }
        }

        async function guardarCambiosPedidoCompleto() {
            const folioActual = document.getElementById('modPedOriginalFolio')?.value || '';
            const archivoActual = document.getElementById('modPedOriginalArchivo')?.value || '';
            const mesActual = document.getElementById('modPedOriginalMes')?.value || 'OCTUBRE';
            const anoActual = parseInt(document.getElementById('modPedOriginalAno')?.value || 2026, 10);

            const nuevoFolio = (document.getElementById('modPedFolio')?.value || '').trim();
            const nuevaFecha = (document.getElementById('modPedFecha')?.value || '').trim();
            const nuevoDia = parseInt(document.getElementById('modPedDia')?.value || 1, 10);
            const nuevoMes = (document.getElementById('modPedMes')?.value || mesActual).trim().toUpperCase();
            const nuevoAno = parseInt(document.getElementById('modPedAno')?.value || anoActual, 10);
            const nuevoArchivo = (document.getElementById('modPedArchivo')?.value || archivoActual).trim();

            if (!nuevoFolio) {
                showToast("El folio del pedido es obligatorio", "error");
                return;
            }

            // Recopilar partidas
            const rows = document.querySelectorAll('.mod-ped-item-row');
            const items = [];
            let hasError = false;

            rows.forEach((r, idx) => {
                const itemIdStr = r.getAttribute('data-item-id');
                const itemId = itemIdStr ? parseInt(itemIdStr, 10) : null;
                const cve = (r.querySelector('.mod-ped-clave')?.value || '').trim();
                const desc = (r.querySelector('.mod-ped-desc')?.value || '').trim();
                const lote = (r.querySelector('.mod-ped-lote')?.value || '').trim();
                const cad = (r.querySelector('.mod-ped-cad')?.value || '').trim();
                const cant = parseFloat(r.querySelector('.mod-ped-cant')?.value || 0);

                if (!cve) {
                    showToast(`La partida #${idx + 1} no tiene clave`, "error");
                    hasError = true;
                    return;
                }
                if (!lote) {
                    showToast(`La partida #${idx + 1} no tiene lote`, "error");
                    hasError = true;
                    return;
                }
                if (isNaN(cant) || cant <= 0) {
                    showToast(`La cantidad de la partida #${idx + 1} debe ser mayor a 0`, "error");
                    hasError = true;
                    return;
                }

                items.push({
                    id: itemId,
                    clave: cve,
                    descripcion: desc,
                    lote_asignado: lote,
                    lote: lote,
                    fecha_caducidad: cad,
                    cantidad: cant
                });
            });

            if (hasError) return;

            const payload = {
                folio_actual: folioActual,
                archivo_actual: archivoActual,
                mes_actual: mesActual,
                ano_actual: anoActual,
                nuevo_folio: nuevoFolio,
                nueva_fecha: nuevaFecha,
                nuevo_dia: nuevoDia,
                nuevo_mes: nuevoMes,
                nuevo_ano: nuevoAno,
                nuevo_archivo: nuevoArchivo,
                items: items
            };

            const btnSave = document.getElementById('btnGuardarModPedido');
            if (btnSave) {
                btnSave.disabled = true;
                btnSave.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';
            }

            try {
                const res = await fetch('/api/control-movimientos/pedido', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.detail || "Error al actualizar pedido");
                }

                showToast(data.message || `Pedido '${nuevoFolio}' actualizado con éxito`, "success");
                closeModal('modalModificarPedidoCompleto');

                // Si se cambió de mes, sincronizar el selector de mes del módulo
                if (nuevoMes !== mesActual) {
                    const selM = document.getElementById('ctrlMonthSelect');
                    if (selM) selM.value = nuevoMes;
                    const selA = document.getElementById('ctrlYearSelect');
                    if (selA) selA.value = String(nuevoAno);
                }

                await loadControlSalidasPdf();
                await loadControlMatriz();
            } catch (err) {
                console.error("Error al guardar pedido:", err);
                showToast(`Error: ${err.message}`, "error");
            } finally {
                if (btnSave) {
                    btnSave.disabled = false;
                    btnSave.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Guardar Cambios del Pedido';
                }
            }
        }

        async function confirmarEliminarPedidoCompleto(folio, archivo, mes, ano) {
            if (!folio) {
                showToast("Folio no especificado para eliminar", "error");
                return;
            }

            const targetMes = mes || document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const targetAno = ano || document.getElementById('ctrlYearSelect')?.value || 2026;

            const msg = `⚠️ ¿CONFIRMAS ELIMINAR EL PEDIDO COMPLETO '${folio}'?\\n\\nSe eliminarán TODAS las partidas asociadas a este pedido/archivo.\\nEsta acción descontará las piezas del reporte diario y no se puede deshacer.`;
            if (!confirm(msg)) return;

            try {
                showToast(`Eliminando pedido '${folio}'...`, "info");
                const url = `/api/control-movimientos/pedido?folio=${encodeURIComponent(folio)}&archivo=${encodeURIComponent(archivo || '')}&mes=${encodeURIComponent(targetMes)}&ano=${encodeURIComponent(targetAno)}`;
                const res = await fetch(url, { method: 'DELETE' });
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.detail || "Error al eliminar pedido");
                }

                showToast(data.message || `Pedido '${folio}' eliminado exitosamente`, "success");

                closeModal('modalModificarPedidoCompleto');
                closeModal('modalGestionarPedidos');

                await loadControlSalidasPdf();
                await loadControlMatriz();
            } catch (err) {
                console.error("Error al eliminar pedido:", err);
                showToast(`Error al eliminar pedido: ${err.message}`, "error");
            }
        }

        async function eliminarPedidoActualDesdeModal() {
            const folio = document.getElementById('modPedOriginalFolio')?.value;
            const arch = document.getElementById('modPedOriginalArchivo')?.value;
            const mes = document.getElementById('modPedOriginalMes')?.value;
            const ano = document.getElementById('modPedOriginalAno')?.value;
            if (folio) {
                await confirmarEliminarPedidoCompleto(folio, arch, mes, ano);
            }
        }

        '''

assert js_target in content, "js_target not found in content"
content = content.replace(js_target, js_code + js_target, 1)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied pedidos frontend patches to templates/index.html successfully!")

