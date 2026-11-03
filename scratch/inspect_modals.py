with open('templates/index.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'class="modal-overlay"' in line or 'id="modal' in line:
            print(f"{idx+1}: {line.strip()[:100]}")

