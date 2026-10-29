#!/usr/bin/env python3
"""Blank-information and broken-link audit for the FWD site.

Crawls every internal page from the home page (plus the magazine print view,
which lays out all flipbook pages) in headless Chrome at desktop 1440 and
mobile 390, after JavaScript runs, and flags:
  placeholder text  TBD, coming soon, lorem, placeholder, your business here,
                    sample slot, image slot, to be confirmed, undefined/null/NaN
  empty elements    visible headings, paragraphs, list items, links, buttons,
                    cards with no text and no image/icon/label
  images            broken (naturalWidth 0) or missing alt attribute
  links             internal links that 404, bad tel: numbers, and (with
                    --external) external links that fail
  listings          directory cards missing an address or a phone/website
Usage:
  python3 scripts/audit_site.py [BASE_URL] [--external] [--json out.json]
BASE_URL defaults to http://localhost:8765/ (python3 -m http.server 8765)."""
import json, re, sys, collections, urllib.parse, urllib.request, ssl
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:] if not a.startswith("--")]
BASE = args[0] if args else "http://localhost:8765/"
EXTERNAL = "--external" in sys.argv
OUT = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
PATTERNS = [
    (r"\bTBD\b|\bTBA\b", "TBD"), (r"coming soon", "coming soon"), (r"lorem ipsum|\blorem\b", "lorem"),
    (r"placeholder", "placeholder"), (r"your (business|practice|clinic|office|nonprofit|program|interview|back cover) here", "your business here"),
    (r"sample slot|image slot", "sample/image slot"), (r"to be confirmed", "to be confirmed"),
    (r"(?<![\w-])(undefined|NaN)(?![\w-])", "undefined/NaN"), (r":\s*null\b|\bnull\s*·", "null"),
    (r"not a real (advertisement|pet|listing)", "not a real …"), (r"sample (pull )?quote", "sample quote"),
]
EVAL = r"""() => {
  const vis = el => { if (el.checkVisibility && !el.checkVisibility({contentVisibilityAuto: true, opacityProperty: true, visibilityProperty: true})) return false;
    const d = el.closest('details:not([open])'); if (d && !el.closest('summary')) return false;
    const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0'; };
  const label = el => (el.innerText || '').trim() || el.getAttribute('aria-label') || el.getAttribute('title') ||
    el.querySelector('img,svg,canvas,picture,input,select,textarea,iframe,video') ;
  const path = el => { const p = []; for (let e = el; e && e !== document.body && p.length < 4; e = e.parentElement)
      p.unshift(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList.length ? '.' + [...e.classList].slice(0, 2).join('.') : '')); return p.join('>'); };
  const empty = [];
  document.querySelectorAll('main h1,main h2,main h3,main h4,main p,main li,main a,main button,main td,main dd,main figcaption,main .card,main .listing,main .story-card,main .pg-card,footer p,footer a,header a')
    .forEach(el => { if (!el.closest('dialog:not([open])') && !el.closest('.leaflet-container') && !el.closest('[aria-hidden="true"]') && vis(el) && !label(el)) empty.push(path(el)); });
  const imgs = [...document.images].map(i => ({src: i.currentSrc || i.src, ok: i.complete && i.naturalWidth > 0, alt: i.hasAttribute('alt'),
     tile: !!i.closest('.leaflet-container'), lazy: i.loading === 'lazy' && !i.complete}));
  const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  const dirPage = !/free-help|partner/.test(location.pathname);
  const cards = [...document.querySelectorAll('.listing-card,article.listing')].filter(c => dirPage && !c.classList.contains('listing-open') && !c.classList.contains('case-card')).map(c => {
     const t = c.innerText; return {name: (c.querySelector('h3,h2') || {}).innerText || '', addr: !!c.querySelector('.meta-addr') || /\d+\s+\w+.*(St|Street|Rd|Road|Ave|Avenue|Hwy|Highway|Way|Lane|Ln|Dr|Drive|Square|Straits|Pl|Place)\b/i.test(t),
       contact: !!c.querySelector('a[href^="tel:"], a[href^="http"]')}; });
  return {text: document.body.innerText, textAll: document.body.textContent, empty, imgs, links, cards};
}"""

def norm(url):
    u = urllib.parse.urlsplit(url); return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, u.query, ""))

def internal(url):
    return url.startswith(BASE)

def status(url, cache={}):
    if url in cache: return cache[url]
    ctx = ssl.create_default_context()
    code = None
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (FWD link check; CapeIslandCafe@gmail.com)"})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as r: code = r.status
            break
        except urllib.error.HTTPError as e:
            code = e.code
            if method == "HEAD" and e.code in (403, 405, 404, 400, 501): continue
            break
        except Exception as e:
            code = "ERR " + type(e).__name__
    cache[url] = code
    return code

