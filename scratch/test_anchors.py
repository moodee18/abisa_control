with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Check snippets
print('1. style closing exists:', '</style>' in text)
print('2. tab-clues button exists:', "switchTab('tab-clues', this)" in text)
print('3. marbetes tab end exists:', 'id="marbetesPrintOnly"' in text)
print('4. syncModal end exists:', 'id="syncModal"' in text)
print('5. setupModalDropZones exists:', 'setupModalDropZones();' in text)
