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
  let body = '<p class="kicker">' + esc(page.kicker || "Sample") + "</p><h2>" + esc(page.title) + "</h2>";
  if (page.dek) body += '<p class="dek">' + esc(page.dek) + "</p>";
  if (page.imageSlot) body += slotHtml(issue, page.imageSlot);
  if (page.lead) body += '<p class="drop">' + esc(page.lead) + "</p>";
  body += paras(page.paragraphs);
  if (page.pullquote) body += '<blockquote class="pull">' + esc(page.pullquote) + "</blockquote>";
  body += cardsHtml(page.cards);
  if (page.kind === "calendar") {
    body += (issue.events || []).map(function (event) {
      return '<article class="event"><p class="kicker">Sample</p><h3>' + esc(event.title) +
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

  function step() { return spreadQuery.matches ? 2 : 1; }

  function paint(animate) {
    const count = step();
    const slice = pages.slice(index, index + count);
    book.classList.toggle("spread", count === 2);
    book.innerHTML = slice.map(function (page, offset) {
      return renderPage(issue, page, index + offset, pages.length);
    }).join("");
    if (animate && !REDUCED) {
      book.querySelectorAll(".leaf").forEach(function (leaf) {
        leaf.classList.add("turning");
        leaf.addEventListener("animationend", function () { leaf.classList.remove("turning"); }, { once: true });
      });
    }
    document.getElementById("page-label").textContent = "Pages " + (index + 1) + "–" + (index + slice.length) + " of " + pages.length;
    document.getElementById("prev-page").disabled = index === 0;
    document.getElementById("next-page").disabled = index + count >= pages.length;
    buildCrossword(issue);
    drawAudioQr();
    const live = document.getElementById("reader-live");
    live.textContent = slice.map(function (page) { return page.title || "Cover"; }).join(" and ");
  }

  function go(delta) {
    const next = Math.max(0, Math.min(pages.length - 1, index + delta * step()));
    const aligned = spreadQuery.matches ? next - (next % 2) : next;
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
  spreadQuery.addEventListener("change", function () { index = index - (index % step()); paint(false); });

  const dialog = document.getElementById("toc-dialog");
  const list = document.getElementById("toc-jump");
  list.innerHTML = pages.map(function (page, i) {
    return '<button type="button" data-i="' + i + '">' + (i + 1) + ". " + esc(page.title || "Cover") + "</button>";
  }).join("");
  list.addEventListener("click", function (event) {
    const button = event.target.closest("button");
    if (!button) return;
    index = Number(button.dataset.i);
    if (spreadQuery.matches) index = index - (index % 2);
    dialog.close();
    paint(false);
  });
  document.getElementById("open-toc").addEventListener("click", function () { dialog.showModal(); });
  paint(false);
  status.textContent = "";
}

boot();
