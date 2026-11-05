#!/usr/bin/env python3
"""Issue update (2026-11-04): the illustrated Falmouth Health & Wellness map becomes the
pull-out insert at pages 12-15 (front = Downtown · Main Street on 12-13, back = Main Street &
Woods Hole on 14-15), replacing the Leaflet walking-map centerfold (which stays online at
map.html / guide.html / map-print.html). Calendar trimmed for a January 2027 release.
Idempotent."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "data/issue1.json"
d = json.loads(P.read_text())
pg = d["pages"]
pg[11:15] = [
    {"kind": "pullout", "face": "downtown", "half": "L", "title": "Pull-out map: Downtown · Main Street"},
    {"kind": "pullout", "face": "downtown", "half": "R", "title": "Pull-out map: Downtown · Main Street (right)"},
    {"kind": "pullout", "face": "woodshole", "half": "L", "title": "Pull-out map: Main Street & Woods Hole"},
    {"kind": "pullout", "face": "woodshole", "half": "R", "title": "Pull-out map: Main Street & Woods Hole (right)"},
]
d["pullout"] = {"pages": [12, 15], "pdf": "assets/fwd-pullout-map-january-2027.pdf", "data": "data/pullout-map.json",
                "online": {"map": "map.html", "guide": "guide.html", "print": "map-print.html"},
                "note": "Two-sided 17x11 sheet, folded once to 8.5x11. Front = pages 12-13, back = pages 14-15."}

# publisher's letter: describe the new insert
for p in pg:
    if p.get("kind") == "letter":
        p["paragraphs"] = [t if "11×17" not in t else
                           "The printed magazine is letter size, made from 11×17 sheets. In the middle is a pull-out map, one 17×11 sheet printed on both sides: "
                           "Downtown and Main Street on the front, Main Street and Woods Hole on the back, with partner ads around the border and a letter-and-number grid "
                           "so you can find a place from the visitor guide. Pull it out and keep it in the car. The interactive walking map and the full visitor guide are online."
                           for t in p["paragraphs"]]

# calendar for a January 2027 release: drop 2026 dates that will have passed, relabel annual ones to 2027
E = [
    {"title": "Friday Night Five-Miler", "when": "Every Friday · Town Hall Square", "status": "Check date", "detail": "Year-round group run, from the Health & Wellness map calendar."},
    {"title": "Local Business Celebration Night", "when": "By reservation · 5–7 p.m.", "status": "Ask for dates", "detail": "Cape Island Café hosts a local business, nonprofit, first-responder or team milestone night: samples from the kitchen ($20 suggested donation per person), your name on the screen, and 10% to the charity you choose. Reserve at capeislandcafe.com or 774-247-5263."},
    {"title": "Winter Farmers Market", "when": "January–March 2027 · Sundays · Mullen Hall lot", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Printmaking: Would You Do Wood? with Alice Galick", "when": "Feb 18, 25 and Mar 4, 6", "status": "Check date", "detail": "Falmouth Art Center woodcut workshop. The listing does not print a year; confirm the 2027 dates at falmouthart.org."},
    {"title": "Daffodil Daze at Spohr Gardens", "when": "Mid to late April 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Thursday Farmers Market", "when": "May–October 2027 · Thursdays 11–3 · Marine Park", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Arts Alive", "when": "Mid-June 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Falmouth Fireworks", "when": "July 4, 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Arts & Crafts Street Fair", "when": "Early July 2027 · Main Street", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Falmouth Sprint Triathlon", "when": "Mid-July 2027 · Surf Drive", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Barnstable County Fair", "when": "Late July 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Woods Hole Film Festival", "when": "Jul 31–Aug 7, 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "ASICS Falmouth Road Race", "when": "Aug 15, 2027 · 7 miles", "status": "Check date", "detail": "Date as printed on the Health & Wellness map. The 2026 race was Sunday, August 16."},
    {"title": "Cape Cod Marathon", "when": "Oct 9–10, 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Falmouth in the Fall", "when": "First Sunday in November 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Chase the Turkey 5K", "when": "Thanksgiving 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Holidays by the Sea", "when": "First weekend in December 2027", "status": "Check date", "detail": "From the Health & Wellness map calendar."},
    {"title": "Falmouth Christmas Parade", "when": "Early December 2027", "status": "Check date", "detail": "Falmouth Chamber of Commerce. The 2026 parade was Sunday, December 6, at noon; the 2027 date is not posted yet."},
]
d["events"] = E
cal = [p for p in pg if p.get("kind") == "calendar"]
half = (len(E) + 1) // 2
cal[0]["eventsRange"] = [0, half]; cal[1]["eventsRange"] = [half, len(E)]
cal[0]["dek"] = "Dates for the year ahead, from January 2027. Anything marked “Check date” comes from last year's pattern or a secondary source, so confirm it with the organizer."
cal[0]["paragraphs"] = ["The winter and spring dates come first, then the year-round Falmouth wellness calendar from the Health & Wellness map. Dates change, so check the organizer's own site before you go."]

g = d["walkingMap"]["guide"]
g["events"] = [e for e in g["events"] if e["id"] not in ("ramen-night", "art-center-reception")]
for e in g["events"]:
    if e["id"] == "christmas-parade":
        e["ref"] = "Dec"; e["detail"] = "Falmouth Chamber of Commerce. Early December 2027; the 2026 parade was Sun Dec 6 at noon. Check date."
    if e["id"] == "winter-runs-markets":
        e["detail"] = "Fridays, Town Hall Sq; Sundays Jan–Mar 2027. Check dates."
    if e["id"] == "fall-holidays":
        e["detail"] = "Oct 9–10, 2027; Nov; Thanksgiving; Dec 2027. Check dates."
P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print("pages", len(pg), "events", len(E), "calendar ranges", cal[0]["eventsRange"], cal[1]["eventsRange"])
