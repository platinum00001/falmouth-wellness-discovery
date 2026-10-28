const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function paras(list) {
  return (list || []).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("");
}

function adHtml(ad) {
  if (!ad) return "";
  const size = ad.size || "eighth";
  const cls = size === "full" ? "ad ad-full" : size === "half" ? "ad ad-half" : "ad";
  return (
    '<aside class="' + cls + '" aria-label="Sample ' + esc(size) + ' page advertisement">' +
    "<p>" + esc(ad.label || "Sample advertisement") + "</p>" +
    "<strong>" + esc(ad.headline || "Your business here") + "</strong>" +
    "<p>" + esc(ad.text || "Not a real advertisement. Size only.") + "</p></aside>"
  );
}

function cardsHtml(cards) {
  if (!cards || !cards.length) return "";
  return '<div class="mag-grid two">' + cards.map(function (card) {
    return (
      '<article class="story-card">' +
      '<p class="kicker">' + esc(card.kicker || (card.placeholder ? "Sample slot" : "Partner")) + "</p>" +
      "<h3>" + esc(card.title) + "</h3>" +
      (card.meta ? "<p><strong>" + esc(card.meta) + "</strong></p>" : "") +
      "<p>" + esc(card.text) + "</p></article>"
    );
  }).join("") + "</div>";
}

function slotHtml(issue, id) {
  const slot = (issue.imageSlots || []).find(function (item) { return item.id === id; });
  if (!slot) return "";
  if (slot.src) {
    const webp = slot.webp ? '<source srcset="' + esc(slot.webp) + '" type="image/webp">' : "";
    return '<figure class="cover-fig"><picture>' + webp +
      '<img src="' + esc(slot.src) + '" alt="' + esc(slot.alt || "") + '"></picture></figure>';
  }
  return '<div class="slot"><p class="kicker">Image slot</p><strong>' + esc(slot.id) +
    '</strong><p>' + esc(slot.note || "Open for a confirmed photo or later generated art.") + "</p></div>";
}

function bannerHtml(banner) {
  if (!banner || !banner.src) return "";
  const srcset = banner.small ? ' srcset="' + esc(banner.small) + ' 800w, ' + esc(banner.src) + ' 1600w" sizes="(min-width: 980px) 45vw, 100vw"' : "";
  return '<figure class="mag-banner"><img src="' + esc(banner.src) + '"' + srcset +
    ' width="1600" height="900" alt="' + esc(banner.alt || "") + '" loading="lazy" decoding="async"></figure>';
}

function footer(issue, page, index, total) {
  return '<p class="page-no"><span>' + esc(issue.issue.name) + " · " + esc(issue.issue.season) +
    ' · Sample</span><span>' + (index + 1) + " / " + total + "</span></p>";
}

function renderPage(issue, page, index, total) {
  const foot = footer(issue, page, index, total);
  if (page.kind === "cover") {
    const cover = issue.images.cover;
    return (
      '<article class="leaf" data-page="' + index + '">' +
      '<figure class="cover-fig"><picture>' +
      '<source srcset="' + esc(cover.webp) + '" type="image/webp">' +
      '<img src="' + esc(cover.src) + '" alt="' + esc(cover.alt) + '">' +
      "</picture></figure>" + foot + "</article>"
    );
  }
  if (page.kind === "toc") {
    const items = issue.pages.map(function (item, i) {
      return "<li><span>" + esc(item.title || item.kind) + "</span><span>" + (i + 1) + "</span></li>";
    }).join("");
    return '<article class="leaf"><p class="kicker">In this issue</p><h2>Contents</h2><ol class="toc-list">' +
      items + "</ol>" + foot + "</article>";
  }
  if (page.kind === "crossword") {
    return '<article class="leaf"><p class="kicker">Sample puzzle</p><h2>' + esc(page.title) + "</h2><p>" +
      esc(page.dek) + '</p><div id="crossword"></div>' + foot + "</article>";
  }
  let body = bannerHtml(page.banner) + '<p class="kicker">' + esc(page.kicker || "Sample") + "</p><h2>" + esc(page.title) + "</h2>";
  if (page.dek) body += '<p class="dek">' + esc(page.dek) + "</p>";
  if (page.imageSlot) body += slotHtml(issue, page.imageSlot);
  if (page.lead) body += '<p class="drop">' + esc(page.lead) + "</p>";
  body += paras(page.paragraphs);
  if (page.pullquote) body += '<blockquote class="pull">' + esc(page.pullquote) + "</blockquote>";
  body += cardsHtml(page.cards);
  if (page.sources && page.sources.length) {
    body += '<p class="sources">Sources: ' + page.sources.map(function (url) {
      return '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(url.replace(/^https?:\/\/(www\.)?/, "").split("/")[0]) + "</a>";
    }).join(", ") + "</p>";
  }
  if (page.kind === "calendar") {
    body += (issue.events || []).map(function (event) {
      return '<article class="event"><p class="kicker">' + esc(event.status || "Check date") + '</p><h3>' + esc(event.title) +
        "</h3><p>" + esc(event.when) + "</p><p>" + esc(event.detail) + "</p></article>";
    }).join("");
  }
  if (page.kind === "audio") {
    body += '<p><a href="audio.html">Open the quarterly audio update</a></p><div id="audio-qr" class="qr-box"></div>';
  }
  body += adHtml(page.ad);
  return '<article class="leaf">' + body + foot + "</article>";
}

