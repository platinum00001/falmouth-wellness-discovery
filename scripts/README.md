# Issue build tooling

Everything needed to rebuild an issue of Falmouth Wellness Discovery from the repo. Run from the repo root.

## One command

```bash
scripts/rebuild_issue.sh
```

Defaults: label `January 2027`, slug `january-2027`, old slugs `winter-2026 winter-2027` kept working.
For the next issue, for example:

```bash
LABEL="April 2027" OLD_LABELS="January 2027" ALIASES="winter-2026 winter-2027 january-2027" PULL_ALIASES="winter-2026 january-2027" scripts/rebuild_issue.sh
```

Options: `NO_SR=1` (Lanczos instead of Real-ESRGAN), `SKIP_AUDIT=1`, `PY_SR=/path/to/python` (a Python that has torch + spandrel), `PORT=8765`.

## The steps

| Step | Script | What it does | Writes |
| --- | --- | --- | --- |
| 1 | `relabel_issue.py --old "Winter 2026" --new "January 2027" [--dry-run]` | Replaces the issue label and its slug (`winter-2026` → `january-2027`) in every text file (HTML, JS, CSS, JSON, XML, MD, Python templates). Skips `assets/`, `build/`, `.git`. | text files in place |
| 2 | `render_cover.py --label "January 2027" [--slug …] [--alias winter-2026 …]` | Draws the Nobska Light cover with the label. Source photo `assets/src/cover/nobska1.jpg`, fonts in `scripts/fonts/`. Aliases get byte-identical copies so old cover URLs show the new art. | `assets/img/cover-<slug>{,-900}.{jpg,webp}` |
| 3 | `build_pullout_map.py [--issue slug] [--label …] [--alias old-slug] [--no-sr]` | Pull-out insert compositor: upscales the owner's 2048×1325 map art (`assets/src/pullout/`) to 5100×3300 (17×11 at 300 dpi) with Real-ESRGAN x2plus + Lanczos (Lanczos only if torch/spandrel are missing), covers the Refuge Fitness ad (slot R4, both sides) with a "Featured spot available" panel, draws the A–F / 1–4 grid inside the ad border, writes web WebP/JPEG and the 2-page PDF. | `build/pullout/print-*.jpg` (print masters, not committed), `assets/img/mag/pullout/*`, `assets/fwd-pullout-map-<slug>.pdf`, `data/pullout-map.json` |
| 4 | `pullout_grid_refs.py [--check] [--mark]` | Computes grid cells for every landmark in `data/pullout-landmarks.json` (x/y = where it sits on the art), writes the "Find it on the pull-out map" index into `guide.html`, and tags `data/issue1.json` visitor-guide entries with refs like "Woods Hole side B4". `--mark` draws the points on `build/pullout/mark-<side>.png` to check them. | `data/pullout-landmarks.json`, `guide.html`, `data/issue1.json` |
| 5 | `build_flipbook_assets.py [base-url] [--slug …] [--alias …]` | Renders `magazine.html?print=1` in Chrome: 32 thumbnails, the letter-size PDF, then splices the two 17×11 pull-out pages in place of pages 12–15. Needs `python3 -m http.server 8765`. | `assets/img/mag/thumbs/pNN.jpg`, `assets/fwd-<slug>.pdf` + alias copies |
| 6 | `audit_site.py [base-url] [--external] [--json out.json]` | Blank-information and broken-link crawl at 1440 and 390 px. | stdout, `build/audit.json` |

Other scripts: `update_issue_2026_11_04_pullout.py` (one-off, idempotent: pages 12–15 become the pull-out, calendar trimmed for a January 2027 release), `build_directory.py`, `build_free_help.py`, `set_site_base.py`, `build_centerfold_images.py` (old Leaflet centerfold images; no longer used by the flipbook).

## Real-ESRGAN setup (optional, CPU is fine, ~40 s per side)

```bash
python3 -m venv build/venv --system-site-packages
build/venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
build/venv/bin/pip install spandrel
PY_SR=build/venv/bin/python scripts/rebuild_issue.sh
```

The model (`RealESRGAN_x2plus.pth`, BSD-3) downloads to `build/models/` on first use. x2plus was chosen over x4plus because x4plus invented small artifacts in fine map text. Upscaling is not a substitute for a true high-resolution export of the map: ask the designer for the layered or 300 dpi original before the print run.

## Pull-out map: print imposition

- Sheet: 17×11 in, printed both sides (4/4), folded once to 8.5×11. Front = Downtown · Main Street (folios 12–13), back = Main Street & Woods Hole (folios 14–15).
- Issue: 32 folios = 28-page saddle-stitched body (7 sheets of 17×11, self-cover) + the 4-page insert. Multiple of 4 either way.
- Placement: the insert is printed separately and tipped in with fugitive (removable) glue between pages 11 and 16, so readers can pull it out and keep it. If the printer must stitch it, it has to be the innermost sheet of the body, which puts it at folios 15–18; change the order in `data/issue1.json` to match.
- PDFs: `assets/fwd-pullout-map-<slug>.pdf` is the insert alone (2 pages, 17×11, 300 dpi, trim size; add 0.125 in bleed at the printer if required, the outer edge is the white border). `assets/fwd-<slug>.pdf` is the reader edition: 30 PDF pages = folios 1–11, the two 17×11 insert pages, folios 16–32.

## Border ads on the pull-out

The map art has its 24 border ads baked in (the health-wellness-maps editor only overlays uploads on top of the same 2048×1325 JPEG; there is no layered source). To change a slot, add it to `COVER` in `build_pullout_map.py` (slot fractions are the same as `maps.json` in platinum00001/health-wellness-maps) or supply new art in `assets/src/pullout/`.
