# Script to inject the "Automatización SIIA" tab, HTML content, and JavaScript into templates/index.html

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add tab button
tab_btn_html = '''                <button class="tab-btn" id="tabBtnSiiaRpa" data-tab-target="tab-siia-rpa" onclick="switchTab('tab-siia-rpa', this)" style="background: linear-gradient(135deg, rgba(234, 88, 12, 0.14), rgba(245, 158, 11, 0.14)); border: 1.5px solid #ea580c; color: #c2410c; font-weight: 800;">
                    <i class="fa-solid fa-robot"></i> Automatización SIIA
                </button>'''

if 'id="tabBtnSiiaRpa"' not in content:
    target_btn = '<button class="tab-btn" id="tabBtnMarbetes"'
    if target_btn in content:
        content = content.replace(target_btn, tab_btn_html + '\n                ' + target_btn)
        print("Tab button injected successfully.")
    else:
        print("Target button tabBtnMarbetes not found.")
else:
    print("Tab button already exists.")

# 2. Add switchTab trigger
if "if (tabId === 'tab-siia-rpa')" not in content:
    target_switch = "if (tabId === 'tab-usuarios' && hasPerm('gestionar_usuarios')) loadUsersTable();"
    replacement_switch = target_switch + "\n            if (tabId === 'tab-siia-rpa') loadSiiaRpaStatus();"
    if target_switch in content:
        content = content.replace(target_switch, replacement_switch)
        print("switchTab trigger injected successfully.")
    else:
        print("target_switch not found.")
else:
    print("switchTab trigger already exists.")

