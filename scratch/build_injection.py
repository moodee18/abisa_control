# -*- coding: utf-8 -*-
"""
Full injection builder for Control de Inventario por Movimientos
"""
import re
import os

INDEX_PATH = r"c:\Users\moode\.gemini\antigravity-ide\scratch\abisalud_automation\templates\index.html"

# 1. CSS
CSS_CODE = """
        /* ========================================================
           ESTILOS CONTROL DE INVENTARIO POR MOVIMIENTOS
           ======================================================== */
        .ctrl-pills-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            padding: 0.85rem 1.25rem;
            background: var(--input-bg);
            border-bottom: 1px solid var(--card-border);
        }

        .ctrl-pills-nav {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
        }

        .ctrl-pill-btn {
            padding: 0.45rem 0.95rem;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid var(--card-border);
            background: var(--card-bg);
            color: var(--text-muted);
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
        }

        .ctrl-pill-btn:hover {
            color: var(--text-main);
            border-color: var(--primary);
            background: var(--primary-light);
        }

        .ctrl-pill-btn.active {
            background: #10b981;
            color: #ffffff;
            border-color: #059669;
            box-shadow: 0 2px 6px rgba(16, 185, 129, 0.35);
        }

        .ctrl-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 1rem;
            padding: 1.25rem;
            background: var(--card-bg);
            border-bottom: 1px solid var(--card-border);
        }

        .ctrl-kpi-card {
            background: var(--input-bg);
            border: 1px solid var(--card-border);
            border-radius: var(--radius);
            padding: 1rem 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: var(--shadow-sm);
        }

        .ctrl-kpi-info p {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }

        .ctrl-kpi-info h3 {
            font-size: 1.35rem;
            font-weight: 800;
        }

        .ctrl-matrix-wrapper {
            width: 100%;
            overflow-x: auto;
            max-height: 72vh;
        }

        .ctrl-matrix-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.77rem;
            min-width: 2150px;
        }

        .ctrl-matrix-table th, .ctrl-matrix-table td {
            border: 1px solid #135824;
            padding: 5px 6px;
            white-space: nowrap;
            text-align: center;
        }

        .ctrl-banner-header {
            background: #135824 !important;
            color: #ffffff !important;
            font-weight: 800;
            font-size: 0.85rem;
            padding: 8px 10px;
            text-align: center;
            letter-spacing: 0.04em;
        }

        .ctrl-col-th {
            background: #196f31 !important;
            color: #ffffff !important;
            font-weight: 700;
            font-size: 0.74rem;
            padding: 6px 4px;
            position: sticky;
            top: 0;
            z-index: 5;
        }

        .ctrl-day-th {
            background: #196f31 !important;
            color: #ffffff !important;
            font-weight: 700;
            font-size: 0.73rem;
            min-width: 32px;
            padding: 6px 2px;
            position: sticky;
            top: 0;
            z-index: 5;
        }

        .ctrl-matrix-table td.text-left {
            text-align: left !important;
        }

        .ctrl-calc-col {
            background: rgba(16, 185, 129, 0.09);
            font-weight: 700;
        }

        .ctrl-day-cell.has-val {
            background: rgba(37, 99, 235, 0.14);
            color: #1d4ed8;
            font-weight: 800;
        }

        .ctrl-disp-ok {
            color: #047857;
            font-weight: 800;
        }

        .ctrl-disp-zero {
            color: #64748b;
        }

        .ctrl-disp-neg {
            color: #dc2626;
            font-weight: 800;
            background: rgba(239, 68, 68, 0.12);
        }

        .ctrl-subtab-view {
            display: none;
        }

        .ctrl-subtab-view.active {
            display: block;
        }
"""

# 2. Toolbar Tab Button
TOOLBAR_BTN = """                <button class="tab-btn" onclick="switchTab('tab-control-movimientos', this)" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15)); border: 1.5px solid #10b981; color: #065f46; font-weight: 800;">
                    <i class="fa-solid fa-cubes-stacked"></i> Control por Movimientos
                </button>
"""

