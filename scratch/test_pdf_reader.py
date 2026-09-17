import pdfplumber, re, glob
from pathlib import Path

def parse_hoja_pedido(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        all_items = []
        doc_info = {}
        for p_no, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            if p_no == 0:
                # Pedido e.g. T N-193823 or N-197105
                ped_m = re.search(r'\(T\s+([A-Za-z0-9\-]+)', text) or re.search(r'\b(N-\d+)\b', text)
                doc_info['pedido'] = ped_m.group(1) if ped_m else ''
                
                # Folio
                fol_m = re.search(r'Folio de Salida\s*[\r\n]+(\d+)', text)
                doc_info['folio_salida'] = fol_m.group(1) if fol_m else ''
                
                # Fecha surtido
                fech_m = re.search(r'Fecha de Surtido:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}(?:\s+[0-9]{2}:[0-9]{2}:[0-9]{2})?)', text)
                doc_info['fecha_surtido'] = fech_m.group(1) if fech_m else ''
                
                # Localidad
                loc_m = re.search(r'Localidad:\s*([^\r\n]+)', text)
                doc_info['localidad'] = loc_m.group(1).strip() if loc_m else ''

            lines = text.splitlines()
            item_pattern = re.compile(r'^(\d{7,16})\s+([0-9]{3}\.[0-9]{3}\.[0-9]{3,5}(?:\.[0-9]{2})?)\s+(.*)$')
            tail_pattern = re.compile(r'(\d+)\s+(\d+)(?:\s+\d+)?\s+([A-Za-z0-9\-_]+)\s+(20[2-3][0-9]-[0-1][0-9]-[0-3][0-9])\s*(.*)$')

            current = None
            in_table = False
            for line in lines:
                l_str = line.strip()
                if 'Codigo Barras' in l_str and 'Clave Cliente' in l_str:
                    in_table = True
                    continue
                if in_table:
                    if 'Observaciones:' in l_str or 'Cant. Pedida:' in l_str or 'PSAI-' in l_str or 'Hoja ' in l_str:
                        if current:
                            all_items.append(current)
                            current = None
                        break
                    
                    m_start = item_pattern.match(l_str)
                    if m_start:
                        if current:
                            all_items.append(current)
                        current = {
                            'codigo_barras': m_start.group(1),
                            'clave_cliente': m_start.group(2),
                            'raw_parts': [m_start.group(3)]
                        }
                    elif current:
                        current['raw_parts'].append(l_str)
            
            if current:
                all_items.append(current)

        parsed_items = []
        for it in all_items:
            combined = ' '.join(it['raw_parts'])
            tm = tail_pattern.search(combined)
            if tm:
                c_pedida = float(tm.group(1))
                c_surtida = float(tm.group(2))
                lote = tm.group(3)
                caducidad = tm.group(4)
                desc = combined[:tm.start()].strip()
                rest = tm.group(5).strip() if tm.group(5) else ""
            else:
                c_pedida = 0.0
                c_surtida = 0.0
                lote = ''
                caducidad = ''
                desc = combined
                rest = ''
            
            dia = 0
            if doc_info.get('fecha_surtido'):
                m_d = re.search(r'-([0-3][0-9])\b', doc_info['fecha_surtido'][:10])
                if m_d:
                    dia = int(m_d.group(1))

            parsed_items.append({
                'pedido': doc_info.get('pedido', ''),
                'folio_salida': doc_info.get('folio_salida', ''),
                'fecha': doc_info.get('fecha_surtido', ''),
                'dia': dia,
                'codigo_barras': it['codigo_barras'],
                'clave_cliente': it['clave_cliente'],
                'clave': it['clave_cliente'],
                'descripcion': desc,
                'c_pedida': c_pedida,
                'cantidad': c_surtida,
                'c_surtida': c_surtida,
                'lote': lote,
                'caducidad': caducidad,
                'localidad': doc_info.get('localidad', ''),
                'tipo': 'SALIDA'
            })

        return doc_info, parsed_items

for f in glob.glob(r'C:\Users\moode\OneDrive\ABISALUD\CADUCADOS\*.pdf')[:4]:
    info, items = parse_hoja_pedido(f)
    print("PDF:", Path(f).name, "Pedido:", info['pedido'], "Folio:", info['folio_salida'], "Fecha:", info['fecha_surtido'], "Items count:", len(items))
    for it in items:
        print("  Item:", it['clave_cliente'], "Lote:", it['lote'], "Cad:", it['caducidad'], "Cant:", it['cantidad'], "Desc:", it['descripcion'][:35])



