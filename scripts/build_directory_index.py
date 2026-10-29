#!/usr/bin/env python3
"""Rewrite the <main> of directory.html from data/directory.json:
Main Street & Homeport first, then every category (in data order) with counts."""
import html, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "data/directory.json").read_text(encoding="utf-8"))
e = lambda s: html.escape(str(s or ""), quote=True)
man = {i["filename"][:-4]: i["alt"] for i in json.loads((ROOT / "assets/img/v3/manifest.json").read_text())["images"]}
real = lambda c: [x for x in c["listings"] if not x.get("placeholder")]
hp = sum(1 for c in d["categories"] for x in real(c) if x.get("district") == "homeport")
ms = sum(1 for c in d["categories"] for x in real(c) if x.get("district") == "main-street")
cards = []
for c in d["categories"]:
    n = len(real(c)); loc = sum(1 for x in real(c) if x.get("district"))
    if n:
        meta = f"{n} listing{'s' if n != 1 else ''}" + (f" · {loc} on Main Street or at Homeport" if loc else "")
    else:
        meta = "Featured spot available"
    cls = "dir-link is-local" if loc else ("dir-link is-open" if not n else "dir-link")
    cards.append(f'<a class="{cls}" href="{e(c["slug"])}/"><strong>{e(c["short"])}</strong><span>{e(c.get("nav") or "")}</span><small>{e(meta)}</small></a>')
cards.append('<a class="dir-link" href="free-help.html"><strong>Free Food &amp; Help</strong><span>Free meals, pantries, recovery meetings and hotlines.</span><small>Free resources</small></a>')
main = f"""<main id="main">
  <div class="wrap page-hero">
    <p class="eyebrow">Falmouth, Cape Cod</p>
    <h1>The Falmouth directory</h1>
    <p class="lede">Local shops, services and wellness businesses, starting on Main Street and at Homeport. Every listing has an address and a phone or website, so you can call ahead or walk in.</p>
  </div>
  <section class="section" style="padding-top:0">
    <div class="wrap">
      <div class="dir-feature">
        <a class="dir-hero reveal" href="shops/"><picture><source type="image/webp" srcset="assets/img/v3/village-main-street-autumn-640.webp"><img src="assets/img/v3/village-main-street-autumn-640.jpg" width="640" height="360" alt="{e(man['village-main-street-autumn'])}" loading="lazy"></picture><span><b>Main Street</b>{ms} shops, studios and services in Falmouth village</span></a>
        <a class="dir-hero reveal" href="map.html?area=homeport"><picture><source type="image/webp" srcset="assets/img/v3/cafe-counter-morning-640.webp"><img src="assets/img/v3/cafe-counter-morning-640.jpg" width="640" height="360" alt="{e(man['cafe-counter-morning'])}" loading="lazy"></picture><span><b>Homeport</b>{hp} neighbors at Gifford Street and Jones Road</span></a>
      </div>
      <div class="sec-head"><p class="eyebrow">Browse by category</p><h2>Every category</h2></div>
      <div class="dir-grid">
      {chr(10).join("      " + c for c in cards).strip()}
      </div>
    </div>
  </section>
</main>"""
p = ROOT / "directory.html"
s = p.read_text(encoding="utf-8")
s = re.sub(r"<main id=\"main\">.*?</main>", lambda m: main, s, flags=re.S)
p.write_text(s, encoding="utf-8")
print("directory.html:", len(cards), "cards; main street", ms, "homeport", hp)
