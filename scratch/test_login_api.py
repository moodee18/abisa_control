import json
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
payload = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/api/auth/login', data=payload, headers={'Content-Type': 'application/json'})
try:
    with opener.open(req) as resp:
        print("Login status:", resp.status, resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Login error:", e.code, e.read().decode('utf-8'))

# Test OCTUBRE
req_oct = urllib.request.Request('http://127.0.0.1:8000/api/control-movimientos/matriz?mes=OCTUBRE&ano=2026')
with opener.open(req_oct) as resp:
    data_oct = json.loads(resp.read().decode('utf-8'))
    print("OCTUBRE KPIs:", data_oct.get('kpis'))

# Test NOVIEMBRE
req_nov = urllib.request.Request('http://127.0.0.1:8000/api/control-movimientos/matriz?mes=NOVIEMBRE&ano=2026')
with opener.open(req_nov) as resp:
    data_nov = json.loads(resp.read().decode('utf-8'))
    print("NOVIEMBRE KPIs:", data_nov.get('kpis'))
