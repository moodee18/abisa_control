import httpx
import re

url_init = 'https://1drv.ms/x/c/019ebf93eb1529d0/IQD2itTtsBcWRKAdyQCkEPOPARq7A4hGwcOGNmAQY0HEwd8?e=UAgWRE'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

with httpx.Client(follow_redirects=True, headers=headers, timeout=30.0) as client:
    r1 = client.get(url_init)
    print('R1 URL:', r1.url)
    
    with open('scratch/onedrive_oct11.html', 'w', encoding='utf-8') as f:
        f.write(r1.text)
        
    print('HTML saved, length:', len(r1.text))
    for m in re.finditer(r'https://[^\s"\'<>]*(?:download|download\.aspx|downloadurl)[^\s"\'<>]*', r1.text, re.IGNORECASE):
        print('DL match:', m.group(0))
        
    for m in re.finditer(r'https://my\.microsoftpersonalcontent\.com[^\s"\'<>]*', r1.text):
        print('Personalcontent match:', m.group(0))

