#!/usr/bin/env python3
"""Build free-help.html (Free Food & Help) from data/free-help.json.

Refresh the data from the daily research file, then rebuild:
    python3 scripts/build_free_help.py --import /workspace/falmouth-free-resources/entries.json
    python3 scripts/build_free_help.py

Every entry keeps its own source link and last-checked date. Entries whose
only dates are in the past are left off the page.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_directory as bd  # noqa: E402

DATA = ROOT / "data" / "free-help.json"
OUT = ROOT / "free-help.html"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
FULL = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}

# (group id, heading, intro, match function on the entry's category)
GROUPS = [
    ("crisis", "Crisis lines and hotlines", "Call any time. In an emergency, dial 911.",
     lambda c: c.startswith(("Crisis", "Hotline"))),
    ("meals", "Free meals", "Sit-down meals, community dinners, senior meals and delivered meals.",
     lambda c: any(k in c for k in ("meal", "Meal", "dinner", "Holiday food", "Food delivery"))),
    ("pantries", "Food pantries", "Groceries to take home. Many ask you to register once.",
     lambda c: c.startswith("Food pantry")),
    ("free-food", "Free food, take what you need", "Micropantries, free food tables and food events.",
     lambda c: "take what you need" in c or c.startswith("Free food") or c.startswith("Food (")),
    ("snap", "SNAP, WIC and food benefits", "Help applying for food benefits.",
     lambda c: c.startswith(("SNAP", "WIC"))),
    ("health", "Health care and insurance help", "Free or sliding-fee care, screenings and insurance counseling. Sliding fee means low cost, not free.",
     lambda c: c.startswith(("Health", "Free health"))),
    ("mental", "Mental health and support", "Free counseling, support groups and referrals.",
     lambda c: c.startswith("Mental health")),
    ("recovery", "Recovery support", "Recovery centers, peer support, harm reduction and treatment.",
     lambda c: (c.startswith("Recovery") and not c.startswith("Recovery meeting")) or c.startswith(("Harm reduction", "Showers / health"))),
    ("housing", "Shelter, housing, showers and utilities", "Shelter, housing help, showers, and fuel or utility assistance.",
     lambda c: c.startswith(("Shelter", "Housing", "Fuel", "Financial", "Showers"))),
    ("clothing", "Free clothing", "", lambda c: c.startswith("Free clothing")),
    ("transportation", "Transportation", "Rides to appointments and services.", lambda c: c.startswith("Transportation")),
    ("veterans", "Veterans services", "Veterans pantries are listed under Food pantries.", lambda c: c.startswith("Veterans")),
    ("legal", "Free legal help", "", lambda c: c.startswith("Legal")),
    ("family", "Free family events", "One-time and seasonal free events.", lambda c: c.startswith("Free family")),
    ("meetings", "Recovery meetings (AA and NA)", "Free. \u201cOpen\u201d meetings are for anyone; \u201cclosed\u201d meetings are for people who want to stop drinking or using. Times are from the Cape Cod AA Intergroup and NERNA lists.",
     lambda c: c.startswith("Recovery meeting")),
]

esc = bd.esc


def t12(s: str) -> str:
    if not s:
        return ""
    h, m = map(int, s.split(":"))
    ap = "a.m." if h < 12 else "p.m."
    h = h % 12 or 12
    return f"{h}:{m:02d} {ap}" if m else f"{h} {ap}"


def when(e: dict) -> str:
    days = e.get("days") or []
    if e.get("dates"):
        dates = ", ".join(dt.date.fromisoformat(d).strftime("%a %b %-d") for d in e["dates"])
        day_part = dates
    elif days:
        day_part = ", ".join(FULL[d] for d in days) if len(days) < 3 else ", ".join(days)
        w = e.get("weeks")
        if w == "last":
            day_part += " (last week of the month)"
        elif w:
            day_part += " (" + " & ".join({1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}[x] for x in w) + " of the month)"
    else:
        day_part = "Any day / by appointment"
    if e.get("time_text"):
        time_part = e["time_text"]
    elif e.get("start") and e.get("end"):
        time_part = f"{t12(e['start'])}\u2013{t12(e['end'])}"
    elif e.get("start"):
        time_part = t12(e["start"])
    else:
        time_part = "call for times" if days else ""
    return day_part + (" \u00b7 " + time_part if time_part else "")


def phone_html(phone: str) -> str:
    if not phone:
        return ""
    m = re.search(r"\(?(\d{3})\)?[ .-]?(\d{3})-(\d{4})", phone)
    if m:
        tel = "+1" + "".join(m.groups())
        return f'<p>Phone: <a href="tel:{tel}">{esc(phone)}</a></p>'
    return f"<p>Phone: {esc(phone)}</p>"


def clean_notes(n: str) -> str:
    return re.sub(r"\bNEW (Oct|Nov) \d+ 2026[:.]?\s*", "", n or "").strip()


def card(e: dict) -> str:
    call = e.get("status") == "Call ahead"
    tag = '<span class="tag sample">Call ahead</span>' if call else '<span class="tag real">Confirmed with source</span>'
    notes = clean_notes(e.get("notes"))
    src = e.get("source") or ""
    src_html = f'<a href="{esc(src)}" rel="noopener noreferrer">Source</a>' if src.startswith("http") else esc(src)
    return f"""
      <article class="listing help-card">
        <header>{tag}<span class="tag">{esc(e.get('town'))}</span></header>
        <h3>{esc(e['name'])}</h3>
        <p class="help-when"><strong>{esc(when(e))}</strong></p>
        {f"<p>{esc(e['address'])}</p>" if e.get('address') else ''}
        {phone_html(e.get('phone'))}
        {f"<p>{esc(e['offered'])}</p>" if e.get('offered') else ''}
        {f"<p class='facts'>Who can go: {esc(e['eligibility'])}</p>" if e.get('eligibility') else ''}
        {f"<p class='facts'>Note: {esc(notes)}</p>" if notes else ''}
        <p class="help-source">{src_html} \u00b7 last checked {esc(e.get('last_checked') or 'n/a')}</p>
      </article>"""


def meeting_row(e: dict) -> str:
    src = e.get("source") or ""
    kind = e["category"].split("-")[-1].strip()
    offered = e.get("offered") or ""
    detail = offered.split(";", 1)[1].strip() if ";" in offered else offered
    return (f"<tr><td>{esc(t12(e.get('start')) or 'see list')}</td><td>{esc(kind)}</td>"
            f"<td>{esc(e['name'])}<br><small>{esc(detail)}</small></td><td>{esc(e.get('town'))}<br><small>{esc(e.get('address'))}</small></td>"
            f"<td><a href=\"{esc(src)}\" rel=\"noopener noreferrer\">Source</a></td></tr>")


def is_current(e: dict, today: dt.date) -> bool:
    dates = e.get("dates") or []
    if not dates:
        return True
    return any(dt.date.fromisoformat(d) >= today for d in dates)


def build() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    meta = payload["meta"]
    entries = payload["entries"]
    today = dt.date.fromisoformat(meta["updated"])
    entries = [e for e in entries if is_current(e, today)]
    grouped: dict[str, list] = {g[0]: [] for g in GROUPS}
    other = []
    for e in entries:
        for gid, _, _, match in GROUPS:
            if match(e["category"]):
                grouped[gid].append(e)
                break
        else:
            other.append(e)
    if other:
        raise SystemExit("Unsorted categories: " + ", ".join(sorted({e['category'] for e in other})))

    def sort_key(e):
        day = min((DAYS.index(d) for d in e.get("days") or []), default=9)
        return (0 if e.get("town", "").startswith(("Falmouth", "East Falmouth", "North Falmouth", "West Falmouth")) else 1, day, e.get("start") or "99", e["name"])

    toc = []
    sections = []
    for gid, title, intro, _ in GROUPS:
        items = grouped[gid]
        if not items:
            continue
        toc.append(f'<a class="btn btn-small btn-ghost" href="#{gid}">{esc(title)} ({len(items)})</a>')
        if gid == "meetings":
            body = []
            for d in DAYS:
                rows = sorted([e for e in items if d in (e.get("days") or [])], key=lambda e: (e.get("start") or "99", e["name"]))
                if not rows:
                    continue
                body.append(f"""<details class="help-day"><summary>{FULL[d]} \u00b7 {len(rows)} meetings</summary>
          <div class="table-wrap"><table class="help-table"><thead><tr><th>Time</th><th>Type</th><th>Meeting</th><th>Where</th><th>Source</th></tr></thead><tbody>{''.join(meeting_row(e) for e in rows)}</tbody></table></div></details>""")
            content = "".join(body)
        else:
            content = '<div class="cards cols-3">' + "".join(card(e) for e in sorted(items, key=sort_key)) + "</div>"
        sections.append(f"""
  <section class="section help-group" id="{gid}" style="padding-top:0">
    <div class="wrap">
      <h2>{esc(title)}</h2>
      {f'<p>{esc(intro)}</p>' if intro else ''}
      {content}
    </div>
  </section>""")

    base = bd.site_base()
    url = f"{base}/free-help.html"
    updated_txt = dt.date.fromisoformat(meta["updated"]).strftime("%B %-d, %Y")
    title = "Free Food & Help in Falmouth MA | Meals, Pantries, Recovery Meetings & Hotlines"
    desc = f"Free meals, food pantries, recovery meetings, hotlines and free services in and around Falmouth, MA. {len(entries)} entries, each with its source. Last updated {updated_txt}."
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "Free Food & Help in Falmouth, MA", "url": url,
                     "description": desc, "dateModified": meta["updated"],
                     "isPartOf": {"@type": "WebSite", "name": "Falmouth Wellness Discovery", "url": base + "/"}}, ensure_ascii=False)
    head = f"""<!DOCTYPE html>
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
<meta name="theme-color" content="#2C7F7B">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/styles.css">
<script type="application/ld+json">{ld}</script>
</head>
"""
    hotlines = "".join(f"<li><strong>{esc(n)}</strong> {esc(v)}</li>" for n, v in meta["hotlines"])
    page = head + f"""<body data-path="free-help.html">
{bd.chrome('', 'free-help.html')}
<main id="main">
  <div class="wrap page-hero">
    <p class="crumbs"><a href="index.html">Home</a> \u00b7 <a href="directory.html">Directory</a> \u00b7 Free Food &amp; Help</p>
    <p class="eyebrow">Falmouth MA \u00b7 Free help</p>
    <h1>Free food and help in and around Falmouth</h1>
    <div class="prose">
      <p class="lede">Free meals, food pantries, recovery meetings, hotlines and other free services in Falmouth, Woods Hole, East, North and West Falmouth, Teaticket, Waquoit and Hatchville, plus nearby Mashpee, Bourne and Sandwich. A few Hyannis and regional services are included where nothing like them runs on the Upper Cape.</p>
      <p><strong>Last updated {esc(updated_txt)}.</strong> {len(entries)} entries. Every time, address and phone number comes from the source linked on its card. Entries marked <em>Call ahead</em> are unconfirmed or have sources that disagree. Hours change for holidays and weather, so call before you go. Community Health Center care is low-cost on a sliding fee, not free.</p>
    </div>
    <aside class="callout teal help-hotlines">
      <h2>Need help now?</h2>
      <ul class="tips">{hotlines}</ul>
    </aside>
    <nav class="related help-toc" aria-label="Sections">{''.join(toc)}</nav>
  </div>
{''.join(sections)}
  <section class="section" style="padding-top:0">
    <div class="wrap prose">
      <h2>About this list</h2>
      <p>{esc(meta['about'])}</p>
      <p>Know a free program we missed, or see something out of date? Email <a href="mailto:CapeIslandCafe@gmail.com">CapeIslandCafe@gmail.com</a> with the program's own web page or flyer.</p>
    </div>
  </section>
