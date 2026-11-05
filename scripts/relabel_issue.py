#!/usr/bin/env python3
"""Relabel the issue site-wide (text only; images and PDFs are rebuilt by their own scripts).

  python3 scripts/relabel_issue.py --old "Winter 2026" --new "January 2027" [--dry-run]

Replaces, in every text file of the site (html, js, css, json, xml, txt, md, py templates):
  "Winter 2026" -> "January 2027", "WINTER 2026" -> "JANUARY 2027", "winter 2026" -> "january 2027"
  slug "winter-2026" -> "january-2027" (cover image and PDF paths)
Old asset files are not deleted: rebuild_issue.sh copies the new cover/PDFs onto the old names so
printed QR codes and old links keep working. Excluded: .git, build/, assets/ binaries, this script,
scripts/README.md and scripts/rebuild_issue.sh (they name the old slugs on purpose)."""
import argparse, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
EXT = {".html", ".js", ".css", ".json", ".xml", ".txt", ".md", ".py", ".svg", ".webmanifest"}
SKIP_DIRS = {".git", "build", "node_modules", "__pycache__"}
SKIP_FILES = {"scripts/relabel_issue.py", "scripts/README.md", "scripts/rebuild_issue.sh", "scripts/render_cover.py", "scripts/build_pullout_map.py"}


def variants(old, new):
    so, sn = old.lower().replace(" ", "-"), new.lower().replace(" ", "-")
    return [(old, new), (old.upper(), new.upper()), (old.lower(), new.lower()), (so, sn)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True); ap.add_argument("--new", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    pairs = variants(a.old, a.new)
    total = 0
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT).as_posix()
        if not p.is_file() or p.suffix.lower() not in EXT or rel in SKIP_FILES: continue
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts): continue
        if rel.startswith("assets/"): continue
        s = p.read_text(encoding="utf-8", errors="surrogateescape"); t = s
        for o, n in pairs:
            t = t.replace(o, n)
        if t != s:
            n = sum(s.count(o) for o, _ in pairs); total += n
            print(f"{n:4d}  {rel}")
            if not a.dry_run: p.write_text(t, encoding="utf-8", errors="surrogateescape")
    print(total, "replacements", "(dry run)" if a.dry_run else "")


if __name__ == "__main__":
    main()
