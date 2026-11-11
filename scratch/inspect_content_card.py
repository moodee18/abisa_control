with open('templates/index.html', encoding='utf-8') as f:
    txt = f.read()

idx = txt.find('<div class="content-card">')
print('content-card at index:', idx)
if idx != -1:
    # let's look for the matching closing div or where the next major section starts
    idx2 = txt.find('<!-- Modal', idx)
    print('First modal after content-card at index:', idx2)
    print(txt[idx2-300:idx2+100])

