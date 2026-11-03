with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
tabs = re.findall(r'id=["\']tab-([^"\']+)["\']', text)
print('Tabs found by id tab-*:', sorted(list(set(tabs))))

nav_items = re.findall(r'data-tab=["\']([^"\']+)["\']', text)
print('Nav items data-tab:', sorted(list(set(nav_items))))

# Let's also look for navigation links
nav_blocks = re.findall(r'<button[^>]*class="[^"]*nav-link[^"]*"[^>]*>([\s\S]*?)</button>', text)
for nb in nav_blocks[:15]:
    clean = re.sub(r'<[^>]+>', '', nb).strip()
    print('Nav button:', clean)
