function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 48);
}

function posterUrl(slug) {
  const base = String((window.FWD_CONFIG || {}).SITE_BASE || "https://healthandwellnessmaps.com/magazine").replace(/\/$/, "");
  const loc = slug || "your-counter";
  return base + "/signup.html?loc=" + encodeURIComponent(loc);
}

function draw() {
  const slug = slugify(document.getElementById("loc-slug").value);
  const name = document.getElementById("loc-name").value.trim() || "Our counter";
  document.getElementById("poster-place").textContent = name;
  const url = posterUrl(slug || "your-counter");
  document.getElementById("poster-url").textContent = url;
  const box = document.getElementById("poster-qr");
  box.innerHTML = "";
  if (typeof QRCode === "undefined") {
    box.textContent = url;
    return;
  }
  new QRCode(box, { text: url, width: 220, height: 220, correctLevel: QRCode.CorrectLevel.M });
}

const params = new URLSearchParams(location.search);
const initial = params.get("loc") || "";
document.getElementById("loc-slug").value = slugify(initial);
if (initial) document.getElementById("loc-name").value = initial.replace(/-/g, " ");
document.getElementById("poster-form").addEventListener("input", draw);
document.getElementById("print-poster").addEventListener("click", function () { window.print(); });
draw();