# 3. Add tab content HTML
tab_content_html = '''
            <!-- TAB 10: Automatización Robótica de Inventarios (SIIA) -->
            <div id="tab-siia-rpa" class="tab-content">
                <div style="padding: 1.25rem 0.5rem;">
                    <!-- Banner Encabezado -->
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; background: linear-gradient(135deg, rgba(234, 88, 12, 0.08), rgba(245, 158, 11, 0.08)); border: 1px solid rgba(234, 88, 12, 0.25); border-radius: 12px; padding: 1.25rem 1.5rem;">
                        <div>
                            <h2 style="font-size: 1.4rem; font-weight: 800; color: #c2410c; margin: 0 0 0.25rem 0; display: flex; align-items: center; gap: 0.6rem;">
                                <i class="fa-solid fa-robot" style="font-size: 1.6rem;"></i> Automatización Robótica de Inventarios (SIIA)
                            </h2>
                            <p style="margin: 0; color: var(--text-muted); font-size: 0.9rem;">
                                Módulo desatendido para <strong>Alta de Inventarios (opc=78)</strong> y <strong>Seguimiento de Inventarios (opc=82)</strong> por lotes desde Excel con evidencias fotográficas.
                            </p>
                        </div>
                        <div style="display: flex; gap: 0.75rem;">
                            <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #065f46; border: 1px solid rgba(16, 185, 129, 0.3); font-weight: 700; padding: 0.4rem 0.8rem; border-radius: 8px;">
                                <i class="fa-solid fa-bolt"></i> Playwright RPA Engine
                            </span>
                        </div>
                    </div>

                    <!-- Subpestañas de Modo (Alta vs Seguimiento) -->
                    <div style="display: flex; gap: 0.75rem; margin-bottom: 1.5rem; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">
                        <button type="button" id="subtabBtnAlta" onclick="switchSiiaRpaSubtab('alta')" class="btn" style="background: #ea580c; color: #fff; font-weight: 700; padding: 0.6rem 1.2rem; border-radius: 8px; border: none; cursor: pointer; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fa-solid fa-folder-plus"></i> 1. Alta de Inventario Masiva (opc=78)
                        </button>
                        <button type="button" id="subtabBtnSeguimiento" onclick="switchSiiaRpaSubtab('seguimiento')" class="btn" style="background: var(--bg-card); color: var(--text-main); font-weight: 700; padding: 0.6rem 1.2rem; border-radius: 8px; border: 1px solid var(--border-color); cursor: pointer; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fa-solid fa-list-check"></i> 2. Seguimiento de Inventario Masivo (opc=82)
                        </button>
                    </div>

                    <!-- PANE A: ALTA DE INVENTARIOS -->
                    <div id="paneSiiaAlta" style="display: block;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
                            <!-- Formulario Alta -->
                            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-top: 0; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <i class="fa-solid fa-upload" style="color: #ea580c;"></i> Cargar Almacenes para Alta
                                </h3>
                                
                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.4rem;">
                                        Localidad en SIIA:
                                    </label>
                                    <select id="siiaAltaLocalidad" style="width: 100%; padding: 0.6rem; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-input); color: var(--text-main); font-size: 0.9rem;">
                                        <option value="1836" selected>CS ALMACEN 2022 (ID: 1836)</option>
                                    </select>
                                </div>

                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.4rem;">
                                        Archivo Excel de Almacenes:
                                    </label>
                                    <div style="border: 2px dashed #ea580c; border-radius: 8px; padding: 1.25rem; text-align: center; background: rgba(234, 88, 12, 0.02); cursor: pointer;" onclick="document.getElementById('siiaAltaFile').click()">
                                        <i class="fa-solid fa-file-excel" style="font-size: 2rem; color: #10b981; margin-bottom: 0.5rem;"></i>
                                        <p id="siiaAltaFileLabel" style="margin: 0; font-size: 0.85rem; color: var(--text-muted);">
                                            Haz clic para seleccionar el Excel con los almacenes (.xlsx, .xls)
                                        </p>
                                        <input type="file" id="siiaAltaFile" accept=".xlsx,.xls" style="display: none;" onchange="handleRpaFileSelect(this, 'siiaAltaFileLabel')">
                                    </div>
                                </div>

                                <div style="margin-bottom: 1.25rem;">
                                    <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-main); cursor: pointer;">
                                        <input type="checkbox" id="siiaAltaDescargarPdfs" checked style="accent-color: #ea580c; width: 16px; height: 16px;">
                                        <span>Descargar automáticamente todos los PDFs generados y empaquetar en ZIP</span>
                                    </label>
                                </div>

                                <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
                                    <button type="button" id="btnStartAlta" onclick="startSiiaAlta()" class="btn" style="flex: 1; background: #ea580c; color: #fff; font-weight: 700; padding: 0.75rem; border-radius: 8px; border: none; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 0.5rem;">
                                        <i class="fa-solid fa-play"></i> Iniciar Generación de Altas
                                    </button>
                                    <a href="/api/siia-rpa/template/alta" class="btn" style="background: var(--bg-hover); color: var(--text-main); border: 1px solid var(--border-color); padding: 0.75rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.85rem; display: flex; align-items: center; gap: 0.4rem;" title="Descargar plantilla de ejemplo">
                                        <i class="fa-solid fa-download"></i> Plantilla
                                    </a>
                                </div>
                            </div>

                            <!-- Tarjeta Informativa Alta -->
                            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-top: 0; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <i class="fa-solid fa-circle-info" style="color: #3b82f6;"></i> Instrucciones de Alta de Inventario
                                </h3>
                                <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.88rem; color: var(--text-muted); line-height: 1.6;">
                                    <li>El archivo Excel debe incluir una columna con el encabezado <strong>Almacén</strong> o <strong>Nombre</strong>.</li>
                                    <li>El bot seleccionará automáticamente la localidad <strong>CS ALMACEN 2022</strong> en el módulo <strong>opc=78</strong>.</li>
                                    <li>Recorrerá cada almacén, pulsará <strong>Generar</strong> y registrará si el corte se creó o si ya tenía un ajuste previo.</li>
                                    <li>Al concluir, generará un archivo comprimido <strong>Altas_Inventario_SIIA.zip</strong> listo para descargar con todas las hojas oficiales de inventario.</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- PANE B: SEGUIMIENTO DE INVENTARIOS -->
                    <div id="paneSiiaSeguimiento" style="display: none;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
                            <!-- Formulario Seguimiento -->
                            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-top: 0; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <i class="fa-solid fa-file-import" style="color: #10b981;"></i> Cargar Inventario para Seguimiento
                                </h3>
                                
                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.4rem;">
                                        Localidad en SIIA:
                                    </label>
                                    <select id="siiaSegLocalidad" style="width: 100%; padding: 0.6rem; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-input); color: var(--text-main); font-size: 0.9rem;">
                                        <option value="1836" selected>CS ALMACEN 2022 (ID: 1836)</option>
                                    </select>
                                </div>

                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.4rem;">
                                        Archivo Excel de Inventario Detallado (7 columnas):
                                    </label>
                                    <div style="border: 2px dashed #10b981; border-radius: 8px; padding: 1.25rem; text-align: center; background: rgba(16, 185, 129, 0.02); cursor: pointer;" onclick="document.getElementById('siiaSegFile').click()">
                                        <i class="fa-solid fa-file-excel" style="font-size: 2rem; color: #10b981; margin-bottom: 0.5rem;"></i>
                                        <p id="siiaSegFileLabel" style="margin: 0; font-size: 0.85rem; color: var(--text-muted);">
                                            Haz clic para seleccionar el Excel (ej. INV OCTUBRE 11.xlsx)
                                        </p>
                                        <input type="file" id="siiaSegFile" accept=".xlsx,.xls" style="display: none;" onchange="handleRpaFileSelect(this, 'siiaSegFileLabel')">
                                    </div>
                                </div>

                                <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.25rem;">
                                    <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-main); cursor: pointer;">
                                        <input type="checkbox" id="siiaSegAutoFinalizar" checked style="accent-color: #10b981; width: 16px; height: 16px;">
                                        <span>Marcar casilla <strong>Finalizado</strong> y aplicar ajuste automáticamente</span>
                                    </label>
                                    <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-main); cursor: pointer;">
                                        <input type="checkbox" id="siiaSegEvidencias" checked style="accent-color: #10b981; width: 16px; height: 16px;">
                                        <span>Capturar y empaquetar evidencias fotográficas de cada almacén en ZIP</span>
                                    </label>
                                </div>

                                <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
                                    <button type="button" id="btnStartSeg" onclick="startSiiaSeguimiento()" class="btn" style="flex: 1; background: #10b981; color: #fff; font-weight: 700; padding: 0.75rem; border-radius: 8px; border: none; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 0.5rem;">
                                        <i class="fa-solid fa-rocket"></i> Iniciar Captura y Finalización
                                    </button>
                                    <a href="/api/siia-rpa/template/seguimiento" class="btn" style="background: var(--bg-hover); color: var(--text-main); border: 1px solid var(--border-color); padding: 0.75rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.85rem; display: flex; align-items: center; gap: 0.4rem;" title="Descargar plantilla de 7 columnas">
                                        <i class="fa-solid fa-download"></i> Plantilla
                                    </a>
                                </div>
                            </div>

                            <!-- Tarjeta Informativa Seguimiento -->
                            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-top: 0; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <i class="fa-solid fa-layer-group" style="color: #8b5cf6;"></i> Características del Seguimiento Inteligente
                                </h3>
                                <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.88rem; color: var(--text-muted); line-height: 1.6;">
                                    <li><strong>Reconocimiento Multinivel:</strong> Empareja insumos por <code>Lote</code>, <code>Código de Barras</code> y <code>Caducidad</code>.</li>
                                    <li><strong>Paginación Autónoma:</strong> Si un almacén cuenta con múltiples hojas (hasta 15 páginas), el bot navega cada hoja, llena cantidades, da clic en Guardar y avanza hasta completar todas.</li>
                                    <li><strong>Activación de Celdas Ocultas:</strong> Dispara los eventos nativos de JavaScript para garantizar que el ERP de Abisalud guarde los cambios en base de datos.</li>
                                    <li><strong>Cierre con Auditoría:</strong> Marca la opción <em>Finalizado</em>, acepta la confirmación y toma una captura fotográfica inmutable.</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- MONITOR EN VIVO Y BITÁCORA -->
                    <div id="siiaRpaMonitor" style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem;">
                            <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 0.5rem;">
                                <i class="fa-solid fa-chart-line" style="color: #3b82f6;"></i> Monitor de Ejecución en Tiempo Real
                            </h3>
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <span id="rpaStatusBadge" class="badge" style="background: var(--bg-hover); color: var(--text-muted); font-weight: 700; padding: 0.4rem 0.8rem; border-radius: 8px;">
                                    En Espera
                                </span>
                                <button type="button" id="btnCancelRpa" onclick="cancelSiiaRpa()" class="btn" style="display: none; background: #ef4444; color: #fff; font-weight: 700; font-size: 0.8rem; padding: 0.4rem 0.8rem; border-radius: 6px; border: none; cursor: pointer;">
                                    <i class="fa-solid fa-stop"></i> Detener
                                </button>
                                <a id="btnDownloadRpaZip" href="#" class="btn" style="display: none; background: #10b981; color: #fff; font-weight: 700; font-size: 0.8rem; padding: 0.4rem 0.8rem; border-radius: 6px; text-decoration: none;">
                                    <i class="fa-solid fa-file-zipper"></i> Descargar ZIP
                                </a>
                            </div>
                        </div>

                        <!-- Barra de Progreso -->
                        <div style="margin-bottom: 1.25rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.4rem;">
                                <span id="rpaProgressLabel">Progreso General: 0%</span>
                                <span id="rpaProgressCount">0 / 0 Almacenes</span>
                            </div>
                            <div style="width: 100%; height: 12px; background: var(--bg-hover); border-radius: 6px; overflow: hidden; position: relative;">
                                <div id="rpaProgressBar" style="width: 0%; height: 100%; background: linear-gradient(90deg, #ea580c, #10b981); transition: width 0.3s ease;"></div>
                            </div>
                        </div>

                        <!-- Métricas Rápidas -->
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.25rem;">
                            <div style="background: var(--bg-main); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Almacén Actual</div>
                                <div id="rpaMetricCurrentAlm" style="font-size: 0.95rem; font-weight: 800; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">-</div>
                            </div>
                            <div style="background: var(--bg-main); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Página / Hoja</div>
                                <div id="rpaMetricPage" style="font-size: 0.95rem; font-weight: 800; color: var(--text-main);">-</div>
                            </div>
                            <div style="background: var(--bg-main); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Insumos Capturados</div>
                                <div id="rpaMetricMatched" style="font-size: 0.95rem; font-weight: 800; color: #10b981;">0</div>
                            </div>
                            <div style="background: var(--bg-main); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Mensaje Actual</div>
                                <div id="rpaMetricMessage" style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">En espera</div>
                            </div>
                        </div>

                        <!-- Tabla de Resultados en Vivo -->
                        <div style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <h4 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: var(--text-main);">
                                    Detalle por Almacén (<span id="rpaTableCount">0</span>)
                                </h4>
                                <input type="text" id="rpaTableFilter" placeholder="Filtrar almacén..." oninput="filterRpaResultsTable()" style="padding: 0.3rem 0.6rem; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-input); color: var(--text-main); font-size: 0.8rem; width: 180px;">
                            </div>
                            <div class="table-responsive" style="max-height: 280px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 8px;">
                                <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                                    <thead style="position: sticky; top: 0; background: var(--bg-main); z-index: 10;">
                                        <tr>
                                            <th style="padding: 0.5rem; text-align: center; width: 40px;">#</th>
                                            <th style="padding: 0.5rem; text-align: left;">Almacén</th>
                                            <th style="padding: 0.5rem; text-align: center; width: 80px;">ID SIIA</th>
                                            <th style="padding: 0.5rem; text-align: center; width: 80px;">Páginas</th>
                                            <th style="padding: 0.5rem; text-align: center; width: 90px;">Insumos</th>
                                            <th style="padding: 0.5rem; text-align: center; width: 110px;">Estatus</th>
                                            <th style="padding: 0.5rem; text-align: left;">Detalle / Resultado</th>
                                        </tr>
                                    </thead>
                                    <tbody id="rpaResultsTableBody">
                                        <tr><td colspan="7" style="text-align: center; padding: 1.5rem; color: var(--text-muted);">Sin tareas ejecutadas aún. Inicia un proceso arriba para ver el progreso aquí.</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- Terminal / Bitácora de Eventos -->
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                                <span style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">
                                    <i class="fa-solid fa-terminal"></i> Bitácora de Eventos (Consola)
                                </span>
                                <button type="button" onclick="clearRpaTerminal()" style="background: none; border: none; color: var(--text-muted); font-size: 0.75rem; cursor: pointer;">Limpiar</button>
                            </div>
                            <div id="rpaTerminal" style="background: #0f172a; color: #38bdf8; font-family: monospace; font-size: 0.78rem; padding: 0.75rem; border-radius: 8px; height: 130px; overflow-y: auto; line-height: 1.4;">
                                <div>[SISTEMA] Motor RPA listo para recibir instrucciones.</div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
'''

