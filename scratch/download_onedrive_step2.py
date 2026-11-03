import httpx

url_init = 'https://1drv.ms/x/c/019ebf93eb1529d0/IQCtgahIBlI3QpX3yLK-ycphARi_IrKaY8qxnFLNTal289I?e=6NqXiy'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

with httpx.Client(follow_redirects=True, headers=headers, timeout=30.0) as client:
    r1 = client.get(url_init)
    print('R1 status:', r1.status_code)

    dl_candidates = [
        'https://my.microsoftpersonalcontent.com/personal/019ebf93eb1529d0/_layouts/15/download.aspx?UniqueId=48a881ad-5206-4237-95f7-c8b2bec9ca61',
        'https://onedrive.live.com/personal/019ebf93eb1529d0/_layouts/15/download.aspx?UniqueId=48a881ad-5206-4237-95f7-c8b2bec9ca61',
        'https://onedrive.live.com/download?cid=019EBF93EB1529D0&resid=019EBF93EB1529D0!s48a881ad5206423795f7c8b2bec9ca61'
    ]

    for dl_url in dl_candidates:
        print('\nTrying:', dl_url)
        r = client.get(dl_url)
        print('Status:', r.status_code)
        print('URL:', r.url)
        print('Content-Type:', r.headers.get('Content-Type'))
        print('Content-Disposition:', r.headers.get('Content-Disposition'))
        print('Length:', len(r.content))
        if len(r.content) > 1000 and (r.content[:4] == b'PK\x03\x04' or 'spreadsheet' in r.headers.get('Content-Type', '')):
            with open('data/INVETARIO_SIMPLIFICADO_OCT.xlsx', 'wb') as f:
                f.write(r.content)
            print('SUCCESS: Saved to data/INVETARIO_SIMPLIFICADO_OCT.xlsx')
            break
