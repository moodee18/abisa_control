import sys
import os
import re
import ssl
import json
import shutil
import zipfile
import urllib.request
import time

sys.path.insert(0, '.')
from downloader import SiiaDownloader

def sanitize_filename(name):
    # Replace invalid chars with underscore
    clean = re.sub(r'[\\/*?:"<>|.]', '_', name)
    clean = re.sub(r'\s+', '_', clean).strip('_')
    return clean

def main():
    print("=== INICIANDO DESCARGA DE LOS 76 PDFS DE ALTA DE INVENTARIO ===")
    
    # 1. Obtener sesión activa
    dl = SiiaDownloader()
    cookies = dl.get_authenticated_session_cookies()
    cookie_header = '; '.join([f'{k}={v}' for k, v in cookies.items()])
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # 2. Cargar diccionario de seguimiento (almacen -> inventario ID)
    seg = {}
    with open('scratch/seguimiento_almacenes.txt', encoding='utf-8') as f:
        for line in f:
            if '|' in line:
                v, n = line.strip().split('|', 1)
                seg[n.strip().upper()] = v.strip()
                
    # 3. Cargar lista de los 76 almacenes
    with open('scratch/results_altas.json', encoding='utf-8') as f:
        altas = json.load(f)
        
    print(f"Total almacenes a procesar: {len(altas)}")
    
    # Directorios destino
    dest_dir = os.path.abspath("downloads/pdfs_inventario_cs_almacen_2022")
    os.makedirs(dest_dir, exist_ok=True)
    
    user_downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Inventarios_CS_ALMACEN_2022")
    os.makedirs(user_downloads_dir, exist_ok=True)
    
    results = []
    
    for idx, item in enumerate(altas, start=1):
        num = item['num']
        nom = item['nombre'].strip()
        almacen_id = item['id']
        inv_id = seg.get(nom.upper())
        
        if not inv_id:
            # Fallback búsqueda parcial
            for k, v in seg.items():
                if nom.upper() in k or k in nom.upper():
                    inv_id = v
                    break
                    
        clean_name = f"{num:02d}_{sanitize_filename(nom)}.pdf"
        file_path = os.path.join(dest_dir, clean_name)
        
        # URL principal: inventario_periodico/pdf.php
        u1 = f"https://siia.abisalud.com/almacen/inventarios/inventario_periodico/pdf.php?localidad=1836&almacen={almacen_id}&idInv={inv_id}"
        u2 = f"https://siia.abisalud.com/almacen/inventarios/seguimiento_inventario/pdf_seguimiento_inventario.php?localidad=1836&inventario={inv_id}"
        
        data = None
        used_url = None
        
        for u in [u1, u2]:
            try:
                req = urllib.request.Request(u, headers={'Cookie': cookie_header, 'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
                    content = r.read()
                    if content.startswith(b'%PDF') and len(content) > 1000:
                        data = content
                        used_url = u
                        break
            except Exception as e:
                print(f"Error descargando {nom} desde {u}: {e}")
                time.sleep(1)
                
        if data:
            with open(file_path, "wb") as f:
                f.write(data)
            size_kb = len(data) / 1024
            print(f"[{num:02d}/76] OK ({size_kb:.1f} KB): {clean_name} (Alm: {almacen_id}, Inv: {inv_id})")
            results.append({
                "num": num,
                "nombre": nom,
                "almacen_id": almacen_id,
                "inventario_id": inv_id,
                "archivo": clean_name,
                "size_kb": round(size_kb, 1),
                "estado": "OK"
            })
        else:
            print(f"[{num:02d}/76] ERROR: No se pudo descargar PDF para {nom}")
            results.append({
                "num": num,
                "nombre": nom,
                "almacen_id": almacen_id,
                "inventario_id": inv_id,
                "archivo": clean_name,
                "size_kb": 0,
                "estado": "ERROR"
            })
            
        time.sleep(0.3)
        
    # Guardar reporte de descargas
    with open("scratch/reporte_descargas_pdf.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    # Crear ZIP en downloads/
    zip_path = os.path.abspath("downloads/PDFs_Inventario_CS_ALMACEN_2022.zip")
    print(f"\nGenerando archivo ZIP en {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for r in results:
            if r['estado'] == 'OK':
                fpath = os.path.join(dest_dir, r['archivo'])
                zipf.write(fpath, arcname=r['archivo'])
                
    # Copiar a C:\Users\moode\Downloads\
    print(f"Copiando archivos a la carpeta Descargas del usuario ({user_downloads_dir})...")
    for r in results:
        if r['estado'] == 'OK':
            src = os.path.join(dest_dir, r['archivo'])
            dst = os.path.join(user_downloads_dir, r['archivo'])
            shutil.copy2(src, dst)
            
    user_zip_path = os.path.join(os.path.expanduser("~"), "Downloads", "PDFs_Inventario_CS_ALMACEN_2022.zip")
    shutil.copy2(zip_path, user_zip_path)
    print(f"ZIP copiado a: {user_zip_path}")
    
    ok_count = sum(1 for r in results if r['estado'] == 'OK')
    print(f"\n=== PROCESO COMPLETADO: {ok_count}/76 PDFs DESCARGADOS CON ÉXITO ===")

if __name__ == '__main__':
    main()