def main():
    issues = collections.defaultdict(list)
    seen, queue = set(), [BASE, BASE + "magazine.html?print=1"]
    pages_done = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        views = {"desktop": dict(viewport={"width": 1440, "height": 900}),
                 "mobile": dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2)}
        ctxs = {k: b.new_context(**v) for k, v in views.items()}
        ext_links = set()
        while queue:
            url = queue.pop(0)
            if url in seen: continue
            seen.add(url)
            for vname, ctx in ctxs.items():
                pg = ctx.new_page(); errs = []
                pg.on("pageerror", lambda e: errs.append(str(e)))
                resp = pg.goto(url, wait_until="networkidle", timeout=60000)
                if resp and resp.status >= 400:
                    issues["dead internal link"].append(f"{url} → {resp.status}"); pg.close(); break
                pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 700) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); }""")
                pg.wait_for_timeout(900)
                r = pg.evaluate(EVAL)
                rel = url.replace(BASE, "/") + f" [{vname}]"
                for e in errs: issues["js error"].append(f"{rel}: {e[:160]}")
                if vname == "desktop":
                    for rx, name in PATTERNS:
                        for m in re.finditer(rx, r["textAll"], re.I):
                            ctxt = r["textAll"][max(0, m.start() - 50): m.end() + 50].replace("\n", " ")
                            issues["placeholder text: " + name].append(f"{rel}: …{ctxt.strip()}…")
                for e in r["empty"]: issues["empty element"].append(f"{rel}: {e}")
                for im in r["imgs"]:
                    if im["tile"]: continue
                    if not im["ok"] and not im["lazy"]: issues["broken image"].append(f"{rel}: {im['src']}")
                    if not im["alt"]: issues["image missing alt"].append(f"{rel}: {im['src']}")
                if vname == "desktop":
                    for c in r["cards"]:
                        if not c["addr"]: issues["listing missing address"].append(f"{rel}: {c['name']}")
                        if not c["contact"]: issues["listing missing phone/website"].append(f"{rel}: {c['name']}")
                    for h in r["links"]:
                        if h.startswith(("mailto:", "javascript:")) or h.startswith("#"): continue
                        if h.startswith("tel:"):
                            if len(re.sub(r"\D", "", h)) < 10: issues["bad tel link"].append(f"{rel}: {h}")
                            continue
                        full = norm(urllib.parse.urljoin(url, h))
                        if internal(full):
                            path_only = urllib.parse.urlsplit(full)
                            target = urllib.parse.urlunsplit((path_only.scheme, path_only.netloc, path_only.path, "", ""))
                            code = status(target)
                            if code != 200: issues["dead internal link"].append(f"{rel}: {h} → {code}")
                            elif re.search(r"(\.html|/)$", path_only.path) and full not in seen:
                                q = full if "print=1" not in full else None
                                if q and "?" not in q: queue.append(q)
                        elif full.startswith("http"):
                            ext_links.add((full, rel))
                pg.close()
            pages_done.append(url)
            print(f"  {len(pages_done)} pages, {len(queue)} queued", file=sys.stderr, flush=True)
        if EXTERNAL:
            by = collections.defaultdict(list)
            for u, rel in ext_links: by[u].append(rel)
            from concurrent.futures import ThreadPoolExecutor
            print(f"checking {len(by)} external links…", flush=True)
            with ThreadPoolExecutor(24) as ex:
                codes = dict(zip(sorted(by), ex.map(status, sorted(by))))
            for u, rels in sorted(by.items()):
                code = codes[u]
                if isinstance(code, int) and code < 400: continue
                if u.startswith("http://") and code in (500, 502, 503) or str(code).startswith("ERR"):
                    alt = status("https://" + u[7:]) if u.startswith("http://") else code
                    if isinstance(alt, int) and alt < 400: continue
                    if u.startswith("http://"):
                        issues["external link not checkable from this machine (plain http blocked; verify by hand)"].append(f"{u} (on {rels[0]})"); continue
                if code in (401, 402, 403, 429, 999): issues["external link blocked bot check (not verified)"].append(f"{u} → {code} (on {rels[0]})")
                else: issues["dead external link"].append(f"{u} → {code} (on {rels[0]}, {len(rels)} pages)")
        b.close()
    total = sum(len(v) for k, v in issues.items() if "not verified" not in k)
    print(f"Crawled {len(pages_done)} pages × 2 viewports. Issues: {total}")
    for k in sorted(issues):
        v = issues[k]; print(f"\n## {k}: {len(v)}")
        for line in v[:40]: print("  -", line)
        if len(v) > 40: print(f"  … {len(v) - 40} more")
    if OUT:
        json.dump({"base": BASE, "pages": pages_done, "total": total, "counts": {k: len(v) for k, v in issues.items()}, "issues": issues}, open(OUT, "w"), indent=1)

if __name__ == "__main__":
    main()
