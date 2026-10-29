#!/usr/bin/env python3
"""One-time data update (2026-10-29): Main Street + Homeport focus.

Adds verified Main Street and Homeport (Gifford St at Jones Rd) businesses,
fills verified phones/websites on existing listings, geocodes LIFT, and tags
every listing with a `district` used for ordering and map emphasis.
Sources are recorded on each listing. Safe to re-run (idempotent by id).
"""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "directory.json"
d = json.loads(P.read_text(encoding="utf-8"))
cats = {c["slug"]: c for c in d["categories"]}
CHK = "checked Oct 29, 2026"

def item(id, name, sub, summary, address, phone, phoneDisplay, website, lat, lng, sources, **extra):
    x = {"id": id, "name": name, "featured": False, "placeholder": False, "subcategory": sub,
         "summary": summary, "address": address, "phone": phone, "phoneDisplay": phoneDisplay,
         "website": website, "booking": None, "lat": lat, "lng": lng, "schemaType": "LocalBusiness",
         "facts": [f for f in [address, phoneDisplay] if f], "sources": sources}
    x.update(extra)
    return x

# ---- new category: Main Street & Homeport shops ----
if "shops" not in cats:
    shops = {
        "slug": "shops", "short": "Main Street Shops", "nav": "Jewelry, boutiques, kids and home",
        "title": "Falmouth MA Main Street Shops | Jewelry, Boutiques, Kids & Home",
        "h1": "Falmouth Main Street and Homeport shops: jewelry, boutiques, kids and home",
        "description": "Independent shops on Falmouth's Main Street and at Homeport on Gifford Street: local jewelers, women's and men's boutiques, a children's shop, home goods and a family insurance agency.",
        "intro": ["Falmouth's Main Street runs from the Village Green past Town Hall Square and the library toward Davis Straits. Most of the shops here are owner-run, and many have been on the street for years.",
                  "Homeport is the cluster of offices and shops on Gifford Street at Jones Road, home to Cape Island Café, a dental group, a chiropractor, a nutrition shop and a family insurance agency."],
        "tips": ["Main Street parking is metered in season; the lots behind the library and off Town Hall Square are a short walk.",
                 "Hours change between summer and winter, so call ahead in the off-season.",
                 "Homeport has its own parking lot off Gifford Street."],
        "related": ["bookstore", "antiques", "florist"], "listings": []}
    d["categories"].append(shops); cats["shops"] = shops

def add(slug, x):
    L = cats[slug]["listings"]
    if any(i.get("id") == x["id"] for i in L): return
    L.append(x)

S_SCENIC = "Scenic Shopping Falmouth guide (scenicshopping.com), " + CHK
S_CHAMBER = "Falmouth Chamber of Commerce member directory (web.falmouthchamber.com), " + CHK
add("shops", item("falmouth-jewelry-shop", "Falmouth Jewelry Shop", "Jeweler",
    "Gold and sterling jewelry, watches and gifts, with owner and local-artisan pieces and custom work, on Main Street.",
    "225 Main Street, Falmouth, MA 02540", "+1-508-548-0487", "(508) 548-0487", "https://www.falmouthjewelryshop.com/",
    41.551594, -70.615704, [S_CHAMBER, "Falmouth Village Association board listing", S_SCENIC], district="main-street"))
add("shops", item("coast-goldworks", "Coast GoldWorks", "Jeweler",
    "Handcrafted fine jewelry with nautical and one-of-a-kind designs, on Main Street.",
    "261-C Main Street, Falmouth, MA 02540", "+1-774-392-6233", "(774) 392-6233", "https://www.coastgoldworks.com/",
    41.551983, -70.615015, ["coastgoldworks.com (store address and phone), " + CHK], district="main-street", approximate=True))
