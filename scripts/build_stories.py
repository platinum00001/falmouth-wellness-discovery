#!/usr/bin/env python3
"""Build stories.html from data/falmouth-stories.json.

Usage (from the site root):  python3 scripts/build_stories.py
"""
from __future__ import annotations
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_chrome import footer, header, FONTS  # noqa: E402


def esc(value: str) -> str:
    return html.escape(str(value or ""), quote=True)


def partner_html(partner: dict) -> str:
    if not partner:
        return ""
    name = esc(partner["name"])
    href = esc(partner["href"])
    note = esc(partner.get("note") or "")
    return (
        f'<p class="story-partner"><strong>Nearby partner:</strong> '
        f'<a href="{href}">{name}</a>'
        + (f" — {note}" if note else "")
        + "</p>"
    )


def loc_block(loc: dict, story: dict) -> str:
    partner = loc.get("nearby_partner") or story["nearby_partner"]
    off = loc.get("off_sheet")
    ref = loc["grid_ref"]
    badge = "Off sheet" if off else ref.split(" side ")[-1] if " side " in ref else ref
    title = loc["title"]
    note = loc.get("grid_note") or ""
    return f"""<div class="story-loc">
      <span class="grid-ref{" is-off" if off else ""}" title="{esc(ref)}">{esc(badge)}</span>
      <div>
        <p class="story-loc-title"><strong>{esc(title)}</strong></p>
        <p class="meta-addr">{esc(loc["address"])}</p>
        <p class="story-grid">{esc(ref)}{(" — " + esc(note)) if note else ""}</p>
        {partner_html(partner) if loc.get("nearby_partner") else ""}
        <p><a href="map.html?story={esc(loc["id"])}">See this pin on the discovery map</a></p>
      </div>
    </div>"""


def card(story: dict) -> str:
    sources = "".join(
        f'<li><a href="{esc(s["url"])}" rel="noopener">{esc(s["label"])}</a></li>'
        for s in story["sources"]
    )
    locs = "".join(loc_block(loc, story) for loc in story["locations"])
    website = story["website"]
    partner = "" if any(loc.get("nearby_partner") for loc in story["locations"]) and len(story["locations"]) > 1 else partner_html(story["nearby_partner"])
    # Always show story-level partner too when locations have their own? For multi-pin, location partners are enough; still show a story-level line if not all locs have one.
    if any(not loc.get("nearby_partner") for loc in story["locations"]):
        partner = partner_html(story["nearby_partner"])
    else:
        partner = ""
    return f"""<article class="story-card" id="{esc(story["id"])}">
  <header>
    <p class="eyebrow">Falmouth Stories</p>
    <h2>{esc(story["title"])}</h2>
    <p class="lede">{esc(story["summary"])}</p>
  </header>
  <div class="story-locs">{locs}</div>
  <p>{esc(story["body"])}</p>
  <p class="visit-note"><strong>If you go:</strong> {esc(story["visit_note"])}</p>
  {partner}
  <p class="story-web"><strong>Learn more:</strong> <a href="{esc(website["url"])}" rel="noopener">{esc(website["label"])}</a></p>
  <div class="story-sources"><h3>Sources</h3><ul>{sources}</ul></div>
</article>"""


def main() -> None:
    data = json.loads((ROOT / "data" / "falmouth-stories.json").read_text(encoding="utf-8"))
    cards = "\n".join(card(s) for s in data["stories"])
    pin_count = sum(len(s["locations"]) for s in data["stories"])
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Falmouth Stories &amp; History | Falmouth Wellness Discovery</title>
<meta name="description" content="Verified Falmouth history and local stories for the January 2027 wellness magazine, each tied to a pull-out map grid square and a nearby partner.">
<link rel="canonical" href="https://platinum00001.github.io/falmouth-wellness-discovery/stories.html">
<meta property="og:title" content="Falmouth Stories &amp; History">
<meta property="og:description" content="Verified local history on the Falmouth Wellness Discovery map, from Katharine Lee Bates to Woods Hole science and the Village Green.">
<meta property="og:url" content="https://platinum00001.github.io/falmouth-wellness-discovery/stories.html">
<meta property="og:image" content="https://platinum00001.github.io/falmouth-wellness-discovery/assets/img/cover-january-2027.jpg" data-abs-img="assets/img/cover-january-2027.jpg">
<meta name="theme-color" content="#2C7F7B">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONTS}
<link rel="stylesheet" href="css/styles.css">
<link rel="stylesheet" href="css/map.css">
<link rel="stylesheet" href="css/polish.css">
</head>
<body data-path="stories.html">
{header("", "stories.html")}
<main id="main" class="stories-page">
  <div class="wrap page-hero">
    <p class="eyebrow">January 2027 · Visitor guide</p>
    <h1>Falmouth Stories &amp; History</h1>
    <p class="lede">{esc(data["intro"])}</p>
    <div class="cta-row">
      <a class="btn btn-sun" href="map.html?layer=history">See them on the discovery map</a>
      <a class="btn btn-ghost" href="guide.html">Visitor guide</a>
      <a class="btn btn-ghost" href="magazine.html?page=12">Open the pull-out map</a>
    </div>
    <p>{len(data["stories"])} stories, {pin_count} map pins. Letters A–F run across the pull-out; numbers 1–4 run down. The front is the Downtown side, the back is the Woods Hole side.</p>
  </div>
  <div class="wrap stories-list">
{cards}
  </div>
</main>
{footer("")}
<script src="config.js"></script>
<script src="js/main.js"></script>
</body>
</html>
"""
    out = ROOT / "stories.html"
    out.write_text(page, encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
