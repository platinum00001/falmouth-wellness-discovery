#!/usr/bin/env python3
"""Apply SITE_BASE from config.js to every static file that bakes in the site URL.

SITE_BASE in config.js is the one setting. The browser code (QR codes, canonical
and og tags at runtime) already reads it from config.js. Static files cannot, so
after you change SITE_BASE run, from the site root:

    python3 scripts/set_site_base.py

It finds the previously applied base from the Sitemap line in robots.txt, swaps it
for the new one in HTML, sitemap.xml, robots.txt, JSON data and docs, points the
404 page at the new folder, and rebuilds the directory pages.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "vendor", "node_modules"}
EXTS = {".html", ".xml", ".txt", ".json", ".md", ".js"}


def read_base() -> str:
    text = (ROOT / "config.js").read_text(encoding="utf-8")
    match = re.search(r'SITE_BASE:\s*"([^"]+)"', text)
    if not match:
        raise SystemExit("SITE_BASE missing from config.js")
    return match.group(1).rstrip("/")


def applied_base() -> str | None:
    robots = ROOT / "robots.txt"
    if not robots.exists():
        return None
    match = re.search(r"^Sitemap:\s*(\S+)/sitemap\.xml\s*$", robots.read_text(encoding="utf-8"), re.M)
    return match.group(1).rstrip("/") if match else None


def files():
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in EXTS and not (set(path.relative_to(ROOT).parts) & SKIP_DIRS):
            if path.name in {"config.js", "set_site_base.py"}:
                continue
            yield path


def main() -> None:
    new = read_base()
    old = applied_base()
    changed = 0
    if old and old != new:
        old_bare = re.sub(r"^https?://", "", old)
        new_bare = re.sub(r"^https?://", "", new)
        for path in files():
            text = path.read_text(encoding="utf-8")
            updated = text.replace(old, new).replace(old_bare, new_bare)
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    # 404.html is served at any missing path, so it needs the absolute folder.
    folder = urlsplit(new).path.rstrip("/") + "/"
    page = ROOT / "404.html"
    if page.exists():
        text = page.read_text(encoding="utf-8")
        text2 = re.sub(r'(<a class="ghost" id="site-folder" href=")[^"]*(">Open )[^<]*(</a>)', r"\g<1>" + folder + r"\g<2>" + folder + r"\g<3>", text)
        text2 = re.sub(r'(var mark = ")[^"]*(";)', r"\g<1>" + folder + r"\g<2>", text2)
        if text2 != text:
            page.write_text(text2, encoding="utf-8")
            changed += 1
    print(f"SITE_BASE {new} (was {old}); {changed} files updated")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_directory.py")], check=True, stdout=subprocess.DEVNULL)
    print("directory pages rebuilt")


if __name__ == "__main__":
    main()
