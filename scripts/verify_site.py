"""Pre-merge integrity checks for the GC Solar static site.
"""Pre-merge integrity checks for the GC Solar static site.

Run locally:   python3 scripts/verify_site.py
Run vs a base: python3 scripts/verify_site.py --base origin/master

Exit code 0 = all checks passed, 1 = at least one error.

Catches, among other things:
  - text/HTML files truncated or turned to binary junk (the "14-byte
    index.html" failure)
  - broken internal links, canonical/sitemap mismatches, invalid
    `_headers` syntax
  - IMAGES THAT WERE ROUND-TRIPPED THROUGH A TEXT/STRING LAYER instead
    of written as raw bytes. This is a real, repeated failure mode in
    this repo: a JPEG decoded as UTF-8 (or JSON-escaped) has ~1/3 of its
    bytes replaced with the UTF-8 replacement character U+FFFD
    (hex EF BF BD), which inflates the file and makes it unopenable as
    an image, while still "looking binary" to a naive text/UTF-8 check.
    We check every image for: a valid magic-byte signature, a
    replacement-character ratio, and (if Pillow is installed) that it
    actually decodes.
"""
import argparse
import json
import os
Run vs a base: python3 scripts/verify_site.py --base origin/master
import subprocess

import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

SITE = "https://gcsolarprojects.com"
PAGES = ["index.html", "projects.html", "404.html"]
SEO_PAGES = ["index.html", "projects.html"]
TEXT_SUFFIXES = {".html", ".css", ".js", ".xml", ".txt", ".md", ".json", ".yml", ".yaml"}
TEXT_NAMES = {"_headers", "_redirects", ".gitignore"}
IMAGE_DIRS = ["images"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MIN_PAGE_BYTES = 500  # 404.html is legitimately small
SHRINK_RATIO = 0.40
SHRINK_MIN_BASE = 2000
REPLACEMENT_CHAR_MAX_RATIO = 0.005   # a real photo should have ~0% of this
STRUCTURAL = {"html", "head", "body", "main", "section", "div", "nav", "footer",
              "header", "article", "ul", "ol", "table", "script", "style", "form"}
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}

MAGIC = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".gif": (b"GIF87a", b"GIF89a"),
    ".webp": (b"RIFF",),  # + "WEBP" at offset 8, checked separately
}

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def tracked_files():
    try:
        return [f for f in git("ls-files").splitlines() if Path(f).exists()]
    except Exception:
        return [str(p) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


def is_text_file(path):
    p = Path(path)
    return p.suffix.lower() in TEXT_SUFFIXES or p.name in TEXT_NAMES


def is_image_file(path):
    p = Path(path)
    return p.suffix.lower() in IMAGE_SUFFIXES and any(
        str(p).startswith(d + "/") or str(p).startswith(d + os.sep) for d in IMAGE_DIRS
    )


# ---------------------------------------------------------------- text integrity
def check_text_integrity(files):
    for f in files:
        if not is_text_file(f):
            continue
        raw = Path(f).read_bytes()
        if b"\x00" in raw:
            err(f"{f}: contains NUL bytes (binary/corrupted)")
            continue
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            err(f"{f}: not valid UTF-8 ({e.reason} at byte {e.start}) - looks corrupted")
            continue
        bad = [c for c in txt if ord(c) < 32 and c not in "\t\n\r"]
        if bad:
            err(f"{f}: contains {len(bad)} control character(s) - looks corrupted")


# ---------------------------------------------------------------- image integrity
def check_image_integrity(files):
    for f in files:
        if not is_image_file(f):
            continue
        raw = Path(f).read_bytes()
        suffix = Path(f).suffix.lower()

        if len(raw) == 0:
            err(f"{f}: 0 bytes")
            continue

        # 1. Magic-byte check - catches wrong/missing signature outright.
        sigs = MAGIC.get(suffix, ())
        if sigs and not any(raw.startswith(s) for s in sigs):
            err(f"{f}: bad magic bytes for {suffix} "
                f"(starts with {raw[:4].hex()}) - not a real {suffix.lstrip('.')} file")
            continue  # no point running further checks on a non-image blob
        if suffix == ".webp" and raw[8:12] != b"WEBP":
            err(f"{f}: RIFF header present but missing WEBP marker")
            continue
Exit code 0 = all checks passed, 1 = at least one error.
        # 2. Replacement-character ratio - catches the specific failure mode
        #    seen repeatedly in this repo: binary image bytes decoded as
        #    UTF-8 (or JSON round-tripped) upstream, silently mangling
        #    ~1/3 of the file into U+FFFD (EF BF BD) before it's ever
        #    written to git. A real photo has ~0% of this triplet.
        repl = raw.count(b"\xef\xbf\xbd")
        ratio = (repl * 3) / len(raw)
        if ratio > REPLACEMENT_CHAR_MAX_RATIO:
            err(f"{f}: {ratio:.0%} of file is the UTF-8 replacement character "
                f"(EF BF BD) - this image was corrupted by being decoded as "
                f"text/UTF-8 (or JSON-escaped) before being written as binary. "
                f"Fix the upload path: base64-decode straight to bytes and "
                f"write with mode='wb', never str()/decode()/json on the payload.")
            continue
  - text/HTML files truncated or turned to binary junk (the "14-byte
        # 3. Full decode, if Pillow is available - catches truncation and
        #    other structural corruption that magic bytes alone would miss.
        if HAVE_PIL:
            try:
                im = Image.open(f)
                im.verify()
            except Exception as e:
                err(f"{f}: fails to decode as an image ({e})")
  - broken internal links, canonical/sitemap mismatches, invalid

def check_images_referenced_are_valid(refs_by_page):
    """Cross-check: every locally-hosted image referenced by a page must
    exist AND pass the integrity checks above (i.e. not be in `errors`
    already for a different reason)."""
    broken_paths = {m.split(":")[0].strip() for m in errors if m.startswith("images/")}
    for page, refs in refs_by_page.items():
        for ref in refs:
            local = ref.lstrip("/")
            if local in broken_paths:
                err(f"{page}: links to {ref}, which failed image integrity checks above")


# ---------------------------------------------------------------- html parsing
class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []
        self.title, self._in_title = "", False
        self.metas, self.links, self.refs = [], [], []
        self.ldjson, self._in_ld = [], False
        self.html_lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            self.metas.append(a)
        if tag == "link":
            self.links.append(a)
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_ld = True
            self.ldjson.append("")
        for attr in ("href", "src"):
            if attr in a and a[attr]:
                self.refs.append(a[attr])
        if tag in STRUCTURAL:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_ld = False
        if tag in VOID or tag not in STRUCTURAL:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.problems.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld and self.ldjson:
            self.ldjson[-1] += data

    def meta(self, key, value):
        for m in self.metas:
            if m.get(key) == value:
                return m.get("content")
        return None

    def link(self, rel):
        for l in self.links:
            if l.get("rel") == rel:
                return l.get("href")
        return None


def resolve_local(path):
    p = path.split("?")[0].split("#")[0].lstrip("/")
    if p == "":
        return Path("index.html").exists()
    return any(Path(c).is_file() for c in (p, p + ".html", p.rstrip("/") + "/index.html"))


def sitemap_paths():
    if not Path("sitemap.xml").exists():
        return None
    try:
        root = ET.parse("sitemap.xml").getroot()
    except ET.ParseError as e:
        err(f"sitemap.xml: invalid XML ({e})")
        return None
    locs = [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]
    paths = set()
    for loc in locs:
        u = urlparse(loc)
        if f"{u.scheme}://{u.netloc}" != SITE:
            err(f"sitemap.xml: {loc} is not on {SITE}")
        paths.add(u.path or "/")
        if not resolve_local(u.path or "/"):
            err(f"sitemap.xml: {loc} does not resolve to a file in the repo")
    return paths


def check_pages(sitemap):
    refs_by_page = {}
    for f in PAGES:
        if not Path(f).exists():
            err(f"{f}: missing")
            continue
        raw = Path(f).read_bytes()
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue  # already reported by check_text_integrity
        if len(raw) < MIN_PAGE_BYTES:
            err(f"{f}: only {len(raw)} bytes (minimum {MIN_PAGE_BYTES}) - truncated?")
        if not txt.lstrip().lower().startswith("<!doctype html>"):
            err(f"{f}: does not start with <!doctype html>")
        if not txt.rstrip().lower().endswith("</html>"):
            err(f"{f}: does not end with </html>")
        p = PageParser()
        p.feed(txt)
        refs_by_page[f] = [r for r in p.refs if r.startswith("/images/")]
        if p.stack:
            err(f"{f}: unclosed structural tags: {p.stack}")
        for prob in p.problems[:3]:
            err(f"{f}: {prob}")
        if not p.html_lang:
            err(f"{f}: <html> has no lang attribute")
        if p.meta("name", "viewport") is None:
            err(f"{f}: missing viewport meta")
        if f in SEO_PAGES:
            if not p.title.strip():
                err(f"{f}: missing or empty <title>")
            if not (p.meta("name", "description") or "").strip():
                err(f"{f}: missing meta description")
            canon = p.link("canonical")
            if not canon:
                err(f"{f}: missing canonical link")
            elif sitemap is not None:
                cpath = urlparse(canon).path or "/"
                if not canon.startswith(SITE):
                    err(f"{f}: canonical {canon} is not on {SITE}")
                if cpath not in sitemap:
                    err(f"{f}: canonical path '{cpath}' is not listed in sitemap.xml "
                        f"(sitemap has: {sorted(sitemap)})")
        for block in p.ldjson:
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                err(f"{f}: JSON-LD block is not valid JSON ({e})")
        for key in ("og:image", "twitter:image"):
            val = p.meta("property", key) or p.meta("name", key)
            if val and val.startswith(SITE) and not resolve_local(urlparse(val).path):
                err(f"{f}: {key} points to missing file {val}")
        for ref in p.refs:
            if re.match(r"^(https?:|mailto:|tel:|data:|#|//|javascript:)", ref):
                continue
            if ref.startswith("/") and not resolve_local(ref):
                err(f"{f}: broken internal link/asset {ref}")
    return refs_by_page


# ---------------------------------------------------------------- _headers syntax
def check_headers_file():
    if not Path("_headers").exists():
        warn("_headers: not present")
        return
    try:
        lines = Path("_headers").read_text(encoding="utf-8").splitlines()
    We check every image for: a valid magic-byte signature, a
        return
    rules, seen_path = 0, False
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if len(line) > 2000:
            err(f"_headers:{n}: line longer than 2000 characters")
        if line[0] not in " \t":
            if not (line.startswith("/") or line.startswith("https://")):
                err(f"_headers:{n}: expected a path starting with '/', got: {line[:60]!r}")
            else:
                rules += 1
                seen_path = True
        else:
            body = line.strip()
            if not seen_path:
                err(f"_headers:{n}: header line before any path")
            elif not (body.startswith("! ") or re.match(r"^[A-Za-z0-9-]+:\s*\S", body)):
                err(f"_headers:{n}: expected 'Header-Name: value', got: {body[:60]!r} "
                    f"(comments must start with #)")
    if rules > 100:
        err(f"_headers: {rules} rules exceeds Cloudflare's limit of 100")


def check_misc():
    if Path("robots.txt").exists():
        if "sitemap:" not in Path("robots.txt").read_text(encoding="utf-8", errors="ignore").lower():
            warn("robots.txt: no Sitemap: line")
    else:
        warn("robots.txt: not present")
    if Path("data/projects.json").exists():
        try:
            json.loads(Path("data/projects.json").read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            err(f"data/projects.json: invalid JSON ({e})")


# ---------------------------------------------------------------- shrink guard
def shrink_guard(base):
    allow = os.environ.get("ALLOW_SHRINK") == "1"
    try:
        mb = git("merge-base", base, "HEAD").strip()
        diff = git("diff", "--name-status", "--no-renames", mb, "HEAD")
    except subprocess.CalledProcessError as e:
        warn(f"shrink guard skipped: cannot compare with {base} ({e})")
        return
    for line in diff.splitlines():
        status, path = line.split("\t", 1)
        if status != "M" or not is_text_file(path):
            continue
        old = int(git("cat-file", "-s", f"{mb}:{path}"))
        new = int(git("cat-file", "-s", f"HEAD:{path}"))
        if old >= SHRINK_MIN_BASE and new < old * SHRINK_RATIO:
            msg = (f"{path}: shrank from {old} to {new} bytes vs {base} "
                   f"({100 - 100 * new // old}% smaller)")
            if allow:
                warn(msg + " [allowed via 'allow-shrink' label]")
            else:
                err(msg + " - if intentional, add the 'allow-shrink' PR label")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref to compare against, e.g. origin/master")
    args = ap.parse_args()

    if not HAVE_PIL:
        warn("Pillow not installed - image decode checks skipped "
             "(magic-byte and replacement-character checks still run)")

    files = tracked_files()
    check_text_integrity(files)
    check_image_integrity(files)
    sm = sitemap_paths()
    refs_by_page = check_pages(sm)
    check_images_referenced_are_valid(refs_by_page)
    check_headers_file()
    check_misc()
    if args.base:
        shrink_guard(args.base)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) across {len(files)} tracked files")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
        "col", "embed", "param", "track", "wbr"}

MAGIC = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".gif": (b"GIF87a", b"GIF89a"),
    ".webp": (b"RIFF",),  # + "WEBP" at offset 8, checked separately
}

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def tracked_files():
    try:
        return [f for f in git("ls-files").splitlines() if Path(f).exists()]
    except Exception:
        return [str(p) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


def is_text_file(path):
    p = Path(path)
    return p.suffix.lower() in TEXT_SUFFIXES or p.name in TEXT_NAMES


def is_image_file(path):
    p = Path(path)
    return p.suffix.lower() in IMAGE_SUFFIXES and any(
        str(p).startswith(d + "/") or str(p).startswith(d + os.sep) for d in IMAGE_DIRS
    )


# ---------------------------------------------------------------- text integrity
def check_text_integrity(files):
    for f in files:
        if not is_text_file(f):
            continue
        raw = Path(f).read_bytes()
        if b"\x00" in raw:
            err(f"{f}: contains NUL bytes (binary/corrupted)")
            continue
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            err(f"{f}: not valid UTF-8 ({e.reason} at byte {e.start}) - looks corrupted")
            continue
        bad = [c for c in txt if ord(c) < 32 and c not in "\t\n\r"]
        if bad:
            err(f"{f}: contains {len(bad)} control character(s) - looks corrupted")


# ---------------------------------------------------------------- image integrity
def check_image_integrity(files):
    for f in files:
        if not is_image_file(f):
            continue
        raw = Path(f).read_bytes()
        suffix = Path(f).suffix.lower()

        if len(raw) == 0:
            err(f"{f}: 0 bytes")
            continue

        # 1. Magic-byte check - catches wrong/missing signature outright.
        sigs = MAGIC.get(suffix, ())
        if sigs and not any(raw.startswith(s) for s in sigs):
            err(f"{f}: bad magic bytes for {suffix} "
                f"(starts with {raw[:4].hex()}) - not a real {suffix.lstrip('.')} file")
            continue  # no point running further checks on a non-image blob
        if suffix == ".webp" and raw[8:12] != b"WEBP":
            err(f"{f}: RIFF header present but missing WEBP marker")
            continue
root = Path(__file__).resolve().parents[1]
        # 2. Replacement-character ratio - catches the specific failure mode
        #    seen repeatedly in this repo: binary image bytes decoded as
        #    UTF-8 (or JSON round-tripped) upstream, silently mangling
        #    ~1/3 of the file into U+FFFD (EF BF BD) before it's ever
        #    written to git. A real photo has ~0% of this triplet.
        repl = raw.count(b"\xef\xbf\xbd")
        ratio = (repl * 3) / len(raw)
        if ratio > REPLACEMENT_CHAR_MAX_RATIO:
            err(f"{f}: {ratio:.0%} of file is the UTF-8 replacement character "
                f"(EF BF BD) - this image was corrupted by being decoded as "
                f"text/UTF-8 (or JSON-escaped) before being written as binary. "
                f"Fix the upload path: base64-decode straight to bytes and "
                f"write with mode='wb', never str()/decode()/json on the payload.")
            continue
def fail(message): errors.append(message)
        # 3. Full decode, if Pillow is available - catches truncation and
        #    other structural corruption that magic bytes alone would miss.
        if HAVE_PIL:
            try:
                im = Image.open(f)
                im.verify()
            except Exception as e:
                err(f"{f}: fails to decode as an image ({e})")
def read(name):

def check_images_referenced_are_valid(refs_by_page):
    """Cross-check: every locally-hosted image referenced by a page must
    exist AND pass the integrity checks above (i.e. not be in `errors`
    already for a different reason)."""
    broken_paths = {m.split(":")[0].strip() for m in errors if m.startswith("images/")}
    for page, refs in refs_by_page.items():
        for ref in refs:
            local = ref.lstrip("/")
            if local in broken_paths:
                err(f"{page}: links to {ref}, which failed image integrity checks above")


# ---------------------------------------------------------------- html parsing
class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []
        self.title, self._in_title = "", False
        self.metas, self.links, self.refs = [], [], []
        self.ldjson, self._in_ld = [], False
        self.html_lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            self.metas.append(a)
        if tag == "link":
            self.links.append(a)
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_ld = True
            self.ldjson.append("")
        for attr in ("href", "src"):
            if attr in a and a[attr]:
                self.refs.append(a[attr])
        if tag in STRUCTURAL:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_ld = False
        if tag in VOID or tag not in STRUCTURAL:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.problems.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld and self.ldjson:
            self.ldjson[-1] += data

    def meta(self, key, value):
        for m in self.metas:
            if m.get(key) == value:
                return m.get("content")
        return None

    def link(self, rel):
        for l in self.links:
            if l.get("rel") == rel:
                return l.get("href")
        return None


def resolve_local(path):
    p = path.split("?")[0].split("#")[0].lstrip("/")
    if p == "":
        return Path("index.html").exists()
    return any(Path(c).is_file() for c in (p, p + ".html", p.rstrip("/") + "/index.html"))


def sitemap_paths():
    if not Path("sitemap.xml").exists():
        return None
    try:
        root = ET.parse("sitemap.xml").getroot()
    except ET.ParseError as e:
        err(f"sitemap.xml: invalid XML ({e})")
        return None
    locs = [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]
    paths = set()
    for loc in locs:
        u = urlparse(loc)
        if f"{u.scheme}://{u.netloc}" != SITE:
            err(f"sitemap.xml: {loc} is not on {SITE}")
        paths.add(u.path or "/")
        if not resolve_local(u.path or "/"):
            err(f"sitemap.xml: {loc} does not resolve to a file in the repo")
    return paths


def check_pages(sitemap):
    refs_by_page = {}
    for f in PAGES:
        if not Path(f).exists():
            err(f"{f}: missing")
            continue
        raw = Path(f).read_bytes()
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue  # already reported by check_text_integrity
        if len(raw) < MIN_PAGE_BYTES:
            err(f"{f}: only {len(raw)} bytes (minimum {MIN_PAGE_BYTES}) - truncated?")
        if not txt.lstrip().lower().startswith("<!doctype html>"):
            err(f"{f}: does not start with <!doctype html>")
        if not txt.rstrip().lower().endswith("</html>"):
            err(f"{f}: does not end with </html>")
        p = PageParser()
        p.feed(txt)
        refs_by_page[f] = [r for r in p.refs if r.startswith("/images/")]
        if p.stack:
            err(f"{f}: unclosed structural tags: {p.stack}")
        for prob in p.problems[:3]:
            err(f"{f}: {prob}")
        if not p.html_lang:
            err(f"{f}: <html> has no lang attribute")
        if p.meta("name", "viewport") is None:
            err(f"{f}: missing viewport meta")
        if f in SEO_PAGES:
            if not p.title.strip():
                err(f"{f}: missing or empty <title>")
            if not (p.meta("name", "description") or "").strip():
                err(f"{f}: missing meta description")
            canon = p.link("canonical")
            if not canon:
                err(f"{f}: missing canonical link")
            elif sitemap is not None:
                cpath = urlparse(canon).path or "/"
                if not canon.startswith(SITE):
                    err(f"{f}: canonical {canon} is not on {SITE}")
                if cpath not in sitemap:
                    err(f"{f}: canonical path '{cpath}' is not listed in sitemap.xml "
                        f"(sitemap has: {sorted(sitemap)})")
        for block in p.ldjson:
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                err(f"{f}: JSON-LD block is not valid JSON ({e})")
        for key in ("og:image", "twitter:image"):
            val = p.meta("property", key) or p.meta("name", key)
            if val and val.startswith(SITE) and not resolve_local(urlparse(val).path):
                err(f"{f}: {key} points to missing file {val}")
        for ref in p.refs:
            if re.match(r"^(https?:|mailto:|tel:|data:|#|//|javascript:)", ref):
                continue
            if ref.startswith("/") and not resolve_local(ref):
                err(f"{f}: broken internal link/asset {ref}")
    return refs_by_page


# ---------------------------------------------------------------- _headers syntax
def check_headers_file():
    if not Path("_headers").exists():
        warn("_headers: not present")
        return
    try:
        lines = Path("_headers").read_text(encoding="utf-8").splitlines()
        fail(f"{name} is not valid UTF-8"); return ""
        return
    rules, seen_path = 0, False
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if len(line) > 2000:
            err(f"_headers:{n}: line longer than 2000 characters")
        if line[0] not in " \t":
            if not (line.startswith("/") or line.startswith("https://")):
                err(f"_headers:{n}: expected a path starting with '/', got: {line[:60]!r}")
            else:
                rules += 1
                seen_path = True
        else:
            body = line.strip()
            if not seen_path:
                err(f"_headers:{n}: header line before any path")
            elif not (body.startswith("! ") or re.match(r"^[A-Za-z0-9-]+:\s*\S", body)):
                err(f"_headers:{n}: expected 'Header-Name: value', got: {body[:60]!r} "
                    f"(comments must start with #)")
    if rules > 100:
        err(f"_headers: {rules} rules exceeds Cloudflare's limit of 100")


def check_misc():
    if Path("robots.txt").exists():
        if "sitemap:" not in Path("robots.txt").read_text(encoding="utf-8", errors="ignore").lower():
            warn("robots.txt: no Sitemap: line")
    else:
        warn("robots.txt: not present")
    if Path("data/projects.json").exists():
        try:
            json.loads(Path("data/projects.json").read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            err(f"data/projects.json: invalid JSON ({e})")


# ---------------------------------------------------------------- shrink guard
def shrink_guard(base):
    allow = os.environ.get("ALLOW_SHRINK") == "1"
    try:
        mb = git("merge-base", base, "HEAD").strip()
        diff = git("diff", "--name-status", "--no-renames", mb, "HEAD")
    except subprocess.CalledProcessError as e:
        warn(f"shrink guard skipped: cannot compare with {base} ({e})")
        return
    for line in diff.splitlines():
        status, path = line.split("\t", 1)
        if status != "M" or not is_text_file(path):
            continue
        old = int(git("cat-file", "-s", f"{mb}:{path}"))
        new = int(git("cat-file", "-s", f"HEAD:{path}"))
        if old >= SHRINK_MIN_BASE and new < old * SHRINK_RATIO:
            msg = (f"{path}: shrank from {old} to {new} bytes vs {base} "
                   f"({100 - 100 * new // old}% smaller)")
            if allow:
                warn(msg + " [allowed via 'allow-shrink' label]")
            else:
                err(msg + " - if intentional, add the 'allow-shrink' PR label")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref to compare against, e.g. origin/master")
    args = ap.parse_args()

    if not HAVE_PIL:
        warn("Pillow not installed - image decode checks skipped "
             "(magic-byte and replacement-character checks still run)")

    files = tracked_files()
    check_text_integrity(files)
    check_image_integrity(files)
    sm = sitemap_paths()
    refs_by_page = check_pages(sm)
    check_images_referenced_are_valid(refs_by_page)
    check_headers_file()
    check_misc()
    if args.base:
        shrink_guard(args.base)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) across {len(files)} tracked files")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()