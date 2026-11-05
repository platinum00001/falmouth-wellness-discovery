#!/usr/bin/env python3
"""Grid references for the pull-out map (A-F across, 1-4 down, inside the ad border).

Reads  data/pullout-map.json        (grid frame, written by build_pullout_map.py)
       data/pullout-landmarks.json  (name, side, category, x/y = where the landmark sits on the art)
Writes data/pullout-landmarks.json  (adds "grid", e.g. "B4", and "ref", e.g. "Woods Hole side B4")
       guide.html                   (static "Find it on the pull-out map" index between the
                                     <!-- pullout-index:start/end --> markers)
       data/issue1.json             (walkingMap.guide items get a "pullout" ref when the name matches)
Usage  python3 scripts/pullout_grid_refs.py [--check]   (--check prints the table only)
To add a landmark: append {name, side: downtown|woodshole, category, x, y} and rerun.
Tip: python3 scripts/pullout_grid_refs.py --mark draws the points on build/pullout/mark-<side>.png."""
import html, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
SIDE_NAME = {"downtown": "Downtown side", "woodshole": "Woods Hole side"}
CATS = [("landmark", "Landmarks & Main Street"), ("museum", "Museums & science"), ("beach", "Beaches"),
        ("trail", "Trails & bikeway"), ("nature", "Ponds, parks & gardens"), ("harbor", "Harbors & ferries"),
        ("ferry", "Harbors & ferries"), ("bus", "Buses & shuttles"), ("market", "Markets")]


def cell(x, y, g):
    l, t, r, b = g["frame"]
    cols, rows = g["cols"], g["rows"]
    if not (l <= x <= r and t <= y <= b):
        return "off map"
    c = min(len(cols) - 1, int((x - l) / (r - l) * len(cols)))
    w = min(rows - 1, int((y - t) / (b - t) * rows))
    return cols[c] + str(w + 1)


def main():
    pm = json.loads((ROOT / "data/pullout-map.json").read_text()); g = pm["grid"]
    P = ROOT / "data/pullout-landmarks.json"
    data = json.loads(P.read_text())
    for lm in data["landmarks"]:
        lm["grid"] = cell(lm["x"], lm["y"], g)
        lm["ref"] = SIDE_NAME[lm["side"]] + " " + lm["grid"]
    for lm in data["landmarks"]:
        print(f'{lm["ref"]:<22} {lm["name"]}')
    if "--mark" in sys.argv:
        from PIL import Image, ImageDraw
        for side, stem in (("downtown", "side1-downtown-17x11"), ("woodshole", "side2-woodshole-17x11")):
            im = Image.open(ROOT / f"build/pullout/print-{stem}.jpg"); d = ImageDraw.Draw(im)
            for lm in data["landmarks"]:
                if lm["side"] == side:
                    x, y = lm["x"] * im.width, lm["y"] * im.height
                    d.ellipse((x - 22, y - 22, x + 22, y + 22), outline=(255, 0, 0), width=8)
            im.resize((2550, 1650)).save(ROOT / f"build/pullout/mark-{side}.png")
    if "--check" in sys.argv:
        return
    P.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")

    # static index for guide.html
    out = ['<section class="pullout-index wrap" id="pullout-index" aria-labelledby="pullout-index-h">',
           '<header class="guide-head"><p class="eyebrow">On the printed pull-out map</p><h2 id="pullout-index-h">Find it on the pull-out map</h2>',
           '<p>The illustrated pull-out in the centre of the magazine has its own grid: letters A–F across the top and bottom, numbers 1–4 down the sides, inside the partner border. '
           'The front is the <strong>Downtown side</strong> (Downtown · Main Street); the back is the <strong>Woods Hole side</strong> (Main Street &amp; Woods Hole). '
           'Some places, such as the Village Green and the library, are drawn on both sides. Beaches marked “inset” are in the Beaches up north box, not to scale with the main map.</p>',
           '<p class="cta-row"><a class="btn btn-small" href="magazine.html?page=12">See the pull-out in the flipbook</a> '
           '<a class="btn btn-small btn-ghost" href="' + pm["pdf"] + '" download>Download the pull-out map (PDF)</a></p></header>',
           '<div class="pullout-index-grid">']
    seen = []
    for key, title in CATS:
        if title in seen: continue
        seen.append(title)
        keys = [k for k, t in CATS if t == title]
        items = sorted([lm for lm in data["landmarks"] if lm["category"] in keys], key=lambda lm: (lm["name"], lm["side"]))
        if not items: continue
        out.append(f'<div class="pullout-group"><h3>{html.escape(title)}</h3><ul>')
        for lm in items:
            out.append(f'<li><span class="grid-ref" title="{html.escape(SIDE_NAME[lm["side"]])}">{lm["grid"]}</span><span><strong>{html.escape(lm["name"])}</strong> '
                       f'<em>{html.escape(SIDE_NAME[lm["side"]])} {lm["grid"]}</em></span></li>')
        out.append("</ul></div>")
    out.append("</div></section>")
    block = "<!-- pullout-index:start -->\n" + "\n".join(out) + "\n<!-- pullout-index:end -->"
    G = ROOT / "guide.html"; s = G.read_text()
    if "<!-- pullout-index:start -->" in s:
        s = re.sub(r"<!-- pullout-index:start -->.*?<!-- pullout-index:end -->", lambda m: block, s, flags=re.S)
    else:
        s = s.replace('  <div class="wrap" id="guide-lists"></div>', block + '\n  <div class="wrap" id="guide-lists"></div>')
    G.write_text(s)

    # tag the online visitor-guide entries with their pull-out refs
    I = ROOT / "data/issue1.json"; issue = json.loads(I.read_text())
    alias = {"nobska": ["Nobska Light"], "village-green": ["Falmouth Village Green"], "museums-on-the-green": ["Museums on the Green"],
             "highfield": ["Highfield Hall & Gardens"], "shining-sea": ["Shining Sea Bikeway (runs south toward Woods Hole)", "Shining Sea Bikeway (Surf Drive to Woods Hole)"],
             "surf-drive": ["Surf Drive Beach"], "old-silver": ["Old Silver Beach (inset, ~5 mi north)"], "falmouth-heights": ["Falmouth Heights Beach"],
             "whoi-discovery": ["WHOI"], "woods-hole-aquarium": ["Woods Hole Science Aquarium"]}
    by = {}
    for lm in data["landmarks"]:
        by.setdefault(lm["name"], []).append(lm["ref"])
    for group in issue["walkingMap"]["guide"].values():
        if not isinstance(group, list): continue
        for it in group:
            refs = [r for n in alias.get(it.get("id"), []) for r in by.get(n, [])]
            if refs: it["pullout"] = " · ".join(dict.fromkeys(refs))
            else: it.pop("pullout", None)
    I.write_text(json.dumps(issue, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
