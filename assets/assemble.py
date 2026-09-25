#!/usr/bin/env python3
"""Assemble the final self-contained HTML report.
Every image is embedded as a data-URI CSS class at the /*__IMAGES__*/ marker.
Optimized: images are resized to their largest display size (retina 2x) and
encoded as WebP; already-optimized WebP files are embedded byte-for-byte
without re-encoding."""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))          # <repo>/assets
REPO = os.path.dirname(ROOT)                               # <repo>
# argv[1] overrides the destination; defaults to the repo's shipped index.html
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(REPO, "index.html")

def embed_file(path, mime):
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()

def data_uri(path, max_w=None, quality=85):
    """Resize to max_w (if larger) and encode as WebP.
    If the file is already WebP and needs no resize: embed as-is (no re-encode)."""
    if path.lower().endswith(".webp") and (not max_w or Image.open(path).width <= max_w):
        return embed_file(path, "image/webp")
    im = Image.open(path).convert("RGBA")
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

classes = []   # (css-class-name, data-uri)

# item icons (display 21px) -> 48px webp        .i-{slug}
items = os.path.join(ROOT, "items")
for f in sorted(os.listdir(items)):
    classes.append((f"i-{os.path.splitext(f)[0]}", data_uri(os.path.join(items, f), 48)))

# featured hero portraits (display up to 56px) -> 112px webp   .h-{slug}
heroes = os.path.join(ROOT, "heroes")
for f in sorted(os.listdir(heroes)):
    classes.append((f"h-{os.path.splitext(f)[0]}", data_uri(os.path.join(heroes, f), 112)))

# extra hero portraits for the counter picker (display up to 34px) -> 72px webp  .h-{slug}
extra = os.path.join(ROOT, "heroes_extra")
for f in sorted(os.listdir(extra)):
    classes.append((f"h-{os.path.splitext(f)[0]}", data_uri(os.path.join(extra, f), 72)))

# emblem (display 21px) -> 48px   |   spell (display 17px) -> 40px
for sub, pre, w in (("emblems", "e", 48), ("spells", "s", 40), ("talents", "t", 40)):
    d = os.path.join(ROOT, sub)
    for f in sorted(os.listdir(d)):
        classes.append((f"{pre}-{os.path.splitext(f)[0]}", data_uri(os.path.join(d, f), w)))

# banner -> webp (fallback to jpg if somehow larger)
banner_uri = data_uri(os.path.join(ROOT, "banner.jpg"), 1440, 82)
jpg_uri = embed_file(os.path.join(ROOT, "banner.jpg"), "image/jpeg")
if len(jpg_uri) < len(banner_uri):
    banner_uri = jpg_uri

css = "\n".join(f".{c}{{background-image:url({uri});}}" for c, uri in classes)

tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
assert "/*__IMAGES__*/" in tpl, "marker missing!"
html = tpl.replace("/*__IMAGES__*/", f"--banner:url({banner_uri});\n{css}")
open(OUT, "w", encoding="utf-8").write(html)

# ---- validation ----
defined = {c for c, _ in classes}
ref_tokens = set()
for r in re.findall(r'class="([^"]+)"', html):
    ref_tokens.update(t for t in r.split() if t != "")
js_refs = set(re.findall(r'"(h-[a-z0-9-]+)"', html))
missing = {t for t in (ref_tokens | js_refs) if re.match(r"^(h|i|e|s)-", t) and t not in defined}
print(f"embedded classes : {len(classes)}")
print(f"referenced tokens: {len(ref_tokens | js_refs)}")
print(f"MISSING          : {sorted(missing) if missing else 'none'}")
print(f"final size       : {os.path.getsize(OUT)/1024/1024:.2f} MB")
sys.exit(1 if missing else 0)
