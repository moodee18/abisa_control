with open('app.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'def get_current_user' in line:
            print(f"Line {idx+1}")
            for j in range(idx, idx+35):
                print(f.readline(), end="")
            break

