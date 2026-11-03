# -*- coding: utf-8 -*-
"""
Script de inyección del módulo "Control de Inventario por Movimientos" en templates/index.html
"""
import os
import sys

INDEX_PATH = r"c:\Users\moode\.gemini\antigravity-ide\scratch\abisalud_automation\templates\index.html"

# 1. CSS Styles
CSS_INJECTION = """
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
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
        }

        .ctrl-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.25rem;
        }

        .ctrl-kpi-card {
            background: var(--card-bg);
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
            max-height: 70vh;
        }

        .ctrl-matrix-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
            min-width: 1950px;
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
            font-size: 0.75rem;
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
            min-width: 34px;
            padding: 6px 2px;
            position: sticky;
            top: 0;
            z-index: 5;
        }

        .ctrl-matrix-table td.text-left {
            text-align: left !important;
        }

        .ctrl-calc-col {
            background: rgba(16, 185, 129, 0.08);
            font-weight: 700;
        }

        .ctrl-day-cell.has-val {
            background: rgba(37, 99, 235, 0.12);
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
            background: rgba(239, 68, 68, 0.1);
        }

        .ctrl-subtab-view {
            display: none;
        }

        .ctrl-subtab-view.active {
            display: block;
        }
"""

print("Preparing injection script...")
