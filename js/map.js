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
  "dry-cleaner": "#c43d78",
  nutrition: "#e07a2f",
  "spa-recovery": "#1c5a5e",
  dental: "#18343d",
  "getting-around": "#18343d",
  shops: "#c98a3d"
};

const AREAS = {
  homeport: { label: "Homeport", center: [41.5626, -70.6104], radius: 190 },
  "main-street": { label: "Main Street", center: [41.5521, -70.6145], radius: 0 }
};

const PIN_BY_ID = {
  "cape-island-cafe": "#e07a2f"
};

function fmtPhone(p) {
  const d = String(p || "").replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
  return d.length === 10 ? "(" + d.slice(0, 3) + ") " + d.slice(3, 6) + "-" + d.slice(6) : String(p || "");
}

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
  // Main Street and Homeport first, then everything else (placeholders are not mapped).
  const rank = function (item) { return item.district === "homeport" ? 0 : item.district === "main-street" ? 1 : 2; };
  for (let i = listings.length - 1; i >= 0; i--) if (listings[i].placeholder) listings.splice(i, 1);
  listings.sort(function (a, b) { return rank(a) - rank(b); });

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

  function isPin(item) {
    return Boolean(numbers[item.id]) || item.id === "cape-island-cafe" || item.placeholder;
  }

  function icon(item) {
    const color = walkColor[item.id] || PIN_BY_ID[item.id] || COLORS[item.category] || "#18343d";
    const extra = item.id === "cape-island-cafe" ? " is-focus" : "";
    return window.FWDWalk.pinIcon(color, numbers[item.id] || "", extra);
  }

  function popup(item) {
    const bits = ["<strong>" + esc(item.name) + "</strong>", "<div>" + esc(item.categoryName || item.category) + "</div>", "<p>" + esc(item.summary || "") + "</p>"];
    if (item.district) bits.push('<p class="pop-area">' + (item.district === "homeport" ? "Homeport" : "Main Street") + "</p>");
    if (item.address) bits.push("<p>" + esc(item.address) + "</p>");
    if (item.phone) bits.push('<p><a href="tel:' + esc(String(item.phone).replace(/[^+\d]/g, "")) + '">' + esc(fmtPhone(item.phone)) + "</a></p>");
    if (item.website) bits.push('<p><a href="' + esc(item.website) + '" target="_blank" rel="noopener">Website</a></p>');
    if (!item.placeholder && item.category) {
      bits.push('<p><a href="' + esc(item.category) + '/">Open the ' + esc(item.categoryName || "category") + " page</a></p>");
    }
    if (item.approximate) bits.push("<p>Main Street position is approximate.</p>");
    if (spots[item.id] && spots[item.id].moved) bits.push("<p>The pin is shifted so it stays readable. The dot is the mapped address.</p>");
    return bits.join("");
  }

  listings.forEach(function (item) {
    if (item.lat == null || item.lng == null) return;
    if (!isPin(item)) {
      // Directory-only listings: a small dot at the mapped address, so the numbered walk pins stay readable.
      const local = item.district === "homeport" || item.district === "main-street";
      const dot = L.circleMarker([item.lat, item.lng], {
        radius: local ? 8 : 5,
        weight: local ? 3 : 2,
        color: "#fffdf9",
        fillColor: COLORS[item.category] || "#18343d",
        fillOpacity: 0.95
      });
      dot.bindPopup(popup(item));
      dot.bindTooltip(item.name, { direction: "top" });
      dot.item = item;
      markers.push(dot);
      return;
    }
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
      return item.lat != null && item.lng != null && active.has(item.category) && isPin(item);
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
        (item.district === "homeport" ? " · Homeport" : item.district === "main-street" ? " · Main Street" : "") + "</small>";
      if (item.district) button.classList.add("is-local");
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

  // Homeport and Main Street emphasis
  const hp = AREAS.homeport;
  L.circle(hp.center, { radius: hp.radius, color: "#e07a2f", weight: 2, dashArray: "6 6", fillColor: "#f4a259", fillOpacity: 0.12, interactive: false }).addTo(map);
  L.marker([hp.center[0] + 0.0021, hp.center[1]], { interactive: false, icon: L.divIcon({ className: "area-label", html: "<span>Homeport</span>", iconSize: [110, 24], iconAnchor: [55, 12] }) }).addTo(map);
  L.marker([41.5508, -70.6150], { interactive: false, icon: L.divIcon({ className: "area-label is-main", html: "<span>Main Street</span>", iconSize: [120, 24], iconAnchor: [60, 12] }) }).addTo(map);
  function showArea(key) {
    const pts = listings.filter(function (item) { return item.district === key && item.lat != null; }).map(function (item) { return [item.lat, item.lng]; });
    if (!pts.length) return;
    map.fitBounds(L.latLngBounds(pts), { padding: [40, 40], maxZoom: 17, animate: true });
    layoutPins();
  }
  document.querySelectorAll("[data-area]").forEach(function (btn) {
    btn.addEventListener("click", function () { showArea(btn.dataset.area); });
  });

  const params = new URLSearchParams(location.search);
  const preset = params.get("cat") || (location.hash || "").replace("#", "");
  if (preset && COLORS[preset]) {
    active.clear();
    active.add(preset);
    document.querySelectorAll("#legend input").forEach(function (input) {
      input.checked = input.dataset.cat === preset;
    });
  }
  render();
  const area = params.get("area");
  const start = function () { if (area && AREAS[area]) showArea(area); else showDowntown(); };
  start();
  setTimeout(function () { map.invalidateSize(); start(); }, 200);
  status.textContent = "Orange pin: Cape Island Café at Homeport, 316 Gifford St. Larger dots are Main Street and Homeport businesses; small dots are other directory listings. Tap any pin or dot for details.";
}

bootMap();
