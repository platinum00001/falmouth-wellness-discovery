#!/usr/bin/env python3
"""One-time data update (2026-11-04, owner decisions):

* Falmouth Transport: contact is the Cape Island Café line, (774) 247-5263, based at the
  café's office, 316 Gifford Street (fills the last audit blank).
* Falmouth Taxi: listed as "Falmouth Taxi · Falmouth Transport"; its own phone is removed
  and the listing points to the Falmouth Transport contact.
* Magazine Falmouth Transport page: the open taxi card becomes the Falmouth Taxi card.
Idempotent.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "directory.json"
d = json.loads(P.read_text(encoding="utf-8"))
L = {i["id"]: i for c in d["categories"] for i in c["listings"]}
cafe = next(i for i in L.values() if "316 Gifford" in (i.get("address") or ""))
PH, PHD = "+1-774-247-5263", "(774) 247-5263"
NOTE = "2026-11-04: owner decision"

t = L["falmouth-transport"]
t.update({"phone": PH, "phoneDisplay": PHD, "address": "316 Gifford Street, Falmouth, MA 02540",
          "lat": cafe["lat"], "lng": cafe["lng"],
          "summary": "A new local guide to rides and moving things around Falmouth, and a founding partner of this magazine. Based at the Cape Island Café office, 316 Gifford Street. Call (774) 247-5263, the same line as the café.",
          "facts": ["Founding partner", "Local rides and moving things around Falmouth",
                    "Based at the Cape Island Café office, 316 Gifford Street, Falmouth, MA 02540", PHD]})
t.setdefault("notes", [])
if not any(NOTE in n for n in t["notes"]):
    t["notes"].append(NOTE + ": phone is the Cape Island Café line; based at the café's office.")

x = L["falmouth-taxi"]
x.update({"name": "Falmouth Taxi · Falmouth Transport", "phone": PH, "phoneDisplay": PHD,
          "summary": "24-hour local taxi and livery: local rides, airport, ferry and long-distance trips, booked through Falmouth Transport. Office at 17 Walker Street, Falmouth. Call Falmouth Transport at (774) 247-5263.",
          "facts": ["17 Walker Street, Falmouth, MA 02540", "Book through Falmouth Transport: " + PHD,
                    "Office at 17 Walker Street (the same building as Jacqueline's Gifts & Antiques; checked Oct 28, 2026)"],
          "contactVia": "falmouth-transport"})
x.setdefault("notes", [])
if not any(NOTE in n for n in x["notes"]):
    x["notes"].append(NOTE + ": taxi's own phone (508) 548-3100 removed; listing points to the Falmouth Transport contact.")
P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

I = ROOT / "data" / "issue1.json"
s = json.loads(I.read_text(encoding="utf-8"))
for pg in s["pages"]:
    if pg.get("title") == "Falmouth Transport" and pg.get("kind") == "story":
        pg["paragraphs"] = [
            "Falmouth Transport is a founding partner. The guide is for rides and for moving things around Falmouth, with local options ahead of the big rideshare apps.",
            "Rides, deliveries and help moving things around town are the beat of this page each quarter. Falmouth Transport is based at the Cape Island Café office, 316 Gifford Street; call (774) 247-5263.",
            "Falmouth Taxi rides are booked through Falmouth Transport. More local transportation is on the Getting Around page of the website directory."]
        pg["cards"] = [{"title": "Falmouth Taxi · Falmouth Transport", "kicker": "Taxi · 24 hour",
                        "meta": PHD, "text": "Local rides, airport, ferry and long-distance trips. Book through Falmouth Transport.",
                        "cta": {"label": "Call (774) 247-5263", "href": "tel:+17742475263"}}]
I.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")

# ---- 2026-11-04 (owner): Cars & Insurance category: Route 28 Auto Center + Calfee moved here ----
d = json.loads(P.read_text(encoding="utf-8"))
cats = {c["slug"]: c for c in d["categories"]}
if "auto-insurance" not in cats:
    cal = None
    for c in d["categories"]:
        for i in list(c["listings"]):
            if i["id"] == "calfee-insurance":
                cal = i; c["listings"].remove(i)
    cal["subcategory"] = "Insurance agency (Homeport Plaza)"
    cal["summary"] = ("The insurance agency at Homeport Plaza on Gifford Street: a family-run, second-generation "
                      "independent agency for home, auto, boat, flood and business insurance, at 336 Gifford Street "
                      "since its Homeport office opened. Weekdays 8:30 a.m. to 4:30 p.m.")
    cal["sources"] = cal.get("sources", []) + ["agent.travelers.com and agents.libertymutual.com agency listings (336 Gifford St), checked Nov 4, 2026"]
    r28 = {"id": "route-28-auto-center", "name": "Route 28 Auto Center", "featured": False, "placeholder": False,
           "subcategory": "Used cars", "summary": "Used-car dealership on Route 28 in East Falmouth: inspected used cars, trucks and SUVs, trade-ins and financing. Call ahead about a specific car.",
           "address": "550 E. Falmouth Highway, East Falmouth, MA 02536", "phone": "+1-508-495-0300",
           "phoneDisplay": "(508) 495-0300", "website": "https://www.route28autos.com/", "booking": None,
           "lat": 41.577832, "lng": -70.553545, "schemaType": "AutoDealer",
           "facts": ["550 E. Falmouth Highway, East Falmouth, MA 02536", "(508) 495-0300"],
           "sources": ["route28autos.com (home, contact-us, about-us), checked Nov 4, 2026"]}
    new = {"slug": "auto-insurance", "short": "Cars & Insurance", "nav": "Insurance at Homeport, cars on Route 28",
           "title": "Falmouth MA Cars & Insurance | Homeport Insurance Agency, Route 28 Auto Center",
           "h1": "Falmouth MA cars and insurance",
           "description": "Arthur D. Calfee Insurance Agency at Homeport Plaza, 336 Gifford Street, and Route 28 Auto Center in East Falmouth, both on the Falmouth walking map.",
           "intro": ["Arthur D. Calfee Insurance Agency is the insurance office at Homeport Plaza, 336 Gifford Street, a few doors from Cape Island Café.",
                     "Route 28 Auto Center sells used cars, trucks and SUVs at 550 E. Falmouth Highway, East Falmouth."],
           "tips": ["Ask your agent to review home, flood and auto coverage together before storm season.",
                    "Call the dealer before you drive over to check a car is still on the lot."],
           "related": ["getting-around", "transportation", "shops"], "listings": [cal, r28]}
    idx = next(n for n, c in enumerate(d["categories"]) if c["slug"] == "transportation") + 1
    d["categories"].insert(idx, new)
    P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    s = json.loads(I.read_text(encoding="utf-8"))
    for pg in s["pages"]:
        for c in pg.get("cards", []) or []:
            if c.get("title") == "Arthur D. Calfee Insurance Agency":
                c["kicker"] = "Insurance · Homeport Plaza"
    I.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("auto-insurance added")

# ---- walking-map pin for the Homeport insurance agency ----
s = json.loads(I.read_text(encoding="utf-8"))
pl = s["walkingMap"]["places"]
if not any(p["id"] == "calfee-insurance" for p in pl):
    pl.append({"number": max(p["number"] for p in pl) + 1, "id": "calfee-insurance",
               "name": "Arthur D. Calfee Insurance Agency", "category": "Insurance · Homeport",
               "pillar": "soul", "address": "336 Gifford St", "lat": 41.562179, "lng": -70.610181,
               "qr": "auto-insurance/index.html#calfee-insurance", "size": "small"})
    I.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("pin added")
