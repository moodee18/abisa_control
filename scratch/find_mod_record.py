with open('templates/index.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'openCtrlModificarRecord' in line:
            print(f"{idx+1}: {line.strip()}")

