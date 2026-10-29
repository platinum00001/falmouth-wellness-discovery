#!/usr/bin/env python3
"""Rebuild category landing pages from data/directory.json.

Usage (from the site root):
    python3 scripts/build_directory.py

SITE_BASE is read from config.js. Change it there, then run this script
so canonical tags and JSON-LD match.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "directory.json"
CONFIG = ROOT / "config.js"
ART_MANIFEST = ROOT / "assets" / "img" / "v2" / "manifest.json"
ART3_MANIFEST = ROOT / "assets" / "img" / "v3" / "manifest.json"

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_chrome import header as _hdr, footer as footer, stamp as _stamp  # noqa: E402


def chrome(root: str, current: str) -> str:
    return _hdr(root, current)

# Header art for category pages (files live in assets/img/v2/, alt text comes from the manifest).
CATEGORY_ART = {
    "transportation": "v3/getting-around-dusk.jpg",
    "home-remodeling": "v2/category-home-remodeling.jpg",
    "doctors": "v2/category-doctors-health.jpg",
    "hotels": "v2/category-hotels.jpg",
    "food": "v3/cafe-lunch-bowl.jpg",
    "community": "v3/charity-hands-boxes.jpg",
    "bookstore": "v3/bookstore-interior.jpg",
    "fitness": "v3/beach-yoga-sunrise.jpg",
    "beauty": "v3/self-care-glow.jpg",
    "golf": "v3/bike-shoreline-path.jpg",
    "bike-shop": "v3/bike-shoreline-path.jpg",
    "art-gallery": "v2/pillar-soul.jpg",
    "antiques": "v3/antique-details.jpg",
    "florist": "v3/farm-stand-produce.jpg",
    "thrift": "v3/antique-details.jpg",
    "music-lessons": "v3/village-main-street-autumn.jpg",
    "bakery": "v3/cafe-counter-morning.jpg",
    "local-market": "v3/farm-stand-produce.jpg",
    "garden-center": "v3/farm-stand-produce.jpg",
    "dry-cleaner": "v3/village-main-street-autumn.jpg",
    "nutrition": "v3/nutrition-bowls.jpg",
    "spa-recovery": "v3/spa-recovery.jpg",
    "dental": "v3/dental-room.jpg",
    "getting-around": "v3/bike-shoreline-path.jpg",
    "shops": "v3/boutique-jewelry.jpg",
}


def art_alt() -> dict:
    out = {}
    for folder, man in (("v2", ART_MANIFEST), ("v3", ART3_MANIFEST)):
        if man.exists():
            data = json.loads(man.read_text(encoding="utf-8"))
            out.update({folder + "/" + item["filename"]: item["alt"] for item in data.get("images", [])})
    return out


def site_base() -> str:
    text = CONFIG.read_text(encoding="utf-8")
    match = re.search(r'SITE_BASE:\s*"([^"]+)"', text)
    if not match:
        raise SystemExit("SITE_BASE missing from config.js")
    return match.group(1).rstrip("/")


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def with_utm(url: str, campaign: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["utm_source"] = "falmouthwellnessdiscovery"
    query["utm_medium"] = "referral"
    query["utm_campaign"] = campaign
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def directions(address: str, campaign: str) -> str:
    from urllib.parse import quote

    return with_utm(
        "https://www.google.com/maps/search/?api=1&query=" + quote(address),
        campaign,
    )


def buttons(item: dict, campaign: str) -> str:
    bits = []
    phone = item.get("phone")
    if phone:
        bits.append(f'<a class="btn btn-small" href="tel:{esc(phone)}">Call</a>')
    website = item.get("website")
    if website:
        label = item.get("websiteLabel") or "Website"
        bits.append(
            f'<a class="btn btn-small" href="{esc(with_utm(website, campaign))}" rel="noopener noreferrer">{esc(label)}</a>'
        )
    if item.get("address"):
        bits.append(
            f'<a class="btn btn-small btn-ghost" href="{esc(directions(item["address"], campaign))}" rel="noopener noreferrer">Directions</a>'
        )
    if item.get("booking"):
        bits.append(
            f'<a class="btn btn-small btn-coral" href="{esc(with_utm(item["booking"], campaign))}" rel="noopener noreferrer">Book a ride</a>'
        )
    if not bits:
        return ""
    return f'<div class="actions">{"".join(bits)}</div>'


DISTRICT_LABEL = {"main-street": "Main Street", "homeport": "Homeport · Gifford St"}


def partner_card(title: str, root: str = "../", note: str = "") -> str:
    return f"""
    <article class="listing listing-open">
      <header><span class="tag tag-open">Featured spot available</span></header>
      <h3>{esc(title)}</h3>
      <p>{esc(note or "One business per category gets the featured card here, on the walking map and in the magazine. Introductory pricing for founding partners.")}</p>
      <div class="actions"><a class="btn btn-small btn-sun" href="{root}partner.html#inquire">Become a partner</a><a class="btn btn-small btn-ghost" href="{root}partner.html">See packages</a></div>
    </article>
    """


def listing_card(item: dict, campaign: str) -> str:
    if item.get("placeholder"):
        name = re.sub(r"\s*\((your [^)]*)\)", "", item.get("name") or "Featured spot").strip()
        name = name.replace("Featured ", "Featured ") if name else "Featured spot"
        return partner_card(name + " — spot available")
    tags = ""
    if item.get("featured"):
        tags += '<span class="tag tag-featured">Featured partner</span>'
    if item.get("district") in DISTRICT_LABEL:
        tags += f'<span class="tag tag-district">{DISTRICT_LABEL[item["district"]]}</span>'
    if item.get("subcategory"):
        tags += f'<span class="tag">{esc(item["subcategory"])}</span>'
    email = f"<p class='meta'>Email: <a href='mailto:{esc(item['email'])}'>{esc(item['email'])}</a></p>" if item.get("email") else ""
    phone_line = f"<p class='meta meta-phone'><a href='tel:{esc(item['phone'])}'>{esc(item.get('phoneDisplay') or item.get('phone'))}</a></p>" if item.get("phone") else ""
    address = f"<p class='meta meta-addr'>{esc(item['address'])}</p>" if item.get("address") else ""
    hours = esc(item.get("hours")) if item.get("hours") else ("Call ahead for current hours" if item.get("phone") else "See the website for current hours")
    hours_line = f"<p class='meta meta-hours'>{hours}</p>"
    if not item.get("phone") and not item.get("website") and not item.get("hours"):
        # No public contact yet (founding partner): route questions to the publisher instead of a blank card.
        hours_line = "<p class='meta meta-phone'>Ask the publisher: <a href='tel:+17742475263'>(774) 247-5263</a> · <a href='mailto:CapeIslandCafe@gmail.com'>CapeIslandCafe@gmail.com</a></p>"
    cls = "listing" + (" is-featured" if item.get("featured") else "") + (" is-local" if item.get("district") else "")
    return f"""
    <article class="{cls}" id="{esc(item['id'])}">
      <header>{tags}</header>
      <h3>{esc(item['name'])}</h3>
      <p>{esc(item.get('summary') or '')}</p>
      {address}{phone_line}{hours_line}{email}
      {buttons(item, campaign)}
    </article>
    """


def schema_item(item: dict, page_url: str) -> dict | None:
    if item.get("placeholder"):
        return None
    node = {
        "@type": item.get("schemaType") or "LocalBusiness",
        "name": item["name"],
        "description": item.get("summary"),
        "url": page_url + "#" + item["id"],
    }
    if item.get("phone"):
        node["telephone"] = item["phone"]
    if item.get("address"):
        node["address"] = {
            "@type": "PostalAddress",
            "streetAddress": item["address"].split(",")[0],
            "addressLocality": "Falmouth",
            "addressRegion": "MA",
            "addressCountry": "US",
        }
    if item.get("lat") is not None:
        node["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": item["lat"],
            "longitude": item["lng"],
        }
    return node


def json_ld(cat: dict, base: str, by_slug: dict) -> str:
    page_url = f"{base}/{cat['slug']}/"
    graph = [
        {
            "@type": "WebPage",
            "@id": page_url,
            "name": cat["h1"],
            "description": cat["description"],
            "url": page_url,
            "isPartOf": {"@type": "WebSite", "name": "Falmouth Wellness Discovery", "url": base + "/"},
            "about": {"@type": "Place", "name": "Falmouth, Massachusetts"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "Directory", "item": base + "/directory.html"},
                {"@type": "ListItem", "position": 3, "name": cat["short"], "item": page_url},
            ],
        },
    ]
    elements = []
    for index, item in enumerate(cat["listings"], start=1):
        node = schema_item(item, page_url)
        if not node:
            continue
        elements.append({"@type": "ListItem", "position": index, "item": node})
    if elements:
        graph.append({
            "@type": "ItemList",
            "name": cat["h1"],
            "itemListElement": elements,
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def _old_chrome(root: str, current: str) -> str:
    def link(href: str, label: str, path: str) -> str:
        current_attr = ' aria-current="page"' if path == current else ""
        return f'<a href="{root}{href}"{current_attr}>{label}</a>'

    return f"""
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a class="brand" href="{root}index.html">
    <svg class="mark" viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="12" fill="#1C5A5E"/><circle cx="30" cy="16" r="7" fill="#F4A259"/><path d="M8 34c6-6 10-6 16 0s10 6 16 0" fill="none" stroke="#A8D8CE" stroke-width="3" stroke-linecap="round"/></svg>
    <span><span class="brand-kicker">Falmouth, Massachusetts</span><span class="brand-name">Wellness <em>Discovery</em></span></span>
  </a>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="sr-only">Menu</span><span class="burger" aria-hidden="true"></span></button>
  <nav id="site-nav" class="site-nav" aria-label="Primary">
    {link("index.html", "Home", "")}
    {link("magazine.html", "Magazine", "magazine.html")}
    {link("map.html", "Map", "map.html")}
    {link("guide.html", "Guide", "guide.html")}
    {link("directory.html", "Directory", "directory.html")}
    {link("free-help.html", "Free Food &amp; Help", "free-help.html")}
    {link("partner.html", "Become a Partner", "partner.html")}
    <a class="btn btn-small" href="{root}signup.html">Get the magazine</a>
  </nav>
