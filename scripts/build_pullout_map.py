#!/usr/bin/env python3
"""Pull-out map compositor (the 17x11 two-sided centerfold insert).

Input  : assets/src/pullout/side1-downtown-17x11.jpg  (front, 2048x1325, ~120 dpi)
         assets/src/pullout/side2-woodshole-17x11.jpg (back)
Steps  : 1. upscale to 5100x3300 (300 dpi at 17x11): Real-ESRGAN x2plus via spandrel/torch
            when available (cached in build/), then Lanczos to size; else plain Lanczos.
         2. cover the Refuge Fitness border ad (slot R4, both sides) with a matching
            "Featured spot available" partner panel (the art has the ads baked in; there
            is no layered source, so the slot is covered, not regenerated), and re-letter
            the Falmouth Taxi ad's contact band (R2, both sides) to "Falmouth Taxi ·
            Falmouth Transport (774) 247-5263" (its own phone removed, owner 2026-11-04).
         3. draw the A-F / 1-4 grid inside the map frame (thin navy lines + edge badges).
Output : build/pullout/print-<side>.jpg                    5100x3300 print composites
         assets/img/mag/pullout/<face>-{4096,2400,1200}.webp, <face>-2400.jpg  web
         assets/fwd-pullout-map-<issue>.pdf (+ copies named by --alias)
         data/pullout-map.json                             grid geometry + image paths
Usage  : python3 scripts/build_pullout_map.py [--issue january-2027] [--alias winter-2026]
         [--no-sr] [--label "January 2027"]
"""
import argparse, json, pathlib, shutil, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS = ROOT / "scripts/fonts"
SRC = ROOT / "assets/src/pullout"
BUILD = ROOT / "build"; (BUILD / "pullout").mkdir(parents=True, exist_ok=True)
WEB = ROOT / "assets/img/mag/pullout"; WEB.mkdir(parents=True, exist_ok=True)
PW, PH = 5100, 3300                       # 17x11 in at 300 dpi
SIDES = [  # (face, source file, title)
    ("downtown", "side1-downtown-17x11", "Downtown · Main Street (front)"),
    ("woodshole", "side2-woodshole-17x11", "Main Street & Woods Hole (back)"),
]
# Map frame inside the ad border, in source pixels (2048x1325), measured from the navy frame lines.
FRAME = (219, 147, 1829, 1179)
COLS, ROWS = "ABCDEF", 4
# Border-ad slots to cover: slot id -> fractions [left, top, width, height] (from health-wellness-maps maps.json)
COVER = {"R4": [0.89588, 0.58091, 0.09941, 0.15091]}   # Refuge Fitness on both sides
SLOTS = {"R2": [0.89588, 0.26818, 0.09941, 0.15091], "R4": [0.89588, 0.58091, 0.09941, 0.15091]}
# Text patches on an ad's bottom contact band: slot -> (band in source px relative to the slot, lines)
# R2 Falmouth Taxi (both sides): its own phone removed; points to Falmouth Transport (owner, 2026-11-04).
PATCH = {"R2": ((30, 171.5, 174.5, 197), [("Falmouth Taxi · Falmouth Transport", "BarlowCondensed-SemiBold.ttf", 0.30, (176, 52, 44)),
                                           ("(774) 247-5263", "BreeSerif-Regular.ttf", 0.42, (35, 35, 40))])}
NAVY, CREAM, RED, TEAL, CORAL = (29, 42, 77), (247, 240, 226), (176, 52, 44), (44, 127, 123), (244, 162, 89)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), int(size))


