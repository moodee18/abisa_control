import httpx
import re
import json

url_init = 'https://1drv.ms/x/c/019ebf93eb1529d0/IQCtgahIBlI3QpX3yLK-ycphARi_IrKaY8qxnFLNTal289I?e=6NqXiy'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

with httpx.Client(follow_redirects=True, headers=headers, timeout=30.0) as client:
    r1 = client.get(url_init)
    print('R1 URL:', r1.url)
    
    # Search for download url or file url inside script or JSON
    # Often OneDrive has WopiUrl, FileGetUrl, or downloadUrl in JSON config
    matches = re.findall(r'"(https:[^"]+download[^"]*)"', r1.text)
    print('Matches for download:', matches)

    file_matches = re.findall(r'"(https:[^"]+api/v2.0/items/[^"]+)"', r1.text)
    print('Matches for api items:', file_matches)

    # OneDrive 1drv direct download link format:
    # https://onedrive.live.com/download?resid=...&authkey=...
    # Look for authkey and resid
    resid_m = re.search(r'resid=([^&"]+)', str(r1.url)) or re.search(r'sourcedoc=%7B([^%]+)%7D', str(r1.url))
    print('Resid / sourcedoc:', resid_m.groups() if resid_m else None)

    # Try action=download directly
    dl_url = str(r1.url).replace('action=default', 'action=download')
    r2 = client.get(dl_url)
    print('R2 URL:', r2.url)
    print('R2 Content-Type:', r2.headers.get('Content-Type'))
    print('R2 Length:', len(r2.content))
    if len(r2.content) > 1000 and (r2.content[:4] == b'PK\x03\x04' or 'spreadsheet' in r2.headers.get('Content-Type', '')):
        with open('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', 'wb') as f:
            f.write(r2.content)
        print('SUCCESS: Saved to data/INVETARIO_SIMPLIFICADO_OCT.xlsx')
    else:
        # Save r1.text for analysis
        with open('scratch/onedrive_page.html', 'w', encoding='utf-8') as f:
            f.write(r1.text)
        print('Saved scratch/onedrive_page.html for inspection')