function buildCrossword(issue) {
  const host = document.getElementById("crossword");
  if (!host || !issue.crossword) return;
  const puzzles = issue.crossword.puzzles || [issue.crossword];
  host.replaceChildren();
  puzzles.forEach(function (puzzle) { host.appendChild(renderPuzzle(puzzle)); });
}

function renderPuzzle(puzzle) {
  const rows = puzzle.grid;
  const numbers = {};
  let n = 1;
  function white(r, c) {
    return rows[r] && rows[r][c] && rows[r][c] !== "#";
  }
  rows.forEach(function (row, r) {
    for (let c = 0; c < row.length; c++) {
      if (!white(r, c)) continue;
      const startA = (!white(r, c - 1)) && white(r, c + 1);
      const startD = (!white(r - 1, c)) && white(r + 1, c);
      if (startA || startD) numbers[r + "," + c] = n++;
    }
  });
  const grid = document.createElement("div");
  grid.className = "xw-grid";
  grid.style.gridTemplateColumns = "repeat(" + rows[0].length + ", 1fr)";
  rows.forEach(function (row, r) {
    for (let c = 0; c < row.length; c++) {
      const wrap = document.createElement("div");
      wrap.className = "cell";
      if (!white(r, c)) {
        const blk = document.createElement("span");
        blk.className = "blk";
        wrap.appendChild(blk);
      } else {
        if (numbers[r + "," + c]) {
          const num = document.createElement("span");
          num.className = "num";
          num.textContent = numbers[r + "," + c];
          wrap.appendChild(num);
        }
        const input = document.createElement("input");
        input.maxLength = 1;
        input.inputMode = "text";
        input.autocomplete = "off";
        input.setAttribute("aria-label", "Row " + (r + 1) + " column " + (c + 1));
        input.dataset.answer = row[c];
        input.addEventListener("input", function () {
          input.value = input.value.toUpperCase().slice(0, 1);
        });
        wrap.appendChild(input);
      }
      grid.appendChild(wrap);
    }
  });
  const clues = document.createElement("div");
  clues.className = "clue-cols";
  ["across", "down"].forEach(function (dir) {
    const col = document.createElement("div");
    col.innerHTML = "<h3>" + dir[0].toUpperCase() + dir.slice(1) + "</h3><ol>" +
      puzzle.clues[dir].map(function (clue) {
        return "<li value='" + clue.n + "'>" + esc(clue.clue) + "</li>";
      }).join("") + "</ol>";
    clues.appendChild(col);
  });
  const controls = document.createElement("p");
  controls.className = "cta-row";
  const check = document.createElement("button");
  check.type = "button";
  check.className = "btn btn-small";
  check.textContent = "Check puzzle";
  const reveal = document.createElement("button");
  reveal.type = "button";
  reveal.className = "btn btn-small btn-ghost";
  reveal.textContent = "Reveal sample answers";
  const msg = document.createElement("p");
  msg.setAttribute("role", "status");
  check.addEventListener("click", function () {
    let wrong = 0;
    let filled = 0;
    grid.querySelectorAll("input").forEach(function (input) {
      if (!input.value) return;
      filled++;
      input.style.outline = input.value.toUpperCase() === input.dataset.answer ? "2px solid #2c7f7b" : "2px solid #a33b28";
      if (input.value.toUpperCase() !== input.dataset.answer) wrong++;
    });
    msg.textContent = filled ? (wrong ? wrong + " letters do not match the sample." : "Those letters match the sample.") : "Type a few letters first.";
  });
  reveal.addEventListener("click", function () {
    grid.querySelectorAll("input").forEach(function (input) { input.value = input.dataset.answer; });
    msg.textContent = "Sample answers revealed.";
  });
  controls.append(check, reveal);
  const section = document.createElement("section");
  section.className = "xw";
  const heading = document.createElement("h3");
  heading.textContent = puzzle.title || "Puzzle";
  section.append(heading, grid, clues, controls, msg);
  return section;
}