add("shops", item("story-falmouth", "story.", "Women's boutique",
    "Women's boutique with contemporary clothing, jewelry and curated gifts, on Main Street.",
    "352 Main Street, Falmouth, MA 02540", "+1-774-763-5451", "(774) 763-5451", "https://www.storyfalmouth.com/",
    41.552248, -70.612404, ["storyfalmouth.com, " + CHK, S_CHAMBER], district="main-street", approximate=True))
add("shops", item("caline-for-kids", "Caline for Kids", "Children's boutique",
    "Children's clothing and footwear boutique, infant to size 14, on Main Street.",
    "149 Main Street, Falmouth, MA 02540", "+1-508-548-2533", "(508) 548-2533", "https://calineforkids.com/",
    41.552739, -70.617659, ["calineforkids.com, " + CHK, S_CHAMBER], district="main-street"))
add("shops", item("nest-and-feathers", "Nest and Feathers", "Home goods",
    "Home goods shop with bed and kitchen linens, dishes, glassware, rugs, throws and seasonal decor, on Main Street.",
    "189 Main Street, Falmouth, MA 02540", "+1-774-612-3123", "(774) 612-3123", "https://www.nestandfeathers.com/",
    41.55227, -70.616885, ["nestandfeathers.com (address and phone), " + CHK, S_SCENIC], district="main-street"))
add("shops", item("maxwell-and-co", "Maxwell & Co.", "Men's and women's clothing",
    "Men's and women's clothing, footwear and accessories, casual to formal, on Main Street.",
    "200 Main Street, Falmouth, MA 02540", "+1-508-540-8752", "(508) 540-8752", "https://www.maxwellandco.com/",
    41.552605, -70.616402, ["maxwellandco.com (address and phone), " + CHK, S_SCENIC], district="main-street"))
add("shops", item("calfee-insurance", "Arthur D. Calfee Insurance Agency", "Insurance agency (Homeport)",
    "Family-run, second-generation independent insurance agency for home, auto, boat and business, at Homeport on Gifford Street. Weekdays 8:30 a.m. to 4:30 p.m.",
    "336 Gifford Street, Falmouth, MA 02540", "+1-508-540-2601", "(508) 540-2601", "https://www.calfeeinsurance.com/",
    41.562179, -70.610181, ["calfeeinsurance.com (Homeport Plaza office, 336 Gifford Street), " + CHK], district="homeport",
    hours="Mon–Fri 8:30 a.m.–4:30 p.m."))
add("spa-recovery", item("harmony-network-chiropractic", "Harmony Network Chiropractic", "Chiropractic (Homeport)",
    "Network chiropractic care with Dr. Susan Aberle, at Homeport on Gifford Street.",
    "346 Gifford Street, Unit 1, Falmouth, MA 02540", "+1-774-392-8454", "(774) 392-8454", "http://www.harmonynetworkchiro.com/",
    41.562797, -70.609968, ["harmonynetworkchiro.com/contact, " + CHK], district="homeport"))
add("spa-recovery", item("acupuncture-health-services-falmouth", "Acupuncture Health Services of Falmouth", "Acupuncture",
    "Acupuncture, cupping and community acupuncture, a short walk off Main Street near Palmer Avenue. Open Monday to Friday, 10 a.m. to 5 p.m.",
    "15 Simpson Lane, Suite 2B, Falmouth, MA 02540", "+1-508-687-0786", "(508) 687-0786", "https://falmouth.acupuncturehealthservices.com/",
    41.554071, -70.623626, ["falmouth.acupuncturehealthservices.com, " + CHK], district="main-street", hours="Mon–Fri 10 a.m.–5 p.m."))
add("dental", item("dental-group-of-falmouth", "Dental Group of Falmouth", "General dentistry (Homeport)",
    "General and family dentistry at Homeport on Gifford Street. Monday to Thursday, 8 a.m. to 5 p.m.",
    "344 Gifford Street, Unit A, Falmouth, MA 02540", "+1-508-524-3732", "(508) 524-3732", "https://www.dentalgroupfalmouth.com/",
    41.562814, -70.610169, ["dentalgroupfalmouth.com/contact-us, " + CHK], district="homeport", hours="Mon–Thu 8 a.m.–5 p.m."))

