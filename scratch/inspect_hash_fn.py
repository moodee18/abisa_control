with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def hash_password' in l or 'def verify_password' in l:
        print(f"--- Line {i+1} ---")
        for j in range(i, min(i+30, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")

