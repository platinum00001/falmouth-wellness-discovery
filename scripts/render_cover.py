#!/usr/bin/env python3
"""Render the magazine cover with a given issue label (Nobska Light photo + masthead).

  python3 scripts/render_cover.py --label "January 2027" [--slug january-2027] [--alias winter-2026 --alias winter-2027]

Source photo: assets/src/cover/nobska1.jpg (Giacomo Barbaro, CC BY-SA 3.0, Wikimedia Commons).
Fonts: scripts/fonts/ (Fraunces, DM Sans; OFL).
Writes assets/img/cover-<slug>.{jpg,webp} (1600x2133) and -900.{jpg,webp} (900x1200);
each --alias gets byte-identical copies so old cover URLs show the new art."""
import argparse, pathlib, shutil
from PIL import Image, ImageDraw, ImageFont
ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS = ROOT / "scripts/fonts"


def f(path, size, wght):
    x = ImageFont.truetype(str(path), size)
    try:
        x.set_variation_by_axes([wght if (a["name"].decode() if isinstance(a["name"], bytes) else a["name"]).lower() in ("weight", "wght") else a["default"] for a in x.get_variation_axes()])
    except Exception:
        pass
    return x


def render(label):
    src = Image.open(ROOT / "assets/src/cover/nobska1.jpg").convert("RGB")
    W, H, TOP = 1800, 2400, 560
    ph = src.resize((W, int(src.size[1] * W / src.size[0])), Image.LANCZOS)
    img = Image.new("RGB", (W, H)); img.paste(ph.crop((0, 0, W, H - TOP)), (0, TOP))
    row = ph.crop((0, 0, W, 6)).resize((1, 1)).getpixel((0, 0))
    top = Image.new("RGB", (W, TOP + 200), row); mask = Image.new("L", (1, TOP + 200))
    for y in range(TOP + 200): mask.putpixel((0, y), 255 if y < TOP else int(255 * (1 - (y - TOP) / 200)))
    img.paste(top, (0, 0), mask.resize((W, TOP + 200)))
    shade = Image.new("RGB", (W, H), (8, 24, 30)); bm = Image.new("L", (1, H))
    for y in range(H): bm.putpixel((0, y), int(190 * max(0, (y - H * 0.62) / (H * 0.38))))
    img = Image.composite(shade, img, bm.resize((W, H)))
    d = ImageDraw.Draw(img)
    F, DM = FONTS / "Fraunces-Variable.ttf", FONTS / "DMSans-Variable.ttf"
    white, coral, sand = (255, 255, 255), (251, 146, 120), (245, 232, 210)
    def ctext(y, t, fo, fill):
        d.text(((W - d.textlength(t, font=fo)) / 2, y), t, font=fo, fill=fill)
    ctext(60, "LOCAL HEALTH & WELLNESS  ·  COMMUNITY  ·  SEASONAL LIVING", f(DM, 38, 600), sand)
    ctext(115, "A QUARTERLY MAGAZINE", f(DM, 36, 700), coral)
    ctext(160, "Falmouth", f(F, 230, 600), white)
    ctext(395, "Wellness Discovery", f(F, 170, 600), white)
    y = 600; d.line((560, y, 870, y), fill=coral, width=5); d.ellipse((888, y - 12, 912, y + 12), fill=coral); d.line((930, y, 1240, y), fill=coral, width=5)
    d.text((80, 660), label, font=f(F, 64, 500), fill=sand)
    d.text((80, 740), "Mind · Body · Soul · Health & Food", font=f(DM, 42, 500), fill=sand)
    lines = [("Local Innovators", "Ideas shaping our community"), ("Where to Eat Well", "Warm, local & inspired"),
             ("Your Quarterly Events Guide", "Happenings & highlights"), ("Falmouth Crossword", "Test your local know-how"),
             ("Pull-out Wellness Map", "Downtown · Main Street & Woods Hole")]
    hf, sf = f(F, 72, 600), f(DM, 42, 400); y = 880
    for h, s in lines:
        d.line((80, y, 280, y), fill=coral, width=5)
        for t, fo, yy in ((h, hf, y + 14), (s, sf, y + 98)):
            d.text((83, yy + 3), t, font=fo, fill=(0, 0, 0)); d.text((80, yy), t, font=fo, fill=white)
        y += 185
    cred = ImageFont.truetype(str(DM), 26); t = "Nobska Light, Woods Hole · Photo: Giacomo Barbaro, CC BY-SA 3.0"
    d.text((W - d.textlength(t, font=cred) - 40, H - 55), t, font=cred, fill=(235, 235, 235))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True); ap.add_argument("--slug"); ap.add_argument("--alias", action="append", default=[])
    a = ap.parse_args()
    slug = a.slug or a.label.lower().replace(" ", "-")
    img = render(a.label)
    out = ROOT / "assets/img"
    big = img.resize((1600, 2133), Image.LANCZOS); sm = img.resize((900, 1200), Image.LANCZOS)
    files = {f"cover-{slug}.jpg": (big, "JPEG"), f"cover-{slug}.webp": (big, "WEBP"), f"cover-{slug}-900.jpg": (sm, "JPEG"), f"cover-{slug}-900.webp": (sm, "WEBP")}
    for name, (im, fmt) in files.items():
        im.save(out / name, fmt, quality=86 if fmt == "JPEG" else 82, **({"optimize": True, "progressive": True} if fmt == "JPEG" else {"method": 6}))
        for al in a.alias:
            shutil.copyfile(out / name, out / name.replace(slug, al))
    print("cover:", ", ".join(files), "+ aliases", a.alias)


if __name__ == "__main__":
    main()
