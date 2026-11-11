import os
import openpyxl

os.makedirs("data/plantillas", exist_ok=True)

# 1. Plantilla Alta de Almacenes
wb1 = openpyxl.Workbook()
ws1 = wb1.active
ws1.title = "Almacenes"
ws1.append(["Almacén"])
ws1.append(["ADVANTA PHARMA SAPI DE CV"])
ws1.append(["AGYPROM"])
ws1.append(["AMBIDERM SA DE CV"])
ws1.append(["DEGASA SA DE C.V CONS"])
ws1.append(["GRUPO INDUSTRIAL POSEIDON S.A DE C.V"])
ws1.column_dimensions['A'].width = 45
wb1.save("data/plantillas/Plantilla_Alta_Almacenes.xlsx")
print("Saved data/plantillas/Plantilla_Alta_Almacenes.xlsx")

# 2. Plantilla Seguimiento de Inventario
wb2 = openpyxl.Workbook()
ws2 = wb2.active
ws2.title = "Hoja2"
ws2.append(["Código Barras", "Clave Cliente", "Descripción", "Lote", "Almacén", "Cantidad", "Caducidad"])
ws2.append(["7506022331816", "060.164.0030", "SONDA PARA DRENAJE URINARIO", "2510950001", "ADVANTA PHARMA SAPI DE CV", 10, "2030-10-25"])
ws2.append(["7503018314396", "060.166.3347", "SONDA PARA ASPIRACION CAL 14", "2604097", "ADVANTA PHARMA SAPI DE CV", 25, "2028-04-30"])
ws2.append(["2010000066621", "060.207.0013", "CIRCUITO VENTILACIÓN ANESTESIA", "0004328539", "ABASTECEDOR TERAPEUTICO SA DE C.V", 90, "2030-07-19"])

for col, w in zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], [18, 16, 35, 15, 35, 12, 14]):
    ws2.column_dimensions[col].width = w
wb2.save("data/plantillas/Plantilla_Seguimiento_Inventario.xlsx")
print("Saved data/plantillas/Plantilla_Seguimiento_Inventario.xlsx")

