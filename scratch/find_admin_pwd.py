with open('database.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'admin' in line.lower() and ('password' in line.lower() or 'pass' in line.lower() or 'hash' in line.lower() or 'crear' in line.lower() or 'seed' in line.lower()):
            print(f"{idx+1}: {line.strip()[:100]}")

