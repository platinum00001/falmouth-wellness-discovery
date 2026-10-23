# Deploy

This folder is the static site. Links between pages are relative, so the same files work as a GitHub Pages repo root or as a `/magazine/` subfolder (for example `https://healthandwellnessmaps.com/magazine/`).

## GitHub Pages

1. Put these files at the publishing root, or inside `magazine/` if the public URL ends in `/magazine/`.
2. Leave `.nojekyll` in place. It tells GitHub Pages not to run Jekyll, so folders and files are published as-is.
3. Leave `404.html` at the publishing root. GitHub Pages serves it for missing URLs. The page links back to `index.html`, and to `/magazine/` when the missing path contains `/magazine/`.
4. In the repository, set Pages to deploy from the branch that contains these files.

If the live URL is not `https://healthandwellnessmaps.com/magazine`, change `SITE_BASE` in `config.js` (no trailing slash) and regenerate the directory pages:

```bash
python3 scripts/build_directory.py
```

That rewrites canonical tags, Open Graph URLs, and `sitemap.xml`.

## Forms and billing

1. In the Supabase SQL editor, run `sql/001_magazine_tables.sql`. It creates `magazine_reader_signups` and `magazine_partner_inquiries` with anonymous insert only.
2. Paste `SUPABASE_URL` and `SUPABASE_ANON_KEY` into `config.js`. Do not put a service-role key in this file.
3. Paste one Square checkout or invoice URL per package into `SQUARE_CHECKOUT` (`neighbor`, `featured`, `wellness`, `cover`). Until those are set, the partner buttons stay placeholders. The site never collects card numbers.

If the Supabase fields are left blank, the forms still show success and keep a copy in the browser. Use that only for a local preview.

## Local check

```bash
python3 -m http.server 4177
```

Open `http://127.0.0.1:4177/`.