if 'id="tab-siia-rpa"' not in content:
    target_content_end = '    <!-- Contenedor exclusivo para impresión en papel Carta (se oculta en pantalla, se activa al imprimir) -->'
    if target_content_end in content:
        # We need to insert right before the closing </div> of content-card
        # Find the last </div> before target_content_end
        idx_target = content.find(target_content_end)
        idx_close = content.rfind('</div>', 0, idx_target)
        idx_close_outer = content.rfind('</div>', 0, idx_close)
        
        content = content[:idx_close] + tab_content_html + '\n' + content[idx_close:]
        print("Tab content HTML injected successfully.")
    else:
        print("target_content_end not found.")
else:
    print("Tab content HTML already exists.")

# 4. Add JavaScript logic
js_logic = '''
    // =========================================================================
    // MODULO AUTOMATIZACION ROBOTICA SIIA (ALTAS Y SEGUIMIENTO)
    // =========================================================================
    let rpaPollInterval = null;
    let rpaCachedResults = [];

    function switchSiiaRpaSubtab(mode) {
        const btnAlta = document.getElementById('subtabBtnAlta');
        const btnSeg = document.getElementById('subtabBtnSeguimiento');
        const paneAlta = document.getElementById('paneSiiaAlta');
        const paneSeg = document.getElementById('paneSiiaSeguimiento');

        if (mode === 'alta') {
            btnAlta.style.background = '#ea580c';
            btnAlta.style.color = '#fff';
            btnAlta.style.border = 'none';

            btnSeg.style.background = 'var(--bg-card)';
            btnSeg.style.color = 'var(--text-main)';
            btnSeg.style.border = '1px solid var(--border-color)';

            paneAlta.style.display = 'block';
            paneSeg.style.display = 'none';
        } else {
            btnSeg.style.background = '#10b981';
            btnSeg.style.color = '#fff';
            btnSeg.style.border = 'none';

            btnAlta.style.background = 'var(--bg-card)';
            btnAlta.style.color = 'var(--text-main)';
            btnAlta.style.border = '1px solid var(--border-color)';

            paneSeg.style.display = 'block';
            paneAlta.style.display = 'none';
        }
    }

    function handleRpaFileSelect(input, labelId) {
        const label = document.getElementById(labelId);
        if (input.files && input.files.length > 0) {
            label.innerHTML = `<strong>${input.files[0].name}</strong> (${(input.files[0].size / 1024).toFixed(1)} KB)`;
            label.style.color = '#10b981';
        }
    }

    async function startSiiaAlta() {
        const fileInput = document.getElementById('siiaAltaFile');
        if (!fileInput.files || fileInput.files.length === 0) {
            showToast("Por favor selecciona un archivo Excel con la lista de almacenes.", "error");
            return;
        }

        const localidad = document.getElementById('siiaAltaLocalidad').value;
        const descargarPdfs = document.getElementById('siiaAltaDescargarPdfs').checked;

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('localidad_id', localidad);
        formData.append('descargar_pdfs', descargarPdfs);

        try {
            document.getElementById('btnStartAlta').disabled = true;
            document.getElementById('btnStartAlta').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Iniciando...';

            const res = await fetch('/api/siia-rpa/alta', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok && data.status === 'started') {
                showToast("Proceso de Alta de Inventario iniciado con éxito en segundo plano.", "success");
                startRpaPolling();
            } else {
                showToast(data.message || "Error al iniciar el proceso de Alta.", "error");
            }
        } catch (e) {
            showToast("Error de conexión al iniciar Alta: " + e.message, "error");
        } finally {
            document.getElementById('btnStartAlta').disabled = false;
            document.getElementById('btnStartAlta').innerHTML = '<i class="fa-solid fa-play"></i> Iniciar Generación de Altas';
        }
    }

    async function startSiiaSeguimiento() {
        const fileInput = document.getElementById('siiaSegFile');
        if (!fileInput.files || fileInput.files.length === 0) {
            showToast("Por favor selecciona el archivo Excel de inventario detallado.", "error");
            return;
        }

        const localidad = document.getElementById('siiaSegLocalidad').value;
        const autoFinalizar = document.getElementById('siiaSegAutoFinalizar').checked;
        const evidencias = document.getElementById('siiaSegEvidencias').checked;

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('localidad_id', localidad);
        formData.append('auto_finalizar', autoFinalizar);
        formData.append('guardar_evidencias', evidencias);

        try {
            document.getElementById('btnStartSeg').disabled = true;
            document.getElementById('btnStartSeg').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Iniciando...';

            const res = await fetch('/api/siia-rpa/seguimiento', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok && data.status === 'started') {
                showToast("Proceso de Seguimiento Masivo iniciado con éxito en segundo plano.", "success");
                startRpaPolling();
            } else {
                showToast(data.message || "Error al iniciar el Seguimiento.", "error");
            }
        } catch (e) {
            showToast("Error de conexión al iniciar Seguimiento: " + e.message, "error");
        } finally {
            document.getElementById('btnStartSeg').disabled = false;
            document.getElementById('btnStartSeg').innerHTML = '<i class="fa-solid fa-rocket"></i> Iniciar Captura y Finalización';
        }
    }

    async function cancelSiiaRpa() {
        if (!confirm("¿Seguro que deseas detener el proceso de RPA actual?")) return;
        try {
            const res = await fetch('/api/siia-rpa/cancel', { method: 'POST' });
            const data = await res.json();
            showToast(data.message || "Cancelación solicitada.", "info");
        } catch (e) {
            showToast("Error al cancelar: " + e.message, "error");
        }
    }

    function startRpaPolling() {
        if (rpaPollInterval) clearInterval(rpaPollInterval);
        loadSiiaRpaStatus();
        rpaPollInterval = setInterval(loadSiiaRpaStatus, 2500);
    }

    async function loadSiiaRpaStatus() {
        try {
            const res = await fetch('/api/siia-rpa/status');
            if (!res.ok) return;
            const data = await res.json();
            updateSiiaRpaUI(data);

            if (!data.running && rpaPollInterval) {
                // Si ya no está corriendo, poll una vez más tras 3s y parar
                setTimeout(async () => {
                    const rLast = await fetch('/api/siia-rpa/status');
                    if (rLast.ok) updateSiiaRpaUI(await rLast.json());
                    clearInterval(rpaPollInterval);
                    rpaPollInterval = null;
                }, 3000);
            }
        } catch (e) {
            console.error("Error al consultar estado de RPA:", e);
        }
    }

    function updateSiiaRpaUI(state) {
        if (!state) return;

        // Badge de estado
        const badge = document.getElementById('rpaStatusBadge');
        const btnCancel = document.getElementById('btnCancelRpa');
        const btnZip = document.getElementById('btnDownloadRpaZip');

        if (state.running) {
            badge.style.background = 'rgba(59, 130, 246, 0.15)';
            badge.style.color = '#2563eb';
            badge.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> En Ejecución (${state.type === 'alta' ? 'Altas' : 'Seguimiento'})`;
            btnCancel.style.display = 'inline-block';
        } else if (state.status === 'completed') {
            badge.style.background = 'rgba(16, 185, 129, 0.15)';
            badge.style.color = '#065f46';
            badge.innerHTML = '<i class="fa-solid fa-check-circle"></i> Completado con Éxito';
            btnCancel.style.display = 'none';
        } else if (state.status === 'failed') {
            badge.style.background = 'rgba(239, 68, 68, 0.15)';
            badge.style.color = '#b91c1c';
            badge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Con Errores';
            btnCancel.style.display = 'none';
        } else if (state.status === 'cancelled') {
            badge.style.background = 'rgba(245, 158, 11, 0.15)';
            badge.style.color = '#b45309';
            badge.innerHTML = '<i class="fa-solid fa-ban"></i> Cancelado';
            btnCancel.style.display = 'none';
        } else {
            badge.style.background = 'var(--bg-hover)';
            badge.style.color = 'var(--text-muted)';
            badge.innerHTML = 'En Espera';
            btnCancel.style.display = 'none';
        }

        // Botón ZIP
        if (state.zip_url) {
            btnZip.href = state.zip_url;
            btnZip.style.display = 'inline-block';
        } else {
            btnZip.style.display = 'none';
        }

        // Progreso
        document.getElementById('rpaProgressLabel').textContent = `Progreso General: ${state.progress_percent || 0}%`;
        document.getElementById('rpaProgressCount').textContent = `${state.current_index || 0} / ${state.total_items || 0} Almacenes`;
        document.getElementById('rpaProgressBar').style.width = `${state.progress_percent || 0}%`;

        // Métricas
        document.getElementById('rpaMetricCurrentAlm').textContent = state.current_item || '-';
        document.getElementById('rpaMetricCurrentAlm').title = state.current_item || '';
        document.getElementById('rpaMetricPage').textContent = (state.total_pages > 0) ? `Página ${state.current_page || 1} de ${state.total_pages}` : '-';
        document.getElementById('rpaMetricMatched').textContent = state.matched_count || 0;
        document.getElementById('rpaMetricMessage').textContent = state.message || '-';
        document.getElementById('rpaMetricMessage').title = state.message || '';

        // Terminal
        if (state.logs && state.logs.length > 0) {
            const terminal = document.getElementById('rpaTerminal');
            terminal.innerHTML = state.logs.map(l => `<div>${escapeHtml(l)}</div>`).join('');
            terminal.scrollTop = terminal.scrollHeight;
        }

        // Tabla de Resultados
        rpaCachedResults = state.items_results || [];
        renderRpaResultsTable(rpaCachedResults);
    }

    function renderRpaResultsTable(items) {
        const tbody = document.getElementById('rpaResultsTableBody');
        document.getElementById('rpaTableCount').textContent = items.length;

        if (!items || items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 1.5rem; color: var(--text-muted);">Sin tareas ejecutadas aún. Inicia un proceso arriba para ver el progreso aquí.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(itm => {
            let badgeBg = 'var(--bg-hover)', badgeColor = 'var(--text-muted)', icon = 'fa-clock';
            if (itm.estado === 'FINALIZADO' || itm.estado === 'GENERADO' || itm.estado === 'GUARDADO') {
                badgeBg = 'rgba(16, 185, 129, 0.15)'; badgeColor = '#065f46'; icon = 'fa-check';
            } else if (itm.estado === 'AJUSTE_PENDIENTE' || itm.estado === 'YA_EXISTE') {
                badgeBg = 'rgba(245, 158, 11, 0.15)'; badgeColor = '#b45309'; icon = 'fa-exclamation-circle';
            } else if (itm.estado === 'ERROR' || itm.estado === 'NO_ENCONTRADO') {
                badgeBg = 'rgba(239, 68, 68, 0.15)'; badgeColor = '#b91c1c'; icon = 'fa-times-circle';
            }

            const insumosStr = (itm.insumos_excel !== undefined) ? `${itm.insumos_capturados || 0} / ${itm.insumos_excel}` : (itm.pdf ? '<i class="fa-solid fa-file-pdf" style="color: #ef4444;"></i> PDF' : '-');
            const pagsStr = (itm.paginas !== undefined && itm.paginas > 0) ? itm.paginas : '-';

            return `
                <tr style="border-bottom: 1px solid var(--border-color);">
                    <td style="padding: 0.5rem; text-align: center; font-weight: 700;">${itm.num || '-'}</td>
                    <td style="padding: 0.5rem; font-weight: 600; color: var(--text-main);">${escapeHtml(itm.almacen || '')}</td>
                    <td style="padding: 0.5rem; text-align: center; font-family: monospace; color: var(--text-muted);">${itm.id || '-'}</td>
                    <td style="padding: 0.5rem; text-align: center;">${pagsStr}</td>
                    <td style="padding: 0.5rem; text-align: center; font-weight: 700;">${insumosStr}</td>
                    <td style="padding: 0.5rem; text-align: center;">
                        <span class="badge" style="background: ${badgeBg}; color: ${badgeColor}; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px;">
                            <i class="fa-solid ${icon}"></i> ${itm.estado || '-'}
                        </span>
                    </td>
                    <td style="padding: 0.5rem; font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(itm.mensaje || '')}</td>
                </tr>
            `;
        }).join('');
    }

    function filterRpaResultsTable() {
        const q = (document.getElementById('rpaTableFilter').value || '').trim().toLowerCase();
        if (!q) {
            renderRpaResultsTable(rpaCachedResults);
            return;
        }
        const filtered = rpaCachedResults.filter(itm => 
            (itm.almacen || '').toLowerCase().includes(q) ||
            (itm.id || '').toLowerCase().includes(q) ||
            (itm.estado || '').toLowerCase().includes(q)
        );
        renderRpaResultsTable(filtered);
    }

    function clearRpaTerminal() {
        document.getElementById('rpaTerminal').innerHTML = '<div>[CONSOLA] Bitácora limpiada.</div>';
    }
'''

if 'function switchSiiaRpaSubtab' not in content:
    target_js_end = '</script>'
    idx_script_end = content.rfind(target_js_end)
    if idx_script_end != -1:
        content = content[:idx_script_end] + js_logic + '\n' + content[idx_script_end:]
        print("JavaScript logic injected successfully.")
    else:
        print("target_js_end not found.")
else:
    print("JavaScript logic already exists.")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved updated templates/index.html successfully!")

