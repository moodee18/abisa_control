import sqlite3
import openpyxl
import re

def populate_procedures_and_contracts():
    conn = sqlite3.connect('data/abisalud.db')
    c = conn.cursor()

    recepciones_path = r'C:\Users\moode\OneDrive\ABISALUD\recepciones_2026_actualizado.xlsx'
    wb = openpyxl.load_workbook(recepciones_path, data_only=True)
    ws = wb['recepciones_2026']
    headers = [ws.cell(1, col).value for col in range(1, ws.max_column + 1)]
    
    order_map = {}
    clave_map = {}

    for r in range(2, ws.max_row + 1):
        row = dict(zip(headers, [ws.cell(r, col).value for col in range(1, ws.max_column + 1)]))
        os_val = str(row.get('orden_suministro') or '').strip()
        proc = str(row.get('tipo_contrato-fuente de financiamiento') or '').strip()
        cont = str(row.get('contrato') or '').strip()
        cve = str(row.get('clave') or '').strip()

        if proc == 'None': proc = ''
        if cont == 'None': cont = ''

        if os_val:
            if os_val not in order_map or (proc and not order_map[os_val][0]):
                order_map[os_val] = (proc, cont)
        if cve:
            if cve not in clave_map or (proc and not clave_map[cve][0]):
                clave_map[cve] = (proc, cont)

    print(f"Loaded {len(order_map)} orders and {len(clave_map)} claves from recepciones.")

    # Also sheet contratos
    if 'contratos' in wb.sheetnames:
        wsc = wb['contratos']
        for r in range(2, wsc.max_row + 1):
            cve_adj = str(wsc.cell(r, 1).value or '').strip()
            cont_adj = str(wsc.cell(r, 2).value or '').strip()
            if cve_adj and cont_adj and cont_adj != 'None':
                if cve_adj not in clave_map:
                    clave_map[cve_adj] = ('', cont_adj)
                elif not clave_map[cve_adj][1]:
                    clave_map[cve_adj] = (clave_map[cve_adj][0], cont_adj)

    # Derivation helper for OS patterns
    def derive_proc_cont(os_val):
        os_clean = os_val.strip()
        m_itp = re.match(r'OS-ITPBMX-(\d+)-(\d{4})', os_clean, re.I)
        if m_itp:
            num, yr = m_itp.group(1), m_itp.group(2)
            return ('IA-12-NEF-012NEF001-I-30-2025', f'CS/ITPBMX/{num}/{yr}')
        
        m_lc = re.match(r'OS-LCBMX-(\d+)-(\d{4})', os_clean, re.I)
        if m_lc:
            num, yr = m_lc.group(1), m_lc.group(2)
            proc = 'LA-12-NEF-012NEF001-I-59-2025' if num in ['019', '023', '026'] else 'LA-12-NEF-012NEF001-I-97-2025'
            return (proc, f'LC/BMX/{num}/{yr}')

        m_ad = re.match(r'OS-ADBMX-(\d+)-(\d{4})', os_clean, re.I)
        if m_ad:
            num, yr = m_ad.group(1), m_ad.group(2)
            n_int = int(num)
            if yr == '2026':
                proc = 'AA-12-NEF-012NEF001-I-91-2026'
            elif n_int in [86, 296, 297, 299, 303, 308, 312, 313, 329, 334]:
                proc = 'AA-12-NEF-012NEF001-I-31-2025'
            elif n_int in [87, 88, 93, 97, 106, 111]:
                proc = 'AA-12-NEF-012NEF001-I-17-2025'
            elif n_int in [170, 171, 178]:
                proc = 'AA-12-NEF-012NEF001-I-18-2025'
            elif n_int in [251]:
                proc = 'AA-12-NEF-012NEF001-I-31-2025'
            elif n_int in [426]:
                proc = 'AA-12-NEF-012NEF001-I-45-2025'
            elif n_int in [507, 519]:
                proc = 'AA-12-NEF-012NEF001-I-67-2025'
            else:
                proc = 'AA-12-NEF-012NEF001-I-31-2025'
            return (proc, f'CS/AD/{num}/{yr}')

        return ('', '')

    # Update entradas_movimientos
    c.execute("SELECT id, folio_documento, clave FROM entradas_movimientos")
    rows = c.fetchall()
    updated_entradas = 0

    for eid, fdoc, cve in rows:
        fdoc = (fdoc or '').strip()
        cve = (cve or '').strip()
        proc = ''
        cont = ''

        if fdoc in order_map:
            proc, cont = order_map[fdoc]
        
        if (not proc or not cont) and fdoc:
            dproc, dcont = derive_proc_cont(fdoc)
            if not proc: proc = dproc
            if not cont: cont = dcont

        if (not proc or not cont) and cve in clave_map:
            cproc, ccont = clave_map[cve]
            if not proc: proc = cproc
            if not cont: cont = ccont

        if proc or cont:
            c.execute("UPDATE entradas_movimientos SET procedimiento = ?, contrato = ? WHERE id = ?", (proc, cont, eid))
            updated_entradas += 1

    print(f"Updated entradas_movimientos: {updated_entradas} / {len(rows)}")

    # Update catalogo_movimientos
    c.execute("SELECT id, clave FROM catalogo_movimientos")
    cat_rows = c.fetchall()
    updated_cat = 0

    for cid, cve in cat_rows:
        cve = (cve or '').strip()
        proc = ''
        cont = ''

        # check if any entrada has it
        c.execute("SELECT procedimiento, contrato FROM entradas_movimientos WHERE clave = ? AND (procedimiento != '' OR contrato != '') LIMIT 1", (cve,))
        ent_match = c.fetchone()
        if ent_match:
            proc, cont = ent_match
        elif cve in clave_map:
            proc, cont = clave_map[cve]

        if proc or cont:
            c.execute("UPDATE catalogo_movimientos SET procedimiento = ?, contrato = ? WHERE id = ?", (proc, cont, cid))
            updated_cat += 1

    print(f"Updated catalogo_movimientos: {updated_cat} / {len(cat_rows)}")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    populate_procedures_and_contracts()