function renderCenterfold(issue, index, total, mode, face) {
  const data = issue.walkingMap || {};
  const mapId = "centerfold-map";
  const qrId = "centerfold-qr";
  const sheet = window.FWDWalk
    ? window.FWDWalk.sheetHtml(data, { mode: mode, mapId: mapId, qrId: qrId, face: face || "front" })
    : "<p>The walking map did not load.</p>";
  const rightNo = mode === "spread" ? (index + 2) : (index + 1);
  const label = face === "back" ? "visitor guide" : "walking map";
  return (
    '<article class="leaf centerfold face-' + (face === "back" ? "back" : "front") + '">' + sheet +
    '<p class="page-no"><span>' + esc(issue.issue.name) + " · " + label + "</span><span>" +
    (index + 1) + (mode === "spread" ? "–" + rightNo : "") + " / " + total + "</span></p></article>"
  );
}

function mountCenterfold(issue, face) {
  if (!window.FWDWalk || !issue.walkingMap) return;
  const host = document.getElementById("centerfold-map");
  if (!host || typeof L === "undefined") {
    if (host) host.textContent = "The map library did not load.";
    return;
  }
  const data = issue.walkingMap;
  let view;
  if (face === "back") {
    const inset = data.inset || {};
    view = window.FWDWalk.mountMap(host, data, {
      interactive: true,
      scrollWheelZoom: false,
      grid: false,
      bounds: inset.bounds,
      places: window.FWDWalk.placesInBounds(data.places, inset.bounds),
      padding: [16, 16]
    });
  } else {
    view = window.FWDWalk.mountMap(host, data, {
      interactive: true,
      scrollWheelZoom: false,
      grid: true,
      padding: [18, 18]
    });
    window.FWDWalk.drawQr("centerfold-qr");
  }
  window.FWDWalk.drawQrSlots(document.getElementById("book"));
  if (view) setTimeout(view.settle, 400);
}

function drawAudioQr() {
  const box = document.getElementById("audio-qr");
  if (!box || typeof QRCode === "undefined") return;
  const base = String((window.FWD_CONFIG || {}).SITE_BASE || "").replace(/\/$/, "");
  const url = (base || location.href.replace(/[^/]*$/, "")) + "/audio.html";
  box.innerHTML = "";
  new QRCode(box, { text: url, width: 140, height: 140, correctLevel: QRCode.CorrectLevel.M });
}