# 3. Content for Tab
TAB_CONTENT = """
            <!-- TAB: Sistema Propuesto: Control de Inventario por Movimientos -->
            <div id="tab-control-movimientos" class="tab-content">
                <!-- Barra de Sub-Pestañas y Acciones Rápidas -->
                <div class="ctrl-pills-bar">
                    <div class="ctrl-pills-nav">
                        <button class="ctrl-pill-btn active" id="btnCtrlSubTabMatriz" onclick="switchControlSubTab('ctrlViewMatriz', this)">
                            <i class="fa-solid fa-table"></i> 1. Reporte Diario (Matriz)
                        </button>
                        <button class="ctrl-pill-btn" id="btnCtrlSubTabEntradas" onclick="switchControlSubTab('ctrlViewEntradas', this)">
                            <i class="fa-solid fa-arrow-down-long"></i> 2. Entradas Manuales
                        </button>
                        <button class="ctrl-pill-btn" id="btnCtrlSubTabSalidas" onclick="switchControlSubTab('ctrlViewSalidas', this)">
                            <i class="fa-solid fa-file-pdf"></i> 3. Salidas desde PDF
                        </button>
                        <button class="ctrl-pill-btn" id="btnCtrlSubTabApoyos" onclick="switchControlSubTab('ctrlViewApoyos', this)">
                            <i class="fa-solid fa-handshake-angle"></i> 4. Apoyo Institucional
                        </button>
                        <button class="ctrl-pill-btn" id="btnCtrlSubTabCatalogos" onclick="switchControlSubTab('ctrlViewCatalogos', this)">
                            <i class="fa-solid fa-book-bookmark"></i> 5. Catálogos (Claves, Prov, UDM)
                        </button>
                    </div>

                    <!-- Selectores de Mes, Año y Descarga de Excel -->
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <select id="ctrlMonthSelect" class="form-control" style="width: auto; padding: 0.4rem 0.65rem; font-size: 0.82rem; font-weight: 600;" onchange="loadControlMovimientos()">
                            <option value="ENERO">Enero</option>
                            <option value="FEBRERO">Febrero</option>
                            <option value="MARZO">Marzo</option>
                            <option value="ABRIL">Abril</option>
                            <option value="MAYO">Mayo</option>
                            <option value="JUNIO">Junio</option>
                            <option value="JULIO">Julio</option>
                            <option value="AGOSTO">Agosto</option>
                            <option value="SEPTIEMBRE">Septiembre</option>
                            <option value="OCTUBRE" selected>Octubre</option>
                            <option value="NOVIEMBRE">Noviembre</option>
                            <option value="DICIEMBRE">Diciembre</option>
                        </select>
                        <select id="ctrlYearSelect" class="form-control" style="width: auto; padding: 0.4rem 0.65rem; font-size: 0.82rem; font-weight: 600;" onchange="loadControlMovimientos()">
                            <option value="2025">2025</option>
                            <option value="2026" selected>2026</option>
                            <option value="2027">2027</option>
                        </select>
                        <button type="button" class="btn btn-success" onclick="exportControlMovimientosExcel()" title="Descargar Libro de Excel con 5 bases separadas y fórmulas vivas" style="padding: 0.45rem 0.85rem; font-size: 0.82rem;">
                            <i class="fa-solid fa-file-excel"></i> Descargar Excel (5 Hojas)
                        </button>
                    </div>
                </div>

                <!-- SUB-VISTA 1: REPORTE DIARIO (MATRIZ) -->
                <div id="ctrlViewMatriz" class="ctrl-subtab-view active">
                    <!-- KPIs de la Matriz del Mes -->
                    <div class="ctrl-kpi-grid">
                        <div class="ctrl-kpi-card" style="border-left: 4px solid var(--primary);">
                            <div class="ctrl-kpi-info">
                                <p>Partidas / Lotes</p>
                                <h3 id="ctrlKpiTotalLotes" style="color: var(--primary);">0</h3>
                                <small id="ctrlKpiTotalClaves" style="color: var(--text-muted);">0 claves únicas</small>
                            </div>
                            <div class="kpi-icon kpi-blue"><i class="fa-solid fa-barcode"></i></div>
                        </div>
                        <div class="ctrl-kpi-card" style="border-left: 4px solid #10b981;">
                            <div class="ctrl-kpi-info">
                                <p>Inventario Total Mensual</p>
                                <h3 id="ctrlKpiInvTotalMensual" style="color: #10b981;">0</h3>
                                <small style="color: var(--text-muted);">= Inicial + Ajustes + Recibida</small>
                            </div>
                            <div class="kpi-icon kpi-emerald"><i class="fa-solid fa-boxes-stacked"></i></div>
                        </div>
                        <div class="ctrl-kpi-card" style="border-left: 4px solid #ea580c;">
                            <div class="ctrl-kpi-info">
                                <p>Total Surtido del Mes</p>
                                <h3 id="ctrlKpiTotalSurtido" style="color: #ea580c;">0</h3>
                                <small style="color: var(--text-muted);">= Salidas PDF + Apoyo Inst.</small>
                            </div>
                            <div class="kpi-icon" style="background: rgba(234, 88, 12, 0.12); color: #ea580c;"><i class="fa-solid fa-truck-ramp-box"></i></div>
                        </div>
                        <div class="ctrl-kpi-card" style="border-left: 4px solid #06b6d4;">
                            <div class="ctrl-kpi-info">
                                <p>Inventario Disponible</p>
                                <h3 id="ctrlKpiInvDisponible" style="color: #0891b2;">0</h3>
                                <small style="color: var(--text-muted);">= Inv. Total Mensual - Surtido</small>
                            </div>
                            <div class="kpi-icon kpi-cyan"><i class="fa-solid fa-cubes"></i></div>
                        </div>
                    </div>

                    <!-- Barra de Búsqueda Rápida de la Matriz -->
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.65rem 1.25rem; background: var(--card-bg); border-bottom: 1px solid var(--card-border); gap: 0.75rem;">
                        <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">
                            <i class="fa-solid fa-circle-info" style="color: var(--primary);"></i>
                            Mostrando consolidado dinámico calculado desde las bases independientes de Entradas, Salidas PDF y Apoyos Institucionales.
                        </div>
                        <div class="search-box" style="min-width: 280px; padding: 0.35rem 0.75rem;">
                            <i class="fa-solid fa-magnifying-glass" style="color: var(--text-muted);"></i>
                            <input type="text" id="ctrlMatrizSearchInput" placeholder="Filtrar clave, lote, descripción..." oninput="handleControlMatrizSearch()">
                        </div>
                    </div>

                    <!-- Tabla Matriz Estilo Excel Oficial -->
                    <div class="ctrl-matrix-wrapper">
                        <table class="ctrl-matrix-table" id="ctrlMatrixTable">
                            <thead>
                                <tr>
                                    <th colspan="45" class="ctrl-banner-header">
                                        SISTEMA PROPUESTO: CONTROL DE INVENTARIO POR MOVIMIENTOS - REPORTE DIARIO DE SALIDAS
                                    </th>
                                </tr>
                                <tr>
                                    <th class="ctrl-col-th" style="width: 100px;">CLAVE</th>
                                    <th class="ctrl-col-th" style="width: 250px;">DESCRIPCIÓN</th>
                                    <th class="ctrl-col-th" style="width: 90px;">LOTE</th>
                                    <th class="ctrl-col-th" style="width: 85px;">CADUCIDAD</th>
                                    <th class="ctrl-col-th" style="width: 130px;">PROVEEDOR</th>
                                    <th class="ctrl-col-th" style="width: 60px;">UDM</th>
                                    <th class="ctrl-col-th" style="width: 75px;">INV. INICIAL</th>
                                    <th class="ctrl-col-th" style="width: 75px;">ENTRADA POR AJUSTE</th>
                                    <th class="ctrl-col-th" style="width: 75px;">CANTIDAD RECIBIDA</th>
                                    <th class="ctrl-col-th ctrl-calc-col" style="width: 90px;">INVENTARIO TOTAL MENSUAL</th>
                                    <!-- 31 DÍAS -->
                                    <th class="ctrl-day-th">01</th>
                                    <th class="ctrl-day-th">02</th>
                                    <th class="ctrl-day-th">03</th>
                                    <th class="ctrl-day-th">04</th>
                                    <th class="ctrl-day-th">05</th>
                                    <th class="ctrl-day-th">06</th>
                                    <th class="ctrl-day-th">07</th>
                                    <th class="ctrl-day-th">08</th>
                                    <th class="ctrl-day-th">09</th>
                                    <th class="ctrl-day-th">10</th>
                                    <th class="ctrl-day-th">11</th>
                                    <th class="ctrl-day-th">12</th>
                                    <th class="ctrl-day-th">13</th>
                                    <th class="ctrl-day-th">14</th>
                                    <th class="ctrl-day-th">15</th>
                                    <th class="ctrl-day-th">16</th>
                                    <th class="ctrl-day-th">17</th>
                                    <th class="ctrl-day-th">18</th>
                                    <th class="ctrl-day-th">19</th>
                                    <th class="ctrl-day-th">20</th>
                                    <th class="ctrl-day-th">21</th>
                                    <th class="ctrl-day-th">22</th>
                                    <th class="ctrl-day-th">23</th>
                                    <th class="ctrl-day-th">24</th>
                                    <th class="ctrl-day-th">25</th>
                                    <th class="ctrl-day-th">26</th>
                                    <th class="ctrl-day-th">27</th>
                                    <th class="ctrl-day-th">28</th>
                                    <th class="ctrl-day-th">29</th>
                                    <th class="ctrl-day-th">30</th>
                                    <th class="ctrl-day-th">31</th>
                                    <th class="ctrl-col-th" style="width: 90px;">APOYO INSTITUCIONAL</th>
                                    <th class="ctrl-col-th ctrl-calc-col" style="width: 85px;">TOTAL SURTIDO</th>
                                    <th class="ctrl-col-th ctrl-calc-col" style="width: 95px;">INVENTARIO DISPONIBLE</th>
                                </tr>
                            </thead>
                            <tbody id="ctrlMatrixTableBody">
                                <tr><td colspan="45" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando matriz de movimientos...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- SUB-VISTA 2: ENTRADAS MANUALES -->
                <div id="ctrlViewEntradas" class="ctrl-subtab-view">
                    <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
                            <div>
                                <h3 style="margin: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <i class="fa-solid fa-arrow-down-long" style="color: var(--success);"></i>
                                    Captura de Entradas Manuales (Base Independiente)
                                </h3>
                                <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0.2rem 0 0 0;">
                                    Cada registro se almacena por Clave + Lote con sus datos administrativos. La descripción se autocompleta automáticamente según la clave ingresada.
                                </p>
                            </div>
                            <div style="display: flex; gap: 0.5rem;">
                                <button type="button" class="btn btn-primary" onclick="openModalControlEntrada()" style="padding: 0.55rem 1rem;">
                                    <i class="fa-solid fa-plus"></i> Nueva Entrada Manual
                                </button>
                            </div>
                        </div>

                        <div class="table-responsive" style="max-height: 65vh; overflow-y: auto;">
                            <table>
                                <thead style="position: sticky; top: 0; z-index: 10;">
                                    <tr>
                                        <th>Fecha Entrada</th>
                                        <th>Clave</th>
                                        <th>Lote</th>
                                        <th>Descripción</th>
                                        <th>Proveedor</th>
                                        <th>UDM</th>
                                        <th>Caducidad</th>
                                        <th>Fabricación</th>
                                        <th>Inv. Inicial</th>
                                        <th>Ajuste</th>
                                        <th>Recibida</th>
                                        <th>Total Entrada</th>
                                        <th>Almacén</th>
                                        <th>Procedimiento</th>
                                        <th>Contrato</th>
                                        <th>Folio</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody id="ctrlEntradasTableBody">
                                    <tr><td colspan="17" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando entradas manuales...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- SUB-VISTA 3: SALIDAS DESDE PDF -->
                <div id="ctrlViewSalidas" class="ctrl-subtab-view">
                    <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 1.25rem;">
                        <div style="background: rgba(37, 99, 235, 0.06); border: 1px solid rgba(37, 99, 235, 0.2); border-radius: 8px; padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                            <div>
                                <h3 style="margin: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem; color: var(--primary);">
                                    <i class="fa-solid fa-file-pdf"></i>
                                    Importador Inteligente de Salidas PDF (FEFO)
                                </h3>
                                <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0.25rem 0 0 0;">
                                    Sube las Hojas de Entrega/Pedidos en PDF día con día. El sistema extrae <strong>Fecha, Clave y Cantidad</strong>, valida la clave en el catálogo y <strong>asigna automáticamente el lote con caducidad más próxima (FEFO)</strong> que cuente con existencias.
                                </p>
                            </div>
                            <div style="display: flex; gap: 0.5rem;">
                                <button type="button" class="btn btn-primary" onclick="openModalControlPdf()">
                                    <i class="fa-solid fa-cloud-arrow-up"></i> Cargar PDFs de Salidas
                                </button>
                                <button type="button" class="btn btn-danger" onclick="vaciarSalidasPdfControl()" title="Vaciar únicamente las salidas de PDFs importadas">
                                    <i class="fa-solid fa-trash-can"></i> Vaciar Salidas PDF
                                </button>
                            </div>
                        </div>

                        <!-- Tabla de Salidas Importadas -->
                        <div class="table-responsive" style="max-height: 65vh; overflow-y: auto;">
                            <table>
                                <thead style="position: sticky; top: 0; z-index: 10;">
                                    <tr>
                                        <th>Fecha Salida</th>
                                        <th>Día (Mes)</th>
                                        <th>Clave</th>
                                        <th>Descripción</th>
                                        <th>Cantidad Surtida</th>
                                        <th>Lote Asignado (FEFO)</th>
                                        <th>Caducidad Lote</th>
                                        <th>Folio Pedido</th>
                                        <th>Archivo Origen</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody id="ctrlSalidasTableBody">
                                    <tr><td colspan="10" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando salidas registradas...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- SUB-VISTA 4: APOYO INSTITUCIONAL -->
                <div id="ctrlViewApoyos" class="ctrl-subtab-view">
                    <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
                            <div>
                                <h3 style="margin: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <i class="fa-solid fa-handshake-angle" style="color: #8b5cf6;"></i>
                                    Captura de Apoyo Institucional (Salida Manual)
                                </h3>
                                <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0.2rem 0 0 0;">
                                    Registro de transferencias y apoyos a otras instituciones (IMSS, ISSSTE, Hospitales, etc.). Se descuenta como salida y alimenta automáticamente la columna "Apoyo Institucional" del reporte diario.
                                </p>
                            </div>
                            <button type="button" class="btn btn-primary" onclick="openModalControlApoyo()" style="background: #8b5cf6; border-color: #7c3aed;">
                                <i class="fa-solid fa-plus"></i> Registrar Apoyo Institucional
                            </button>
                        </div>

                        <div class="table-responsive" style="max-height: 65vh; overflow-y: auto;">
                            <table>
                                <thead style="position: sticky; top: 0; z-index: 10;">
                                    <tr>
                                        <th>Fecha</th>
                                        <th>Clave</th>
                                        <th>Descripción</th>
                                        <th>Lote</th>
                                        <th>Institución Receptora</th>
                                        <th>Cantidad</th>
                                        <th>Folio / Observaciones</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody id="ctrlApoyosTableBody">
                                    <tr><td colspan="8" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando registros de apoyo institucional...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- SUB-VISTA 5: CATÁLOGOS (CLAVES, PROVEEDORES, UNIDADES) -->
                <div id="ctrlViewCatalogos" class="ctrl-subtab-view">
                    <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 1.5rem;">
                        
                        <!-- Sección A: Catálogo de Claves y Descripciones -->
                        <div style="border: 1px solid var(--card-border); border-radius: var(--radius); padding: 1.25rem; background: var(--card-bg);">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem;">
                                <div>
                                    <h4 style="margin: 0; font-size: 1.05rem; display: flex; align-items: center; gap: 0.5rem;">
                                        <i class="fa-solid fa-barcode" style="color: var(--primary);"></i>
                                        Catálogo de Claves y Descripciones
                                    </h4>
                                    <span style="font-size: 0.8rem; color: var(--text-muted);">Al escribir la clave en cualquier formulario de entrada o apoyo, la descripción y unidad se autocompletan al instante.</span>
                                </div>
                                <div style="display: flex; gap: 0.5rem;">
                                    <button type="button" class="btn btn-secondary" onclick="syncControlCatalogo()" title="Importar automáticamente todas las claves únicas desde el inventario del sistema">
                                        <i class="fa-solid fa-rotate"></i> Sincronizar desde Inventario
                                    </button>
                                    <button type="button" class="btn btn-primary" onclick="openModalControlCatalogo()">
                                        <i class="fa-solid fa-plus"></i> Nueva Clave
                                    </button>
                                </div>
                            </div>

                            <div class="table-responsive" style="max-height: 40vh; overflow-y: auto;">
                                <table>
                                    <thead style="position: sticky; top: 0; z-index: 10;">
                                        <tr>
                                            <th>Clave</th>
                                            <th>Descripción</th>
                                            <th>UDM Default</th>
                                            <th>Proveedor Default</th>
                                            <th>Procedimiento</th>
                                            <th>Contrato</th>
                                            <th>Reg. Sanitario</th>
                                            <th>Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody id="ctrlCatalogoTableBody">
                                        <tr><td colspan="8" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando catálogo...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- Grid 2 Columnas: Proveedores y Unidades de Medida -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem;">
                            
                            <!-- Proveedores -->
                            <div style="border: 1px solid var(--card-border); border-radius: var(--radius); padding: 1.25rem; background: var(--card-bg);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                                    <h4 style="margin: 0; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem;">
                                        <i class="fa-solid fa-truck" style="color: #ea580c;"></i>
                                        Catálogo de Proveedores
                                    </h4>
                                    <button type="button" class="btn btn-secondary" onclick="openModalControlProveedor()" style="padding: 0.35rem 0.7rem; font-size: 0.78rem;">
                                        <i class="fa-solid fa-plus"></i> Agregar Proveedor
                                    </button>
                                </div>
                                <div class="table-responsive" style="max-height: 30vh; overflow-y: auto;">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Nombre del Proveedor</th>
                                                <th>Contacto / RFC</th>
                                            </tr>
                                        </thead>
                                        <tbody id="ctrlProveedoresTableBody">
                                            <tr><td colspan="2" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando proveedores...</td></tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- Unidades de Medida -->
                            <div style="border: 1px solid var(--card-border); border-radius: var(--radius); padding: 1.25rem; background: var(--card-bg);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                                    <h4 style="margin: 0; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem;">
                                        <i class="fa-solid fa-scale-balanced" style="color: var(--accent);"></i>
                                        Catálogo de Unidades de Medida
                                    </h4>
                                    <button type="button" class="btn btn-secondary" onclick="openModalControlUnidad()" style="padding: 0.35rem 0.7rem; font-size: 0.78rem;">
                                        <i class="fa-solid fa-plus"></i> Agregar Unidad
                                    </button>
                                </div>
                                <div class="table-responsive" style="max-height: 30vh; overflow-y: auto;">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Código (UDM)</th>
                                                <th>Descripción</th>
                                            </tr>
                                        </thead>
                                        <tbody id="ctrlUnidadesTableBody">
                                            <tr><td colspan="2" class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><br>Cargando unidades...</td></tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                        </div>

                    </div>
                </div>

            </div>
"""

