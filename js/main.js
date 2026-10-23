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
