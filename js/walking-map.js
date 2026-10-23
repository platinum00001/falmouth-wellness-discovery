/* Shared Falmouth Wellness walking map: centerfold, print sheet, and pin style. */
(function (global) {
  const PILLARS = {
    mind: { label: "Mind", color: "#18343d" },
    body: { label: "Body", color: "#1c5a5e" },
    soul: { label: "Soul", color: "#c43d78" },
    "health-food": { label: "Health & Food", color: "#e07a2f" },
    town: { label: "Town desk", color: "#18343d" },
    stay: { label: "Stay", color: "#18343d" }
  };

  function esc(value) {
    return String(value ?? "").replace(/[&<>"]/g, function (ch) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch];
    });
  }

  function mapPageUrl() {
    const base = String((global.FWD_CONFIG || {}).SITE_BASE || "").replace(/\/$/, "");
    if (base) return base + "/map.html";
    try {
      return new URL("map.html", global.location.href).href;
    } catch (err) {
      return "map.html";
    }
  }

  function colorFor(place) {
    if (place && place.color) return place.color;
    const pillar = PILLARS[place && place.pillar];
    return pillar ? pillar.color : "#18343d";
  }

  function pinIcon(color, badge, extraClass) {
    const mark = badge == null || badge === "" ? "" : esc(badge);
    const cls = extraClass ? " " + extraClass : "";
    return L.divIcon({
      className: "leaflet-div-icon walk-icon",
      html: '<span class="walk-pin' + cls + '" style="--pin:' + esc(color) + '"><span class="head"></span><span class="walk-badge">' + mark + "</span></span>",
      iconSize: [32, 32],
      iconAnchor: [16, 30],
      popupAnchor: [0, -28]
    });
  }

  function legendItem(place) {
    const color = colorFor(place);
    const pillar = PILLARS[place.pillar];
    const pillarLabel = place.pillarLabel || (pillar ? pillar.label : "");
    const where = place.placeholder
      ? "Pick not confirmed. No pin until an address is real."
      : (place.address || "");
    const num = place.number ? esc(place.number) : "–";
    return (
      "<li>" +
      '<span class="legend-num" style="background:' + esc(color) + '">' + num + "</span>" +
      "<span><strong>" + esc(place.name) + "</strong>" +
      (pillarLabel ? "<small>" + esc(pillarLabel) + "</small>" : "") +
      (where ? "<small>" + esc(where) + "</small>" : "") +
      "</span></li>"
    );
  }

  const GRID_COLS = "ABCDEFGH";
  const GRID_ROWS = 6;

  function boundsOf(data) {
    const b = data && data.bounds;
    if (!b || b.length < 2) return null;
    return { south: b[0][0], west: b[0][1], north: b[1][0], east: b[1][1] };
  }

  function gridRef(lat, lng, data) {
    const box = boundsOf(data);
    if (!box || lat == null || lng == null) return "Off this sheet";
    if (lat < box.south || lat > box.north || lng < box.west || lng > box.east) return "Off this sheet";
    const c = Math.min(GRID_COLS.length - 1, Math.max(0, Math.floor(((lng - box.west) / (box.east - box.west)) * GRID_COLS.length)));
    const r = Math.min(GRID_ROWS - 1, Math.max(0, Math.floor(((box.north - lat) / (box.north - box.south)) * GRID_ROWS)));
    return GRID_COLS.charAt(c) + String(r + 1);
  }

  function absUrl(path) {
    const clean = String(path || "").replace(/^\//, "");
    const base = String((global.FWD_CONFIG || {}).SITE_BASE || "").replace(/\/$/, "");
    if (base) return base + "/" + clean;
    try { return new URL(clean, global.location.href).href; } catch (err) { return clean; }
  }

  function adTile(place) {
    const size = place.size || "small";
    const sample = place.placeholder ? " sample" : "";
    const line = place.placeholder
      ? "Sample. No pin until an address is confirmed."
      : (place.address || "");
    const qr = place.qr && !place.placeholder
      ? '<div class="mini-qr" data-qr="' + esc(absUrl(place.qr)) + '" title="QR to ' + esc(place.name) + '"></div>'
      : "";
    return (
      '<article class="ad-tile size-' + esc(size) + sample + '">' +
      '<span class="legend-num" style="background:' + esc(colorFor(place)) + '">' + esc(place.number) + "</span>" +
      "<div><strong>" + esc(place.name) + "</strong>" +
      "<p>" + esc(place.category || place.pillarLabel || (PILLARS[place.pillar] && PILLARS[place.pillar].label) || "") +
      (line ? " · " + esc(line) : "") + "</p></div>" + qr + "</article>"
    );
  }

  function frontHtml(data, opts) {
    const places = (data.places || []).slice().sort(function (a, b) { return a.number - b.number; });
    const mid = Math.ceil(places.length / 2);
    function tiles(list) {
      return list.map(adTile).join("");
    }
    const highlight = data.highlight || {};
    const beacon = (data.offsheet || [])[0];
    const beaconCard = beacon
      ? '<div class="walk-card beacon-card"><p class="kicker">North of this sheet</p><strong>' +
        esc(beacon.name) + "</strong><p>" + esc(beacon.address || "") +
        ". The arrow on the top edge of the map points that way.</p></div>"
      : "";
    const mode = opts.mode || "spread";
    return (
      '<div class="walk-sheet front-sheet mode-' + esc(mode) + (opts.print ? " is-print" : "") + '">' +
      '<i class="trim nw"></i><i class="trim ne"></i><i class="trim sw"></i><i class="trim se"></i>' +
      '<i class="fold-tick top"></i><i class="fold-tick bottom"></i>' +
      '<div class="front-frame">' +
      '<div class="ad-mid">' +
      '<div class="ad-side">' + tiles(places.slice(0, mid)) + "</div>" +
      '<div class="map-col">' +
      '<div class="walk-card title-card">' +
      '<p class="kicker">Front · pull out</p>' +
      "<h2>" + esc(data.title || "Falmouth Wellness Walking Map") + "</h2>" +
      '<div class="qr-row"><div class="walk-qr" id="' + esc(opts.qrId) + '" data-size="64"></div><p>' + esc(data.dek || "") + "</p></div>" +
      "</div>" +
      '<div class="map-well fwd-frame">' +
      '<div class="walk-map" id="' + esc(opts.mapId) + '" role="region" aria-label="Falmouth Wellness Walking Map"></div>' +
      '<div class="walk-fold" aria-hidden="true"><span class="top">Tear here</span><span class="bottom">Take me with you</span></div>' +
      "</div></div>" +
      '<div class="ad-side">' + tiles(places.slice(mid)) + "</div>" +
      "</div>" +
      '<div class="ad-row ad-bottom">' +
      '<div class="walk-card cafe-card cafe-inline"><p class="kicker">Orange pin</p><strong>' +
      esc(highlight.title || "Cape Island Cafe, 316 Gifford St") + "</strong><p>" +
      esc(highlight.text || "") + "</p></div>" + beaconCard + "</div>" +
      "</div></div>"
    );
  }

  function guideItem(item, data) {
    const ref = item.ref || gridRef(item.lat, item.lng, data);
    const qr = item.qr
      ? '<div class="mini-qr" data-qr="' + esc(absUrl(item.qr)) + '" title="QR to ' + esc(item.name) + '"></div>'
      : "";
    return (
      '<li id="' + esc(item.id) + '"><span class="grid-ref">' + esc(ref) + "</span><div><strong>" + esc(item.name) + "</strong>" +
      "<p>" + esc(item.detail || "") + "</p></div>" + qr + "</li>"
    );
  }

  function guideGroup(title, items, data) {
    return '<section><h3>' + esc(title) + "</h3><ul class=\"guide-list\">" +
      (items || []).map(function (item) { return guideItem(item, data); }).join("") + "</ul></section>";
  }

  function guideHtml(data, opts) {
    const guide = data.guide || {};
    const mode = opts.mode || "spread";
    const web = mode === "web";
    const insetNote = (data.inset && data.inset.dek) || "Main Street, closer in.";
    const head = web
      ? '<header class="guide-head"><h2>Places on that grid</h2><p>Each cell matches the letters and numbers on the map above. A code beside a name opens that place in this guide.</p></header>'
      : '<header class="guide-head"><p class="kicker">Back of the pull-out</p><h2>Falmouth Visitor Guide</h2><p>Grid letters run west to east (A–H) and numbers run north to south (1–6) on the map on the other side. Off this sheet means the place is outside that map. Dates say check date unless a published date is in hand.</p></header>';
    return (
      '<div class="walk-sheet guide-sheet mode-' + esc(mode) + (opts.print ? " is-print" : "") + '">' +
      (web ? "" : '<i class="trim nw"></i><i class="trim ne"></i><i class="trim sw"></i><i class="trim se"></i><i class="fold-tick top"></i><i class="fold-tick bottom"></i>') +
      '<div class="guide-frame">' +
      head +
      '<div class="guide-cols">' +
      "<div>" + guideGroup("Landmarks", guide.landmarks, data) + guideGroup("Museums and historic houses", guide.museums, data) + "</div>" +
      "<div>" + guideGroup("Trails and the bikeway", guide.trails, data) + guideGroup("Beaches", guide.beaches, data) + "</div>" +
      "<div>" + guideGroup("Seasonal events", guide.events, data) +
      '<section class="inset-block"><h3>' + esc((data.inset && data.inset.title) || "Main Street") + "</h3>" +
      '<div class="walk-map inset-map" id="' + esc(opts.mapId) + '" role="region" aria-label="Inset map"></div>' +
      "<p>" + esc(insetNote) + "</p></section></div>" +
      "</div></div></div>"
    );
  }

  function sheetHtml(data, opts) {
    opts = opts || {};
    if (opts.face === "back") return guideHtml(data, opts);
    return frontHtml(data, opts);
  }

  function placesInBounds(places, bounds) {
    return (places || []).filter(function (place) {
      if (place.lat == null || place.lng == null || place.placeholder) return false;
      if (!bounds) return true;
      return place.lat >= bounds[0][0] && place.lat <= bounds[1][0] &&
        place.lng >= bounds[0][1] && place.lng <= bounds[1][1];
    });
  }

  function drawGrid(map, data) {
    const box = boundsOf(data);
    if (!box || typeof L === "undefined") return;
    const line = { color: "#18343d", weight: 1, opacity: 0.38, interactive: false };
    let i;
    for (i = 1; i < GRID_COLS.length; i++) {
      const lng = box.west + ((box.east - box.west) * i) / GRID_COLS.length;
      L.polyline([[box.south, lng], [box.north, lng]], line).addTo(map);
    }
    for (i = 1; i < GRID_ROWS; i++) {
      const lat = box.north - ((box.north - box.south) * i) / GRID_ROWS;
      L.polyline([[lat, box.west], [lat, box.east]], line).addTo(map);
    }
    function tag(lat, lng, text) {
      L.marker([lat, lng], {
        interactive: false,
        keyboard: false,
        icon: L.divIcon({
          className: "grid-label",
          html: esc(text),
          iconSize: [18, 16],
          iconAnchor: [9, 8]
        })
      }).addTo(map);
    }
    for (i = 0; i < GRID_COLS.length; i++) {
      const lng = box.west + ((box.east - box.west) * (i + 0.5)) / GRID_COLS.length;
      const lat = box.north - (box.north - box.south) * 0.035;
      tag(lat, lng, GRID_COLS.charAt(i));
    }
    for (i = 0; i < GRID_ROWS; i++) {
      const lat = box.north - ((box.north - box.south) * (i + 0.5)) / GRID_ROWS;
      const lng = box.west + (box.east - box.west) * 0.02;
      tag(lat, lng, String(i + 1));
    }
  }

  function spreadLatLngs(points, bounds, map) {
    const box = boundsOf({ bounds: bounds });
    const out = {};
    function keep(point) {
      out[point.id] = { lat: point.lat, lng: point.lng, trueLat: point.lat, trueLng: point.lng, moved: false };
    }
    const list = points || [];
    const size = map && map.getSize ? map.getSize() : null;
    if (!box || !map || !size || size.x < 40 || size.y < 40 || typeof map.latLngToContainerPoint !== "function") {
      list.forEach(function (point) {
        if (point.lat == null || point.lng == null) return;
        keep(point);
      });
      return out;
    }
    const items = [];
    list.forEach(function (point, index) {
      if (point.lat == null || point.lng == null) return;
      if (point.lat < box.south || point.lat > box.north || point.lng < box.west || point.lng > box.east) {
        keep(point);
        return;
      }
      const pt = map.latLngToContainerPoint([point.lat, point.lng]);
      items.push({
        id: point.id,
        trueLat: point.lat,
        trueLng: point.lng,
        x: pt.x,
        y: pt.y,
        ox: pt.x,
        oy: pt.y,
        i: index
      });
    });
    // Icon boxes are 32px. Separate on the shorter axis until the boxes clear.
    const sep = 40;
    const maxShift = 150;
    const crowded = items.map(function () { return false; });
    let a;
    let b;
    for (a = 0; a < items.length; a++) {
      for (b = a + 1; b < items.length; b++) {
        if (Math.abs(items[a].x - items[b].x) < sep && Math.abs(items[a].y - items[b].y) < sep) {
          crowded[a] = true;
          crowded[b] = true;
        }
      }
    }
    let n;
    for (n = 0; n < 160; n++) {
      let changed = false;
      for (a = 0; a < items.length; a++) {
        for (b = a + 1; b < items.length; b++) {
          if (!crowded[a] && !crowded[b]) continue;
          let dx = items[b].x - items[a].x;
          let dy = items[b].y - items[a].y;
          const adx = Math.abs(dx);
          const ady = Math.abs(dy);
          if (adx >= sep || ady >= sep) continue;
          if (adx < 0.01 && ady < 0.01) {
            const ang = items[a].i * 1.7;
            dx = Math.cos(ang) * 0.3;
            dy = items[a].i % 2 === 0 ? 0.9 : -0.9;
          }
          const overlapX = sep - Math.abs(dx);
          const overlapY = sep - Math.abs(dy);
          let sx = 0;
          let sy = 0;
          let push;
          if (overlapX < overlapY - 2) {
            push = overlapX + 0.5;
            sx = dx >= 0 ? 1 : -1;
          } else {
            push = overlapY + 0.5;
            sy = dy > 0 ? 1 : (dy < 0 ? -1 : (items[b].i % 2 ? 1 : -1));
          }
          if (crowded[a] && crowded[b]) {
            items[a].x -= sx * push / 2;
            items[a].y -= sy * push / 2;
            items[b].x += sx * push / 2;
            items[b].y += sy * push / 2;
          } else if (crowded[a]) {
            items[a].x -= sx * push;
            items[a].y -= sy * push;
          } else {
            items[b].x += sx * push;
            items[b].y += sy * push;
          }
          changed = true;
        }
      }
      for (a = 0; a < items.length; a++) {
        if (!crowded[a]) continue;
        const item = items[a];
        const sdx = item.x - item.ox;
        const sdy = item.y - item.oy;
        const dist = Math.hypot(sdx, sdy);
        if (dist > maxShift) {
          item.x = item.ox + sdx / dist * maxShift;
          item.y = item.oy + sdy / dist * maxShift;
        }
        item.x = Math.max(20, Math.min(size.x - 20, item.x));
        item.y = Math.max(36, Math.min(size.y - 8, item.y));
      }
      if (!changed) break;
    }
    items.forEach(function (item) {
      const ll = map.containerPointToLatLng([item.x, item.y]);
      const shift = Math.hypot(item.x - item.ox, item.y - item.oy);
      out[item.id] = {
        lat: ll.lat,
        lng: ll.lng,
        trueLat: item.trueLat,
        trueLng: item.trueLng,
        moved: shift > 8
      };
    });
    return out;
  }

  function drawLeaders(map, spots, colorForId, layer) {
    const dest = layer || map;
    Object.keys(spots).forEach(function (id) {
      const spot = spots[id];
      if (!spot.moved) return;
      const color = colorForId ? colorForId(id) : "#18343d";
      const line = [[spot.trueLat, spot.trueLng], [spot.lat, spot.lng]];
      L.polyline(line, {
        color: "#fffdf9",
        weight: 5,
        opacity: 0.95,
        interactive: false
      }).addTo(dest);
      L.polyline(line, {
        color: "#18343d",
        weight: 2,
        opacity: 0.95,
        interactive: false
      }).addTo(dest);
      L.circleMarker([spot.trueLat, spot.trueLng], {
        radius: 3.5,
        color: color,
        weight: 2,
        fillColor: "#fffdf9",
        fillOpacity: 1,
        interactive: false
      }).addTo(dest);
    });
  }

  function drawEdgeArrows(map, data) {
    const box = boundsOf(data);
    if (!box) return;
    (data.offsheet || []).forEach(function (item) {
      if (item.lat == null || item.lng == null) return;
      const x = Math.max(0.08, Math.min(0.82, (item.lng - box.west) / (box.east - box.west)));
      const lng = box.west + x * (box.east - box.west);
      const lat = box.north - (box.north - box.south) * 0.045;
      const hangLeft = x > 0.62;
      const marker = L.marker([lat, lng], {
        interactive: true,
        keyboard: true,
        zIndexOffset: 500,
        icon: L.divIcon({
          className: "edge-icon",
          html: '<div class="edge-arrow"><span class="arrow" aria-hidden="true">↑</span><span>' + esc(item.name) + "</span></div>",
          iconSize: [168, 26],
          iconAnchor: hangLeft ? [158, 4] : [12, 4]
        }),
        title: item.name
      });
      marker.bindPopup("<strong>" + esc(item.name) + "</strong><p>" + esc(item.address || "") +
        ". North of this sheet.</p>");
      marker.addTo(map);
    });
  }

  function mountMap(container, data, opts) {
    opts = opts || {};
    if (!container || typeof L === "undefined") return null;
    const map = L.map(container, {
      scrollWheelZoom: !!opts.scrollWheelZoom,
      zoomControl: opts.zoomControl !== false,
      attributionControl: true,
      dragging: opts.interactive !== false,
      tap: opts.interactive !== false,
      keyboard: opts.interactive !== false,
      boxZoom: opts.interactive !== false,
      doubleClickZoom: opts.interactive !== false
    });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    const route = opts.route === false ? null : data.route;
    if (route && route.points && route.points.length > 1) {
      L.polyline(route.points, { color: "#fffdf9", weight: 9, opacity: 0.92, lineCap: "round" }).addTo(map);
      const line = L.polyline(route.points, {
        color: "#1c5a5e",
        weight: 4,
        opacity: 0.95,
        dashArray: "2 10",
        lineCap: "round"
      }).addTo(map);
      line.bindTooltip(route.label || "Suggested walk along Main Street", { sticky: true });
    }

    const markers = [];
    const places = opts.places || data.places || [];
    const fitBounds = opts.bounds || data.bounds;
    const pinLayer = L.layerGroup().addTo(map);

    function colorForId(id) {
      const place = places.filter(function (item) { return item.id === id; })[0];
      return colorFor(place || {});
    }

    function drawPins() {
      pinLayer.clearLayers();
      markers.length = 0;
      const spots = spreadLatLngs(places, fitBounds, map);
      drawLeaders(map, spots, colorForId, pinLayer);
      places.forEach(function (place) {
        if (place.lat == null || place.lng == null || place.placeholder) return;
        const spot = spots[place.id] || { lat: place.lat, lng: place.lng, moved: false };
        const extra = place.id === "cape-island-cafe" ? " is-focus" : "";
        const marker = L.marker([spot.lat, spot.lng], {
          icon: pinIcon(colorFor(place), place.number, extra),
          title: place.name,
          alt: place.name,
          keyboard: opts.interactive !== false,
          zIndexOffset: place.id === "cape-island-cafe" ? 400 : 0
        });
        let note = "";
        if (place.approximate) note += "<p>Main Street position is approximate.</p>";
        if (spot.moved) note += "<p>The pin is shifted so it stays readable. The dot is the mapped address.</p>";
        const popup = "<strong>" + esc(place.number) + ". " + esc(place.name) + "</strong><p>" +
          esc(place.address || "") + "</p>" + note;
        if (opts.interactive === false) marker.bindTooltip(place.number + ". " + place.name, { direction: "top" });
        else marker.bindPopup(popup);
        marker.addTo(pinLayer);
        marker.place = place;
        markers.push(marker);
      });
    }

    if (opts.grid !== false) drawGrid(map, data);
    if (opts.arrow !== false && !opts.bounds) drawEdgeArrows(map, data);
    const bounds = L.latLngBounds(opts.bounds || data.bounds);
    function settle() {
      map.invalidateSize();
      if (bounds.isValid()) map.fitBounds(bounds, { padding: opts.padding || [28, 28], animate: false });
      drawPins();
    }
    settle();
    requestAnimationFrame(settle);
    setTimeout(settle, 180);
    return { map: map, markers: markers, bounds: bounds, settle: settle };
  }

  function drawQr(id) {
    const box = document.getElementById(id);
    if (!box || typeof QRCode === "undefined") return;
    box.innerHTML = "";
    const size = Number(box.dataset.size) || 92;
    new QRCode(box, {
      text: mapPageUrl(),
      width: size,
      height: size,
      correctLevel: QRCode.CorrectLevel.M
    });
  }

  function drawQrSlots(root) {
    const scope = root || document;
    scope.querySelectorAll(".mini-qr[data-qr]").forEach(function (box) {
      if (box.dataset.drawn === "1" || typeof QRCode === "undefined") return;
      box.dataset.drawn = "1";
      const size = Number(box.dataset.size) || 64;
      new QRCode(box, {
        text: box.getAttribute("data-qr"),
        width: size,
        height: size,
        correctLevel: QRCode.CorrectLevel.L
      });
    });
  }

  global.FWDWalk = {
    PILLARS: PILLARS,
    esc: esc,
    colorFor: colorFor,
    pinIcon: pinIcon,
    mapPageUrl: mapPageUrl,
    gridRef: gridRef,
    placesInBounds: placesInBounds,
    spreadLatLngs: spreadLatLngs,
    drawLeaders: drawLeaders,
    drawEdgeArrows: drawEdgeArrows,
    sheetHtml: sheetHtml,
    mountMap: mountMap,
    drawGrid: drawGrid,
    drawQr: drawQr,
    drawQrSlots: drawQrSlots
  };
})(window);
