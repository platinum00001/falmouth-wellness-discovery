async function bootGuide() {
  const status = document.getElementById("guide-status");
  const lists = document.getElementById("guide-lists");
  if (!window.FWDWalk || typeof L === "undefined") {
    status.textContent = "The map library did not load.";
    return;
  }
  let issue;
  try {
    issue = await (await fetch("data/issue1.json")).json();
  } catch (err) {
    status.textContent = "The visitor guide did not load.";
    return;
  }
  const data = issue.walkingMap;
  if (!data || !data.guide) {
    status.textContent = "This issue has no visitor guide yet.";
    return;
  }
  lists.innerHTML = window.FWDWalk.sheetHtml(data, { mode: "web", face: "back", mapId: "inset-map" });
  const main = window.FWDWalk.mountMap(document.getElementById("guide-map"), data, {
    interactive: true,
    scrollWheelZoom: false,
    grid: true,
    padding: [24, 24]
  });
  const inset = data.inset || {};
  const close = window.FWDWalk.mountMap(document.getElementById("inset-map"), data, {
    interactive: true,
    scrollWheelZoom: false,
    grid: false,
    bounds: inset.bounds,
    places: window.FWDWalk.placesInBounds(data.places, inset.bounds),
    padding: [16, 16]
  });
  window.FWDWalk.drawQrSlots(lists);
  status.textContent = "Letters run west to east. Numbers run north to south. Off this sheet means the place is outside the map above.";
  setTimeout(function () {
    if (main) main.settle();
    if (close) close.settle();
  }, 250);
}

bootGuide();