# 4. Modals
MODALS_CONTENT = """
    <!-- ========================================================
         MODALES: CONTROL DE INVENTARIO POR MOVIMIENTOS
         ======================================================== -->

    <!-- Modal 1: Entrada Manual -->
    <div class="modal-overlay" id="modalControlEntrada">
        <div class="modal-container" style="max-width: 720px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-arrow-down-long" style="color: var(--success);"></i> <span id="ctrlEntradaModalTitle">Registrar Entrada Manual</span></h3>
                <button class="modal-close" onclick="closeModal('modalControlEntrada')">&times;</button>
            </div>
            <form id="ctrlEntradaForm" onsubmit="submitControlEntrada(event)">
                <input type="hidden" id="ctrlEntradaId" value="">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Clave * (Autocompleta descripción)</label>
                            <input type="text" class="form-control" id="ctrl_e_clave" required placeholder="Ej. 010.000.0104.00" oninput="onCtrlEntradaClaveInput()">
                        </div>
                        <div class="form-group">
                            <label>Lote *</label>
                            <input type="text" class="form-control" id="ctrl_e_lote" required placeholder="Ej. LOT2026A">
                        </div>
                        <div class="form-group col-span-2">
                            <label>Descripción del Insumo (Automática según catálogo)</label>
                            <input type="text" class="form-control" id="ctrl_e_descripcion" required placeholder="Se completará automáticamente...">
                        </div>
                        <div class="form-group">
                            <label>Proveedor (Lista desplegable)</label>
                            <select class="form-control" id="ctrl_e_proveedor">
                                <option value="">Seleccione proveedor...</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Unidad de Medida (UDM)</label>
                            <select class="form-control" id="ctrl_e_udm">
                                <option value="PZA">PZA</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Fecha de Entrada</label>
                            <input type="date" class="form-control" id="ctrl_e_fecha_entrada">
                        </div>
                        <div class="form-group">
                            <label>Fecha de Caducidad *</label>
                            <input type="date" class="form-control" id="ctrl_e_caducidad" required>
                        </div>
                        <div class="form-group">
                            <label>Fecha de Fabricación</label>
                            <input type="date" class="form-control" id="ctrl_e_fabricacion">
                        </div>
                        <div class="form-group">
                            <label>Almacén</label>
                            <input type="text" class="form-control" id="ctrl_e_almacen" value="CS ALMACEN 2022">
                        </div>
                        
                        <!-- Cantidades y Cálculos -->
                        <div class="form-group" style="background: rgba(37,99,235,0.04); padding: 8px; border-radius: 6px;">
                            <label style="font-weight: 700; color: var(--primary);">Inventario Inicial (Fijo)</label>
                            <input type="number" step="any" class="form-control" id="ctrl_e_inv_inicial" value="0" oninput="recalcControlEntradaTotals()">
                        </div>
                        <div class="form-group" style="background: rgba(245,158,11,0.04); padding: 8px; border-radius: 6px;">
                            <label style="font-weight: 700; color: var(--warning);">Entrada por Ajuste</label>
                            <input type="number" step="any" class="form-control" id="ctrl_e_ajuste" value="0" oninput="recalcControlEntradaTotals()">
                        </div>
                        <div class="form-group" style="background: rgba(16,185,129,0.04); padding: 8px; border-radius: 6px;">
                            <label style="font-weight: 700; color: var(--success);">Cantidad Recibida</label>
                            <input type="number" step="any" class="form-control" id="ctrl_e_recibida" value="0" oninput="recalcControlEntradaTotals()">
                        </div>
                        <div class="form-group" style="background: rgba(16,185,129,0.12); padding: 8px; border-radius: 6px;">
                            <label style="font-weight: 800; color: #047857;">Total Entrada Mensual</label>
                            <input type="number" step="any" class="form-control" id="ctrl_e_total_mensual" readonly style="font-weight: 800; color: #047857; background: #ffffff;">
                        </div>

                        <!-- Opcionales Administrativos Columnas A:D -->
                        <div class="form-group">
                            <label>No. Procedimiento (Opcional)</label>
                            <input type="text" class="form-control" id="ctrl_e_procedimiento" placeholder="Ej. IA-012000999-E1-2026">
                        </div>
                        <div class="form-group">
                            <label>No. Contrato (Opcional)</label>
                            <input type="text" class="form-control" id="ctrl_e_contrato" placeholder="Ej. CONTRATO-2026-001">
                        </div>
                        <div class="form-group">
                            <label>Registro Sanitario (Opcional)</label>
                            <input type="text" class="form-control" id="ctrl_e_registro_sanitario" placeholder="Ej. 123M2020 SSA">
                        </div>
                        <div class="form-group">
                            <label>Folio Administrativo (Opcional)</label>
                            <input type="text" class="form-control" id="ctrl_e_folio" placeholder="Ej. FOL-9921">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('modalControlEntrada')">Cancelar</button>
                    <button type="submit" class="btn btn-success"><i class="fa-solid fa-floppy-disk"></i> Guardar Entrada</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal 2: Apoyo Institucional -->
    <div class="modal-overlay" id="modalControlApoyo">
        <div class="modal-container" style="max-width: 600px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-handshake-angle" style="color: #8b5cf6;"></i> Registrar Apoyo Institucional</h3>
                <button class="modal-close" onclick="closeModal('modalControlApoyo')">&times;</button>
            </div>
            <form id="ctrlApoyoForm" onsubmit="submitControlApoyo(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Fecha de Salida *</label>
                            <input type="date" class="form-control" id="ctrl_a_fecha" required>
                        </div>
                        <div class="form-group">
                            <label>Institución Receptora *</label>
                            <input type="text" class="form-control" id="ctrl_a_institucion" required placeholder="Ej. IMSS BIENESTAR / ISSSTE...">
                        </div>
                        <div class="form-group">
                            <label>Clave * (Autocompleta descripción)</label>
                            <input type="text" class="form-control" id="ctrl_a_clave" required placeholder="Ej. 010.000.0104.00" oninput="onCtrlApoyoClaveInput()">
                        </div>
                        <div class="form-group">
                            <label>Lote con Existencia *</label>
                            <select class="form-control" id="ctrl_a_lote" required>
                                <option value="">Escriba la clave primero...</option>
                            </select>
                        </div>
                        <div class="form-group col-span-2">
                            <label>Descripción del Insumo</label>
                            <input type="text" class="form-control" id="ctrl_a_descripcion" readonly style="background: var(--input-bg);">
                        </div>
                        <div class="form-group">
                            <label>Cantidad a Transferir *</label>
                            <input type="number" step="any" min="0.01" class="form-control" id="ctrl_a_cantidad" required placeholder="0">
                        </div>
                        <div class="form-group">
                            <label>Folio / Observaciones</label>
                            <input type="text" class="form-control" id="ctrl_a_folio" placeholder="Ej. OFICIO-APOYO-884">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('modalControlApoyo')">Cancelar</button>
                    <button type="submit" class="btn btn-primary" style="background: #8b5cf6; border-color: #7c3aed;">
                        <i class="fa-solid fa-check"></i> Registrar Salida por Apoyo
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal 3: Subir PDFs de Salidas -->
    <div class="modal-overlay" id="modalControlPdf">
        <div class="modal-container" style="max-width: 620px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-file-pdf" style="color: #dc2626;"></i> Cargar Hojas de Entrega de Pedidos (PDF)</h3>
                <button class="modal-close" onclick="closeModal('modalControlPdf')">&times;</button>
            </div>
            <div class="modal-body">
                <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
                    Seleccione uno o varios archivos PDF de Hojas de Pedido o Reporte de Entrega. El sistema leerá automáticamente la <strong>Fecha</strong> (colocándola en el día 01..31), la <strong>Clave</strong> y la <strong>Cantidad Surtida</strong>, asignando el lote con la caducidad más próxima (<strong>FEFO</strong>).
                </p>
                <div class="upload-area" id="ctrlPdfDropZone" onclick="document.getElementById('ctrlPdfFileInput').click()" style="padding: 2rem 1rem; border: 2px dashed #dc2626; border-radius: 8px; text-align: center; cursor: pointer; background: rgba(220, 38, 38, 0.04);">
                    <i class="fa-solid fa-file-pdf" style="font-size: 2.5rem; color: #dc2626; margin-bottom: 0.5rem;"></i>
                    <h4 style="margin: 0.25rem 0; font-size: 1rem;">Haz clic para seleccionar o arrastra tus archivos PDF</h4>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0;">Soporta selección múltiple de PDFs</p>
                    <div id="ctrlPdfSelectedList" style="margin-top: 0.75rem; text-align: left; max-height: 120px; overflow-y: auto; font-size: 0.82rem; display: none;"></div>
                </div>
                <input type="file" id="ctrlPdfFileInput" accept=".pdf" multiple style="display: none;" onchange="handleControlPdfSelected(this)">
                <div id="ctrlPdfProgress" style="display: none; margin-top: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: #dc2626; font-weight: 600; font-size: 0.85rem;">
                        <i class="fa-solid fa-spinner fa-spin"></i>
                        <span>Extrayendo partidas y asignando lotes por caducidad (FEFO)...</span>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalControlPdf')">Cancelar</button>
                <button type="button" class="btn btn-primary" id="btnUploadCtrlPdf" onclick="submitControlPdf()" disabled>
                    <i class="fa-solid fa-upload"></i> Procesar Salidas PDF
                </button>
            </div>
        </div>
    </div>

    <!-- Modal 4: Catálogo Clave / Insumo -->
    <div class="modal-overlay" id="modalControlCatalogo">
        <div class="modal-container" style="max-width: 600px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-barcode" style="color: var(--primary);"></i> <span id="ctrlCatModalTitle">Agregar Clave al Catálogo</span></h3>
                <button class="modal-close" onclick="closeModal('modalControlCatalogo')">&times;</button>
            </div>
            <form id="ctrlCatForm" onsubmit="submitControlCatalogo(event)">
                <input type="hidden" id="ctrlCatId" value="">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group col-span-2">
                            <label>Clave *</label>
                            <input type="text" class="form-control" id="ctrl_c_clave" required placeholder="Ej. 010.000.0104.00">
                        </div>
                        <div class="form-group col-span-2">
                            <label>Descripción / Concepto *</label>
                            <input type="text" class="form-control" id="ctrl_c_descripcion" required placeholder="Ej. PARACETAMOL TABLETA 500 MG...">
                        </div>
                        <div class="form-group">
                            <label>UDM por Defecto</label>
                            <select class="form-control" id="ctrl_c_udm"></select>
                        </div>
                        <div class="form-group">
                            <label>Proveedor por Defecto</label>
                            <select class="form-control" id="ctrl_c_proveedor"></select>
                        </div>
                        <div class="form-group">
                            <label>No. Procedimiento (Opcional)</label>
                            <input type="text" class="form-control" id="ctrl_c_procedimiento" placeholder="Ej. IA-012000999-E1-2026">
                        </div>
                        <div class="form-group">
                            <label>No. Contrato (Opcional)</label>
                            <input type="text" class="form-control" id="ctrl_c_contrato" placeholder="Ej. CONTRATO-2026-001">
                        </div>
                        <div class="form-group col-span-2">
                            <label>Registro Sanitario (Opcional)</label>
                            <input type="text" class="form-control" id="ctrl_c_registro_sanitario" placeholder="Ej. 123M2020 SSA">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('modalControlCatalogo')">Cancelar</button>
                    <button type="submit" class="btn btn-primary"><i class="fa-solid fa-floppy-disk"></i> Guardar en Catálogo</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal 5: Agregar Proveedor -->
    <div class="modal-overlay" id="modalControlProveedor">
        <div class="modal-container" style="max-width: 480px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-truck" style="color: #ea580c;"></i> Agregar Proveedor al Catálogo</h3>
                <button class="modal-close" onclick="closeModal('modalControlProveedor')">&times;</button>
            </div>
            <form id="ctrlProvForm" onsubmit="submitControlProveedor(event)">
                <div class="modal-body">
                    <div class="form-group" style="margin-bottom: 1rem;">
                        <label>Nombre o Razón Social del Proveedor *</label>
                        <input type="text" class="form-control" id="ctrl_p_nombre" required placeholder="Ej. LABORATORIOS PISA, S.A. DE C.V.">
                    </div>
                    <div class="form-group">
                        <label>Contacto / RFC / Teléfono (Opcional)</label>
                        <input type="text" class="form-control" id="ctrl_p_contacto" placeholder="Ej. RFC: PIS800101XYZ / Tel: 33-1234-5678">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('modalControlProveedor')">Cancelar</button>
                    <button type="submit" class="btn btn-primary"><i class="fa-solid fa-plus"></i> Guardar Proveedor</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal 6: Agregar Unidad de Medida -->
    <div class="modal-overlay" id="modalControlUnidad">
        <div class="modal-container" style="max-width: 480px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-scale-balanced" style="color: var(--accent);"></i> Agregar Unidad de Medida</h3>
                <button class="modal-close" onclick="closeModal('modalControlUnidad')">&times;</button>
            </div>
            <form id="ctrlUnidadForm" onsubmit="submitControlUnidad(event)">
                <div class="modal-body">
                    <div class="form-group" style="margin-bottom: 1rem;">
                        <label>Código de Unidad (UDM) *</label>
                        <input type="text" class="form-control" id="ctrl_u_codigo" required placeholder="Ej. PZA, CAJA, FCO, ENV..." style="text-transform: uppercase;">
                    </div>
                    <div class="form-group">
                        <label>Descripción / Nombre Completo (Opcional)</label>
                        <input type="text" class="form-control" id="ctrl_u_descripcion" placeholder="Ej. PIEZA, CAJA CON 100 PZAS...">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('modalControlUnidad')">Cancelar</button>
                    <button type="submit" class="btn btn-primary"><i class="fa-solid fa-plus"></i> Guardar Unidad</button>
                </div>
            </form>
        </div>
    </div>
"""

print("Build injection prepared successfully.")
