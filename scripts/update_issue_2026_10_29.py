#!/usr/bin/env python3
"""Issue 1 clean-up (2026-10-29): no sample/placeholder copy, real images in the
image slots, open spots become partner CTAs, and a Main Street + Homeport
opener. Keeps the centerfold at pages 12-15. Idempotent."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "data/issue1.json"
d = json.loads(P.read_text())
pages = d["pages"]
if any(p.get("id") == "main-street" for p in pages):
    print("already applied"); raise SystemExit
V = "assets/img/v3/"
man = {m["filename"].rsplit(".", 1)[0]: m for m in json.loads((ROOT / "assets/img/v3/manifest.json").read_text())["images"]}

def img(name):
    m = man.get(name, {})
    return {"src": V + name + ".jpg", "webp": V + name + ".webp", "small": V + name + "-640.jpg", "alt": m.get("alt", "")}

slot_map = {"tanorama-story": "self-care-glow", "cape-island-story": "cafe-lunch-bowl",
            "transport-story": "getting-around-dusk", "innovators": "innovators-workbench",
            "family-story": "wagon-groceries-porch", "charity": "charity-hands-boxes", "pets": "rescue-dog-beach"}
slots = []
for s in d["imageSlots"]:
    if s["id"] in slot_map:
        n = img(slot_map[s["id"]]); s.update(n); s["note"] = "Generated editorial image of a generic scene (no real people or storefronts)."
        slots.append(s)
d["imageSlots"] = slots  # map-illustration dropped: the centerfold is the map

def open_card(title, text, kicker="Featured spot available", href="partner.html", label="Become a partner"):
    return {"title": title, "kicker": kicker, "open": True, "text": text, "cta": {"label": label, "href": href}}

def open_ad(size, headline, text):
    return {"size": size, "open": True, "label": {"eighth": "1/8 page", "quarter": "1/4 page", "half": "1/2 page", "full": "Full page"}[size] + " · available",
            "headline": headline, "text": text, "cta": {"label": "See partner packages", "href": "partner.html"}}

def card(name, kicker, addr, phone, web=""):
    t = addr + " · " + phone + ((" · " + web) if web else "")
    return {"title": name, "kicker": kicker, "text": t}

def by_title(t):
    return next(p for p in pages if p.get("title") == t)

# 2 letter
p = by_title("A magazine for the time you spend waiting")
p["paragraphs"][1] = "The pages follow four pillars: Mind, Body, Soul, and Health & Food. Stories are written from interviews. Open spots are marked as available and link to the partner page."
p["ad"] = open_ad("eighth", "Your business, in front of Falmouth", "Eighth-page placements put a local business beside the stories readers keep.")
# innovators
inn = by_title("Innovators")
inn["dek"] = "Falmouth people trying something new in learning, care and local research."
inn["paragraphs"][0] = "This section is for people in Falmouth who are trying something new in learning, care, or local research."
inn["cards"] = [open_card("Nominate a Falmouth innovator", "Tell us about a neighbor building something new. Profiles run with the person's permission and in their own words.", kicker="Open profile", href="mailto:CapeIslandCafe@gmail.com?subject=FWD%20innovator%20nomination", label="Send a nomination")]
inn["ad"] = open_ad("quarter", "Quarter page available", "A quarter page sits beside the Mind pillar.")
# tanorama
t = by_title("Tanorama, nearly three decades on Main Street")
t["dek"] = "Nearly three decades of tanning at 365 Main Street."
t["paragraphs"][1] = "This spread is where the interview sits: how the shop fits the winter town, who comes in, and what Scott wants readers to know."
t2 = by_title("What the interview will hold")
t2["title"] = "Tanorama, continued"
t2.pop("pullquote", None)
t2["paragraphs"] = ["The salon is one of the longest-running shops on Main Street. Look for pin 12 on the walking map, a short walk east of the library.",
                    "The conversation with Scott runs here once he signs off on the words."]
t2["cards"] = [{"title": "Tanorama", "kicker": "Main Street · Tanning", "text": "365 Main Street, Falmouth · (508) 495-9905 · tanoramafalmouth.net"},
               {"title": "Owner", "kicker": "On Main Street", "text": "Scott, nearly three decades on Main Street."}]
# transport / food / body
tr = by_title("Falmouth Transport")
tr["cards"] = [c for c in tr.get("cards", []) if not c.get("placeholder")] + [open_card("Taxi partner spot", "A local taxi or ride service can take this card with its phone and service area.")]
b = by_title("Breakfast, lunch, and dinner")
f = by_title("Food truck, farm stand, pharmacy")
b["title"] = "Breakfast to dinner, farm stand to pharmacy"
b["dek"] = "One featured table for each part of the day, plus the places that keep a kitchen stocked."
b["cards"] = [c for c in b.get("cards", []) if not c.get("placeholder")] + [
    open_card("Breakfast spot available", "A Falmouth breakfast spot can take this card."),
    open_card("Dinner spot available", "An evening restaurant can take this card."),
    open_card("Food truck · farm stand · pharmacy", "Three more featured cards for the places that feed and care for Falmouth.")]
b["paragraphs"] = b.get("paragraphs", [])[:2]
b["ad"] = open_ad("half", "Half page available", "A half page sits under the food cards.")
pages.remove(f)
g = by_title("Gym, yoga, and a trainer")
g["cards"] = [c for c in g.get("cards", []) if not c.get("placeholder")] + [card("SWEAT Studio Cape Cod", "Main Street · Fitness", "661 Main St", "(774) 392-2686"), open_card("Gym, yoga or trainer spot", "One featured business in each of these three. Studios on Main Street and at Homeport are on the walking map.")]
# after the centerfold
h = by_title("Hair, golf, and social clubs")
h["cards"] = [c for c in h.get("cards", []) if not c.get("placeholder")] + [open_card("Salon, golf or club spot", "One featured card for each: a hair salon, a course, and a social club.")]
ho = by_title("Hotels")
ho["cards"] = [c for c in ho.get("cards", []) if not c.get("placeholder")] + [open_card("Featured stay available", "An inn or hotel near the village, the Sound, or Woods Hole can take this card.")]
ys = by_title("Library, senior center, youth sports")
ys["cards"] = [c for c in ys.get("cards", []) if not c.get("placeholder")] + [open_card("Youth sports league spot", "A league can list its season and sign-up link here for free.", kicker="Free community listing", href="mailto:CapeIslandCafe@gmail.com?subject=FWD%20youth%20sports%20listing", label="Send your league")]
pol = by_title("Police, fire, Town Hall, Chamber")
pol["dek"] = "Where to reach the town desks this winter."
pol["paragraphs"] = [
    "Each quarter these four desks can send a short 'what's happening' note. For emergencies, call 911.",
    "Falmouth Police Department is at 750 Main Street. Falmouth Fire-Rescue publishes its stations through the town. Town Hall is at 59 Town Hall Square, and the Falmouth Chamber of Commerce visitor center is at 20 Academy Lane.",
    "The town website, falmouthma.gov, has current hours and department numbers."]
pol["cards"] = [{"title": "Falmouth Town Hall", "kicker": "Town", "text": "59 Town Hall Square · (508) 548-7611 · falmouthma.gov"},
                {"title": "Falmouth Chamber of Commerce", "kicker": "Visitors", "text": "20 Academy Lane · (508) 548-8500"}]
fam = by_title("A sample good deed")
fam["title"] = "A good deed on a windy day"
fam["dek"] = "An illustration of the neighbor stories this page will tell."
fam.pop("pullquote", None)
fam["paragraphs"] = ["Picture it: a neighbor lends a wagon so someone can get groceries home when the wind is up off Vineyard Sound.",
                     "The real page is told only with permission, in the people's own details. Know a Falmouth family whose kindness deserves a page? Send it in."]
fam["cards"] = [open_card("Share a good deed", "Tell us about a neighbor's kindness. We ask everyone involved before anything runs.", kicker="Reader stories", href="mailto:CapeIslandCafe@gmail.com?subject=FWD%20good%20deed", label="Send a story")]
ch = by_title("Featured Charity (your nonprofit here)")
ch["title"] = "Charity spotlight"
ch["dek"] = "One local nonprofit each issue: what it does, and how to help."
ch["paragraphs"] = ["Every issue gives one local charity a page: what the group does, what it needs this quarter, and where to give time or money. Those facts come from the charity.",
                    "Tommy's Place, at 26 Elm Arch Way, is pin 19 on the walking map. A nonprofit that wants the spotlight can ask through the partner page."]
ch["cards"] = [open_card("Charity spotlight available", "Local nonprofits can request the page for a coming issue.", kicker="Free for nonprofits", label="Ask about the spotlight")]
pets = by_title("Adoptable pets")
pets["dek"] = "Adoptable animals come straight from the shelter, with the shelter's own contact."
pets["paragraphs"] = ["The pet page uses animals a shelter or rescue confirms. Friends of Falmouth Dogs, on the page before, is the place to start."]
pets["cards"] = [open_card("Shelter partner spot", "A shelter or rescue can list adoptable animals here each quarter for free.", kicker="Free for shelters", href="mailto:CapeIslandCafe@gmail.com?subject=FWD%20adoptable%20pets", label="List your animals")]
au = next(p for p in pages if p.get("kind") == "audio")
au["dek"] = "A short recording rides with each issue."
au["paragraphs"] = ["Point a phone at the code to open the audio page. Partners on the introductory packages are mentioned in the quarterly update."]
back = by_title("Full-page placement")
back["title"] = "The back cover"
back["paragraphs"] = ["The back cover is the most-seen page in every lobby. Cover Partner is the package built for it."]
back["ad"] = open_ad("full", "Back cover available", "Put your business on the page every reader sees last.")


ms = {"id": "main-street", "kind": "story", "kicker": "Start here · Main Street", "title": "A walk down Main Street",
      "dek": "Falmouth village, from the Village Green to the library and beyond: shops, studios and services worth the stroll.",
      "banner": {"src": V + "village-main-street-autumn.jpg", "small": V + "village-main-street-autumn-640.jpg", "alt": man.get("village-main-street-autumn", {}).get("alt", "")},
      "paragraphs": ["Main Street is the heart of the walking map. Park once, then follow the dotted line between the pins: independent shops, a bookstore, salons, bakeries and the library sit within a few blocks."],
      "cards": [card("Eight Cousins Books", "Bookstore", "199 Main St", "(508) 548-5548"),
                card("Falmouth Jewelry Shop", "Jewelry", "225 Main St", "(508) 548-0487"),
                card("Coast GoldWorks", "Jewelry studio", "261-C Main St", "(774) 392-6233"),
                card("Maison Villatte", "Bakery", "267 Main St", "(774) 255-1855"),
                card("story.", "Gifts", "352 Main St", "(774) 763-5451"),
                card("The Salty Florist & More", "Florist", "362 Main St", "(774) 255-1793"),
                card("Nest and Feathers", "Home & gifts", "189 Main St", "(774) 612-3123"),
                card("Falmouth Public Library", "Community", "300 Main St", "(508) 457-2555")]}
hp = {"id": "homeport", "kind": "story", "kicker": "Start here · Homeport", "title": "Homeport, Gifford Street at Jones Road",
      "dek": "A small plaza of neighbors where this magazine is made: lunch, nutrition, dental care and more.",
      "banner": {"src": V + "cafe-counter-morning.jpg", "small": V + "cafe-counter-morning-640.jpg", "alt": man.get("cafe-counter-morning", {}).get("alt", "")},
      "paragraphs": ["Homeport sits on Gifford Street at Jones Road, a short drive up from Main Street, with easy parking. The orange pin on the walking map marks it."],
      "cards": [card("Cape Island Café", "Lunch · alcohol-free", "316 Gifford St", "(774) 247-5263"),
                card("Arthur D. Calfee Insurance Agency", "Insurance", "336 Gifford St", "(508) 540-2601"),
                card("Dental Group of Falmouth", "Dental", "344 Gifford St, Unit A", "(508) 524-3732"),
                card("Harmony Network Chiropractic", "Chiropractic", "346 Gifford St, Unit 1", "(774) 392-8454"),
                card("Vital Nutrition", "Nutrition", "358 Gifford St", "(508) 548-8862"),
                card("Falmouth Dental Associates", "Dental", "210 Jones Rd", "(508) 540-0303")]}
shops = {"id": "main-street-shops", "kind": "story", "kicker": "Main Street · Shop local", "title": "Shops on Main Street",
         "dek": "Gifts, jewelry and kids' clothes, all a short walk apart.",
         "banner": {"src": V + "boutique-jewelry.jpg", "small": V + "boutique-jewelry-640.jpg", "alt": man.get("boutique-jewelry", {}).get("alt", "")},
         "paragraphs": ["Every shop below is independent and on or just off Main Street. The full list, with hours and websites, is on the Main Street page of the website."],
         "cards": [card("Caline for Kids", "Kids' clothing", "149 Main St", "(508) 548-2533"),
                   card("Maxwell & Co.", "Clothing", "200 Main St", "(508) 540-8752"),
                   card("Jacqueline's Gifts & Antiques", "Antiques", "17 Walker St", "(508) 548-4648"),
                   card("Falmouth Art Center", "Art", "137 Gifford St", "(508) 540-3304")]}
# Main Street + Homeport right after the contents; Innovators moves after the guide.
pages.remove(inn)
toc_i = next(i for i, p in enumerate(pages) if p.get("kind") == "toc")
pages[toc_i + 1:toc_i + 1] = [ms, hp]
guide_end = max(i for i, p in enumerate(pages) if p.get("kind") == "centerfold")
pages[guide_end + 1:guide_end + 1] = [inn, shops]
cf = next(i for i, p in enumerate(pages) if p.get("kind") == "centerfold")
assert cf == 11, cf
for pl in d["walkingMap"]["places"]:
    if pl["id"] == "golden-crown-cleaners": pl["address"] = "196 Teaticket Hwy"
P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print("pages", len(pages))
