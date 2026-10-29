#!/usr/bin/env python3
"""One header and one footer for every public page.

Usage (from the site root):  python3 scripts/site_chrome.py
build_directory.py and build_free_help.py import header()/footer() from here,
and running this file re-stamps the hand-written pages (index, magazine, map,
guide, directory, partner, signup, etc.) so nav and footer always match.
It also makes sure css/polish.css and the brand fonts are linked.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NAV = [
    ("index.html", "Home", ""),
    ("magazine.html", "Magazine", "magazine.html"),
    ("map.html", "Map", "map.html"),
    ("shops/", "Main Street", "shops/"),
    ("directory.html", "Directory", "directory.html"),
    ("guide.html", "Visitor Guide", "guide.html"),
    ("free-help.html", "Free Help", "free-help.html"),
    ("partner.html", "Partner", "partner.html"),
]

MARK = ('<svg class="mark" viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="12" fill="#1C5A5E"/>'
        '<circle cx="30" cy="16" r="7" fill="#F4A259"/><path d="M8 34c6-6 10-6 16 0s10 6 16 0" fill="none" stroke="#A8D8CE" '
        'stroke-width="3" stroke-linecap="round"/></svg>')

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400'
         '&family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&display=swap" rel="stylesheet">')


def header(root: str, current: str) -> str:
    links = []
    for href, label, path in NAV:
        cur = ' aria-current="page"' if path == current else ""
        links.append(f'<a href="{root}{href}"{cur}>{label}</a>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a class="brand" href="{root}index.html">
    {MARK}
    <span><span class="brand-kicker">Falmouth · Cape Cod</span><span class="brand-name">Wellness <em>Discovery</em></span></span>
  </a>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="sr-only">Menu</span><span class="burger" aria-hidden="true"></span></button>
  <nav id="site-nav" class="site-nav" aria-label="Primary">
    {" ".join(links)}
    <a class="btn btn-sun btn-small" href="{root}signup.html">Get the magazine</a>
  </nav>
</header>"""


def footer(root: str) -> str:
    return f"""<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="brand brand-light" href="{root}index.html">{MARK}<span><span class="brand-kicker">Falmouth · Cape Cod</span><span class="brand-name">Wellness <em>Discovery</em></span></span></a>
      <p>A free quarterly health and wellness magazine and walking map for Falmouth, Massachusetts. Published from Homeport, Gifford Street at Jones Road.</p>
    </div>
    <div>
      <h2>Read</h2>
      <p><a href="{root}magazine.html">Winter 2026 flipbook</a><br><a href="{root}map.html">Discovery map</a><br><a href="{root}guide.html">Visitor guide</a><br><a href="{root}map-print.html">17×11 pull-out</a><br><a href="{root}audio.html">Audio update</a></p>
    </div>
    <div>
      <h2>Find</h2>
      <p><a href="{root}shops/">Main Street &amp; Homeport shops</a><br><a href="{root}directory.html">Service directory</a><br><a href="{root}free-help.html">Free food &amp; help</a><br><a href="{root}credits.html">Image credits</a></p>
    </div>
    <div>
      <h2>Publisher</h2>
      <p>Cape Island<br>316 Gifford Street, Falmouth, MA 02540<br><a href="tel:+17742475263">(774) 247-5263</a><br><a href="mailto:CapeIslandCafe@gmail.com">CapeIslandCafe@gmail.com</a></p>
      <p><a class="btn btn-sun btn-small" href="{root}partner.html">Become a partner</a></p>
    </div>
  </div>
  <div class="wrap credit-line">
    <p>Nobska Light cover photo: Giacomo Barbaro, CC BY-SA 3.0, via Wikimedia Commons (<a href="https://commons.wikimedia.org/wiki/File:Nobska_Lighthouse.jpg">source</a>); modified with added text. Other photographs are generated editorial images of generic scenes, not real people or storefronts.</p>
    <p>© 2026 Falmouth Wellness Discovery · Winter 2026 · Issue 1 · <a href="{root}partner.html">Advertise</a> · <a href="{root}signup.html">Get the magazine</a></p>
  </div>
</footer>"""


HEADER_RE = re.compile(r'(?:<a class="skip"[^>]*>[^<]*</a>\s*)?<header class="site-header( no-print)?">.*?</header>', re.S)
FOOTER_RE = re.compile(r'<footer class="site-footer( no-print)?">.*?</footer>', re.S)
FONT_RE = re.compile(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">')


def stamp(text: str, root: str, current: str) -> str:
    if HEADER_RE.search(text):
        text = HEADER_RE.sub(lambda m: header(root, current).replace('<header class="site-header">', '<header class="site-header%s">' % (m.group(1) or ""), 1), text, count=1)
    if FOOTER_RE.search(text):
        text = FOOTER_RE.sub(lambda m: footer(root).replace('<footer class="site-footer">', '<footer class="site-footer%s">' % (m.group(1) or ""), 1), text, count=1)
    if FONT_RE.search(text):
        text = FONT_RE.sub(FONTS, text, count=1)
    polish = f'<link rel="stylesheet" href="{root}css/polish.css">'
    if "css/polish.css" not in text and "</head>" in text:
        text = text.replace("</head>", polish + "\n</head>", 1)
    return text


def main() -> None:
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/index.html"))
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        if rel.startswith(("pitch/", "assets/", "node_modules/")):
            continue
        text = page.read_text(encoding="utf-8")
        if not HEADER_RE.search(text) and not FOOTER_RE.search(text):
            continue
        depth = rel.count("/")
        root = "../" * depth
        current = rel if depth == 0 else rel.replace("index.html", "")
        new = stamp(text, root, current)
        if new != text:
            page.write_text(new, encoding="utf-8")
            print("stamped", rel)


if __name__ == "__main__":
    main()
