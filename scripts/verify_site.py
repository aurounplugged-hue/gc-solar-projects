#!/usr/bin/env python3
"""Validate site text integrity, headers syntax, links, and sensitive-file leakage."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
errors = []

def fail(message):
    errors.append(message)

def read(name):
    path = root / name
    if not path.is_file() or path.stat().st_size == 0:
        fail(f"{name} missing or empty")
        return ""
    data = path.read_bytes()
    if b"\0" in data:
        fail(f"{name} contains NUL bytes")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"{name} is not valid UTF-8")
        return ""

for name in ("index.html", "projects.html"):
    text = read(name)
    stripped = text.strip()
    if not re.match(r"^<!doctype\s+html", stripped, re.I):
        fail(f"{name} must start with <!doctype html>")
    if not re.search(r"</html>\s*$", stripped, re.I):
        fail(f"{name} must end with </html>")
    for needle in ('<title>', '<meta name="description"', '<link rel="canonical"'):
        if needle.lower() not in text.lower():
            fail(f"{name} missing {needle}")

headers = read("_headers")
for number, line in enumerate(headers.splitlines(), 1):
    stripped = line.strip()
    if "*/" in line or ("/*" in line and stripped != "/*"):
        fail(f"_headers C-style comment marker on line {number}")
    if not stripped or stripped.startswith("#"):
        continue
    if line.startswith("  "):
        if not re.match(r"^  [A-Za-z][A-Za-z0-9-]*:\s+\S", line):
            fail(f"_headers invalid header line {number}")
    elif not line.startswith("/") and not line.startswith("http"):
        fail(f"_headers invalid route line {number}")

for path in (root / ".env", root / "public/.env", root / "dist/.env"):
    if path.exists():
        fail(f"sensitive file present: {path.relative_to(root)}")

for name in ("index.html", "projects.html"):
    path = root / name
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    targets = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', text, re.I)
    for target in targets:
        if target.startswith(("#", "http:", "https:", "mailto:", "tel:", "javascript:")):
            continue
        local = target.split("?", 1)[0].split("#", 1)[0]
        if local == "/":
            local = "index.html"
        elif local.startswith("/"):
            local = local[1:]
        if local and not (root / local).exists():
            fail(f"{name} local target missing: {target}")

if errors:
    print("\n".join("FAIL: " + error for error in errors))
    sys.exit(1)
print("PASS: site integrity, headers, links, and leakage checks")