async function boot() {
  const book = document.getElementById("book");
  const status = document.getElementById("reader-status");
  let issue;
  try {
    const response = await fetch("data/issue1.json");
    if (!response.ok) throw new Error("Could not load issue data");
    issue = await response.json();
  } catch (err) {
    status.textContent = "The issue file did not load. Check data/issue1.json.";
    return;
  }
  const pages = issue.pages;
  let index = 0;
  const spreadQuery = window.matchMedia("(min-width: 980px)");
  const requested = Number(new URLSearchParams(location.search).get("page"));
  if (requested >= 1 && requested <= pages.length) index = requested - 1;

  function viewStart(i) {
    const last = pages.length - 1;
    const n = Math.max(0, Math.min(last, i));
    if (!spreadQuery.matches || n === 0) return n;
    if (n === last && last % 2 === 1) return last;
    return n % 2 === 0 ? n - 1 : n;
  }

  function viewCount(start) {
    if (!spreadQuery.matches || start === 0) return 1;
    if (start >= pages.length - 1) return 1;
    return 2;
  }

  function nextStart(start) {
    if (!spreadQuery.matches) return Math.min(pages.length - 1, start + 1);
    if (start === 0) return pages.length > 1 ? 1 : 0;
    const n = start + 2;
    if (n >= pages.length) return start;
    return n;
  }

  function prevStart(start) {
    if (!spreadQuery.matches) return Math.max(0, start - 1);
    if (start <= 1) return 0;
    return start - 2;
  }

  function paint(animate) {
    const count = viewCount(index);
    const slice = pages.slice(index, index + count);
    const faceOf = function (page) { return (page && page.face) || "front"; };
    const centerSpread = count === 2 && slice[0].kind === "centerfold" && slice[1].kind === "centerfold" && faceOf(slice[0]) === faceOf(slice[1]);
    const centerSingle = count === 1 && slice[0] && slice[0].kind === "centerfold";
    const face = (centerSpread || centerSingle) ? faceOf(slice[0]) : "";
    book.classList.toggle("spread", count === 2 && !centerSpread);
    book.classList.toggle("center-open", centerSpread || centerSingle);
    if (centerSpread) book.innerHTML = renderCenterfold(issue, index, pages.length, "spread", face);
    else if (centerSingle) book.innerHTML = renderCenterfold(issue, index, pages.length, "spread", face);
    else {
      book.innerHTML = slice.map(function (page, offset) {
        return renderPage(issue, page, index + offset, pages.length);
      }).join("");
    }
    if (animate && !REDUCED) {
      book.querySelectorAll(".leaf").forEach(function (leaf) {
        leaf.classList.add("turning");
        leaf.addEventListener("animationend", function () { leaf.classList.remove("turning"); }, { once: true });
      });
    }
    const end = index + slice.length;
    document.getElementById("page-label").textContent = (slice.length > 1 ? "Pages " : "Page ") +
      (index + 1) + (slice.length > 1 ? "–" + end : "") + " of " + pages.length +
      (face === "back" ? " · visitor guide" : (face === "front" ? " · walking map" : ""));
    document.getElementById("prev-page").disabled = index === 0;
    document.getElementById("next-page").disabled = nextStart(index) === index;
    buildCrossword(issue);
    drawAudioQr();
    if (centerSpread || centerSingle) mountCenterfold(issue, face);
    const live = document.getElementById("reader-live");
    live.textContent = face === "back" ? "Falmouth Visitor Guide" : (face === "front" ? "Walking map centerfold" : slice.map(function (page) { return page.title || "Cover"; }).join(" and "));
  }

  function go(delta) {
    const aligned = delta < 0 ? prevStart(index) : nextStart(index);
    if (aligned === index) return;
    index = aligned;
    paint(true);
  }

  document.getElementById("prev-page").addEventListener("click", function () { go(-1); });
  document.getElementById("next-page").addEventListener("click", function () { go(1); });
  document.addEventListener("keydown", function (event) {
    if (event.target.matches("input, textarea, select")) return;
    if (event.key === "ArrowRight") go(1);
    if (event.key === "ArrowLeft") go(-1);
  });
  let touchX = null;
  book.addEventListener("touchstart", function (event) { touchX = event.changedTouches[0].clientX; }, { passive: true });
  book.addEventListener("touchend", function (event) {
    if (touchX == null) return;
    const dx = event.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1);
    touchX = null;
  }, { passive: true });
  spreadQuery.addEventListener("change", function () { index = viewStart(index); paint(false); });

  const dialog = document.getElementById("toc-dialog");
  const list = document.getElementById("toc-jump");
  list.innerHTML = pages.map(function (page, i) {
    return '<button type="button" data-i="' + i + '">' + (i + 1) + ". " + esc(page.title || "Cover") + "</button>";
  }).join("");
  list.addEventListener("click", function (event) {
    const button = event.target.closest("button");
    if (!button) return;
    index = viewStart(Number(button.dataset.i));
    dialog.close();
    paint(false);
  });
  document.getElementById("open-toc").addEventListener("click", function () { dialog.showModal(); });
  index = viewStart(index);
  paint(false);
  status.textContent = "";
}

boot();
