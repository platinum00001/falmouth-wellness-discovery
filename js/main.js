(function () {
  const cfg = window.FWD_CONFIG || {};
  const base = String(cfg.SITE_BASE || "").replace(/\/$/, "");
  const path = (document.body.dataset.path || "").replace(/^\//, "");
  if (base) {
    const url = path ? base + "/" + path : base + "/";
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) canonical.href = url;
    const og = document.querySelector('meta[property="og:url"]');
    if (og) og.setAttribute("content", url);
    document.querySelectorAll("[data-abs-img]").forEach(function (node) {
      const rel = node.getAttribute("data-abs-img");
      if (rel) node.setAttribute("content", base + "/" + rel.replace(/^\//, ""));
    });
  }

  const btn = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      const open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", open ? "false" : "true");
      nav.classList.toggle("is-open", !open);
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        btn.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      });
    });
  }
})();

(function () {
  /* subtle reveal-on-scroll for elements marked .reveal */
  const els = document.querySelectorAll(".reveal");
  if (!els.length) return;
  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    els.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  document.documentElement.classList.add("js-reveal");
  const io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { entry.target.classList.add("in"); io.unobserve(entry.target); }
    });
  }, { rootMargin: "0px 0px -8% 0px" });
  els.forEach(function (el) { io.observe(el); });
  /* never leave content hidden: reveal everything after a short grace period */
  setTimeout(function () { els.forEach(function (el) { el.classList.add("in"); }); }, 2500);
})();
