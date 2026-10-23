# Falmouth Wellness Discovery

A static site for the quarterly Falmouth health and wellness magazine and its fold-out discovery map. It is plain HTML, CSS, and JavaScript so it can be copied to GitHub Pages at `platinum00001.github.io/falmouth-wellness-discovery/`. Links are relative.

Deployment steps are in `DEPLOY.md` (GitHub Pages root or a `/magazine/` subfolder, Supabase, and Square).

## Run it locally

From this folder:

```bash
python3 -m http.server 4177
```

Open `http://127.0.0.1:4177/`.

## Pages

- `index.html` — home
- `magazine.html` — Winter 2027 sample issue, page-turn reader
- `map.html` — Leaflet discovery map, with the A–H by 1–6 grid
- `guide.html` — Falmouth Visitor Guide, the back of the pull-out
- `map-print.html` — 17×11 print-ready pull-out, front and back
- `directory.html` and the category folders — local SEO directory
- `partner.html` — packages, gift-card calculator, pitch deck, inquiry
- `signup.html` — reader sign-up
- `perk.html` — sample reader perk card, after sign-up
- `poster.html` — printable counter QR (`?loc=slug`)
- `audio.html` — quarterly audio placeholder
- `credits.html` — photo credit
- `pitch/` — advertiser pitch deck

## Data

- `data/issue1.json` — magazine pages, crossword, events, and empty image slots
- `data/directory.json` — category pages

After editing the directory file:

```bash
python3 scripts/build_directory.py
```

`SITE_BASE` in `config.js` is the canonical root with no trailing slash. Change it, then run `python3 scripts/set_site_base.py` so canonical tags, the sitemap and robots.txt match.

## Forms and Supabase

`config.js` holds empty `SUPABASE_URL` and `SUPABASE_ANON_KEY`. Fill those in locally. Do not commit a service-role key. If the keys are empty, the forms still show success and store the submission in this browser.

Run `sql/001_magazine_tables.sql` in the Supabase SQL editor for project **james-sites**. It creates `magazine_reader_signups` and `magazine_partner_inquiries` with row-level security: anonymous insert only, no public select.

Square checkout links also live in `config.js` under `SQUARE_CHECKOUT`, one URL per package. Until they are filled, the button labeled “Start subscription (Square checkout)” stays a placeholder. The site does not collect card numbers.

## Packages

Introductory, per month, billed monthly, subject to change:

| Package | Monthly | Founding (25% off, nearest dollar) |
| --- | --- | --- |
| Neighbor | $250 | $188 |
| Featured (core, one per category) | $500 | $375 |
| Wellness Partner | $750 | $563 |
| Cover Partner | $950 | $713 |

Gift cards may cover up to half the bill. The first 25% of the bill is credited at face value. The slice between 25% and 50% is credited at 75% of face value.

## Cover credit

Nobska Light cover photo: Giacomo Barbaro, CC BY-SA 3.0, via Wikimedia Commons (https://commons.wikimedia.org/wiki/File:Nobska_Lighthouse.jpg); modified with added text.
