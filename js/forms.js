const UPPER_CAPE = [
  "Falmouth",
  "East Falmouth",
  "North Falmouth",
  "West Falmouth",
  "Woods Hole",
  "Hatchville",
  "Teaticket",
  "Waquoit",
  "Falmouth Heights",
  "Mashpee",
  "New Seabury",
  "Popponesset",
  "Bourne",
  "Pocasset",
  "Cataumet",
  "Monument Beach",
  "Buzzards Bay",
  "Sagamore",
  "Sagamore Beach",
  "Sandwich",
  "East Sandwich",
  "Forestdale"
];

const LOCAL_READERS = "fwd-reader-signups";
const LOCAL_PARTNERS = "fwd-partner-inquiries";
const SESSION_READER = "fwd-reader";

function cfg() {
  return window.FWD_CONFIG || {};
}

function isConfigured() {
  const c = cfg();
  return Boolean(String(c.SUPABASE_URL || "").trim() && String(c.SUPABASE_ANON_KEY || "").trim());
}

function storeLocal(key, row) {
  const current = JSON.parse(localStorage.getItem(key) || "[]");
  current.push(row);
  localStorage.setItem(key, JSON.stringify(current));
}

async function insertRow(table, row) {
  if (!isConfigured()) return { ok: true, mode: "local" };
  try {
    const { createClient } = await import("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.49.1/+esm");
    const client = createClient(cfg().SUPABASE_URL, cfg().SUPABASE_ANON_KEY, {
      auth: { persistSession: false, autoRefreshToken: false },
      global: { headers: { Prefer: "return=minimal" } }
    });
    const { error } = await client.from(table).insert(row);
    if (error) return { ok: false, mode: "error", message: error.message };
    return { ok: true, mode: "remote" };
  } catch (err) {
    return { ok: false, mode: "error", message: err && err.message ? err.message : "Network error" };
  }
}

function show(el, message, kind) {
  if (!el) return;
  el.hidden = false;
  el.className = kind === "error" ? "error" : "success";
  el.textContent = message;
}

function emailOk(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function initReaderForm() {
  const form = document.getElementById("reader-form");
  if (!form) return;
  const params = new URLSearchParams(location.search);
  const loc = (params.get("loc") || "").trim();
  const locInput = form.querySelector('[name="partner_location"]');
  const locNote = document.getElementById("loc-note");
  if (locInput && loc) locInput.value = loc;
  if (locNote && loc) {
    locNote.hidden = false;
    locNote.textContent = "This sign-up is tagged to the counter card: " + loc + ".";
  }
  const deliveryInputs = form.querySelectorAll('input[name="delivery"]');
  const addressBlock = document.getElementById("print-address");
  function syncAddress() {
    const print = form.querySelector('input[name="delivery"]:checked')?.value === "print";
    addressBlock.hidden = !print;
    addressBlock.querySelectorAll("input, select").forEach(function (field) {
      if (field.name === "postal_code") return;
      field.required = print;
    });
  }
  deliveryInputs.forEach(function (input) { input.addEventListener("change", syncAddress); });
  syncAddress();

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const status = document.getElementById("form-status");
    const data = new FormData(form);
    if (String(data.get("company_website") || "").trim()) {
      show(status, "You are signed up.", "success");
      return;
    }
    const fullName = String(data.get("full_name") || "").trim();
    const email = String(data.get("email") || "").trim();
    const delivery = String(data.get("delivery") || "");
    const street = String(data.get("street_address") || "").trim();
    const city = String(data.get("city") || "").trim();
    const postal = String(data.get("postal_code") || "").trim();
    const interests = data.getAll("interests").map(String);
    const consent = data.get("consent") === "yes";
    if (!fullName || !emailOk(email) || (delivery !== "digital" && delivery !== "print") || !consent) {
      show(status, "Add your name, a real email, digital or print, and consent.", "error");
      return;
    }
    if (delivery === "print") {
      if (!street || !UPPER_CAPE.includes(city)) {
        show(status, "Print copies go to Falmouth and the Upper Cape. Add a street address and choose a town from the list.", "error");
        return;
      }
    }
    const row = {
      full_name: fullName,
      email: email,
      delivery: delivery,
      street_address: delivery === "print" ? street : null,
      city: delivery === "print" ? city : null,
      postal_code: delivery === "print" && postal ? postal : null,
      partner_location: String(data.get("partner_location") || "").trim() || null,
      interests: interests,
      consent: true,
      user_agent: navigator.userAgent.slice(0, 240)
    };
    const button = form.querySelector('[type="submit"]');
    button.disabled = true;
    const result = await insertRow("magazine_reader_signups", row);
    if (!result.ok) {
      storeLocal(LOCAL_READERS, row);
      button.disabled = false;
      show(status, "We could not reach the signup inbox (" + result.message + "). A copy is saved in this browser. Please try again later.", "error");
      return;
    }
    if (result.mode === "local") storeLocal(LOCAL_READERS, row);
    const pass = {
      name: fullName,
      email: email,
      delivery: delivery,
      interests: interests,
      loc: row.partner_location || "",
      at: new Date().toISOString(),
      mode: result.mode
    };
    sessionStorage.setItem(SESSION_READER, JSON.stringify(pass));
    location.href = "perk.html";
  });
}

function initPartnerForm() {
  const form = document.getElementById("partner-form");
  if (!form) return;
  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const status = document.getElementById("form-status");
    const data = new FormData(form);
    if (String(data.get("company_website") || "").trim()) {
      show(status, "Thanks. We have your inquiry.", "success");
      return;
    }
    const row = {
      business_name: String(data.get("business_name") || "").trim(),
      contact_name: String(data.get("contact_name") || "").trim(),
      email: String(data.get("email") || "").trim(),
      phone: String(data.get("phone") || "").trim() || null,
      category: String(data.get("category") || "").trim() || null,
      package: String(data.get("package") || "").trim() || null,
      gift_cards: data.get("gift_cards") === "yes",
      message: String(data.get("message") || "").trim() || null,
      consent: data.get("consent") === "yes",
      user_agent: navigator.userAgent.slice(0, 240)
    };
    if (!row.business_name || !row.contact_name || !emailOk(row.email) || !row.consent) {
      show(status, "Add the business, a contact name, a real email, and consent.", "error");
      return;
    }
    const button = form.querySelector('[type="submit"]');
    button.disabled = true;
    const result = await insertRow("magazine_partner_inquiries", row);
    if (!result.ok) {
      storeLocal(LOCAL_PARTNERS, row);
      button.disabled = false;
      show(status, "We could not reach the inquiry inbox (" + result.message + "). A copy is saved in this browser.", "error");
      return;
    }
    if (result.mode === "local") storeLocal(LOCAL_PARTNERS, row);
    form.hidden = true;
    const done = document.getElementById("inquiry-success");
    done.hidden = false;
    const localNote = result.mode === "local"
      ? " Saved on this device until the Supabase keys are added in config.js."
      : "";
    document.getElementById("inquiry-success-copy").textContent =
      "Thanks. Your inquiry is in." + localNote + " When you are ready to pay, use the Square checkout for the package you chose. Card numbers are never typed on this site.";
    if (window.FWD_mountSquare) window.FWD_mountSquare(row.package || "featured");
  });
}

initReaderForm();
initPartnerForm();
