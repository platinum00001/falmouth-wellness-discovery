#!/usr/bin/env python3
"""Render the 17x11 pull-out (map-print.html) to static spread images for the
flipbook centerfold, and record pin positions for the animated overlay.
Needs a local server: python3 -m http.server 8765 (in the site root)."""
import json, pathlib, sys, io
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/"
OUT = ROOT / "assets/img/mag"; OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 1900, "height": 1300}, device_scale_factor=2)
    pg.goto(BASE + "map-print.html", wait_until="networkidle")
    pg.wait_for_timeout(3500)
    pg.evaluate("document.querySelectorAll('.leaflet-control-container').forEach(e=>e.style.display='none')")
    sheets = pg.query_selector_all(".print-page .walk-sheet")
    info = {}
    for face, el in zip(["front", "back"], sheets):
        png = el.screenshot()
        im = Image.open(io.BytesIO(png)).convert("RGB")
        w = 2400; im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(OUT / f"centerfold-{face}.jpg", quality=84, optimize=True, progressive=True)
        im.save(OUT / f"centerfold-{face}.webp", quality=80)
        sm = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
        sm.save(OUT / f"centerfold-{face}-1200.jpg", quality=82, optimize=True, progressive=True)
        info[face] = {"src": f"assets/img/mag/centerfold-{face}.jpg", "webp": f"assets/img/mag/centerfold-{face}.webp",
                      "small": f"assets/img/mag/centerfold-{face}-1200.jpg", "width": im.width, "height": im.height}
    pins = pg.evaluate("""() => {
      const sheet = document.querySelector('.print-page .walk-sheet').getBoundingClientRect();
      return [...document.querySelectorAll('#print-map .walk-icon')].map(el => {
        const badge = el.querySelector('.walk-badge'); const r0 = (badge || el).getBoundingClientRect();
        const r = {left: r0.left + r0.width / 2 - 16, top: r0.top + r0.height / 2 - 30};
        const pin = el.querySelector('.walk-pin');
        return {n: badge ? badge.textContent : '', x: +(((r.left + 16) - sheet.left) / sheet.width * 100).toFixed(3),
                y: +(((r.top + 30) - sheet.top) / sheet.height * 100).toFixed(3),
                color: pin ? pin.style.getPropertyValue('--pin') : '', focus: pin ? pin.classList.contains('is-focus') : false,
                title: el.getAttribute('title') || el.getAttribute('alt') || ''};
      });
    }""")
    info["front"]["pins"] = pins
    b.close()
(ROOT / "data/centerfold-images.json").write_text(json.dumps(info, indent=2) + "\n")
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "pins"} for k, v in info.items()}, indent=1), len(pins), "pins")
