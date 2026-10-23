async function bootPrint() {
  const status = document.getElementById("print-status");
  const stack = document.getElementById("print-stack");
  if (!window.FWDWalk || typeof L === "undefined") {
    status.textContent = "The map library did not load.";
    return;
  }
  let issue;
  try {
    issue = await (await fetch("data/issue1.json")).json();
  } catch (err) {
    status.textContent = "The walking map did not load.";
    return;
  }
  const data = issue.walkingMap;
  if (!data) {
    status.textContent = "This issue has no walking map yet.";
    return;
  }

  const faces = [
    { face: "front", mapId: "print-map", qrId: "print-qr", label: "Front. Wellness map with partner boxes." },
    { face: "back", mapId: "print-inset", qrId: "", label: "Back. Falmouth Visitor Guide." }
  ];
  stack.innerHTML = faces.map(function (face) {
    return (
      '<article class="print-page" aria-label="' + face.label + '">' +
      window.FWDWalk.sheetHtml(data, {
        mode: "spread",
        print: true,
        face: face.face,
        mapId: face.mapId,
        qrId: face.qrId
      }) +
      "</article>"
    );
  }).join("");

  const front = window.FWDWalk.mountMap(document.getElementById("print-map"), data, {
    interactive: true,
    scrollWheelZoom: false,
    zoomControl: false,
    grid: true,
    padding: [16, 16]
  });
  const inset = data.inset || {};
  const back = window.FWDWalk.mountMap(document.getElementById("print-inset"), data, {
    interactive: true,
    scrollWheelZoom: false,
    zoomControl: false,
    grid: false,
    bounds: inset.bounds,
    places: window.FWDWalk.placesInBounds(data.places, inset.bounds),
    padding: [12, 12]
  });
  window.FWDWalk.drawQr("print-qr");
  window.FWDWalk.drawQrSlots(stack);
  const views = [front, back].filter(Boolean);

  const narrow = window.matchMedia("(max-width: 800px)");
  const stage = document.getElementById("fold-stage");
  function fit() {
    stack.querySelectorAll(".print-page").forEach(function (page) {
      const sheet = page.querySelector(".walk-sheet");
      if (!sheet) return;
      if (narrow.matches) {
        page.style.transform = "none";
        page.style.width = "100%";
        page.style.height = "auto";
        return;
      }
      page.style.width = "17in";
      const scale = Math.min(1, (stage.clientWidth - 8) / sheet.offsetWidth);
      page.style.transform = "scale(" + scale + ")";
      page.style.height = (sheet.offsetHeight * scale + 12) + "px";
    });
    views.forEach(function (view) { view.settle(); });
  }
  function restorePrint() {
    stack.querySelectorAll(".print-page").forEach(function (page) {
      page.style.transform = "none";
      page.style.width = "17in";
      page.style.height = "11in";
    });
    views.forEach(function (view) { view.settle(); });
  }
  window.addEventListener("resize", fit);
  document.getElementById("do-print").addEventListener("click", function () {
    restorePrint();
    window.print();
    fit();
  });
  window.addEventListener("beforeprint", restorePrint);
  window.addEventListener("afterprint", fit);
  fit();
  status.textContent = "Two 17×11 pages: the wellness map, then the visitor guide. Sample boxes are not real listings. A date says check date unless that date is printed.";
}

bootPrint();
