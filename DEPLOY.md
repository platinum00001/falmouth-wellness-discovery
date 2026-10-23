# Deploy

This folder is the static site. Links between pages are relative, so the same files work as a GitHub Pages repo root or as a project folder (it is live at `https://platinum00001.github.io/falmouth-wellness-discovery/`).

## GitHub Pages

1. Put these files at the publishing root, or inside `magazine/` if the public URL ends in `/magazine/`.
2. Leave `.nojekyll` in place. It tells GitHub Pages not to run Jekyll, so folders and files are published as-is.
3. Leave `404.html` at the publishing root. GitHub Pages serves it for missing URLs. The page links back to `index.html`, and to `/magazine/` when the missing path contains `/magazine/`.
4. In the repository, set Pages to deploy from the branch that contains these files.

`SITE_BASE` in `config.js` is the one base-URL setting (no trailing slash). QR codes and runtime canonical/Open Graph tags read it directly. When a custom domain is pointed at the site, change `SITE_BASE` and run:

```bash
python3 scripts/set_site_base.py
```

That swaps the old base for the new one in canonical tags, Open Graph URLs, JSON-LD, `sitemap.xml`, `robots.txt`, the 404 page and the docs, then rebuilds the directory pages.

## Forms and billing

1. `sql/001_magazine_tables.sql` is applied to the james-sites project as the `magazine_tables` migration. It creates `magazine_reader_signups` and `magazine_partner_inquiries` with anonymous insert only.
2. Paste `SUPABASE_URL` and `SUPABASE_ANON_KEY` into `config.js`. Do not put a service-role key in this file.
3. Paste one Square checkout or invoice URL per package into `SQUARE_CHECKOUT` (`neighbor`, `featured`, `wellness`, `cover`). Until those are set, the partner buttons stay placeholders. The site never collects card numbers.

If the Supabase fields are left blank, the forms still show success and keep a copy in the browser. Use that only for a local preview.

`map-print.html` is the 17×11 pull-out: the wellness map on the first page and the Falmouth Visitor Guide on the second. In the print dialog, set the paper to 17 by 11 inches and the margins to none so the `@page` rule can use the full sheet. The dashed line on the map is the center fold. `guide.html` is the same visitor guide as a page you can open on a phone.

## Local check

```bash
python3 -m http.server 4177
```

Open `http://127.0.0.1:4177/`.
