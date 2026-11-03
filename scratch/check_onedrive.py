import re

with open('scratch/onedrive_oct.xlsx', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

links = re.findall(r'https?://[^\s"\'<>]+', text)
for l in set(links):
    if any(k in l.lower() for k in ['download', 'excel', 'item', 'res', 'resid', 'onedrive']):
        print(l[:150])
