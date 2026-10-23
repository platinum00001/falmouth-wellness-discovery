const COLORS = {
  transportation: "#1c5a5e",
  "home-remodeling": "#8a5a2a",
  doctors: "#4b7f9a",
  food: "#d9773b",
  fitness: "#2c7f7b",
  beauty: "#b7577b",
  hotels: "#a33b28",
  golf: "#3e5a61",
  community: "#18343d"
};

function esc(value) {
  return String(value ?? "").replace(/[&<>"]/g, function (ch) {
    return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch];
  });
}

async function bootMap() {
  const status = document.getElementById("map-status");
  if (typeof L === "undefined") {
    status.textContent = "The map library did not load.";
    return;
  }
  let data;
  try {
    const response = await fetch("data/directory.json");
    if (!response.ok) throw new Error("missing");
    data = await response.json();
  } catch (err) {
    status.textContent = "The directory data did not load.";
    return;
  }
  const listings = [];
  data.categories.forEach(function (cat) {
    (cat.listings || []).forEach(function (item) {
      listings.push(Object.assign({ category: cat.slug, categoryName: cat.short }, item));
    });
  });
  (data.mapOnly || []).forEach(function (item) { listings.push(item); });

  const map = L.map("discovery-map", { scrollWheelZoom: false }).setView([41.5518, -70.6148], 13);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  const markers = [];
  const list = document.getElementById("pin-list");
  const active = new Set(Object.keys(COLORS));

  function icon(color) {
    return L.divIcon({
      className: "leaflet-div-icon",
      html: '<span class="pin-dot" style="background:' + color + '"></span>',
      iconSize: [18, 18],
      iconAnchor: [9, 16]
    });
  }

  function popup(item) {
    const bits = ["<strong>" + esc(item.name) + "</strong>", "<div>" + esc(item.categoryName || item.category) + "</div>", "<p>" + esc(item.summary || "") + "</p>"];
    if (item.address) bits.push("<p>" + esc(item.address) + "</p>");
    if (!item.placeholder && item.category) {
      bits.push('<p><a href="' + esc(item.category) + '/">Open the ' + esc(item.categoryName || "category") + " page</a></p>");
    }
    if (item.placeholder) bits.push("<p>Sample slot. No address is shown until a business confirms it.</p>");
    return bits.join("");
  }

  listings.forEach(function (item) {
    if (item.lat == null || item.lng == null) return;
    const marker = L.marker([item.lat, item.lng], { icon: icon(COLORS[item.category] || "#1c5a5e"), title: item.name, alt: item.name });
    marker.bindPopup(popup(item));
    marker.item = item;
    markers.push(marker);
  });

  function render() {
    markers.forEach(function (marker) {
      if (active.has(marker.item.category)) marker.addTo(map);
      else marker.remove();
    });
    list.innerHTML = "";
    listings.forEach(function (item) {
      if (!active.has(item.category)) return;
      const button = document.createElement("button");
      button.type = "button";
      button.innerHTML = esc(item.name) + "<small>" + esc(item.categoryName || item.category) +
        (item.placeholder ? " · sample slot" : "") +
        (item.lat == null ? " · pin waiting on a confirmed address" : "") + "</small>";
      button.addEventListener("click", function () {
        const marker = markers.find(function (m) { return m.item.id === item.id; });
        if (!marker) return;
        map.setView(marker.getLatLng(), 16);
        marker.openPopup();
      });
      list.appendChild(button);
    });
  }

  document.getElementById("legend").innerHTML = data.categories.map(function (cat) {
    return '<label><input type="checkbox" checked data-cat="' + esc(cat.slug) + '"><span class="swatch" style="background:' +
      (COLORS[cat.slug] || "#1c5a5e") + '"></span>' + esc(cat.short) + "</label>";
  }).join("");
  document.getElementById("legend").addEventListener("change", function (event) {
    const input = event.target;
    if (!input.dataset.cat) return;
    if (input.checked) active.add(input.dataset.cat);
    else active.delete(input.dataset.cat);
    render();
  });

  document.getElementById("zoom-main").addEventListener("click", function () {
    map.setView([41.5521, -70.6142], 16);
  });
  document.getElementById("zoom-town").addEventListener("click", function () {
    map.setView([41.558, -70.62], 12);
  });

  const preset = new URLSearchParams(location.search).get("cat") || (location.hash || "").replace("#", "");
  if (preset && COLORS[preset]) {
    active.clear();
    active.add(preset);
    document.querySelectorAll("#legend input").forEach(function (input) {
      input.checked = input.dataset.cat === preset;
    });
  }
  render();
  status.textContent = "";
}

bootMap();
