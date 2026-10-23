/* Falmouth Wellness Discovery — public site config.
   SUPABASE_ANON_KEY holds the project's publishable key. It is meant to be public:
   the SQL in /sql (applied) lets the anon role INSERT only, with no read, update
   or delete. Never put the service-role or a secret key here.

   SITE_BASE is the one base-URL setting: canonical origin and folder, no trailing slash.
   QR codes and runtime canonical tags read it here. Static files (canonical tags,
   sitemap.xml, robots.txt, 404.html) are updated by running, after you change it:
   python3 scripts/set_site_base.py
*/
window.FWD_CONFIG = {
  SITE_BASE: "https://platinum00001.github.io/falmouth-wellness-discovery",
  SUPABASE_URL: "https://oiousqgzqcjanikglkxl.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_IJHa5taHcttV2DSZq45fWQ_bVbRDbA2",
  /* Secure Square checkout or invoice links. One URL per package.
     Leave blank until the Square links exist. The site never collects card numbers. */
  SQUARE_CHECKOUT: {
    neighbor: "",
    featured: "",
    wellness: "",
    cover: ""
  }
};
