const COLORS = {
  transportation: "#18343d",
  "home-remodeling": "#18343d",
  doctors: "#18343d",
  food: "#e07a2f",
  fitness: "#1c5a5e",
  beauty: "#c43d78",
  hotels: "#18343d",
  golf: "#1c5a5e",
  community: "#18343d",
  bookstore: "#18343d",
  antiques: "#c43d78",
  florist: "#c43d78",
  "art-gallery": "#c43d78",
  thrift: "#c43d78",
  "music-lessons": "#18343d",
  "bike-shop": "#1c5a5e",
  "garden-center": "#1c5a5e",
  "local-market": "#e07a2f",
  bakery: "#e07a2f",
  "dry-cleaner": "#c43d78"
};

const PIN_BY_ID = {
  "cape-island-cafe": "#e07a2f"
};

function esc(value) {
  return String(value ?? "").replace(/[&<>"]/g, function (ch) {
    return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch];
  });
}

async function bootMap() {
  const status = document.getElementById("map-status");
  if (typeof L === "undefined" || !window.FWDWalk) {
    status.textContent = "The map library did not load.";
    return;
  }
  let data;
  let walking;
  try {
    const response = await fetch("data/directory.json");
    if (!response.ok) throw new Error("missing");
    data = await response.json();
    walking = await (await fetch("data/issue1.json")).json();
  } catch (err) {
    status.textContent = "The directory data did not load.";
    return;
  }
  const walk = (walking && walking.walkingMap) || {};
  const numbers = {};
  const walkColor = {};
  (walk.places || []).forEach(function (place) {
    if (!place.id) return;
    numbers[place.id] = place.number;
    walkColor[place.id] = place.color || window.FWDWalk.colorFor(place);
  });
  const downtown = L.latLngBounds(walk.bounds || [[41.5385, -70.629], [41.5735, -70.592]]);

  const listings = [];
  data.categories.forEach(function (cat) {
    (cat.listings || []).forEach(function (item) {
      listings.push(Object.assign({ category: cat.slug, categoryName: cat.short }, item));
    });
  });
  (data.mapOnly || []).forEach(function (item) { listings.push(item); });

  const map = L.map("discovery-map", { scrollWheelZoom: false });
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  if (walk.bounds) window.FWDWalk.drawGrid(map, walk);
  if (walk.route && walk.route.points) {
    L.polyline(walk.route.points, { color: "#fffdf9", weight: 9, opacity: 0.92 }).addTo(map);
    L.polyline(walk.route.points, {
      color: "#1c5a5e",
      weight: 4,
      opacity: 0.95,
      dashArray: "2 10",
      lineCap: "round"
    }).addTo(map).bindTooltip("Suggested walk along Main Street", { sticky: true });
  }

  const leaderLayer = L.layerGroup().addTo(map);
  let spots = {};
  if (walk.offsheet) window.FWDWalk.drawEdgeArrows(map, walk);

  const markers = [];
  const list = document.getElementById("pin-list");
  const active = new Set(Object.keys(COLORS));

  function icon(item) {
    const color = walkColor[item.id] || PIN_BY_ID[item.id] || COLORS[item.category] || "#18343d";
    const extra = item.id === "cape-island-cafe" ? " is-focus" : "";
    return window.FWDWalk.pinIcon(color, numbers[item.id] || "", extra);
  }

  function popup(item) {
    const bits = ["<strong>" + esc(item.name) + "</strong>", "<div>" + esc(item.categoryName || item.category) + "</div>", "<p>" + esc(item.summary || "") + "</p>"];
    if (item.address) bits.push("<p>" + esc(item.address) + "</p>");
    if (!item.placeholder && item.category) {
      bits.push('<p><a href="' + esc(item.category) + '/">Open the ' + esc(item.categoryName || "category") + " page</a></p>");
    }
    if (item.approximate) bits.push("<p>Main Street position is approximate.</p>");
    if (spots[item.id] && spots[item.id].moved) bits.push("<p>The pin is shifted so it stays readable. The dot is the mapped address.</p>");
    if (item.placeholder) bits.push("<p>Sample slot. No address is shown until a business confirms it.</p>");
    return bits.join("");
  }

  listings.forEach(function (item) {
    if (item.lat == null || item.lng == null) return;
    const marker = L.marker([item.lat, item.lng], {
      icon: icon(item),
      title: item.name,
      alt: item.name,
      zIndexOffset: item.id === "cape-island-cafe" ? 400 : 0
    });
    marker.bindPopup(popup(item));
    marker.item = item;
    markers.push(marker);
  });

  function layoutPins() {
    const visible = listings.filter(function (item) {
      return item.lat != null && item.lng != null && active.has(item.category);
    });
    spots = window.FWDWalk.spreadLatLngs(visible, walk.bounds || [[41.545, -70.632], [41.57, -70.59]], map);
    leaderLayer.clearLayers();
    window.FWDWalk.drawLeaders(map, spots, function (id) {
      const item = listings.filter(function (entry) { return entry.id === id; })[0] || {};
      return walkColor[id] || PIN_BY_ID[id] || COLORS[item.category] || "#18343d";
    }, leaderLayer);
    markers.forEach(function (marker) {
      const spot = spots[marker.item.id];
      if (!spot) return;
      marker.setLatLng([spot.lat, spot.lng]);
      marker.setPopupContent(popup(marker.item));
    });
  }

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
      const num = numbers[item.id] ? numbers[item.id] + ". " : "";
      button.innerHTML = esc(num + item.name) + "<small>" + esc(item.categoryName || item.category) +
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
      (COLORS[cat.slug] || "#18343d") + '"></span>' + esc(cat.short) + "</label>";
  }).join("");
  document.getElementById("legend").addEventListener("change", function (event) {
    const input = event.target;
    if (!input.dataset.cat) return;
    if (input.checked) active.add(input.dataset.cat);
    else active.delete(input.dataset.cat);
    render();
    layoutPins();
  });

  function showDowntown() {
    map.fitBounds(downtown, { padding: [24, 24], animate: false });
    layoutPins();
  }
  document.getElementById("zoom-main").addEventListener("click", showDowntown);
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
  showDowntown();
  setTimeout(function () { map.invalidateSize(); showDowntown(); }, 200);
  status.textContent = "Orange pin: Cape Island Cafe, 316 Gifford St. Pins that share a block are pulled apart, with a line back to the address. Beacon Gardens is north of the sheet, on Brick Kiln Road.";
}

bootMap();
