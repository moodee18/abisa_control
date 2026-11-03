import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws_rep = wb.active
ws_rep.title = "Reporte Diario"

header_fill = PatternFill(start_color="1E7145", end_color="1E7145", fill_type="solid")
header_font = Font(name="Aptos Narrow", size=10, bold=True, color="FFFFFF")
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
thin_side = Side(style="thin", color="135824")
border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

# Headers
headers = [
    "FOLIO / ADM", "PROVEEDOR", "CLAVE", "DESCRIPCIÓN", "UDM", "LOTE", "F_CAD", "F_FAB",
    "INVENTARIO INICIAL", "ENTRADA AJUSTE", "CANTIDAD RECIBIDA", "INV. TOTAL MENSUAL"
] + [str(d) for d in range(1, 32)] + ["APOYO INSTITUCIONAL", "TOTAL SURTIDO", "INVENTARIO DISPONIBLE"]

# Banner
ws_rep.merge_cells("M1:AQ1")
b_cell = ws_rep["M1"]
b_cell.value = "SALIDAS OCTUBRE 2026"
b_cell.fill = header_fill
b_cell.font = Font(name="Aptos Narrow", size=11, bold=True, color="FFFFFF")
b_cell.alignment = center_align

for c in range(13, 44):
    cell = ws_rep.cell(1, c)
    cell.fill = header_fill
    cell.border = border_cell

for idx, h in enumerate(headers, 1):
    c = ws_rep.cell(2, idx, h)
    c.fill = header_fill
    c.font = header_font
    c.alignment = center_align
    c.border = border_cell

# Sample row 3
ws_rep.cell(3, 1, "E-2026-001")
ws_rep.cell(3, 2, "PROVEEDOR 1")
ws_rep.cell(3, 3, "010.000.2306.00")
ws_rep.cell(3, 4, "MANITOL 20 G 250 ML")
ws_rep.cell(3, 5, "PZA")
ws_rep.cell(3, 6, "73N5E0143")
ws_rep.cell(3, 7, "2027-05-10")
ws_rep.cell(3, 8, "2025-05-10")
ws_rep.cell(3, 9, 100) # Inv. inicial
ws_rep.cell(3, 10, 10) # Ajuste
ws_rep.cell(3, 11, 40) # Recibida
ws_rep.cell(3, 12, "=I3+J3+K3") # Total mensual

for d in range(1, 32):
    ws_rep.cell(3, 12 + d, 2 if d == 15 else 0)

ws_rep.cell(3, 44, 5) # Apoyo institucional
ws_rep.cell(3, 45, "=SUM(M3:AQ3)+AR3") # Total surtido
ws_rep.cell(3, 46, "=L3-AS3") # Inv. disponible

# Test creating other sheets
wb.create_sheet(title="Entradas")
wb.create_sheet(title="Salidas PDF")
wb.create_sheet(title="Apoyo Institucional")
wb.create_sheet(title="Catálogos")

wb.save("data/test_5sheets_export.xlsx")
wb.close()
print("Saved 5-sheet test workbook successfully!")
