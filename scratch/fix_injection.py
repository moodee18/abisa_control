# -*- coding: utf-8 -*-
import io

INDEX_PATH = r"c:\Users\moode\.gemini\antigravity-ide\scratch\abisalud_automation\templates\index.html"

from build_injection import CSS_CODE
from execute_injection import JS_CODE

with io.open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. CSS
if ".ctrl-pills-bar" not in content:
    print("Injecting CSS...")
    content = content.replace("</style>", CSS_CODE + "\n    </style>", 1)
else:
    print("CSS already present.")

# 2. JS Controller
if "async function loadControlMovimientos" not in content:
    print("Injecting JS Controller...")
    
    # Update switchTab
    switch_old = "if (tabId === 'tab-marbetes') renderMarbetesPreview();"
    switch_new = "if (tabId === 'tab-marbetes') renderMarbetesPreview();\n            if (tabId === 'tab-control-movimientos') loadControlMovimientos();"
    if switch_old in content:
        content = content.replace(switch_old, switch_new, 1)

    # Update exportCurrentReport
    export_old = "if (activeTab === 'tab-clues') {"
    export_new = """if (activeTab === 'tab-control-movimientos') {
                exportControlMovimientosExcel();
                return;
            }
            if (activeTab === 'tab-clues') {"""
    if export_old in content:
        content = content.replace(export_old, export_new, 1)

    # Update refreshAll
    refresh_old = "if (activeTab === 'tab-logs') loadLogs();"
    refresh_new = "if (activeTab === 'tab-logs') loadLogs();\n            if (activeTab === 'tab-control-movimientos') loadControlMovimientos();"
    if refresh_old in content:
        content = content.replace(refresh_old, refresh_new, 1)

    # Update setupDZ
    dz_old = "setupDZ('clientSyncDropZone', 'clientSyncFileInput', handleClientSyncFile);"
    dz_new = "setupDZ('clientSyncDropZone', 'clientSyncFileInput', handleClientSyncFile);\n            setupDZ('ctrlPdfDropZone', 'ctrlPdfFileInput', handleControlPdfSelected);"
    if dz_old in content:
        content = content.replace(dz_old, dz_new, 1)

    # Insert JS Controller right before setupDZ
    target_js = "        // Setup dropzones para modales"
    replacement_js = JS_CODE + "\n        // Setup dropzones para modales"
    if target_js in content:
        content = content.replace(target_js, replacement_js, 1)
else:
    print("JS controller already present.")

with io.open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated index.html successfully.")