</header>
"""


def _old_footer(root: str) -> str:
    return f"""
<footer class="site-footer">
  <div class="wrap foot-grid">
    <div>
      <h2>Cape Island</h2>
      <p>316 Gifford Street, Falmouth, MA<br><a href="tel:+17742475263">(774) 247-5263</a><br><a href="mailto:CapeIslandCafe@gmail.com">CapeIslandCafe@gmail.com</a></p>
    </div>
    <div>
      <h2>Explore</h2>
      <p><a href="{root}magazine.html">Winter 2027 sample issue</a><br><a href="{root}map.html">Discovery map</a><br><a href="{root}guide.html">Visitor guide</a><br><a href="{root}directory.html">Service directory</a><br><a href="{root}free-help.html">Free food &amp; help</a><br><a href="{root}credits.html">Image credits</a></p>
    </div>
    <div>
      <h2>Partners</h2>
      <p><a href="{root}partner.html">Become a partner</a><br><a href="{root}poster.html">Counter QR poster</a><br><a href="{root}pitch/">Pitch deck</a></p>
    </div>
  </div>
  <div class="wrap credit-line">
    <p>Nobska Light cover photo: Giacomo Barbaro, CC BY-SA 3.0, via Wikimedia Commons (<a href="https://commons.wikimedia.org/wiki/File:Nobska_Lighthouse.jpg">https://commons.wikimedia.org/wiki/File:Nobska_Lighthouse.jpg</a>); modified with added text.</p>
    <p>Issue 1 and unconfirmed directory cards are samples. Placeholder businesses are not real listings.</p>
  </div>
</footer>
"""


def head(cat: dict, base: str, root: str, ld: str) -> str:
    url = f"{base}/{cat['slug']}/"
    title = cat["title"]
    desc = cat["description"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Falmouth Wellness Discovery">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(base)}/assets/img/cover-winter-2027.jpg" data-abs-img="assets/img/cover-winter-2027.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2C7F7B">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/styles.css">
<script type="application/ld+json">{ld}</script>
</head>
"""


def hero_html(cat: dict, intro: str) -> str:
    crumbs = f'<p class="crumbs"><a href="../index.html">Home</a> · <a href="../directory.html">Directory</a> · {esc(cat['short'])}</p>'
    eyebrow = f'<p class="eyebrow">Falmouth MA · {esc(cat['short'])}</p>'
    h1 = f"<h1>{esc(cat['h1'])}</h1>"
    art = CATEGORY_ART.get(cat["slug"])
    if not art:
        return f"""  <div class="wrap page-hero">
    {crumbs}
    {eyebrow}
    {h1}
    <div class="prose">{intro}</div>
  </div>"""
    alt = art_alt().get(art, "")
    stem = art[:-4]
    if art.startswith("v3/"):
        img = (f'<picture><source type="image/webp" srcset="../assets/img/{stem}-640.webp 640w, ../assets/img/{stem}.webp 1280w" sizes="100vw">'
               f'<img src="../assets/img/{art}" srcset="../assets/img/{stem}-640.jpg 640w, ../assets/img/{art} 1280w" sizes="100vw" width="1280" height="720" alt="{esc(alt)}" fetchpriority="high" decoding="async"></picture>')
    else:
        img = f'<img src="../assets/img/{art}" srcset="../assets/img/{stem}-800.jpg 800w, ../assets/img/{art} 1600w" sizes="100vw" width="1600" height="900" alt="{esc(alt)}" fetchpriority="high" decoding="async">'
    return f"""  <section class="art-banner">
    {img}
    <div class="wrap art-banner-copy">
      {crumbs}
      {eyebrow}
      {h1}
    </div>
  </section>
  <div class="wrap page-hero page-hero-after-art">
    <div class="prose">{intro}</div>
  </div>"""


def render_category(cat: dict, data: dict, base: str) -> str:
    root = "../"
    by_slug = {c["slug"]: c for c in data["categories"]}
    tips = "".join(f"<li>{esc(tip)}</li>" for tip in cat["tips"])
    intro = "".join(f"<p>{esc(p)}</p>" for p in cat["intro"])
    real = [i for i in cat["listings"] if not i.get("placeholder")]
    open_slots = [i for i in cat["listings"] if i.get("placeholder")]
    has_featured = any(i.get("featured") for i in real)
    cards = ""
    if not has_featured:
        cards += partner_card(f"Featured {cat['short']} spot", "../",
                              f"This is the top spot on the {cat['short']} page, the walking map and the magazine. It is open for one Falmouth business.")
        open_slots = [i for i in open_slots if not re.match(r"Featured", i.get("name") or "")] if len(open_slots) <= 1 else open_slots
    cards += "".join(listing_card(item, cat["slug"]) for item in real)
    cards += "".join(listing_card(item, cat["slug"]) for item in open_slots)
    related = "".join(
        f'<a class="btn btn-small btn-ghost" href="../{esc(slug)}/">{esc(by_slug[slug]["short"])}</a>'
        for slug in cat["related"]
        if slug in by_slug
    )
    ld = json_ld(cat, base, by_slug)
    return head(cat, base, root, ld) + f"""
<body data-path="{esc(cat['slug'])}/">
{chrome(root, cat['slug'] + "/")}
<main id="main">
{hero_html(cat, intro)}
  <section class="section">
    <div class="wrap">
      <h2>Before you call</h2>
      <ul class="tips">{tips}</ul>
    </div>
  </section>
  <section class="section" style="padding-top:0">
    <div class="wrap">
      <h2>Listings</h2>
      <div class="cards">{cards}</div>
      <aside class="feature-cta">
        <div>
          <h2>Get featured here</h2>
          <p>The Featured package is the core listing, one business per category. Introductory price, per month, billed monthly.</p>
        </div>
        <a class="btn" href="../partner.html#inquire">Become a Partner</a>
      </aside>
    </div>
  </section>
  <section class="section" style="padding-top:0">
    <div class="wrap">
      <h2>Related in Falmouth</h2>
      <div class="related">{related}</div>
      <p><a href="../map.html?cat={esc(cat['slug'])}">See confirmed pins on the discovery map</a></p>
    </div>
  </section>
</main>
{footer(root)}
<script src="{root}config.js"></script>
<script src="{root}js/main.js"></script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    base = site_base()
    for cat in data["categories"]:
        folder = ROOT / cat["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        page = _stamp(render_category(cat, data, base), "../", cat["slug"] + "/")
        (folder / "index.html").write_text(page, encoding="utf-8")
        print("wrote", cat["slug"] + "/index.html")


if __name__ == "__main__":
    main()
