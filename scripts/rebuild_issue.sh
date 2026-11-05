#!/usr/bin/env bash
# Rebuild the whole issue in one go: relabel -> cover -> pull-out map -> grid refs -> thumbnails + PDFs -> audit.
#
#   scripts/rebuild_issue.sh                      # January 2027, Real-ESRGAN if PY_SR has torch+spandrel
#   LABEL="April 2027" OLD_LABELS="January 2027" ALIASES="winter-2026 winter-2027 january-2027" scripts/rebuild_issue.sh
#   NO_SR=1 SKIP_AUDIT=1 scripts/rebuild_issue.sh # Lanczos only, no crawl
#
# Env: LABEL (issue label), SLUG (default: label lower-cased, spaces -> '-'), OLD_LABELS (';'-separated labels to
# replace site-wide), ALIASES (old slugs whose issue PDF/cover URLs must keep working), PULL_ALIASES (same for the
# pull-out PDF), PY_SR (python with torch + spandrel for Real-ESRGAN), NO_SR=1, SKIP_AUDIT=1, PORT (default 8765).
set -euo pipefail
cd "$(dirname "$0")/.."
LABEL="${LABEL:-January 2027}"
SLUG="${SLUG:-$(echo "$LABEL" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')}"
OLD_LABELS="${OLD_LABELS:-Winter 2026}"
ALIASES="${ALIASES:-winter-2026 winter-2027}"
PULL_ALIASES="${PULL_ALIASES:-winter-2026}"
PY_SR="${PY_SR:-python3}"
PORT="${PORT:-8765}"
BASE="http://localhost:$PORT/"

step() { printf '\n== %s\n' "$*"; }

step "1/6 relabel text -> $LABEL"
IFS=';' read -ra OLDS <<< "$OLD_LABELS"
for old in "${OLDS[@]}"; do
  [ -n "$old" ] && [ "$old" != "$LABEL" ] && python3 scripts/relabel_issue.py --old "$old" --new "$LABEL"
done

step "2/6 cover art"
cover_alias=(); for a in $ALIASES; do cover_alias+=(--alias "$a"); done
python3 scripts/render_cover.py --label "$LABEL" --slug "$SLUG" "${cover_alias[@]}"

step "3/6 pull-out map (upscale, Refuge cover panel, A-F/1-4 grid, web images, 2-page PDF)"
pull_alias=(); for a in $PULL_ALIASES; do pull_alias+=(--alias "$a"); done
sr=(); [ "${NO_SR:-}" = "1" ] && sr=(--no-sr)
"$PY_SR" scripts/build_pullout_map.py --issue "$SLUG" --label "$LABEL" "${pull_alias[@]}" "${sr[@]}"

step "4/6 grid references (data/pullout-landmarks.json, guide.html index, issue1.json)"
python3 scripts/pullout_grid_refs.py

step "5/6 thumbnails + issue PDF (with the 17x11 insert spliced in)"
started=""
if ! curl -s -o /dev/null "$BASE"; then
  python3 -m http.server "$PORT" >/dev/null 2>&1 & started=$!
  trap '[ -n "$started" ] && kill $started' EXIT
  sleep 1
fi
issue_alias=(); for a in $ALIASES; do issue_alias+=(--alias "$a"); done
python3 scripts/build_flipbook_assets.py "$BASE" --slug "$SLUG" "${issue_alias[@]}"

if [ "${SKIP_AUDIT:-}" != "1" ]; then
  step "6/6 blank-info + link audit (build/audit.json)"
  python3 scripts/audit_site.py "$BASE" --json build/audit.json || true
else
  step "6/6 audit skipped"
fi
echo; echo "Done: assets/fwd-$SLUG.pdf, assets/fwd-pullout-map-$SLUG.pdf, assets/img/cover-$SLUG.jpg"
