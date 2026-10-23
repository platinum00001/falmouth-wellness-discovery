async function bootPrint() {
  const status = document.getElementById("print-status");
  if (typeof L === "undefined") {
    status.textContent = "The map library did not load.";
    return;
  }
  let data;
  try {
    data = await (await fetch("data/directory.json")).json();
  } catch (err) {
    status.textContent = "Directory data did not load.";
    return;
  }
  const listings = [];
  data.categories.forEach(function (cat) {
    cat.listings.forEach(function (item) {
      listings.push(Object.assign({ categoryName: cat.short }, item));
    });
  });
  (data.mapOnly || []).forEach(function (item) { listings.push(item); });

  const buckets = {
    top: document.getElementById("pockets-top"),
    bottom: document.getElementById("pockets-bottom"),
    left: document.getElementById("pockets-left"),
    right: document.getElementById("pockets-right")
  };
  const order = ["top", "right", "bottom", "left"];
  listings.forEach(function (item, i) {
    const pocket = document.createElement("article");
    pocket.className = "pocket";
    const text = function (value) {
      return String(value ?? "").replace(/[&<>]/g, function (ch) {
        return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[ch];
      });
    };
    pocket.innerHTML = '<p class="pk">' + (item.placeholder ? "Sample slot" : "Partner") + " · " + text(item.categoryName || "") +
      "</p><h3>" + text(item.name) + "</h3><p>" + text(item.address || "Address not confirmed") + "</p>";
    buckets[order[i % 4]].appendChild(pocket);
  });

  const map = L.map("print-map", { zoomControl: false, attributionControl: true }).setView([41.5522, -70.6145], 14);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap"
  }).addTo(map);
  listings.forEach(function (item) {
    if (item.lat == null) return;
    L.circleMarker([item.lat, item.lng], {
      radius: 6,
      color: "#1c5a5e",
      weight: 2,
      fillColor: "#e8684a",
      fillOpacity: 0.9
    }).addTo(map).bindTooltip(item.name);
  });

  function fit() {
    const stage = document.getElementById("fold-stage");
    const fold = document.getElementById("fold");
    if (window.matchMedia("(max-width: 800px)").matches) {
      fold.style.transform = "none";
      stage.style.height = "auto";
      map.invalidateSize();
      return;
    }
    const scale = Math.min(1, (stage.clientWidth - 8) / fold.offsetWidth);
    fold.style.transform = "scale(" + scale + ")";
    stage.style.height = (fold.offsetHeight * scale + 8) + "px";
    map.invalidateSize();
  }
  window.addEventListener("resize", fit);
  document.getElementById("do-print").addEventListener("click", function () {
    document.getElementById("fold").style.transform = "none";
    window.print();
    fit();
  });
  fit();
  status.textContent = "";
}

bootPrint();
