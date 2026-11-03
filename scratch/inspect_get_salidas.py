with open('database.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'def get_salidas_pdf_movimientos' in line:
            print(f"Found get_salidas_pdf_movimientos at line {idx+1}")
            for j in range(idx, idx+30):
                print(f.readline(), end="")
            break

