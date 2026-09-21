#!/usr/bin/env python3
"""Validate site text integrity, headers syntax, links, and sensitive-file leakage."""
from pathlib import Path
import re, sys
root=Path(__file__).resolve().parents[1]
errors=[]
def fail(msg): errors.append(msg)
def read(name):
 p=root/name
 if not p.is_file() or p.stat().st_size==0: fail(f'{name} missing or empty'); return ''
 b=p.read_bytes()
 if b'\0' in b: fail(f'{name} contains NUL bytes')
 try: return b.decode('utf-8')
 except UnicodeDecodeError: fail(f'{name} is not valid UTF-8'); return ''
for name in ('index.html','projects.html'):
 s=read(name); t=s.strip()
 if not re.match(r'^<!doctype\s+html',t,re.I): fail(f'{name} must start with <!doctype html>')
 if not re.search(r'</html>\s*$',t,re.I): fail(f'{name} must end with </html>')
 for needle in ('<title>', '<meta name="description"', '<link rel="canonical"'):
  if needle.lower() not in s.lower(): fail(f'{name} missing {needle}')
h=read('_headers'); in_block=False
for i,line in enumerate(h.splitlines(),1):
 if '/*' in line or '*/' in line: fail(f'_headers C-style comment marker on line {i}')
 if not line.strip() or line.lstrip().startswith('#'): continue
 if line.startswith('  '):
  if not re.match(r'^  [A-Za-z][A-Za-z0-9-]*:\s+\S',line): fail(f'_headers invalid header line {i}')
 else:
  if not line.startswith('/') and not line.startswith('http'): fail(f'_headers invalid route line {i}')
for p in (root/'.env', root/'public/.env', root/'dist/.env'): 
 if p.exists(): fail(f'sensitive file present: {p.relative_to(root)}')
for name in ('index.html','projects.html'):
 s=(root/name).read_text(errors='ignore') if (root/name).exists() else ''
 for attr,target in re.findall(r'(?:href|src)=["\']([^"\']+)["\']',s,re.I):
  pass
 for target in re.findall(r'(?:href|src)=["\']([^"\']+)["\']',s,re.I):
  if target.startswith(('#','http:','https:','mailto:','tel:','javascript:')): continue
  path=target.split('?',1)[0].split('#',1)[0]
  if path=='/': path='index.html'
  elif path.startswith('/'): path=path[1:]
  if path and not (root/path).exists(): fail(f'{name} local target missing: {target}')
if errors:
 print('\n'.join('FAIL: '+e for e in errors)); sys.exit(1)
print('PASS: site integrity, headers, links, and leakage checks')
