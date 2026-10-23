const PACKAGES = {
  neighbor: { id: "neighbor", label: "Neighbor", cents: 25000, founding: 18800 },
  featured: { id: "featured", label: "Featured", cents: 50000, founding: 37500 },
  wellness: { id: "wellness", label: "Wellness Partner", cents: 75000, founding: 56300 },
  cover: { id: "cover", label: "Cover Partner", cents: 95000, founding: 71300 }
};

function money(cents) {
  const sign = cents < 0 ? "-" : "";
  const abs = Math.abs(cents);
  return sign + "$" + (abs / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function quote(id, founding, faceCents) {
  const plan = PACKAGES[id] || PACKAGES.featured;
  const bill = founding ? plan.founding : plan.cents;
  const fullBand = Math.round(bill * 0.25);
  const maxFace = Math.round(bill * 0.5);
  const face = Math.max(0, Math.min(Math.round(faceCents), maxFace));
  const fullPortion = Math.min(face, fullBand);
  const reducedPortion = Math.max(0, face - fullBand);
  const credit = fullPortion + Math.round(reducedPortion * 0.75);
  return {
    plan: plan,
    list: plan.cents,
    bill: bill,
    discount: plan.cents - bill,
    face: face,
    fullPortion: fullPortion,
    reducedPortion: reducedPortion,
    credit: credit,
    cash: bill - credit,
    maxFace: maxFace
  };
}

function squareUrl(id) {
  const links = (window.FWD_CONFIG && window.FWD_CONFIG.SQUARE_CHECKOUT) || {};
  return String(links[id] || "").trim();
}

function squareButton(id) {
  const url = squareUrl(id);
  const label = "Start subscription (Square checkout)";
  if (!url) {
    return (
      '<button type="button" class="btn btn-small" disabled>' + label + "</button>" +
      '<p class="square-help">Placeholder. Add the Square checkout link for this package in config.js. No card fields live on this site.</p>'
    );
  }
  return (
    '<a class="btn btn-small" href="' + url.replace(/"/g, "") + '" target="_blank" rel="noopener noreferrer">' + label + "</a>" +
    '<p class="square-help">Opens a secure Square checkout or invoice. Cancel terms are on that invoice. The 3-month founding term is proposed.</p>'
  );
}

function mountPackageButtons() {
  document.querySelectorAll("[data-square]").forEach(function (slot) {
    slot.innerHTML = squareButton(slot.getAttribute("data-square"));
  });
}

function mountSquare(id) {
  const slot = document.getElementById("success-square");
  if (!slot) return;
  const plan = PACKAGES[id] ? id : "featured";
  slot.innerHTML = "<h3>Next: " + PACKAGES[plan].label + "</h3>" + squareButton(plan);
}

window.FWD_mountSquare = mountSquare;

function initCalc() {
  const form = document.getElementById("calc");
  if (!form) return;
  const out = document.getElementById("calc-out");
  const faceInput = document.getElementById("gift-face");
  const range = document.getElementById("gift-range");
  const founding = document.getElementById("founding");

  function selected() {
    return form.querySelector('input[name="plan"]:checked')?.value || "featured";
  }

  function render() {
    const id = selected();
    const current = quote(id, founding.checked, Number(faceInput.value || 0) * 100);
    const maxDollars = current.maxFace / 100;
    faceInput.max = String(maxDollars);
    range.max = "50";
    if (Number(faceInput.value) > maxDollars) faceInput.value = maxDollars.toFixed(2);
    const q = quote(id, founding.checked, Number(faceInput.value || 0) * 100);
    const pct = q.bill ? Math.round((q.face / q.bill) * 100) : 0;
    range.value = String(Math.min(50, pct));
    out.innerHTML =
      "<div><dt>List price</dt><dd>" + money(q.list) + " / month</dd></div>" +
      "<div><dt>Founding discount</dt><dd>" + (founding.checked ? money(q.discount) + " off" : "$0.00") + "</dd></div>" +
      "<div><dt>Monthly bill</dt><dd>" + money(q.bill) + "</dd></div>" +
      "<div><dt>Gift card face value</dt><dd>" + money(q.face) + " (max " + money(q.maxFace) + ")</dd></div>" +
      "<div><dt>Credited at full value</dt><dd>" + money(q.fullPortion) + "</dd></div>" +
      "<div><dt>Credited at 75%</dt><dd>" + money(q.reducedPortion) + " face</dd></div>" +
      "<div><dt>Credit applied</dt><dd>" + money(q.credit) + "</dd></div>" +
      '<div class="due"><dt>Cash due this month</dt><dd>' + money(q.cash) + "</dd></div>";
  }

  form.addEventListener("input", function (event) {
    if (event.target === range) {
      const id = selected();
      const bill = quote(id, founding.checked, 0).bill;
      faceInput.value = ((bill * Number(range.value)) / 100 / 100).toFixed(2);
    }
    render();
  });
  document.getElementById("example-250")?.addEventListener("click", function () {
    form.querySelector('input[value="featured"]').checked = true;
    founding.checked = false;
    faceInput.value = "250.00";
    render();
  });
  document.getElementById("example-125")?.addEventListener("click", function () {
    form.querySelector('input[value="featured"]').checked = true;
    founding.checked = false;
    faceInput.value = "125.00";
    render();
  });
  render();
}

mountPackageButtons();
initCalc();