# ---- verified fills on existing listings ----
FILL = {
 "jacquelines-gifts": dict(phone="+1-508-548-4648", phoneDisplay="(508) 548-4648", src="Falmouth business listings (exa.ai place record, loc8nearme), " + CHK),
 "salty-florist": dict(phone="+1-774-255-1793", phoneDisplay="(774) 255-1793", website="https://www.thesaltyflorist.com/", src="thesaltyflorist.com, " + CHK),
 "windfall-market": dict(phone="+1-508-548-0099", phoneDisplay="(508) 548-0099", website="https://www.windfallmarket.com/", src="windfallmarket.com/contact, " + CHK),
 "rooted-hot-yoga": dict(phone="+1-508-314-6073", phoneDisplay="(508) 314-6073", website="https://www.rootedhotyogafalmouth.com/", address="80 Davis Straits, Unit 103, Falmouth, MA 02540", src="rootedhotyogafalmouth.com, " + CHK),
 "cape-symphony-conservatory": dict(phone="+1-508-540-0611", phoneDisplay="(508) 540-0611", website="https://www.capesymphony.org/", src="capesymphony.org/contact-us, " + CHK),
 "maison-villatte": dict(phone="+1-774-255-1855", phoneDisplay="(774) 255-1855", src=S_CHAMBER),
 "hospital-auxiliary-thrift": dict(phone="+1-508-457-7799", phoneDisplay="(508) 457-7799", website="https://www.capecodhealth.org/locations-and-directions/profile/falmouth-hospital-auxiliary-thrift-shop/", websiteLabel="Hours & info", hours="Tue–Sat 11 a.m.–3 p.m.", src="capecodhealth.org location profile, " + CHK),
 "golden-crown-cleaners": dict(phone="+1-774-612-3824", phoneDisplay="(774) 612-3824", website="https://www.goldencrowncleaners.com/", address="196 Teaticket Highway, East Falmouth, MA 02536", lat=41.566229, lng=-70.595622, src="goldencrowncleaners.com/contact-us (address 196 Teaticket Hwy), " + CHK),
 "spa-and-nails": dict(phone="+1-508-495-0861", phoneDisplay="(508) 495-0861", src="Falmouth business listings (bestprosintown, conprofi), " + CHK),
 "tommys-place": dict(phone="+1-617-249-4462", phoneDisplay="(617) 249-4462", website="https://tommysplace.org/", src="tommysplace.org, " + CHK),
 "palmer-house-inn": dict(phone="+1-508-548-1230", phoneDisplay="(508) 548-1230", website="https://www.palmerhouseinn.com/", src="palmerhouseinn.com; " + S_CHAMBER),
 "falmouth-art-center": dict(phone="+1-508-540-3304", phoneDisplay="(508) 540-3304", website="https://falmouthart.org/", src="falmouthart.org/contactdirections, " + CHK),
 "falmouth-elks": dict(phone="+1-508-548-2380", phoneDisplay="(508) 548-2380", website="https://www.elks.org/lodges/home.cfm?lodgenumber=2380", src="elks.org Lodge #2380 contact page, " + CHK),
 "beacon-gardens": dict(phone="+1-508-648-9256", phoneDisplay="(508) 648-9256", website="https://beacongardens.com/pages/welcome-to-beacon-gardens-at-brick-kiln", hours="Mon–Sat 7:30 a.m.–5 p.m.", src="beacongardens.com (Brick Kiln location), " + CHK),
 "falmouth-public-library": dict(phone="+1-508-457-2555", phoneDisplay="(508) 457-2555", src="falmouthpubliclibrary.org/about/locations-hours, " + CHK),
 "falmouth-town-hall": dict(phone="+1-508-548-7611", phoneDisplay="(508) 548-7611", src="falmouthma.gov staff directory, " + CHK),
 "falmouth-chamber": dict(phone="+1-508-548-8500", phoneDisplay="(508) 548-8500", address="20 Academy Lane, Falmouth, MA 02540", src="capecodchamber.org Falmouth Chamber contact page, " + CHK),
 "falmouth-pilates": dict(phone="+1-646-207-1719", phoneDisplay="(646) 207-1719", src="falmouthpilates.com, " + CHK),
 "uptownbody-cape-cod": dict(phone="+1-508-548-2857", phoneDisplay="(508) 548-2857", src="uptownbodycapecod.com/contact, " + CHK),
 "lift-aerial-yoga-loft": dict(lat=41.627222, lng=-70.541851, src="Geocoded Oct 29, 2026: Nominatim/OpenStreetMap and U.S. Census geocoder both match 95 Club Valley Dr, East Falmouth"),
}
# map ids by fuzzy name when ids differ
byid = {}
for c in d["categories"]:
    for x in c["listings"]:
        byid[x["id"]] = x