</main>
{bd.footer('')}
<script src="config.js"></script>
<script src="js/main.js"></script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print("wrote free-help.html with", len(entries), "entries")


def import_entries(path: str) -> None:
    src = Path(path)
    entries = json.loads(src.read_text(encoding="utf-8"))
    updated = dt.date.fromtimestamp(src.stat().st_mtime).isoformat()
    payload = {
        "meta": {
            "updated": updated,
            "source": "Falmouth free food & services research file (daily refresh), " + src.name,
            "about": "This list is compiled from each program's own website, the Town of Falmouth, Barnstable County's resource guide, the Greater Boston Food Bank partner list, the Cape Cod AA Intergroup and NERNA meeting lists, and similar public sources, and it is rechecked every morning. It is a guide, not an official directory. Falmouth Wellness Discovery does not run these programs.",
            "hotlines": [
                ["911", "Emergency"],
                ["988", "Suicide and crisis line, call or text (answered locally by Samaritans)"],
                ["211", "Mass 211, help finding any service"],
                ["(833) 229-2683", "Cape & Islands mobile crisis team"],
                ["(800) 645-8333", "Project Bread FoodSource Hotline"],
                ["(800) 439-6507", "Independence House domestic violence hotline"],
                ["(800) 327-5050", "Massachusetts Substance Use Helpline"],
            ],
        },
        "entries": entries,
    }
    DATA.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("imported", len(entries), "entries, updated", updated)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--import":
        import_entries(sys.argv[2])
    build()
