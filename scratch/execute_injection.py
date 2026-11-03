# -*- coding: utf-8 -*-
"""
Full Python injector for templates/index.html to integrate "Control de inventario por movimientos"
"""
import io
import sys

INDEX_PATH = r"c:\Users\moode\.gemini\antigravity-ide\scratch\abisalud_automation\templates\index.html"

from build_injection import CSS_CODE, TOOLBAR_BTN, TAB_CONTENT, MODALS_CONTENT

JS_CODE = """
        /* ========================================================
           CONTROLADOR JAVASCRIPT: CONTROL DE INVENTARIO POR MOVIMIENTOS
           ======================================================== */
        let ctrlCatalogMap = {};
        let ctrlProveedoresList = [];
        let ctrlUnidadesList = [];
        let ctrlMatrizData = [];
        let ctrlEntradasData = [];
        let ctrlSalidasPdfData = [];
        let ctrlApoyosData = [];
        let ctrlSearchTimeout = null;
        let ctrlSelectedPdfFiles = [];

        // 1. Cargar y orquestar el módulo completo
        async function loadControlMovimientos() {
            await loadControlCatalogoData();
            const activeSub = document.querySelector('.ctrl-subtab-view.active')?.id || 'ctrlViewMatriz';
            if (activeSub === 'ctrlViewMatriz') loadControlMatriz();
            if (activeSub === 'ctrlViewEntradas') loadControlEntradas();
            if (activeSub === 'ctrlViewSalidas') loadControlSalidasPdf();
            if (activeSub === 'ctrlViewApoyos') loadControlApoyos();
            if (activeSub === 'ctrlViewCatalogos') loadControlCatalogosTab();
        }

        // 2. Cambiar de sub-pestaña interna
        function switchControlSubTab(viewId, btn) {
            document.querySelectorAll('.ctrl-subtab-view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.ctrl-pill-btn').forEach(b => b.classList.remove('active'));
            const targetView = document.getElementById(viewId);
            if (targetView) targetView.classList.add('active');
            if (btn) btn.classList.add('active');

            if (viewId === 'ctrlViewMatriz') loadControlMatriz();
            if (viewId === 'ctrlViewEntradas') loadControlEntradas();
            if (viewId === 'ctrlViewSalidas') loadControlSalidasPdf();
            if (viewId === 'ctrlViewApoyos') loadControlApoyos();
            if (viewId === 'ctrlViewCatalogos') loadControlCatalogosTab();
        }

        // 3. Cargar Catálogos Auxiliares (Claves, Proveedores, Unidades)
        async function loadControlCatalogoData() {
            try {
                const [resCat, resProv, resUnd] = await Promise.all([
                    fetch('/api/control-movimientos/catalogo'),
                    fetch('/api/control-movimientos/proveedores'),
                    fetch('/api/control-movimientos/unidades')
                ]);
                
                const catData = await resCat.json();
                ctrlProveedoresList = await resProv.json();
                ctrlUnidadesList = await resUnd.json();

                ctrlCatalogMap = {};
                (catData.items || []).forEach(item => {
                    ctrlCatalogMap[item.clave] = item;
                });

                // Llenar selects en modales
                populateControlSelects();
            } catch (err) {
                console.error("Error al cargar datos auxiliares del control:", err);
            }
        }

        function populateControlSelects() {
            // Proveedores en Entrada
            const provSelect = document.getElementById('ctrl_e_proveedor');
            if (provSelect) {
                const cur = provSelect.value;
                provSelect.innerHTML = '<option value="">Seleccione proveedor...</option>' + 
                    ctrlProveedoresList.map(p => `<option value="${p.nombre}">${p.nombre}</option>`).join('');
                if (cur) provSelect.value = cur;
            }

            // Proveedores en Catálogo
            const catProvSelect = document.getElementById('ctrl_c_proveedor');
            if (catProvSelect) {
                const cur = catProvSelect.value;
                catProvSelect.innerHTML = '<option value="">Ninguno por defecto</option>' + 
                    ctrlProveedoresList.map(p => `<option value="${p.nombre}">${p.nombre}</option>`).join('');
                if (cur) catProvSelect.value = cur;
            }

            // Unidades en Entrada
            const udmSelect = document.getElementById('ctrl_e_udm');
            if (udmSelect) {
                const cur = udmSelect.value || 'PZA';
                udmSelect.innerHTML = ctrlUnidadesList.map(u => `<option value="${u.codigo}">${u.codigo} - ${u.descripcion || ''}</option>`).join('');
                udmSelect.value = cur;
            }

            // Unidades en Catálogo
            const catUdmSelect = document.getElementById('ctrl_c_udm');
            if (catUdmSelect) {
                const cur = catUdmSelect.value || 'PZA';
                catUdmSelect.innerHTML = ctrlUnidadesList.map(u => `<option value="${u.codigo}">${u.codigo} - ${u.descripcion || ''}</option>`).join('');
                catUdmSelect.value = cur;
            }
        }

        // 4. Cargar Matriz Consolidada (Reporte Diario)
        async function loadControlMatriz() {
            const tbody = document.getElementById('ctrlMatrixTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="45" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Consultando movimientos y calculando fórmulas...</td></tr>';

            const mes = document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const ano = document.getElementById('ctrlYearSelect')?.value || '2026';
            const q = document.getElementById('ctrlMatrizSearchInput')?.value || '';

            try {
                const res = await fetch(`/api/control-movimientos/matriz?mes=${encodeURIComponent(mes)}&ano=${encodeURIComponent(ano)}&q=${encodeURIComponent(q)}`);
                const data = await res.json();
                ctrlMatrizData = data.items || [];

                // Actualizar KPIs
                const kpis = data.kpis || {};
                document.getElementById('ctrlKpiTotalLotes').innerText = formatNumber(kpis.total_lotes || 0);
                document.getElementById('ctrlKpiTotalClaves').innerText = `${formatNumber(kpis.total_claves || 0)} claves únicas`;
                document.getElementById('ctrlKpiInvTotalMensual').innerText = formatNumber(kpis.total_inventario_mensual || 0);
                document.getElementById('ctrlKpiTotalSurtido').innerText = formatNumber(kpis.total_surtido_mensual || 0);
                document.getElementById('ctrlKpiInvDisponible').innerText = formatNumber(kpis.total_inventario_disponible || 0);

                renderControlMatrizTable(ctrlMatrizData);
            } catch (err) {
                console.error("Error al cargar matriz:", err);
                tbody.innerHTML = `<tr><td colspan="45" class="empty-state" style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i><br>Error al cargar el reporte: ${err.message}</td></tr>`;
            }
        }

        function renderControlMatrizTable(items) {
            const tbody = document.getElementById('ctrlMatrixTableBody');
            if (!tbody) return;

            if (!items || items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="45" class="empty-state"><i class="fa-solid fa-box-open"></i><br>No se encontraron registros de inventario para este mes. Agregue entradas manuales o importe PDFs.</td></tr>';
                return;
            }

            let html = '';
            items.forEach(row => {
                const dispClass = (row.inventario_disponible > 0) ? 'ctrl-disp-ok' : ((row.inventario_disponible === 0) ? 'ctrl-disp-zero' : 'ctrl-disp-neg');

                html += `<tr>
                    <td class="text-left" style="font-weight: 700; font-family: monospace;">${row.clave || ''}</td>
                    <td class="text-left" style="max-width: 250px; overflow: hidden; text-overflow: ellipsis;" title="${row.descripcion || ''}">${row.descripcion || ''}</td>
                    <td style="font-weight: 700;">${row.lote || ''}</td>
                    <td>${row.fecha_caducidad || ''}</td>
                    <td class="text-left" style="max-width: 130px; overflow: hidden; text-overflow: ellipsis;">${row.proveedor || ''}</td>
                    <td style="font-weight: 600;">${row.unidad_medida || 'PZA'}</td>
                    <td style="text-align: right;">${formatNumber(row.inventario_inicial || 0)}</td>
                    <td style="text-align: right;">${formatNumber(row.entrada_por_ajuste || 0)}</td>
                    <td style="text-align: right;">${formatNumber(row.cantidad_recibida || 0)}</td>
                    <td class="ctrl-calc-col" style="text-align: right; color: #047857;">${formatNumber(row.inventario_total_mensual || 0)}</td>`;

                // 31 Días
                for (let d = 1; d <= 31; d++) {
                    const val = (row.dias && row.dias[d]) ? row.dias[d] : 0;
                    const cellClass = val > 0 ? 'ctrl-day-cell has-val' : 'ctrl-day-cell';
                    html += `<td class="${cellClass}">${val > 0 ? formatNumber(val) : ''}</td>`;
                }

                html += `<td style="text-align: right; font-weight: 600; color: #8b5cf6;">${(row.apoyo_institucional || 0) > 0 ? formatNumber(row.apoyo_institucional) : ''}</td>
                    <td class="ctrl-calc-col" style="text-align: right; color: #ea580c;">${formatNumber(row.total_surtido || 0)}</td>
                    <td class="ctrl-calc-col ${dispClass}" style="text-align: right;">${formatNumber(row.inventario_disponible || 0)}</td>
                </tr>`;
            });

            tbody.innerHTML = html;
        }

        function handleControlMatrizSearch() {
            clearTimeout(ctrlSearchTimeout);
            ctrlSearchTimeout = setTimeout(() => {
                loadControlMatriz();
            }, 300);
        }

        // 5. Cargar Entradas Manuales
        async function loadControlEntradas() {
            const tbody = document.getElementById('ctrlEntradasTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="17" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando entradas...</td></tr>';

            try {
                const res = await fetch('/api/control-movimientos/entradas');
                const data = await res.json();
                ctrlEntradasData = data.items || [];
                renderControlEntradasTable(ctrlEntradasData);
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="17" class="empty-state" style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i><br>Error al cargar entradas: ${err.message}</td></tr>`;
            }
        }

        function renderControlEntradasTable(items) {
            const tbody = document.getElementById('ctrlEntradasTableBody');
            if (!tbody) return;

            if (!items || items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="17" class="empty-state"><i class="fa-solid fa-box-open"></i><br>No hay entradas manuales registradas. Haga clic en "+ Nueva Entrada Manual".</td></tr>';
                return;
            }

            let html = '';
            items.forEach(e => {
                const total = (e.inventario_inicial || 0) + (e.entrada_por_ajuste || 0) + (e.cantidad_recibida || 0);
                html += `<tr>
                    <td>${e.fecha_entrada || '-'}</td>
                    <td style="font-weight: 700; font-family: monospace;">${e.clave || ''}</td>
                    <td style="font-weight: 700;">${e.lote || ''}</td>
                    <td style="max-width: 220px; overflow: hidden; text-overflow: ellipsis;" title="${e.descripcion || ''}">${e.descripcion || ''}</td>
                    <td>${e.proveedor || '-'}</td>
                    <td style="font-weight: 600;">${e.unidad_medida || 'PZA'}</td>
                    <td>${e.fecha_caducidad || '-'}</td>
                    <td>${e.fecha_fabricacion || '-'}</td>
                    <td style="text-align: right;">${formatNumber(e.inventario_inicial || 0)}</td>
                    <td style="text-align: right;">${formatNumber(e.entrada_por_ajuste || 0)}</td>
                    <td style="text-align: right; font-weight: 600; color: #10b981;">${formatNumber(e.cantidad_recibida || 0)}</td>
                    <td style="text-align: right; font-weight: 800; color: #047857;">${formatNumber(total)}</td>
                    <td>${e.almacen || '-'}</td>
                    <td>${e.no_procedimiento || '-'}</td>
                    <td>${e.no_contrato || '-'}</td>
                    <td>${e.folio_administrativo || '-'}</td>
                    <td>
                        <div class="action-btn-group">
                            <button type="button" class="btn-action btn-edit" onclick="editControlEntrada(${e.id})" title="Editar"><i class="fa-solid fa-pen-to-square"></i></button>
                            <button type="button" class="btn-action btn-delete" onclick="deleteControlEntrada(${e.id})" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    </td>
                </tr>`;
            });
            tbody.innerHTML = html;
        }

        // 6. Cargar Salidas desde PDF
        async function loadControlSalidasPdf() {
            const tbody = document.getElementById('ctrlSalidasTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="10" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando salidas registradas...</td></tr>';

            try {
                const res = await fetch('/api/control-movimientos/salidas-pdf');
                const data = await res.json();
                ctrlSalidasPdfData = data.items || [];
                renderControlSalidasPdfTable(ctrlSalidasPdfData);
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="10" class="empty-state" style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i><br>Error al cargar salidas: ${err.message}</td></tr>`;
            }
        }

        function renderControlSalidasPdfTable(items) {
            const tbody = document.getElementById('ctrlSalidasTableBody');
            if (!tbody) return;

            if (!items || items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="10" class="empty-state"><i class="fa-solid fa-file-pdf"></i><br>No hay salidas importadas desde PDF. Suba una Hoja de Pedido/Entrega.</td></tr>';
                return;
            }

            let html = '';
            items.forEach(s => {
                const loteBadge = s.lote_asignado ? 
                    `<span style="background: rgba(16, 185, 129, 0.15); color: #047857; font-weight: 700; padding: 2px 6px; border-radius: 4px;"><i class="fa-solid fa-check"></i> ${s.lote_asignado}</span>` :
                    `<span style="background: rgba(239, 68, 68, 0.15); color: #dc2626; font-weight: 700; padding: 2px 6px; border-radius: 4px;"><i class="fa-solid fa-triangle-exclamation"></i> Sin stock asignado</span>`;

                html += `<tr>
                    <td>${s.fecha_salida || '-'}</td>
                    <td style="font-weight: 800; color: var(--primary);">Día ${s.dia_mes || '-'}</td>
                    <td style="font-weight: 700; font-family: monospace;">${s.clave || ''}</td>
                    <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis;" title="${s.descripcion || ''}">${s.descripcion || ''}</td>
                    <td style="text-align: right; font-weight: 800; color: #ea580c;">${formatNumber(s.cantidad || 0)}</td>
                    <td>${loteBadge}</td>
                    <td>${s.fecha_caducidad_lote || '-'}</td>
                    <td style="font-weight: 600;">${s.pedido_folio || '-'}</td>
                    <td style="font-size: 0.75rem; color: var(--text-muted);">${s.archivo_fuente || '-'}</td>
                    <td>
                        <button type="button" class="btn-action btn-delete" onclick="deleteControlSalidaPdf(${s.id})" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
                    </td>
                </tr>`;
            });
            tbody.innerHTML = html;
        }

        // 7. Cargar Apoyo Institucional
        async function loadControlApoyos() {
            const tbody = document.getElementById('ctrlApoyosTableBody');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando apoyos...</td></tr>';

            try {
                const res = await fetch('/api/control-movimientos/apoyo-institucional');
                const data = await res.json();
                ctrlApoyosData = data.items || [];
                renderControlApoyosTable(ctrlApoyosData);
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="8" class="empty-state" style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i><br>Error al cargar apoyos: ${err.message}</td></tr>`;
            }
        }

        function renderControlApoyosTable(items) {
            const tbody = document.getElementById('ctrlApoyosTableBody');
            if (!tbody) return;

            if (!items || items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><i class="fa-solid fa-handshake-angle"></i><br>No hay registros de apoyo institucional. Haga clic en "+ Registrar Apoyo Institucional".</td></tr>';
                return;
            }

            let html = '';
            items.forEach(a => {
                html += `<tr>
                    <td>${a.fecha || '-'}</td>
                    <td style="font-weight: 700; font-family: monospace;">${a.clave || ''}</td>
                    <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis;" title="${a.descripcion || ''}">${a.descripcion || ''}</td>
                    <td style="font-weight: 700;">${a.lote || ''}</td>
                    <td style="font-weight: 600; color: #8b5cf6;">${a.institucion || ''}</td>
                    <td style="text-align: right; font-weight: 800; color: #8b5cf6;">${formatNumber(a.cantidad || 0)}</td>
                    <td>${a.folio_observaciones || '-'}</td>
                    <td>
                        <button type="button" class="btn-action btn-delete" onclick="deleteControlApoyo(${a.id})" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
                    </td>
                </tr>`;
            });
            tbody.innerHTML = html;
        }

        // 8. Cargar Pestaña de Catálogos (Claves, Proveedores, Unidades)
        async function loadControlCatalogosTab() {
            // Claves
            const catTbody = document.getElementById('ctrlCatalogoTableBody');
            if (catTbody) {
                const keys = Object.values(ctrlCatalogMap);
                if (keys.length === 0) {
                    catTbody.innerHTML = '<tr><td colspan="8" class="empty-state"><i class="fa-solid fa-barcode"></i><br>Catálogo vacío. Presione "Sincronizar desde Inventario" para cargarlo en 1 segundo.</td></tr>';
                } else {
                    catTbody.innerHTML = keys.slice(0, 300).map(c => `<tr>
                        <td style="font-weight: 700; font-family: monospace;">${c.clave}</td>
                        <td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis;" title="${c.descripcion}">${c.descripcion}</td>
                        <td>${c.udm_default || 'PZA'}</td>
                        <td>${c.proveedor_default || '-'}</td>
                        <td>${c.procedimiento || '-'}</td>
                        <td>${c.contrato || '-'}</td>
                        <td>${c.registro_sanitario || '-'}</td>
                        <td>
                            <div class="action-btn-group">
                                <button type="button" class="btn-action btn-edit" onclick="editControlCatalogo(${c.id})" title="Editar"><i class="fa-solid fa-pen-to-square"></i></button>
                                <button type="button" class="btn-action btn-delete" onclick="deleteControlCatalogo(${c.id})" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>`).join('');
                }
            }

            // Proveedores
            const provTbody = document.getElementById('ctrlProveedoresTableBody');
            if (provTbody) {
                if (ctrlProveedoresList.length === 0) {
                    provTbody.innerHTML = '<tr><td colspan="2" class="empty-state">No hay proveedores registrados.</td></tr>';
                } else {
                    provTbody.innerHTML = ctrlProveedoresList.map(p => `<tr>
                        <td style="font-weight: 600;">${p.nombre}</td>
                        <td style="color: var(--text-muted);">${p.contacto || '-'}</td>
                    </tr>`).join('');
                }
            }

            // Unidades
            const undTbody = document.getElementById('ctrlUnidadesTableBody');
            if (undTbody) {
                if (ctrlUnidadesList.length === 0) {
                    undTbody.innerHTML = '<tr><td colspan="2" class="empty-state">No hay unidades registradas.</td></tr>';
                } else {
                    undTbody.innerHTML = ctrlUnidadesList.map(u => `<tr>
                        <td style="font-weight: 700; color: var(--accent);">${u.codigo}</td>
                        <td>${u.descripcion || '-'}</td>
                    </tr>`).join('');
                }
            }
        }

        // 9. Autocompletado Dinámico de Clave -> Descripción, UDM, Proveedor
        function onCtrlEntradaClaveInput() {
            const clave = document.getElementById('ctrl_e_clave')?.value.trim();
            if (!clave) return;

            if (ctrlCatalogMap[clave]) {
                const c = ctrlCatalogMap[clave];
                document.getElementById('ctrl_e_descripcion').value = c.descripcion || '';
                if (c.udm_default) document.getElementById('ctrl_e_udm').value = c.udm_default;
                if (c.proveedor_default) document.getElementById('ctrl_e_proveedor').value = c.proveedor_default;
                if (c.procedimiento && !document.getElementById('ctrl_e_procedimiento').value) {
                    document.getElementById('ctrl_e_procedimiento').value = c.procedimiento;
                }
                if (c.contrato && !document.getElementById('ctrl_e_contrato').value) {
                    document.getElementById('ctrl_e_contrato').value = c.contrato;
                }
                if (c.registro_sanitario && !document.getElementById('ctrl_e_registro_sanitario').value) {
                    document.getElementById('ctrl_e_registro_sanitario').value = c.registro_sanitario;
                }
            }
        }

        function recalcControlEntradaTotals() {
            const ini = parseFloat(document.getElementById('ctrl_e_inv_inicial')?.value || 0);
            const aju = parseFloat(document.getElementById('ctrl_e_ajuste')?.value || 0);
            const rec = parseFloat(document.getElementById('ctrl_e_recibida')?.value || 0);
            const total = ini + aju + rec;
            const el = document.getElementById('ctrl_e_total_mensual');
            if (el) el.value = total;
        }

        // Autocompletado en Apoyo Institucional con búsqueda de Lotes Vigentes
        async function onCtrlApoyoClaveInput() {
            const clave = document.getElementById('ctrl_a_clave')?.value.trim();
            const loteSelect = document.getElementById('ctrl_a_lote');
            const descInput = document.getElementById('ctrl_a_descripcion');
            if (!clave || !loteSelect) return;

            if (ctrlCatalogMap[clave]) {
                descInput.value = ctrlCatalogMap[clave].descripcion || '';
            }

            try {
                const res = await fetch(`/api/control-movimientos/lotes-disponibles/${encodeURIComponent(clave)}`);
                const lotes = await res.json();
                if (lotes && lotes.length > 0) {
                    loteSelect.innerHTML = lotes.map(l => `<option value="${l.lote}">${l.lote} | Cad: ${l.fecha_caducidad || 'S/F'} | Disp: ${formatNumber(l.disponible)} ${l.unidad_medida}</option>`).join('');
                } else {
                    loteSelect.innerHTML = '<option value="">Sin lotes con stock para esta clave</option>';
                }
            } catch (err) {
                console.error("Error al consultar lotes disponibles:", err);
            }
        }

        // 10. Modales y CRUD de Entrada Manual
        function openModalControlEntrada(id = null) {
            document.getElementById('ctrlEntradaId').value = '';
            document.getElementById('ctrlEntradaForm').reset();
            document.getElementById('ctrl_e_fecha_entrada').value = new Date().toISOString().split('T')[0];
            document.getElementById('ctrl_e_total_mensual').value = '0';
            document.getElementById('ctrlEntradaModalTitle').innerText = 'Registrar Entrada Manual';
            populateControlSelects();
            openModal('modalControlEntrada');
        }

        function editControlEntrada(id) {
            const item = ctrlEntradasData.find(e => e.id === id);
            if (!item) return;

            document.getElementById('ctrlEntradaId').value = item.id;
            document.getElementById('ctrl_e_clave').value = item.clave || '';
            document.getElementById('ctrl_e_lote').value = item.lote || '';
            document.getElementById('ctrl_e_descripcion').value = item.descripcion || '';
            document.getElementById('ctrl_e_proveedor').value = item.proveedor || '';
            document.getElementById('ctrl_e_udm').value = item.unidad_medida || 'PZA';
            document.getElementById('ctrl_e_fecha_entrada').value = item.fecha_entrada || '';
            document.getElementById('ctrl_e_caducidad').value = item.fecha_caducidad || '';
            document.getElementById('ctrl_e_fabricacion').value = item.fecha_fabricacion || '';
            document.getElementById('ctrl_e_almacen').value = item.almacen || 'CS ALMACEN 2022';
            document.getElementById('ctrl_e_inv_inicial').value = item.inventario_inicial || 0;
            document.getElementById('ctrl_e_ajuste').value = item.entrada_por_ajuste || 0;
            document.getElementById('ctrl_e_recibida').value = item.cantidad_recibida || 0;
            document.getElementById('ctrl_e_procedimiento').value = item.no_procedimiento || '';
            document.getElementById('ctrl_e_contrato').value = item.no_contrato || '';
            document.getElementById('ctrl_e_registro_sanitario').value = item.registro_sanitario || '';
            document.getElementById('ctrl_e_folio').value = item.folio_administrativo || '';
            
            recalcControlEntradaTotals();
            document.getElementById('ctrlEntradaModalTitle').innerText = `Editar Entrada: ${item.clave} (Lote: ${item.lote})`;
            openModal('modalControlEntrada');
        }

        async function submitControlEntrada(e) {
            e.preventDefault();
            const id = document.getElementById('ctrlEntradaId').value;
            const payload = {
                clave: document.getElementById('ctrl_e_clave').value.trim(),
                lote: document.getElementById('ctrl_e_lote').value.trim(),
                descripcion: document.getElementById('ctrl_e_descripcion').value.trim(),
                proveedor: document.getElementById('ctrl_e_proveedor').value,
                unidad_medida: document.getElementById('ctrl_e_udm').value,
                fecha_entrada: document.getElementById('ctrl_e_fecha_entrada').value,
                fecha_caducidad: document.getElementById('ctrl_e_caducidad').value,
                fecha_fabricacion: document.getElementById('ctrl_e_fabricacion').value,
                almacen: document.getElementById('ctrl_e_almacen').value,
                inventario_inicial: parseFloat(document.getElementById('ctrl_e_inv_inicial').value || 0),
                entrada_por_ajuste: parseFloat(document.getElementById('ctrl_e_ajuste').value || 0),
                cantidad_recibida: parseFloat(document.getElementById('ctrl_e_recibida').value || 0),
                no_procedimiento: document.getElementById('ctrl_e_procedimiento').value.trim(),
                no_contrato: document.getElementById('ctrl_e_contrato').value.trim(),
                registro_sanitario: document.getElementById('ctrl_e_registro_sanitario').value.trim(),
                folio_administrativo: document.getElementById('ctrl_e_folio').value.trim()
            };

            const url = id ? `/api/control-movimientos/entradas/${id}` : '/api/control-movimientos/entradas';
            const method = id ? 'PUT' : 'POST';

            try {
                const res = await fetch(url, {
                    method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al guardar entrada');

                showToast(`Entrada guardada con éxito (${payload.clave} - Lote: ${payload.lote})`, 'success');
                closeModal('modalControlEntrada');
                loadControlEntradas();
                loadControlMatriz();
            } catch (err) {
                showToast(`Error: ${err.message}`, 'error');
            }
        }

        async function deleteControlEntrada(id) {
            if (!confirm("¿Está seguro de eliminar esta entrada? Esto afectará los totales de la matriz.")) return;
            try {
                const res = await fetch(`/api/control-movimientos/entradas/${id}`, { method: 'DELETE' });
                if (!res.ok) throw new Error('Error al eliminar');
                showToast("Entrada eliminada correctamente", "info");
                loadControlEntradas();
                loadControlMatriz();
            } catch (err) {
                showToast(`Error: ${err.message}`, "error");
            }
        }

        // 11. Modal y CRUD Apoyo Institucional
        function openModalControlApoyo() {
            document.getElementById('ctrlApoyoForm').reset();
            document.getElementById('ctrl_a_fecha').value = new Date().toISOString().split('T')[0];
            openModal('modalControlApoyo');
        }

        async function submitControlApoyo(e) {
            e.preventDefault();
            const payload = {
                fecha: document.getElementById('ctrl_a_fecha').value,
                clave: document.getElementById('ctrl_a_clave').value.trim(),
                lote: document.getElementById('ctrl_a_lote').value.trim(),
                descripcion: document.getElementById('ctrl_a_descripcion').value.trim(),
                institucion: document.getElementById('ctrl_a_institucion').value.trim(),
                cantidad: parseFloat(document.getElementById('ctrl_a_cantidad').value || 0),
                folio_observaciones: document.getElementById('ctrl_a_folio').value.trim()
            };

            try {
                const res = await fetch('/api/control-movimientos/apoyo-institucional', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al registrar apoyo');

                showToast(`Apoyo registrado con éxito: ${formatNumber(payload.cantidad)} a ${payload.institucion}`, 'success');
                closeModal('modalControlApoyo');
                loadControlApoyos();
                loadControlMatriz();
            } catch (err) {
                showToast(`Error: ${err.message}`, 'error');
            }
        }

        async function deleteControlApoyo(id) {
            if (!confirm("¿Desea eliminar este registro de apoyo institucional?")) return;
            try {
                const res = await fetch(`/api/control-movimientos/apoyo-institucional/${id}`, { method: 'DELETE' });
                if (!res.ok) throw new Error("Error al eliminar");
                showToast("Registro eliminado", "info");
                loadControlApoyos();
                loadControlMatriz();
            } catch (err) {
                showToast(`Error: ${err.message}`, "error");
            }
        }

        // 12. Modal y Subida de PDFs de Salidas
        function openModalControlPdf() {
            ctrlSelectedPdfFiles = [];
            const listEl = document.getElementById('ctrlPdfSelectedList');
            if (listEl) { listEl.style.display = 'none'; listEl.innerHTML = ''; }
            const prog = document.getElementById('ctrlPdfProgress');
            if (prog) prog.style.display = 'none';
            const btn = document.getElementById('btnUploadCtrlPdf');
            if (btn) btn.disabled = true;
            openModal('modalControlPdf');
        }

        function handleControlPdfSelected(input) {
            if (!input.files || input.files.length === 0) return;
            ctrlSelectedPdfFiles = Array.from(input.files);

            const listEl = document.getElementById('ctrlPdfSelectedList');
            const btn = document.getElementById('btnUploadCtrlPdf');

            if (listEl) {
                listEl.style.display = 'block';
                listEl.innerHTML = `<strong>${ctrlSelectedPdfFiles.length} archivo(s) PDF seleccionado(s):</strong><br>` + 
                    ctrlSelectedPdfFiles.map(f => `<i class="fa-solid fa-file-pdf" style="color: #dc2626;"></i> ${f.name} (${(f.size/1024).toFixed(1)} KB)`).join('<br>');
            }
            if (btn) btn.disabled = false;
        }

        async function submitControlPdf() {
            if (!ctrlSelectedPdfFiles || ctrlSelectedPdfFiles.length === 0) return;

            const prog = document.getElementById('ctrlPdfProgress');
            const btn = document.getElementById('btnUploadCtrlPdf');
            if (prog) prog.style.display = 'block';
            if (btn) btn.disabled = true;

            const formData = new FormData();
            ctrlSelectedPdfFiles.forEach(f => formData.append('files', f));

            try {
                const res = await fetch('/api/control-movimientos/salidas-pdf/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al procesar PDFs');

                showToast(`¡Salidas procesadas! ${data.salidas_insertadas} partidas registradas con asignación FEFO en ${data.archivos_procesados} archivo(s).`, 'success');
                closeModal('modalControlPdf');
                loadControlSalidasPdf();
                loadControlMatriz();
            } catch (err) {
                showToast(`Error al procesar PDFs: ${err.message}`, 'error');
            } finally {
                if (prog) prog.style.display = 'none';
                if (btn) btn.disabled = false;
            }
        }

        async function deleteControlSalidaPdf(id) {
            if (!confirm("¿Desea eliminar este registro de salida?")) return;
            try {
                const res = await fetch(`/api/control-movimientos/salidas-pdf/${id}`, { method: 'DELETE' });
                if (!res.ok) throw new Error("Error al eliminar");
                showToast("Salida eliminada", "info");
                loadControlSalidasPdf();
                loadControlMatriz();
            } catch (err) {
                showToast(`Error: ${err.message}`, "error");
            }
        }

        async function vaciarSalidasPdfControl() {
            if (!confirm("¿Está seguro de vaciar TODAS las salidas registradas desde PDF en este control? Las entradas manuales se mantendrán intactas.")) return;
            try {
                const res = await fetch('/api/control-movimientos/salidas-pdf/clear', { method: 'POST' });
                const data = await res.json();
                showToast(data.message || "Salidas PDF eliminadas", "info");
                loadControlSalidasPdf();
                loadControlMatriz();
            } catch (err) {
                showToast(`Error: ${err.message}`, "error");
            }
        }

        // 13. Catálogos: Sincronizar, Agregar Claves, Prov, UDM
        async function syncControlCatalogo() {
            showToast("Sincronizando catálogo desde las partidas del sistema...", "info");
            try {
                const res = await fetch('/api/control-movimientos/catalogo/sync-from-insumos', { method: 'POST' });
                const data = await res.json();
                showToast(data.message || "Catálogo sincronizado exitosamente", "success");
                await loadControlCatalogoData();
                loadControlCatalogosTab();
            } catch (err) {
                showToast(`Error al sincronizar: ${err.message}`, "error");
            }
        }

        function openModalControlCatalogo(id = null) {
            document.getElementById('ctrlCatId').value = '';
            document.getElementById('ctrlCatForm').reset();
            document.getElementById('ctrlCatModalTitle').innerText = 'Agregar Clave al Catálogo';
            populateControlSelects();
            openModal('modalControlCatalogo');
        }

        function editControlCatalogo(id) {
            const item = Object.values(ctrlCatalogMap).find(c => c.id === id);
            if (!item) return;

            document.getElementById('ctrlCatId').value = item.id;
            document.getElementById('ctrl_c_clave').value = item.clave;
            document.getElementById('ctrl_c_descripcion').value = item.descripcion;
            document.getElementById('ctrl_c_udm').value = item.udm_default || 'PZA';
            document.getElementById('ctrl_c_proveedor').value = item.proveedor_default || '';
            document.getElementById('ctrl_c_procedimiento').value = item.procedimiento || '';
            document.getElementById('ctrl_c_contrato').value = item.contrato || '';
            document.getElementById('ctrl_c_registro_sanitario').value = item.registro_sanitario || '';

            document.getElementById('ctrlCatModalTitle').innerText = `Editar Clave: ${item.clave}`;
            openModal('modalControlCatalogo');
        }

        async function submitControlCatalogo(e) {
            e.preventDefault();
            const id = document.getElementById('ctrlCatId').value;
            const payload = {
                clave: document.getElementById('ctrl_c_clave').value.trim(),
                descripcion: document.getElementById('ctrl_c_descripcion').value.trim(),
                udm_default: document.getElementById('ctrl_c_udm').value,
                proveedor_default: document.getElementById('ctrl_c_proveedor').value,
                procedimiento: document.getElementById('ctrl_c_procedimiento').value.trim(),
                contrato: document.getElementById('ctrl_c_contrato').value.trim(),
                registro_sanitario: document.getElementById('ctrl_c_registro_sanitario').value.trim()
            };

            const url = id ? `/api/control-movimientos/catalogo/${id}` : '/api/control-movimientos/catalogo';
            const method = id ? 'PUT' : 'POST';

            try {
                const res = await fetch(url, {
                    method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al guardar clave');

                showToast(`Clave ${payload.clave} guardada en el catálogo`, 'success');
                closeModal('modalControlCatalogo');
                await loadControlCatalogoData();
                loadControlCatalogosTab();
            } catch (err) {
                showToast(`Error: ${err.message}`, 'error');
            }
        }

        async function deleteControlCatalogo(id) {
            if (!confirm("¿Desea eliminar esta clave del catálogo?")) return;
            try {
                const res = await fetch(`/api/control-movimientos/catalogo/${id}`, { method: 'DELETE' });
                if (!res.ok) throw new Error("Error al eliminar");
                showToast("Clave eliminada del catálogo", "info");
                await loadControlCatalogoData();
                loadControlCatalogosTab();
            } catch (err) {
                showToast(`Error: ${err.message}`, "error");
            }
        }

        function openModalControlProveedor() {
            document.getElementById('ctrlProvForm').reset();
            openModal('modalControlProveedor');
        }

        async function submitControlProveedor(e) {
            e.preventDefault();
            const payload = {
                nombre: document.getElementById('ctrl_p_nombre').value.trim(),
                contacto: document.getElementById('ctrl_p_contacto').value.trim()
            };
            try {
                const res = await fetch('/api/control-movimientos/proveedores', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!res.ok) throw new Error('Error al guardar proveedor');
                showToast(`Proveedor ${payload.nombre} agregado`, 'success');
                closeModal('modalControlProveedor');
                await loadControlCatalogoData();
                loadControlCatalogosTab();
            } catch (err) {
                showToast(`Error: ${err.message}`, 'error');
            }
        }

        function openModalControlUnidad() {
            document.getElementById('ctrlUnidadForm').reset();
            openModal('modalControlUnidad');
        }

        async function submitControlUnidad(e) {
            e.preventDefault();
            const payload = {
                codigo: document.getElementById('ctrl_u_codigo').value.trim().toUpperCase(),
                descripcion: document.getElementById('ctrl_u_descripcion').value.trim()
            };
            try {
                const res = await fetch('/api/control-movimientos/unidades', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!res.ok) throw new Error('Error al guardar unidad');
                showToast(`Unidad ${payload.codigo} agregada`, 'success');
                closeModal('modalControlUnidad');
                await loadControlCatalogoData();
                loadControlCatalogosTab();
            } catch (err) {
                showToast(`Error: ${err.message}`, 'error');
            }
        }

        // 14. Exportar Reporte de 5 Hojas con Fórmulas Vivas a Excel
        function exportControlMovimientosExcel() {
            const mes = document.getElementById('ctrlMonthSelect')?.value || 'OCTUBRE';
            const ano = document.getElementById('ctrlYearSelect')?.value || '2026';
            showToast(`Generando libro Excel de 5 hojas para ${mes} ${ano}...`, 'info');
            window.location.href = `/api/control-movimientos/export-excel?mes=${encodeURIComponent(mes)}&ano=${encodeURIComponent(ano)}`;
        }
"""

