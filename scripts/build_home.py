#!/usr/bin/env python3
"""Fill the home page 'Main Street & Homeport' block from data/directory.json.

Usage: python3 scripts/build_home.py   (rewrites the block between HL markers in index.html)
"""
import html, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "data/directory.json").read_text(encoding="utf-8"))
items = []
for c in d["categories"]:
    for x in c["listings"]:
        if x.get("placeholder") or not x.get("district"): continue
        items.append((c, x))
e = lambda s: html.escape(str(s or ""), quote=True)
def num(x):
    m = re.match(r"(\d+)", x.get("address") or ""); return int(m.group(1)) if m else 9999
def li(c, x):
    cls = ' class="home-base"' if x["id"] == "cape-island-cafe" else ""
    street = (x.get("address") or "").split(",")[0]
    return f'<li{cls}><a href="{c["slug"]}/#{e(x["id"])}">{e(x["name"])}</a><small>{e(x.get("subcategory") or c["short"])} · {e(street)}</small></li>'
home = sorted([t for t in items if t[1]["district"] == "homeport"], key=lambda t: (t[1]["id"] != "cape-island-cafe", num(t[1])))
# Main Street: keep it about wellness + shops; skip bars/restaurants other than the healthy picks to stay focused
SKIP_CATS = {"food"}
ms = sorted([t for t in items if t[1]["district"] == "main-street" and (t[0]["slug"] not in SKIP_CATS or t[1].get("featured"))], key=lambda t: num(t[1]))
def pic(stem, alt):
    return (f'<div class="photo"><picture><source type="image/webp" srcset="assets/img/v3/{stem}-640.webp 640w, assets/img/v3/{stem}.webp 1280w" sizes="(min-width: 900px) 50vw, 100vw">'
            f'<img src="assets/img/v3/{stem}.jpg" srcset="assets/img/v3/{stem}-640.jpg 640w, assets/img/v3/{stem}.jpg 1280w" sizes="(min-width: 900px) 50vw, 100vw" width="1280" height="720" alt="{e(alt)}" loading="lazy" decoding="async"></picture></div>')
man = {i["filename"][:-4]: i["alt"] for i in json.loads((ROOT / "assets/img/v3/manifest.json").read_text())["images"]}
block = f"""<div class="local-grid">
        <article class="local-col reveal">
          {pic("cafe-counter-morning", man["cafe-counter-morning"])}
          <div class="local-body">
            <p class="eyebrow">Gifford Street at Jones Road</p>
            <h3>Homeport</h3>
            <p>The magazine’s home base. Lunch, two dental offices, a chiropractor, a nutrition shop and a family insurance agency share one parking lot.</p>
            <ul class="local-list">{"".join(li(c, x) for c, x in home)}</ul>
            <a class="btn btn-small" href="map.html?area=homeport">See Homeport on the map</a>
          </div>
        </article>
        <article class="local-col reveal">
          {pic("village-main-street-autumn", man["village-main-street-autumn"])}
          <div class="local-body">
            <p class="eyebrow">Falmouth village</p>
            <h3>Main Street</h3>
            <p>From the Village Green to Davis Straits: the library, Town Hall Square, bookshop, jewelers, boutiques, salons and studios. {len(ms)} wellness and shopping stops, in walking order.</p>
            <ul class="local-list">{"".join(li(c, x) for c, x in ms[:10])}</ul>
            <a class="btn btn-small" href="map.html?area=main-street">Walk Main Street on the map</a> <a class="btn btn-small btn-ghost" href="shops/">All Main Street shops</a>
          </div>
        </article>
      </div>"""
p = ROOT / "index.html"
s = p.read_text(encoding="utf-8")
s = re.sub(r"<!-- HL:start -->.*?<!-- HL:end -->", "<!-- HL:start -->\n      " + block + "\n      <!-- HL:end -->", s, flags=re.S)
p.write_text(s, encoding="utf-8")
print("home: homeport", len(home), "main street", len(ms))
