/* Falmouth Wellness Discovery — public site config.
   Fill in the blanks locally. Do not commit real keys.
   The anon key is meant to be public only after the SQL in /sql is applied
   (anonymous insert, no public read). Never put the service-role key here.

   SITE_BASE is the canonical origin and folder, with no trailing slash.
   Category pages bake this into canonical tags. After you change it, run:
   python3 scripts/build_directory.py
*/
window.FWD_CONFIG = {
  SITE_BASE: "https://healthandwellnessmaps.com/magazine",
  SUPABASE_URL: "",
  SUPABASE_ANON_KEY: "",
  /* Secure Square checkout or invoice links. One URL per package.
     Leave blank until the Square links exist. The site never collects card numbers. */
  SQUARE_CHECKOUT: {
    neighbor: "",
    featured: "",
    wellness: "",
    cover: ""
  }
};