def run():
    print(f"Reading {INDEX_PATH}...")
    with io.open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Step A: Inject CSS before </style>
    if "/* ESTILOS CONTROL DE INVENTARIO POR MOVIMIENTOS */" not in content:
        print("Injecting CSS...")
        content = content.replace("</style>", CSS_CODE + "\n    </style>", 1)
    else:
        print("CSS already injected.")

    # Step B: Inject Toolbar Button in .tabs
    if "switchTab('tab-control-movimientos'" not in content:
        print("Injecting Toolbar Button...")
        # Insert right after tab-clues button
        target = "</button>\n                <button class=\"tab-btn\" onclick=\"switchTab('tab-upload'"
        replacement = "</button>\n" + TOOLBAR_BTN + "                <button class=\"tab-btn\" onclick=\"switchTab('tab-upload'"
        if target in content:
            content = content.replace(target, replacement, 1)
        else:
            # Fallback before tab-marbetes
            target = "<button class=\"tab-btn\" onclick=\"switchTab('tab-marbetes'"
            replacement = TOOLBAR_BTN + "                <button class=\"tab-btn\" onclick=\"switchTab('tab-marbetes'"
            content = content.replace(target, replacement, 1)
    else:
        print("Toolbar Button already injected.")

    # Step C: Inject Tab Content in .content-card
    if 'id="tab-control-movimientos"' not in content:
        print("Injecting Tab Content...")
        target = "            </div>\n\n        </div>\n    </main>"
        replacement = "            </div>\n" + TAB_CONTENT + "\n        </div>\n    </main>"
        if target in content:
            content = content.replace(target, replacement, 1)
        else:
            # Try alternate whitespace
            target = "</div>\n    </main>"
            replacement = TAB_CONTENT + "\n        </div>\n    </main>"
            content = content.replace(target, replacement, 1)
    else:
        print("Tab Content already injected.")

    # Step D: Inject Modals right before <!-- Toast Container -->
    if 'id="modalControlEntrada"' not in content:
        print("Injecting Modals...")
        target = "    <!-- Toast Container -->"
        replacement = MODALS_CONTENT + "\n    <!-- Toast Container -->"
        content = content.replace(target, replacement, 1)
    else:
        print("Modals already injected.")

    # Step E: Inject JS and update switchTab, exportCurrentReport, refreshAll, setupDZ
    if "loadControlMovimientos" not in content:
        print("Injecting JavaScript controller and hooks...")
        # 1. Update switchTab
        switch_old = "if (tabId === 'tab-marbetes') renderMarbetesPreview();"
        switch_new = "if (tabId === 'tab-marbetes') renderMarbetesPreview();\n            if (tabId === 'tab-control-movimientos') loadControlMovimientos();"
        content = content.replace(switch_old, switch_new, 1)

        # 2. Update exportCurrentReport
        export_old = "if (activeTab === 'tab-clues') {"
        export_new = """if (activeTab === 'tab-control-movimientos') {
                exportControlMovimientosExcel();
                return;
            }
            if (activeTab === 'tab-clues') {"""
        content = content.replace(export_old, export_new, 1)

        # 3. Update refreshAll
        refresh_old = "if (activeTab === 'tab-logs') loadLogs();"
        refresh_new = "if (activeTab === 'tab-logs') loadLogs();\n            if (activeTab === 'tab-control-movimientos') loadControlMovimientos();"
        content = content.replace(refresh_old, refresh_new, 1)

        # 4. Update setupDZ
        dz_old = "setupDZ('clientSyncDropZone', 'clientSyncFileInput', handleClientSyncFile);"
        dz_new = "setupDZ('clientSyncDropZone', 'clientSyncFileInput', handleClientSyncFile);\n            setupDZ('ctrlPdfDropZone', 'ctrlPdfFileInput', handleControlPdfSelected);"
        content = content.replace(dz_old, dz_new, 1)

        # 5. Insert JS Controller code right before setupModalDropZones
        target_js = "        // Setup dropzones para modales"
        replacement_js = JS_CODE + "\n        // Setup dropzones para modales"
        content = content.replace(target_js, replacement_js, 1)
    else:
        print("JS Controller already injected.")

    print(f"Writing updated {INDEX_PATH}...")
    with io.open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("Injection finished successfully!")

if __name__ == "__main__":
    run()
