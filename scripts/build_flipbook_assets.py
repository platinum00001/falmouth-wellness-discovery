#!/usr/bin/env python3
"""Build the flipbook's page thumbnails and the downloadable PDF from
magazine.html?print=1 (every page laid out at 8.5x11 in).
Needs a local server in the site root: python3 -m http.server 8765
Outputs: assets/img/mag/thumbs/pNN.jpg, assets/fwd-winter-2027.pdf"""
import io, pathlib, sys
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/"
TH = ROOT / "assets/img/mag/thumbs"; TH.mkdir(parents=True, exist_ok=True)
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
    pg.pdf(path=str(ROOT / "assets/fwd-winter-2027.pdf"), width="8.5in", height="11in", print_background=True,
           prefer_css_page_size=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print(len(pages), "pages;", (ROOT / "assets/fwd-winter-2027.pdf").stat().st_size // 1024, "KB PDF")

# Chrome stores photos losslessly; recompress them as JPEG so the PDF stays small.
try:
    import pikepdf
    from pikepdf import PdfImage, Name
    path = ROOT / "assets/fwd-winter-2027.pdf"
    pdf = pikepdf.open(path, allow_overwriting_input=True)
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
            for k in ("/DecodeParms",):
                if k in raw: del raw[k]
    pdf.save(path, compress_streams=True)
    print("recompressed PDF:", path.stat().st_size // 1024, "KB")
except ImportError:
    print("pikepdf not installed; PDF left as Chrome wrote it")
