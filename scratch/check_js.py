import re

with open('templates/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Check function openModal
print("Has openModal definition:", "function openModal(" in text)

# Find where script starts
script_start = text.find('<script>')
html_part = text[:script_start]
js_part = text[script_start:]

# Find all inline handlers
pattern = r'(?:onclick|oninput|onsubmit|onchange)="([^"]+)"'
handlers = re.findall(pattern, html_part)
print(f"Total inline handlers in HTML: {len(handlers)}")

called_funcs = set()
for h in handlers:
    m = re.match(r'([a-zA-Z0-9_]+)\(', h.strip())
    if m:
        called_funcs.add(m.group(1))

defined_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', js_part))
defined_funcs.update(re.findall(r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\(', js_part))

print("\nFunctions called in HTML:")
missing = []
for f in sorted(called_funcs):
    if f not in defined_funcs:
        missing.append(f)

print("MISSING functions called directly from HTML:")
for m in missing:
    print(f"  - {m}")

# Also check functions called within JS itself
js_calls = re.findall(r'([a-zA-Z0-9_]+)\(', js_part)
standard_js = {
    'alert', 'confirm', 'prompt', 'console', 'fetch', 'setTimeout', 'clearTimeout',
    'setInterval', 'clearInterval', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
    'encodeURIComponent', 'decodeURIComponent', 'btoa', 'atob', 'JSON', 'Math', 'Date',
    'Array', 'Object', 'String', 'Number', 'Boolean', 'RegExp', 'Map', 'Set', 'Promise',
    'FormData', 'URL', 'Blob', 'FileReader', 'document', 'window', 'addEventListener',
    'removeEventListener', 'getElementById', 'getElementsByClassName', 'getElementsByTagName',
    'querySelector', 'querySelectorAll', 'createElement', 'appendChild', 'removeChild',
    'insertBefore', 'replaceChild', 'cloneNode', 'contains', 'matches', 'closest',
    'getAttribute', 'setAttribute', 'removeAttribute', 'hasAttribute', 'classList',
    'focus', 'blur', 'click', 'submit', 'reset', 'select', 'scrollIntoView',
    'includes', 'indexOf', 'lastIndexOf', 'startsWith', 'endsWith', 'substring',
    'substr', 'slice', 'split', 'trim', 'toLowerCase', 'toUpperCase', 'replace',
    'replaceAll', 'match', 'search', 'push', 'pop', 'shift', 'unshift', 'splice',
    'sort', 'reverse', 'concat', 'join', 'filter', 'map', 'forEach', 'reduce',
    'reduceRight', 'some', 'every', 'find', 'findIndex', 'findLast', 'findLastIndex',
    'flat', 'flatMap', 'keys', 'values', 'entries', 'fill', 'copyWithin', 'has',
    'get', 'set', 'delete', 'clear', 'add', 'then', 'catch', 'finally', 'resolve',
    'reject', 'all', 'race', 'allSettled', 'any', 'append', 'preventDefault',
    'stopPropagation', 'toFixed', 'toString', 'valueOf', 'toExponential',
    'toPrecision', 'toLocaleString', 'toISOString', 'toDateString', 'toTimeString',
    'toLocaleDateString', 'toLocaleTimeString', 'getTime', 'getFullYear',
    'getMonth', 'getDate', 'getDay', 'getHours', 'getMinutes', 'getSeconds',
    'getMilliseconds', 'getTimezoneOffset', 'setFullYear', 'setMonth', 'setDate',
    'setHours', 'setMinutes', 'setSeconds', 'setMilliseconds', 'setTime',
    'now', 'parse', 'UTC', 'log', 'error', 'warn', 'info', 'debug', 'table',
    'group', 'groupEnd', 'time', 'timeEnd', 'floor', 'ceil', 'round', 'abs',
    'max', 'min', 'random', 'sqrt', 'pow', 'sin', 'cos', 'tan', 'asin', 'acos',
    'atan', 'atan2', 'exp', 'stringify', 'assign', 'create', 'freeze', 'seal',
    'from', 'isArray', 'is', 'hasOwn', 'getOwnPropertyNames', 'open', 'close',
    'write', 'writeln', 'exec', 'test', 'readAsDataURL', 'readAsText',
    'readAsArrayBuffer', 'createObjectURL', 'revokeObjectURL', 'send', 'reload'
}

js_internal_missing = set()
for c in js_calls:
    if c not in defined_funcs and c not in standard_js and not c.startswith('_'):
        js_internal_missing.add(c)

print("\nPotentially missing internal JS calls:")
for m in sorted(js_internal_missing):
    # filter out obvious method calls if possible
    print(f"  - {m}")
