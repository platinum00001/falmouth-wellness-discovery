#!/usr/bin/env python3
"""Build the flipbook thumbnails and the downloadable issue PDF.

Renders magazine.html?print=1 (every page laid out at 8.5x11 in) in headless Chrome, saves
one thumbnail per page, prints the 32 letter pages to PDF, then splices in the pull-out map:
pages 12-13 (front spread) and 14-15 (back spread) are replaced by the two full-bleed 17x11
pages of assets/fwd-pullout-map-<slug>.pdf (built by build_pullout_map.py). The issue PDF
therefore has 30 PDF pages = 32 folios: 11 letter pages, 2 tabloid insert pages, 17 letter pages.

Needs a local server in the site root:  python3 -m http.server 8765
Usage: python3 scripts/build_flipbook_assets.py [base-url] [--slug january-2027] [--alias january-2027 ...]
Outputs: assets/img/mag/thumbs/pNN.jpg, assets/fwd-<slug>.pdf (+ alias copies)"""
import argparse, io, json, pathlib, shutil
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("base", nargs="?", default="http://localhost:8765/")
ap.add_argument("--slug", default="january-2027")
ap.add_argument("--alias", action="append", default=[])
a = ap.parse_args()
BASE = a.base
TH = ROOT / "assets/img/mag/thumbs"; TH.mkdir(parents=True, exist_ok=True)
OUT = ROOT / f"assets/fwd-{a.slug}.pdf"
BODY = ROOT / "build/issue-body.pdf"; BODY.parent.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 816, "height": 1056}, device_scale_factor=1)
    pg.goto(BASE + "magazine.html?print=1", wait_until="networkidle")
    pg.wait_for_function("document.documentElement.dataset.ready === '1'", timeout=30000)
    pg.wait_for_timeout(800)
    pages = pg.query_selector_all("#book .page")
    for i, el in enumerate(pages):
        im = Image.open(io.BytesIO(el.screenshot())).convert("RGB")
        im = im.resize((240, round(240 * im.height / im.width)), Image.LANCZOS)
        im.save(TH / f"p{i + 1:02d}.jpg", quality=78, optimize=True, progressive=True)
    pg.emulate_media(media="print")
    pg.pdf(path=str(BODY), width="8.5in", height="11in", print_background=True,
           prefer_css_page_size=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print(len(pages), "pages rendered")

import pikepdf
from pikepdf import PdfImage, Name
pdf = pikepdf.open(BODY)
# Chrome stores photos losslessly; recompress them as JPEG so the PDF stays small.
seen = set()
for page in pdf.pages:
    for _, raw in page.images.items():
        if raw.objgen in seen: continue
        seen.add(raw.objgen)
        if raw.get("/Filter") == Name.DCTDecode or raw.get("/BitsPerComponent") != 8: continue
        try: im = PdfImage(raw).as_pil_image().convert("RGB")
        except Exception: continue
        if im.width * im.height < 120000: continue
        cap = 2000 if im.width > 2000 else 1400
        if max(im.size) > cap:
            s = cap / max(im.size); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=80, optimize=True, progressive=True)
        raw.write(buf.getvalue(), filter=Name.DCTDecode)
        raw.Width, raw.Height = im.width, im.height
        raw.ColorSpace = Name.DeviceRGB; raw.BitsPerComponent = 8
        if "/DecodeParms" in raw: del raw["/DecodeParms"]

issue = json.loads((ROOT / "data/issue1.json").read_text())
kinds = [pp["kind"] for pp in issue["pages"]]
ins = [i for i, k in enumerate(kinds) if k == "pullout"]
out = pikepdf.new()
if ins and len(pdf.pages) == len(kinds):
    first, last = ins[0], ins[-1]
    pull = pikepdf.open(ROOT / f"assets/fwd-pullout-map-{a.slug}.pdf")
    out.pages.extend(pdf.pages[:first])
    out.pages.extend(pull.pages)                     # 2 x 17x11 full-bleed pages
    out.pages.extend(pdf.pages[last + 1:])
    print(f"insert: letter pages {first + 1}-{last + 1} replaced by {len(pull.pages)} tabloid pages")
else:
    out.pages.extend(pdf.pages)
with out.open_metadata() as meta:
    meta["dc:title"] = f"Falmouth Wellness Discovery · {issue['issue']['season']} · Issue {issue['issue']['number']}"
    meta["dc:description"] = "32 folios. Pages 12-15 are the pull-out map insert, printed here as two 17x11 pages (front: Downtown · Main Street; back: Main Street & Woods Hole)."
out.save(OUT, compress_streams=True)
for al in a.alias:
    shutil.copyfile(OUT, ROOT / f"assets/fwd-{al}.pdf")
print("issue PDF:", OUT.relative_to(ROOT), len(out.pages), "PDF pages,", OUT.stat().st_size // 1024, "KB; aliases:", a.alias)