alias = {"jacquelines-gifts": "jacqueline", "salty-florist": "salty", "hospital-auxiliary-thrift": "thrift", "falmouth-elks": "elks",
         "falmouth-public-library": "public library", "falmouth-town-hall": "town hall", "falmouth-chamber": "chamber",
         "tommys-place": "tommy", "palmer-house-inn": "palmer house", "falmouth-art-center": "art center", "beacon-gardens": "beacon",
         "golden-crown-cleaners": "golden crown", "maison-villatte": "villatte", "windfall-market": "windfall", "spa-and-nails": "spa & nails",
         "cape-symphony-conservatory": "symphony", "rooted-hot-yoga": "rooted", "falmouth-pilates": "falmouth pilates", "uptownbody-cape-cod": "uptownbody",
         "lift-aerial-yoga-loft": "lift aerial"}
for key, f in FILL.items():
    target = byid.get(key) or next((x for x in byid.values() if alias[key] in x["name"].lower()), None)
    if not target:
        print("NOT FOUND", key); continue
    src = f.pop("src")
    for k, v in f.items():
        if k in ("lat", "lng") or not target.get(k) or k == "address":
            target[k] = v
    target.pop("geoNote", None) if "lat" in f else None
    target["facts"] = [x for x in [target.get("address"), target.get("phoneDisplay")] if x]
    if target.get("hours"): target["facts"].append(target["hours"])
    if src not in target.setdefault("sources", []): target["sources"].append(src)

# ---- district tags + ordering ----
def district(x):
    a = (x.get("address") or "")
    m = re.match(r"(\d+)\D", a)
    n = int(m.group(1)) if m else 0
    if re.search(r"Gifford St", a) and 314 <= n <= 358 and n % 2 == 0: return "homeport"
    if re.search(r"Jones R", a) and 200 <= n <= 210: return "homeport"
    if re.search(r"\b(N\.? |North )?Main St(reet)?\b", a) and "Falmouth Hwy" not in a and ("Falmouth, MA" in a or a.endswith("Falmouth")): return "main-street"
    if "Simpson Lane" in a or "Walker St" in a or "Town Hall Square" in a or "Academy Lane" in a: return "main-street"
    return None
for c in d["categories"]:
    for x in c["listings"]:
        if x.get("placeholder"): continue
        dist = x.get("district") or district(x)
        if dist: x["district"] = dist
        else: x.pop("district", None)
    rank = lambda x: (0 if x.get("featured") and not x.get("placeholder") else 1 if x.get("district") == "homeport" else 2 if x.get("district") == "main-street" else 3 if not x.get("placeholder") else 4)
    c["listings"].sort(key=rank)
P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
from collections import Counter
print(Counter(x.get("district") for c in d["categories"] for x in c["listings"]))
