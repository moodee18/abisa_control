import httpx
import os

url = "https://my.microsoftpersonalcontent.com/personal/019ebf93eb1529d0/_layouts/15/download.aspx?UniqueId=edd48af6-17b0-4416-a01d-c900a410f38f"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

with httpx.Client(follow_redirects=True, headers=headers, timeout=60.0) as client:
    r = client.get(url)
    print("Status:", r.status_code)
    print("Length:", len(r.content))
    print("Content-Type:", r.headers.get("Content-Type"))
    print("Content-Disposition:", r.headers.get("Content-Disposition"))
    
    if len(r.content) > 1000 and r.content[:4] == b'PK\x03\x04':
        dest = os.path.abspath("data/INV_OCTUBRE_11.xlsx")
        with open(dest, "wb") as f:
            f.write(r.content)
        print("SUCCESS! Saved to", dest)
    else:
        print("Error: content is not a valid zip/xlsx")

