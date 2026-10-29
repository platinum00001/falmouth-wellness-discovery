/* Falmouth Wellness Discovery — Winter 2026 flipbook.
   Page-turn reader built on StPageFlip (page-flip@2.0.7, MIT).
   ?page=N deep links (centerfold = ?page=12), thumbnails, zoom, fullscreen,
   keyboard / swipe / click navigation, PDF download. ?print=1 lays every page
   out at 8.5×11 in for the PDF and thumbnail build (scripts/build_flipbook_assets.py). */
(function () {
  "use strict";
  const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const PARAMS = new URLSearchParams(location.search);
  const PRINT = PARAMS.get("print") === "1";
  const RATIO = 8.5 / 11;
  const PDF = "assets/fwd-winter-2026.pdf";
  const THUMB = function (i) { return "assets/img/mag/thumbs/p" + String(i + 1).padStart(2, "0") + ".jpg"; };
  let issue, fold, pf = null, pages = [];

  function esc(v) {
    return String(v ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function ani(html, d) { return html.replace(/^<(\w+)( class=")?/, function (m, tag, cls) { return "<" + tag + ' style="--d:' + d + '"' + (cls ? ' class="ani ' : ' class="ani"'); }); }
  function paras(list) { return (list || []).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join(""); }
  function picture(src, webp, alt, cls, small) {
    return '<figure class="' + cls + '"><picture>' + (webp ? '<source srcset="' + esc(webp) + '" type="image/webp">' : "") +
      '<img src="' + esc(small || src) + '" alt="' + esc(alt || "") + '" loading="lazy" decoding="async"></picture></figure>';
  }
  function cta(c, light) {
    if (!c) return "";
    const ext = /^mailto:|^https?:/.test(c.href);
    return '<a class="pg-btn' + (light ? " light" : "") + '" href="' + esc(c.href) + '"' + (ext && !/^mailto/.test(c.href) ? ' target="_blank" rel="noopener"' : "") + ">" + esc(c.label) + " →</a>";
  }
  function adHtml(ad) {
    if (!ad) return "";
    const size = ad.size || "eighth";
    return '<aside class="pg-ad size-' + esc(size) + '"><p class="pg-kicker">' + esc(ad.label || "Advertising") + "</p><strong>" +
      esc(ad.headline || "") + "</strong><p>" + esc(ad.text || "") + "</p>" + cta(ad.cta, true) + "</aside>";
  }
  function cardsHtml(cards) {
    if (!cards || !cards.length) return "";
    return '<div class="pg-cards n' + Math.min(cards.length, 8) + '">' + cards.map(function (c) {
      return '<article class="pg-card' + (c.open ? " is-open" : "") + '"><p class="pg-kicker">' + esc(c.kicker || "") + "</p><h3>" +
        esc(c.title) + "</h3>" + (c.meta ? "<p><strong>" + esc(c.meta) + "</strong></p>" : "") + "<p>" + esc(c.text) + "</p>" + cta(c.cta, false) + "</article>";
    }).join("") + "</div>";
  }
  function slot(id) {
    const s = (issue.imageSlots || []).find(function (x) { return x.id === id; });
    if (!s || !s.src) return "";
    return picture(s.src, s.webp, s.alt, "pg-slot", s.small);
  }
  function foot(i) {
    const side = i % 2 ? "is-left" : "is-right";
    return '<footer class="pg-foot ' + side + '"><span>' + esc(issue.issue.name) + " · " + esc(issue.issue.season) + "</span><b>" + (i + 1) + "</b></footer>";
  }

  /* ---------- crossword ---------- */
  function numbersFor(rows) {
    const nums = {}; let n = 1;
    const white = function (r, c) { return rows[r] && rows[r][c] && rows[r][c] !== "#"; };
    rows.forEach(function (row, r) {
      for (let c = 0; c < row.length; c++) {
        if (!white(r, c)) continue;
        if ((!white(r, c - 1) && white(r, c + 1)) || (!white(r - 1, c) && white(r + 1, c))) nums[r + "," + c] = n++;
      }
    });
    return { nums: nums, white: white };
  }
  function puzzleStatic(p) {
    const info = numbersFor(p.grid);
    let cells = "";
    p.grid.forEach(function (row, r) {
      for (let c = 0; c < row.length; c++) {
        cells += info.white(r, c) ? '<i>' + (info.nums[r + "," + c] ? "<b>" + info.nums[r + "," + c] + "</b>" : "") + "</i>" : '<i class="blk"></i>';
      }
    });
    const clues = ["across", "down"].map(function (dir) {
      return "<div><h4>" + dir[0].toUpperCase() + dir.slice(1) + "</h4><ol>" + p.clues[dir].map(function (cl) {
        return '<li value="' + cl.n + '">' + esc(cl.clue) + "</li>";
      }).join("") + "</ol></div>";
    }).join("");
    return '<section class="pz"><h3>' + esc(p.title) + '</h3><div class="pz-body"><div class="pz-grid" style="--cols:' + p.grid[0].length + '">' + cells + '</div><div class="pz-clues">' + clues + "</div></div></section>";
  }
  function puzzleLive(p) {
    const info = numbersFor(p.grid);
    const sec = document.createElement("section"); sec.className = "xw";
    const h = document.createElement("h3"); h.textContent = p.title || "Puzzle";
    const grid = document.createElement("div"); grid.className = "xw-grid"; grid.style.gridTemplateColumns = "repeat(" + p.grid[0].length + ", 1fr)";
    p.grid.forEach(function (row, r) {
      for (let c = 0; c < row.length; c++) {
        const cell = document.createElement("div"); cell.className = "cell";
        if (!info.white(r, c)) { const b = document.createElement("span"); b.className = "blk"; cell.appendChild(b); }
        else {
          if (info.nums[r + "," + c]) { const n = document.createElement("span"); n.className = "num"; n.textContent = info.nums[r + "," + c]; cell.appendChild(n); }
          const inp = document.createElement("input"); inp.maxLength = 1; inp.autocomplete = "off";
          inp.setAttribute("aria-label", "Row " + (r + 1) + " column " + (c + 1)); inp.dataset.answer = row[c];
          inp.addEventListener("input", function () { inp.value = inp.value.toUpperCase().slice(0, 1); });
          cell.appendChild(inp);
        }
        grid.appendChild(cell);
      }
    });
    const clues = document.createElement("div"); clues.className = "clue-cols";
    clues.innerHTML = ["across", "down"].map(function (dir) {
      return "<div><h4>" + dir[0].toUpperCase() + dir.slice(1) + "</h4><ol>" + p.clues[dir].map(function (cl) { return '<li value="' + cl.n + '">' + esc(cl.clue) + "</li>"; }).join("") + "</ol></div>";
    }).join("");
    const ctl = document.createElement("p"); ctl.className = "cta-row";
    const msg = document.createElement("p"); msg.setAttribute("role", "status");
    const check = document.createElement("button"); check.type = "button"; check.className = "btn btn-small btn-navy"; check.textContent = "Check puzzle";
    const reveal = document.createElement("button"); reveal.type = "button"; reveal.className = "btn btn-small btn-ghost"; reveal.textContent = "Reveal answers";
    check.addEventListener("click", function () {
      let wrong = 0, filled = 0;
      grid.querySelectorAll("input").forEach(function (i) {
        if (!i.value) return; filled++;
        const ok = i.value.toUpperCase() === i.dataset.answer; if (!ok) wrong++;
        i.style.outline = ok ? "2px solid #2c7f7b" : "2px solid #a33b28";
      });
      msg.textContent = filled ? (wrong ? wrong + " letters don't match yet." : "Every letter so far is right.") : "Type a few letters first.";
    });
    reveal.addEventListener("click", function () { grid.querySelectorAll("input").forEach(function (i) { i.value = i.dataset.answer; }); msg.textContent = "Answers revealed."; });
    ctl.append(check, reveal);
    sec.append(h, grid, clues, ctl, msg);
    return sec;
  }

  /* ---------- centerfold ---------- */
  function foldHtml(i, page) {
    const face = page.face === "back" ? "back" : "front";
    const first = pages.findIndex(function (p) { return p.kind === "centerfold" && (p.face === "back" ? "back" : "front") === face; });
    const half = i === first ? "L" : "R";
    const img = fold[face];
    let pins = "";
    if (face === "front") {
      (img.pins || []).forEach(function (p, k) {
        const onLeft = p.x < 50;
        if ((half === "L") !== onLeft) return;
        const x = half === "L" ? p.x * 2 : (p.x - 50) * 2;
        pins += '<span class="fold-pin' + (p.focus ? " is-focus" : "") + '" style="left:' + x.toFixed(2) + "%;top:" + p.y.toFixed(2) + "%;--pin:" + esc(p.color || "#1c5a5e") + ";--d:" + k + '" title="' + esc(p.n + ". " + p.title) + '"><i></i></span>';
      });
    }
    const label = face === "front" ? "Walking map" : "Visitor guide";
    const ctaHtml = half === "R"
      ? '<div class="fold-cta">' + (face === "front"
          ? '<a class="pg-btn light" href="map.html">Open the interactive map →</a><button type="button" class="pg-btn light" data-zoom>Zoom the map</button>'
          : '<a class="pg-btn light" href="guide.html">Open the visitor guide →</a><button type="button" class="pg-btn light" data-zoom>Zoom the guide</button>') + "</div>"
      : '<p class="fold-tag">' + label + " · pull-out centerfold</p>";
    return '<div class="pg pg-fold fold-' + half + " face-" + face + '"><picture>' +
      '<source srcset="' + esc(img.webp) + '" type="image/webp"><img src="' + esc(img.src) + '" alt="' +
      esc(face === "front" ? "Falmouth Wellness Walking Map: 20 numbered pins from Palmer Avenue to Teaticket Highway, framed by partner boxes; the orange pin is Cape Island Café at 316 Gifford Street." : "Falmouth Visitor Guide: landmarks, museums, trails, beaches, seasonal events and a Main Street inset map.") +
      '" decoding="async"></picture><div class="fold-pins">' + pins + "</div>" + ctaHtml + "</div>";
  }

  /* ---------- pages ---------- */
  function pageInner(page, i, live) {
    const k = page.kind;
    if (k === "cover") {
      const c = issue.images.cover;
      return '<div class="pg pg-cover">' + picture(c.src, c.webp, c.alt, "cover-art") +
        (PRINT ? "" : '<p class="cover-hint"><span>Open the issue</span></p>') + "</div>";
    }
    if (k === "centerfold") return foldHtml(i, page);
    let b = "", d = 0;
    if (page.banner && page.banner.src) b += ani(picture(page.banner.src, "", page.banner.alt, "pg-banner", page.banner.small), d++);
    b += '<div class="pg-in">';
    if (page.kicker || k === "toc") b += ani('<p class="pg-kicker">' + esc(page.kicker || "In this issue") + "</p>", d++);
    b += ani("<h2>" + esc(page.title) + "</h2>", d++);
    if (page.dek) b += ani('<p class="pg-dek">' + esc(page.dek) + "</p>", d++);
    if (k === "toc") {
      b += ani('<ol class="pg-toc">' + pages.map(function (p, j) {
        if (j === 0) return "";
        const t = p.kind === "centerfold" ? (p.face === "back" ? "Visitor guide (pull-out back)" : "Walking map (pull-out)") : p.title;
        if (p.kind === "centerfold" && pages[j - 1].kind === "centerfold" && pages[j - 1].face === p.face) return "";
        return '<li><a href="?page=' + (j + 1) + '" data-goto="' + j + '"><span>' + esc(t) + "</span><b>" + (j + 1) + "</b></a></li>";
      }).join("") + "</ol>", d++);
      return b + "</div>" + foot(i);
    }
    if (k === "crossword") {
      const pz = (issue.crossword && issue.crossword.puzzles) || [];
      if (live) b += '<div class="xw-live" data-xw></div>';
      else b += ani('<div class="pz-wrap">' + pz.map(puzzleStatic).join("") + "</div>", d++) +
        (PRINT ? "" : ani('<p class="pg-actions"><button type="button" class="pg-btn" data-zoom>Play the puzzles →</button></p>', d++));
      return b + "</div>" + foot(i);
    }
    const s = page.imageSlot ? slot(page.imageSlot) : "";
    if (s) b += ani(s, d++);
    if (page.lead) b += ani('<p class="pg-drop">' + esc(page.lead) + "</p>", d++);
    if (page.paragraphs && page.paragraphs.length) b += ani('<div class="pg-body">' + paras(page.paragraphs) + "</div>", d++);
    if (page.pullquote) b += ani('<blockquote class="pg-pull">' + esc(page.pullquote) + "</blockquote>", d++);
    if (page.cards && page.cards.length) b += ani(cardsHtml(page.cards), d++);
    if (k === "calendar") {
      b += ani('<div class="pg-events">' + (issue.events || []).slice((page.eventsRange || [0])[0], (page.eventsRange || [0, 999])[1]).map(function (e) {
        return '<article><p class="pg-kicker' + (/confirm/i.test(e.status || "") ? " ok" : "") + '">' + esc(e.status || "Check date") + "</p><h3>" + esc(e.title) + '</h3><p class="when">' + esc(e.when) + "</p><p>" + esc(e.detail) + "</p></article>";
      }).join("") + "</div>", d++);
    }
    if (page.audio) {
      const a = page.audio;
      b += ani('<section class="pg-audio-sec"><p class="pg-kicker">' + esc(a.kicker) + "</p><h3>" + esc(a.title) + "</h3>" + (a.dek ? '<p class="pg-dek">' + esc(a.dek) + "</p>" : "") +
        '<div class="pg-audio"><div class="qr" data-audio-qr></div><div>' + paras(a.paragraphs) + '<p><a class="pg-btn" href="audio.html">Open the audio page →</a></p></div></div></section>', d++);
    }
    if (k === "audio") b += ani('<div class="pg-audio"><div class="qr" data-audio-qr></div><p><a class="pg-btn" href="audio.html">Open the audio page →</a></p></div>', d++);
    if (page.sources && page.sources.length) {
      b += ani('<p class="pg-src">Sources: ' + page.sources.map(function (u) {
        return '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + esc(u.replace(/^https?:\/\/(www\.)?/, "").split("/")[0]) + "</a>";
      }).join(", ") + "</p>", d++);
    }
    b += ani(adHtml(page.ad), d++);
    return b + "</div>" + foot(i);
  }
  function pageEl(page, i) {
    const el = document.createElement("div");
    el.className = "page kind-" + page.kind + (i % 2 ? " side-L" : " side-R") + (page.ad && page.ad.size === "full" ? " has-full-ad" : "");
    el.dataset.i = i;
    if (i === 0 || i === pages.length - 1) el.dataset.density = "hard";
    el.innerHTML = page.kind === "centerfold" || page.kind === "cover" ? pageInner(page, i) : '<div class="pg pg-' + page.kind + '">' + pageInner(page, i) + "</div>";
    return el;
  }

  function drawQrs(root) {
    if (typeof QRCode === "undefined") return;
    const base = String((window.FWD_CONFIG || {}).SITE_BASE || "").replace(/\/$/, "");
    const url = (base || location.href.replace(/[^/]*$/, "").replace(/\/$/, "")) + "/audio.html";
    root.querySelectorAll("[data-audio-qr]").forEach(function (box) {
      if (box.childElementCount) return;
      new QRCode(box, { text: url, width: 128, height: 128, correctLevel: QRCode.CorrectLevel.M });
      box.setAttribute("role", "img"); box.setAttribute("aria-label", "QR code: open the quarterly audio page");
      box.querySelectorAll("img").forEach(function (img) { img.alt = "QR code: open the quarterly audio page"; });
    });
  }

  /* fit text: shrink type on crowded pages, scroll as a last resort */
  function fit(root) {
    root.querySelectorAll(".pg:not(.pg-fold):not(.pg-cover)").forEach(function (pg) {
      let fs = 1;
      pg.style.setProperty("--fs", fs);
      pg.classList.remove("is-scroll");
      pg.classList.remove("compact");
      const over = function () { return pg.scrollHeight > pg.clientHeight + 2; };
      while (over() && fs > 0.9) { fs = Math.round((fs - 0.04) * 100) / 100; pg.style.setProperty("--fs", fs); }
      if (over()) pg.classList.add("compact");
      while (pg.scrollHeight > pg.clientHeight + 2 && fs > 0.66) {
        fs = Math.round((fs - 0.04) * 100) / 100;
        pg.style.setProperty("--fs", fs);
      }
      if (pg.scrollHeight > pg.clientHeight + 2) pg.classList.add("is-scroll");
    });
  }


  /* measure every page off-screen at the live page width (hidden pages can't be measured in place) */
  function fitAll(els, pw) {
    const box = document.createElement("div");
    box.style.cssText = "position:absolute;left:-10000px;top:0;visibility:hidden;width:" + pw + "px";
    document.body.appendChild(box);
    els.forEach(function (el) {
      const pg = el.querySelector(".pg"); if (!pg || pg.classList.contains("pg-fold") || pg.classList.contains("pg-cover")) return;
      const c = el.cloneNode(true);
      c.style.cssText = "position:relative;display:block;width:" + pw + "px;height:" + Math.round(pw / RATIO) + "px";
      box.appendChild(c);
      fit(c);
      const cp = c.querySelector(".pg");
      pg.style.setProperty("--fs", cp.style.getPropertyValue("--fs"));
      ["compact", "is-scroll"].forEach(function (k) { pg.classList.toggle(k, cp.classList.contains(k)); });
      c.remove();
    });
    box.remove();
  }

  /* ---------- print / PDF layout ---------- */
  function bootPrint(host) {
    document.documentElement.classList.add("mag-print");
    document.getElementById("reader-status").textContent = "";
    pages.forEach(function (p, i) { host.appendChild(pageEl(p, i)); });
    drawQrs(host);
    const base = String((window.FWD_CONFIG || {}).SITE_BASE || "").replace(/\/$/, "");
    if (base) host.querySelectorAll("a[href]").forEach(function (a) {
      const h = a.getAttribute("href");
      if (/^(https?:|mailto:|tel:|#)/.test(h)) return;
      a.setAttribute("href", base + "/" + (h.charAt(0) === "?" ? "magazine.html" + h : h));
    });
    const imgs = [].slice.call(host.querySelectorAll("img"));
    imgs.forEach(function (im) { im.loading = "eager"; });
    Promise.all(imgs.map(function (im) { return im.complete ? 0 : new Promise(function (r) { im.onload = im.onerror = r; }); }))
      .then(function () { return document.fonts ? document.fonts.ready : 0; })
      .then(function () { fit(host); document.documentElement.dataset.ready = "1"; });
  }

  /* ---------- flipbook ---------- */
  function boot(host) {
    const stage = document.getElementById("mag-stage");
    const label = document.getElementById("page-label");
    const live = document.getElementById("reader-live");
    const els = pages.map(pageEl);
    els.forEach(function (el) { host.appendChild(el); });
    drawQrs(host);
    const req = Number(PARAMS.get("page"));
    const start = req >= 1 && req <= pages.length ? req - 1 : 0;

    function size() {
      const full = document.fullscreenElement === stage;
      const bar = document.getElementById("mag-bar").offsetHeight;
      const head = full ? 0 : (document.querySelector(".site-header") || { offsetHeight: 0 }).offsetHeight;
      const availH = Math.max(380, window.innerHeight - head - bar - (full ? 40 : 56));
      const w = stage.clientWidth - 16;
      const portrait = w < 680;
      let pw = portrait ? Math.min(w, availH * RATIO) : Math.min(w / 2, availH * RATIO);
      pw = Math.max(portrait ? 260 : 340, Math.floor(pw));
      document.getElementById("book-box").style.width = (portrait ? pw : pw * 2) + "px";
      stage.classList.toggle("is-portrait", portrait);
      document.documentElement.style.setProperty("--pw", pw + "px");
    }
    size();
    const curPW = function () { const v = els.find(function (e) { return e.offsetWidth > 0; }); return v ? v.offsetWidth : parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--pw")) || 560; };
    if (typeof St === "undefined" || !St.PageFlip) {
      host.classList.add("no-flip");
      document.getElementById("reader-status").textContent = "The page-turn library did not load, so the pages are shown in a scrolling column.";
      fit(host);
      return;
    }
    pf = new St.PageFlip(host, {
      width: 680, height: 880, size: "stretch", minWidth: 340, maxWidth: 1100, minHeight: 300, maxHeight: 1424,
      showCover: true, usePortrait: true, autoSize: true, mobileScrollSupport: true, maxShadowOpacity: 0.45,
      flippingTime: REDUCED ? 300 : 850, drawShadow: !REDUCED, startPage: start, showPageCorners: true
    });
    pf.loadFromHTML(els);
    const visible = function () {
      const i = pf.getCurrentPageIndex();
      if (pf.getOrientation() === "portrait" || i === 0) return [i];
      const l = i % 2 ? i : i - 1;
      return l + 1 < pages.length ? [l, l + 1] : [l];
    };
    function onPage() {
      const v = visible();
      els.forEach(function (el, j) { el.classList.toggle("is-live", v.indexOf(j) >= 0); });
      const n = v.map(function (j) { return j + 1; });
      const pg = pages[v[0]];
      const tail = pg.kind === "centerfold" ? (pg.face === "back" ? " · visitor guide" : " · walking map") : "";
      label.innerHTML = (n.length > 1 ? "Pages <b>" + n[0] + "–" + n[1] + "</b>" : "Page <b>" + n[0] + "</b>") + " of " + pages.length + tail;
      live.textContent = v.map(function (j) { return pages[j].title || "Cover"; }).join(" and ");
      document.getElementById("prev-page").disabled = v[0] === 0;
      document.getElementById("next-page").disabled = v[v.length - 1] >= pages.length - 1;
      const url = new URL(location.href);
      if (v[0] === 0) url.searchParams.delete("page"); else url.searchParams.set("page", v[0] + 1);
      history.replaceState(null, "", url);
      document.querySelectorAll(".thumbs [data-goto]").forEach(function (t) { t.classList.toggle("is-current", v.indexOf(Number(t.dataset.goto)) >= 0); });
      const bar = document.getElementById("mag-progress");
      if (bar) bar.style.width = ((v[v.length - 1] + 1) / pages.length * 100) + "%";
    }
    pf.on("flip", onPage);
    pf.on("changeOrientation", function () { setTimeout(function () { fitAll(els, curPW()); onPage(); }, 60); });
    pf.on("changeState", function (e) { stage.classList.toggle("is-flipping", e.data !== "read"); });
    window.goToPage = function (j) {
      j = Math.max(0, Math.min(pages.length - 1, j));
      const v = visible();
      if (v.indexOf(j) >= 0) return;
      if (REDUCED || Math.abs(j - v[0]) > 2) { pf.turnToPage(j); onPage(); } else pf.flip(j);
    };
    requestAnimationFrame(function () { fitAll(els, curPW()); onPage(); });
    let rt;
    window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(function () { size(); pf.update(); fitAll(els, curPW()); onPage(); }, 120); });
    document.addEventListener("fullscreenchange", function () {
      stage.classList.toggle("is-full", document.fullscreenElement === stage);
      setTimeout(function () { size(); pf.update(); fitAll(els, curPW()); }, 80);
    });
    document.getElementById("prev-page").addEventListener("click", function () { pf.flipPrev(); });
    document.getElementById("next-page").addEventListener("click", function () { pf.flipNext(); });
    document.addEventListener("keydown", function (e) {
      if (e.target.matches("input, textarea, select") || document.querySelector("dialog[open]")) return;
      if (e.key === "ArrowRight" || e.key === "PageDown") { e.preventDefault(); pf.flipNext(); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); pf.flipPrev(); }
      else if (e.key === "Home") window.goToPage(0);
      else if (e.key === "End") window.goToPage(pages.length - 1);
      else if (e.key === "f" || e.key === "F") toggleFull();
      else if (e.key === "z" || e.key === "Z") openZoom();
    });
    host.addEventListener("click", function (e) {
      const go = e.target.closest("[data-goto]");
      if (go) { e.preventDefault(); window.goToPage(Number(go.dataset.goto)); return; }
      if (e.target.closest("[data-zoom]")) { e.preventDefault(); openZoom(); }
    });
    wireChrome(visible);
    document.getElementById("reader-status").textContent = "";
    if (!PARAMS.get("page") && !REDUCED) setTimeout(function () { stage.classList.add("hint-on"); }, 900);
  }

  function toggleFull() {
    const stage = document.getElementById("mag-stage");
    if (document.fullscreenElement) document.exitFullscreen();
    else if (stage.requestFullscreen) stage.requestFullscreen().catch(function () {});
  }

  /* ---------- zoom ---------- */
  let zoomLevel = 1;
  function openZoom() {
    const dlg = document.getElementById("zoom-dialog");
    const body = document.getElementById("zoom-body");
    const i = pf ? pf.getCurrentPageIndex() : 0;
    const portrait = !pf || pf.getOrientation() === "portrait" || i === 0;
    const l = portrait ? i : (i % 2 ? i : i - 1);
    const v = portrait ? [l] : [l, l + 1].filter(function (j) { return j < pages.length; });
    body.innerHTML = "";
    const p0 = pages[v[0]];
    if (p0.kind === "centerfold") {
      const face = p0.face === "back" ? "back" : "front";
      body.innerHTML = '<div class="zoom-sheet"><img src="' + esc(fold[face].src) + '" alt="' + (face === "front" ? "Falmouth Wellness Walking Map, full sheet" : "Falmouth Visitor Guide, full sheet") + '"></div>';
      body.dataset.mode = "sheet";
    } else {
      body.dataset.mode = "pages";
      v.forEach(function (j) {
        const wrap = document.createElement("div");
        wrap.className = "zoom-page kind-" + pages[j].kind;
        wrap.innerHTML = pages[j].kind === "cover" ? pageInner(pages[j], j) : '<div class="pg pg-' + pages[j].kind + '">' + pageInner(pages[j], j, true) + "</div>";
        body.appendChild(wrap);
      });
      body.querySelectorAll("[data-xw]").forEach(function (host) {
        ((issue.crossword && issue.crossword.puzzles) || []).forEach(function (p) { host.appendChild(puzzleLive(p)); });
      });
      body.querySelectorAll("[data-zoom]").forEach(function (b) { b.remove(); });
      drawQrs(body);
    }
    zoomLevel = 1; applyZoom();
    document.getElementById("zoom-title").textContent = v.map(function (j) { return "Page " + (j + 1); }).join(" · ");
    dlg.showModal();
  }
  function applyZoom() {
    const body = document.getElementById("zoom-body");
    body.style.setProperty("--z", zoomLevel);
    document.getElementById("zoom-level").textContent = Math.round(zoomLevel * 100) + "%";
  }

  function wireChrome(visible) {
    document.getElementById("zoom-btn").addEventListener("click", openZoom);
    document.getElementById("zoom-in").addEventListener("click", function () { zoomLevel = Math.min(3, zoomLevel + 0.25); applyZoom(); });
    document.getElementById("zoom-out").addEventListener("click", function () { zoomLevel = Math.max(0.75, zoomLevel - 0.25); applyZoom(); });
    document.getElementById("full-btn").addEventListener("click", toggleFull);
    if (!document.fullscreenEnabled) document.getElementById("full-btn").hidden = true;
    const drawer = document.getElementById("thumbs-dialog");
    const grid = document.getElementById("thumbs-grid");
    grid.innerHTML = pages.map(function (p, j) {
      const t = p.kind === "cover" ? "Cover" : p.kind === "centerfold" ? (p.face === "back" ? "Visitor guide" : "Walking map") : p.title;
      return '<button type="button" data-goto="' + j + '"><span class="th"><img src="' + THUMB(j) + '" alt="" loading="lazy" onerror="this.parentNode.classList.add(\'no-img\');this.remove()"></span><span class="tn">' + (j + 1) + '</span><span class="tt">' + esc(t) + "</span></button>";
    }).join("");
    grid.addEventListener("click", function (e) {
      const b = e.target.closest("[data-goto]"); if (!b) return;
      drawer.close(); window.goToPage(Number(b.dataset.goto));
    });
    document.getElementById("thumbs-btn").addEventListener("click", function () {
      drawer.showModal();
      const cur = grid.querySelector(".is-current"); if (cur) cur.scrollIntoView({ block: "center" });
    });
    document.querySelectorAll("dialog").forEach(function (d) {
      d.addEventListener("click", function (e) { if (e.target === d) d.close(); });
    });
    const dl = document.getElementById("pdf-btn");
    fetch(PDF, { method: "HEAD" }).then(function (r) { if (!r.ok) dl.hidden = true; }).catch(function () { dl.hidden = true; });
  }

  async function start() {
    const host = document.getElementById("book");
    try {
      const [a, b] = await Promise.all([fetch("data/issue1.json"), fetch("data/centerfold-images.json")]);
      issue = await a.json(); fold = await b.json();
    } catch (err) {
      document.getElementById("reader-status").textContent = "The issue did not load. Please refresh the page.";
      return;
    }
    pages = issue.pages;
    if (PRINT) bootPrint(host); else boot(host);
  }
  start();
})();
