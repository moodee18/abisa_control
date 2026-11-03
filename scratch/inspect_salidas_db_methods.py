with open('database.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'salida_pdf' in line.lower() and ('def ' in line or 'delete' in line or 'update' in line):
            print(f"{idx+1}: {line.strip()}")