def upscale(stem, use_sr):
    """Return a 5100x3300 RGB image for this side."""
    src = Image.open(SRC / f"{stem}.jpg").convert("RGB")
    cache = BUILD / f"pullout-x2-{stem}.png"
    if use_sr and not cache.exists():
        try:
            import numpy as np, torch
            from spandrel import ModelLoader
            model_file = BUILD / "models/RealESRGAN_x2plus.pth"
            if not model_file.exists():
                import urllib.request
                model_file.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve("https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth", model_file)
            m = ModelLoader().load_from_file(str(model_file)).eval()
            x = torch.from_numpy(np.asarray(src).astype(np.float32) / 255).permute(2, 0, 1)[None]
            H, W = x.shape[2:]; S, T, P = m.scale, 256, 16
            out = torch.zeros(1, 3, H * S, W * S)
            with torch.inference_mode():
                for y0 in range(0, H, T):
                    for x0 in range(0, W, T):
                        ya, xa = max(0, y0 - P), max(0, x0 - P)
                        o = m.model(x[:, :, ya:min(H, y0 + T + P), xa:min(W, x0 + T + P)])
                        hh, ww = min(T, H - y0) * S, min(T, W - x0) * S
                        out[:, :, y0 * S:y0 * S + hh, x0 * S:x0 * S + ww] = o[:, :, (y0 - ya) * S:(y0 - ya) * S + hh, (x0 - xa) * S:(x0 - xa) * S + ww]
            a = (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype("uint8")
            Image.fromarray(a).save(cache)
            print(f"  {stem}: Real-ESRGAN x2plus -> {a.shape[1]}x{a.shape[0]}")
        except Exception as e:  # torch/spandrel missing or failed
            print(f"  {stem}: Real-ESRGAN unavailable ({type(e).__name__}: {e}); using Lanczos")
    base = Image.open(cache).convert("RGB") if (use_sr and cache.exists()) else src
    how = "Real-ESRGAN x2 + Lanczos" if base is not src else "Lanczos only"
    return base.resize((PW, PH), Image.LANCZOS), how


def partner_panel(w, h):
    """'Featured spot available' panel, same footprint as the side ad art it replaces."""
    import math
    im = Image.new("RGB", (w, h), CREAM); d = ImageDraw.Draw(im)
    U = h / 100.0                                  # layout unit = 1% of panel height
    band = int(h * 0.50)
    d.rectangle((0, 0, w, band), fill=TEAL)
    def ctext(y, t, f, fill):
        d.text(((w - d.textlength(t, font=f)) / 2, y), t, font=f, fill=fill)
    ctext(4 * U, "FEATURED SPOT", font("BarlowCondensed-Bold.ttf", 8.5 * U), (255, 255, 255))
    cx, cy, r = w * 0.5, 27 * U, 9.5 * U            # sun + waves (the magazine mark)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CORAL)
    for i, yy in enumerate((38 * U, 44 * U)):
        pts = [(w * 0.1 + w * 0.8 * t / 100, yy + math.sin(t / 100 * 3 * math.pi) * 1.6 * U) for t in range(101)]
        d.line(pts, fill=(168, 216, 206) if i == 0 else (255, 255, 255), width=max(3, int(1.3 * U)), joint="curve")
    ctext(53 * U, "Your ad here", font("BreeSerif-Regular.ttf", 11.5 * U), NAVY)
    ctext(67 * U, "Featured spot available", font("BarlowCondensed-SemiBold.ttf", 7.2 * U), RED)
    d.line((w * 0.1, 75 * U, w * 0.9, 75 * U), fill=RED, width=max(2, int(0.5 * U)))
    ctext(77 * U, "Become a partner", font("BreeSerif-Regular.ttf", 8 * U), NAVY)
    ctext(86.5 * U, "(774) 247-5263", font("BreeSerif-Regular.ttf", 8.5 * U), NAVY)
    d.rectangle((0, 0, w - 1, h - 1), outline=NAVY, width=max(3, int(0.7 * U)))
    return im


def cover_slots(im):
    s = PW / 2048
    for slot, (fx, fy, fw, fh) in COVER.items():
        x, y = fx * 2048, fy * 1325
        # the ad art inside the R4 card spans x+29..x+175, y+3..y+197 (source px, measured)
        box = [round(v * s) for v in (x + 29, y + 3, x + 175, y + 197)]
        im.paste(partner_panel(box[2] - box[0], box[3] - box[1]), (box[0], box[1]))
    return im


def patch_bands(im):
    s = PW / 2048
    d = ImageDraw.Draw(im)
    for slot, ((x0, y0, x1, y1), lines) in PATCH.items():
        sx, sy = SLOTS[slot][0] * 2048, SLOTS[slot][1] * 1325
        box = [round((sx + x0) * s), round((sy + y0) * s), round((sx + x1) * s), round((sy + y1) * s)]
        d.rectangle(box, fill=(252, 236, 211))
        H = box[3] - box[1]
        y = box[1] + H * 0.12
        for text, fnt, frac, col in lines:
            f = font(fnt, H * frac)
            while d.textlength(text, font=f) > (box[2] - box[0]) * 0.94: f = font(fnt, f.size - 1)
            d.text(((box[0] + box[2] - d.textlength(text, font=f)) / 2, y), text, font=f, fill=col)
            y += f.size * 1.12
    return im


def grid(im):
    s = PW / 2048
    x0, y0, x1, y1 = [v * s for v in FRAME]
    cw, rh = (x1 - x0) / len(COLS), (y1 - y0) / ROWS
    over = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(over)
    lw = max(2, round(1.25 * s))
    for i in range(1, len(COLS)):
        x = x0 + i * cw; d.line((x, y0, x, y1), fill=NAVY + (110,), width=lw)
    for j in range(1, ROWS):
        y = y0 + j * rh; d.line((x0, y, x1, y), fill=NAVY + (110,), width=lw)
    r = 10.5 * s; f = font("BreeSerif-Regular.ttf", 14.5 * s)
    def badge(cx, cy, t):
        d.ellipse((cx - r - 2.2 * s, cy - r - 2.2 * s, cx + r + 2.2 * s, cy + r + 2.2 * s), fill=(255, 255, 255, 235))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NAVY + (240,))
        bb = d.textbbox((0, 0), t, font=f)
        d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), t, font=f, fill=(255, 255, 255, 255))
    pad = r + 4 * s
    for i, c in enumerate(COLS):
        cx = x0 + (i + 0.5) * cw; badge(cx, y0 + pad, c); badge(cx, y1 - pad, c)
    for j in range(ROWS):
        cy = y0 + (j + 0.5) * rh; badge(x0 + pad, cy, str(j + 1)); badge(x1 - pad, cy, str(j + 1))
    out = im.convert("RGBA"); out.alpha_composite(over)
    return out.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", default="january-2027")
    ap.add_argument("--label", default="January 2027")
    ap.add_argument("--alias", action="append", default=[], help="extra PDF slugs that get a copy (old links)")
    ap.add_argument("--no-sr", action="store_true", help="skip Real-ESRGAN, Lanczos only")
    a = ap.parse_args()
    info = {"issue": a.label, "sheet": "17x11 in, two-sided, folds to 8.5x11", "grid": {
        "cols": list(COLS), "rows": ROWS,
        "frame": [round(FRAME[0] / 2048, 5), round(FRAME[1] / 1325, 5), round(FRAME[2] / 2048, 5), round(FRAME[3] / 1325, 5)],
        "note": "frame = [left, top, right, bottom] of the map area as fractions of the sheet"}, "faces": {}}
    prints = []
    for face, stem, title in SIDES:
        im, how = upscale(stem, not a.no_sr)
        im = grid(patch_bands(cover_slots(im)))
        p = BUILD / "pullout" / f"print-{stem}.jpg"
        im.save(p, quality=95, subsampling=0, dpi=(300, 300), optimize=True)      # print master
        q = BUILD / "pullout" / f"pdf-{stem}.jpg"                                  # PDF copy, smaller
        im.save(q, quality=86, dpi=(300, 300), optimize=True, progressive=False)
        prints.append(q)
        for wpx in (4096, 2400, 1200):
            sm = im.resize((wpx, round(PH * wpx / PW)), Image.LANCZOS)
            sm.save(WEB / f"{face}-{wpx}.webp", quality=84 if wpx < 4096 else 80, method=6)
            if wpx == 2400: sm.save(WEB / f"{face}-2400.jpg", quality=82, optimize=True, progressive=True)
        base = f"assets/img/mag/pullout/{face}"
        info["faces"][face] = {"title": title, "src": base + "-2400.jpg", "webp": base + "-2400.webp",
                               "small": base + "-1200.webp", "zoom": base + "-4096.webp", "width": 2400, "height": round(PH * 2400 / PW),
                               "upscale": how}
        print(f"{face}: {how}; print {p.relative_to(ROOT)}")
    # standalone 2-page map PDF, full-bleed 17x11 (JPEGs embedded as-is)
    from reportlab.pdfgen import canvas
    pdf = ROOT / f"assets/fwd-pullout-map-{a.issue}.pdf"
    c = canvas.Canvas(str(pdf), pagesize=(17 * 72, 11 * 72))
    c.setTitle(f"Falmouth Health & Wellness pull-out map · {a.label}"); c.setAuthor("Falmouth Wellness Discovery")
    c.setSubject("Pull-out map insert: front Downtown · Main Street, back Main Street & Woods Hole. 17x11 in, 300 dpi.")
    for p in prints:
        c.drawImage(str(p), 0, 0, 17 * 72, 11 * 72); c.showPage()
    c.save()
    for al in a.alias:
        shutil.copyfile(pdf, ROOT / f"assets/fwd-pullout-map-{al}.pdf")
    info["pdf"] = f"assets/fwd-pullout-map-{a.issue}.pdf"
    info["print"] = [f"build/pullout/print-{stem}.jpg" for _, stem, _ in SIDES]
    (ROOT / "data/pullout-map.json").write_text(json.dumps(info, indent=2) + "\n")
    print("PDF", pdf.relative_to(ROOT), pdf.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
