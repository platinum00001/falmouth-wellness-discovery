const PERKS = [
  {
    partner: "Cape Island Café",
    detail: "Sample only: a reader welcome at weekday lunch, 316 Gifford Street. Not a live discount until the café confirms one."
  },
  {
    partner: "Tanorama",
    detail: "Sample only: a reader note at 365 Main Street. Not a confirmed offer from Scott or the salon."
  },
  {
    partner: "Falmouth Transport",
    detail: "Sample only: a mention in the rides guide. No fare discount exists until Falmouth Transport publishes one."
  },
  {
    partner: "Featured partner (your business here)",
    detail: "Sample perk slot. Real offers are added only after a partner confirms the wording."
  }
];

const raw = sessionStorage.getItem("fwd-reader");
const locked = document.getElementById("perk-locked");
const card = document.getElementById("perk-card");
if (!raw) {
  locked.hidden = false;
  card.hidden = true;
} else {
  const reader = JSON.parse(raw);
  locked.hidden = true;
  card.hidden = false;
  document.getElementById("perk-name").textContent = reader.name || "Reader";
  document.getElementById("perk-meta").textContent =
    (reader.delivery === "print" ? "Print + digital" : "Digital") +
    (reader.interests && reader.interests.length ? " · " + reader.interests.join(", ") : "") +
    (reader.loc ? " · via " + reader.loc : "");
  document.getElementById("perk-list").innerHTML = PERKS.map(function (perk) {
    return "<article class='story-card'><p class='sample-watermark'>Sample perk</p><h3>" + perk.partner + "</h3><p>" + perk.detail + "</p></article>";
  }).join("");
}
document.getElementById("print-perk")?.addEventListener("click", function () { window.print(); });
