import httpx

candidates = [
    'https://onedrive.live.com/download?cid=019ebf93eb1529d0&resid=019EBF93EB1529D0!sedd48af617b04416a01dc900a410f38f',
    'https://onedrive.live.com/download?cid=019ebf93eb1529d0&resid=019EBF93EB1529D0!48a881ad5206423795f7c8b2bec9ca61',
    'https://onedrive.live.com/download?resid=019EBF93EB1529D0!sedd48af617b04416a01dc900a410f38f&authkey=!APq7A4hGwcOGNmA',
    'https://onedrive.live.com/download?resid=019EBF93EB1529D0!edd48af617b04416a01dc900a410f38f'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

with httpx.Client(follow_redirects=True, headers=headers, timeout=20.0) as client:
    for u in candidates:
        print('Testing:', u)
        try:
            r = client.get(u)
            print(f" -> Status: {r.status_code}, Len: {len(r.content)}, Content-Type: {r.headers.get('Content-Type')}")
            if len(r.content) > 1000 and r.content[:4] == b'PK\x03\x04':
                print("FOUND WORKING DOWNLOAD URL!")
                with open('data/INV_OCTUBRE_11.xlsx', 'wb') as f:
                    f.write(r.content)
                break
        except Exception as e:
            print(" -> Error:", e)

