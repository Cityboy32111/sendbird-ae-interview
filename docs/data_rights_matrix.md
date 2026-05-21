# Data Rights Matrix

**Product:** External Product Intelligence Graph · **Buyer:** Amplitude · **Date:** 2026-05-21

Purpose: make the **sample safe** while showing Amplitude a clear path from public sample data to **licensed/permissioned production data**. Every YELLOW or RED source has a fully specified replacement path. All costs are **third-party/list estimates** (vendors rarely publish enterprise pricing), accessed 2026-05-21 — negotiation-range references, not quotes.

## Tier definitions
- **SAFE PUBLIC** — fair use, no ToS concern (company sites, public RSS, press releases, funding announcements).
- **SAMPLE TOLERABLE** — fine for a one-time sample, not production (public search results, scraped Reddit / Product Hunt).
- **SCRAPED RISKY** — explicit ToS friction, demo-only, must be replaced at scale (G2/Capterra/Trustpilot scraping, LinkedIn scraping, competitor app-store scraping where official APIs exist).
- **REQUIRES LICENSE OR PARTNERSHIP** — production needs a paid feed/API/partnership (G2 Partner, Crunchbase, BuiltWith, LinkedIn Talent Insights, Apple/Google developer APIs).

## Production-ready status legend
🟢 production-ready as-is · 🟡 needs replacement before production · 🔴 must not ship in Amplitude's product under any circumstances.

## Summary matrix

| # | Source | Tier | Status | Legal risk | Product risk |
|---|---|---|---|---|---|
| 1 | Company websites (home/pricing/product/integrations/docs/changelog/blog/careers) | SAFE PUBLIC | 🟢 | Low | Low |
| 2 | Public RSS / company blogs | SAFE PUBLIC | 🟢 | Low | Low |
| 3 | Public press releases / funding announcements | SAFE PUBLIC | 🟢 | Low | Low |
| 4 | Technographic detection via own crawl (HTML/scripts/privacy policy) | SAFE PUBLIC | 🟡 | Low | Medium |
| 5 | Public search results (Google SERP scraper) | SAMPLE TOLERABLE | 🟡 | Medium | Medium |
| 6 | Reddit (scraped) | SAMPLE TOLERABLE | 🟡 | Medium | Medium |
| 7 | Product Hunt (scraped) | SAMPLE TOLERABLE | 🟡 | Medium | Low |
| 8 | G2 reviews (scraped) | SCRAPED RISKY | 🔴 | High | High |
| 9 | Capterra reviews (scraped) | SCRAPED RISKY | 🔴 | High | High |
| 10 | Trustpilot reviews (scraped) | SCRAPED RISKY | 🟡 | Medium | Medium |
| 11 | Competitor app-store reviews — Apple (scraped) | SCRAPED RISKY | 🟡 | Medium | Medium |
| 12 | Competitor app-store reviews — Google Play (scraped) | SCRAPED RISKY | 🟡 | Medium | Medium |
| 13 | LinkedIn jobs / company / profiles (scraped) | SCRAPED RISKY | 🔴 | High | High |
| 14 | BuiltWith (licensed technographics) | REQUIRES LICENSE | 🟢 | Low | Low |
| 15 | Crunchbase (licensed funding/firmographic) | REQUIRES LICENSE | 🟢 | Low | Low |
| 16 | G2 Partner Program / Buyer Intent API | REQUIRES LICENSE | 🟢 | Low | Low |

## Per-source detail

**1. Company websites** — *sample_use:* product motion, pricing model, integrations, API docs, changelog, launches, careers. *legal_risk:* Low — public pages, honor robots.txt/rate limits. *product_risk:* Low — first-party, accurate. *replacement_path:* none needed (stays first-party crawl). *status:* 🟢. *est_prod_cost:* compute only (see scaling model). *buyer_language:* "Sourced directly from each company's own public website."

**2. Public RSS / blogs** — *sample_use:* product launches, announcements, market events. *legal_risk:* Low. *product_risk:* Low. *replacement_path:* none. *status:* 🟢. *est_prod_cost:* compute only. *buyer_language:* "Pulled from companies' own published feeds."

**3. Press releases / funding announcements** — *sample_use:* funding events, exec changes, M&A, expansion. *legal_risk:* Low. *product_risk:* Low (but verify — secondary aggregators can be wrong). *replacement_path:* Crunchbase for structured funding (see #15). *status:* 🟢. *est_prod_cost:* compute only. *buyer_language:* "From public press releases; structured funding data upgraded to a licensed Crunchbase feed in production."

**4. Technographic detection (own crawl)** — *sample_use:* detect Amplitude/Mixpanel/Pendo/PostHog/etc. from HTML, script tags, tag manager, privacy-policy vendors, docs SDK mentions. *legal_risk:* Low — reading public page source. *product_risk:* Medium — code detection has false negatives (tag managers, server-side tagging hide vendors); freshness varies. *replacement_path:* **BuiltWith Enterprise feed** (#14) for coverage + historical shift data. *status:* 🟡. *est_prod_cost:* compute in sample; BuiltWith license in production (see #14). *buyer_language:* "For the sample we detect tools from public page source; for production this becomes a licensed BuiltWith feed with historical change tracking."

**5. Public search results (SERP scraper)** — *sample_use:* discover comparison/alternative pages, reviews, Reddit threads, changelogs. *legal_risk:* Medium — search-engine ToS friction at scale. *product_risk:* Medium — results drift; not a stable contract. *replacement_path:* official search API (e.g., licensed SERP API / Bing API) or direct first-party crawl where possible. *status:* 🟡. *est_prod_cost:* ~$0.05–$1.80 per 1K results (Apify, [pricing](https://apify.com/pricing)); licensed SERP API in production. *buyer_language:* "Sample used public web search; production uses a licensed search API or direct first-party crawls."

**6. Reddit (scraped)** — *sample_use:* community feedback themes, pain language, competitor mentions. *legal_risk:* Medium — Reddit content/API ToS; store short excerpts only, not full reposts. *product_risk:* Medium — noisy, unstructured, attribution care needed. *replacement_path:* **official Reddit Data API** (licensed/permissioned tier). *status:* 🟡. *est_prod_cost:* ~$1–$4 per 1K posts (Apify, [Reddit scraper](https://apify.com/trudax/reddit-scraper-lite)); official Reddit API licensing in production. *buyer_language:* "Sample used public Reddit threads with short excerpts; production moves to the official Reddit Data API."

**7. Product Hunt (scraped)** — *sample_use:* launch detection, early-feedback comments. *legal_risk:* Medium — ToS friction. *product_risk:* Low — supplementary signal. *replacement_path:* **Product Hunt official API** (GraphQL). *status:* 🟡. *est_prod_cost:* pay-per-usage (no clearly-priced public actor surfaced — verify in Apify Store); Product Hunt API in production (free/low). *buyer_language:* "Sample used public Product Hunt pages; production uses the official Product Hunt API."

**8. G2 reviews (scraped)** — *sample_use:* review volume/rating, recent negative/positive themes, competitor mentions, displacement language. *legal_risk:* **High** — explicit G2 ToS friction; IP exposure on review text. *product_risk:* **High** — partner conflict (G2 sells this), brand/trust risk if shipped in Amplitude. *replacement_path:* **G2 Partner Program / Buyer Intent API** (#16) — the licensed, compliant route ([partner.g2.com](https://partner.g2.com/developer)). *status:* 🔴 — must not ship scraped G2 in Amplitude's product. *est_prod_cost:* ~$5–$6.50 per 1K reviews scraped (sample only, [Apify G2](https://apify.com/junipr/g2-reviews-scraper)); production = G2 Partner license ~$10K–$40K/yr+ ([Vendr](https://www.vendr.com/marketplace/g2)). *buyer_language:* "For the sample we used public web crawls; for production this becomes a licensed G2 partner feed with monthly refresh."

**9. Capterra reviews (scraped)** — *sample_use:* additional review themes/ratings. *legal_risk:* **High** — Gartner Digital Markets ToS; IP exposure. *product_risk:* **High** — partner conflict, trust. *replacement_path:* **Gartner Digital Markets / Capterra partner program** (licensed). *status:* 🔴. *est_prod_cost:* ~$8 per 1K results scraped (sample only, [multi-review actor](https://apify.com/focused_vanguard/multi-platform-reviews-scraper)); production = Gartner Digital Markets license (custom). *buyer_language:* "Sample used public Capterra pages; production requires a Gartner Digital Markets license."

**10. Trustpilot (scraped)** — *sample_use:* consumer-side sentiment/themes. *legal_risk:* Medium. *product_risk:* Medium — less B2B-relevant. *replacement_path:* **Trustpilot Business / official API**. *status:* 🟡. *est_prod_cost:* ~$8 per 1K results (sample); Trustpilot API in production. *buyer_language:* "Sample used public Trustpilot pages; production uses the official Trustpilot Business API."

**11. Apple App Store reviews — competitors (scraped)** — *sample_use:* mobile review volume/rating/negative themes for *competitor/target* apps. *legal_risk:* Medium — Apple ToS. *product_risk:* Medium — mobile not relevant to all targets. *replacement_path:* **Apple App Store Connect API** ([docs](https://developer.apple.com/app-store-connect/api/)) — **but only returns *your own* apps' reviews.** Competitor reviews at scale have **no official API** → remains a scraping dependency or a licensed app-intelligence feed (e.g., data.ai/Sensor Tower). *status:* 🟡. *est_prod_cost:* ~$3.99 per 1K reviews scraped (sample, [Apify](https://apify.com/focused_vanguard/appstore-reviews-scraper)); App Store Connect = $99/yr (own apps only); competitor coverage = app-intelligence license (custom). *buyer_language:* "Sample used public App Store pages; a customer's own app reviews move to the official App Store Connect API, and competitor coverage to a licensed app-intelligence feed."

**12. Google Play reviews — competitors (scraped)** — *sample_use:* Android review volume/rating/negative themes. *legal_risk:* Medium. *product_risk:* Medium. *replacement_path:* **Google Play Developer API** ([docs](https://developer.android.com/google/play/developer-api)) — **own apps only** (one-time $25); competitor coverage = licensed app-intelligence feed. *status:* 🟡. *est_prod_cost:* ~$0.10–$0.75 per 1K reviews scraped (sample, [Apify](https://apify.com/neatrat/google-play-store-reviews-scraper)); Play Developer API ~free (own apps); competitor coverage licensed. *buyer_language:* "Same as Apple — own-app reviews via the official Play Developer API; competitor coverage via a licensed feed."

**13. LinkedIn jobs/company/profiles (scraped)** — *sample_use:* hiring signals (role counts, titles, keywords). *legal_risk:* **High** — LinkedIn ToS + *hiQ v. LinkedIn* history; GDPR exposure on personal profiles. *product_risk:* **High** — personal-data and brand risk. *replacement_path:* **company careers pages (first-party, SAFE PUBLIC) as primary**, plus **LinkedIn Talent Insights** (licensed) for aggregate hiring trends. *status:* 🔴 for profile scraping; hiring signals are sourced first-party from careers pages instead. *est_prod_cost:* careers-page crawl = compute only; LinkedIn Talent Insights = enterprise license (custom). *buyer_language:* "We never ship scraped LinkedIn data; hiring signals come from companies' own public careers pages, with LinkedIn Talent Insights as a licensed aggregate option."

**14. BuiltWith (licensed)** — *sample_use:* (not in sample; replacement for #4 at scale). *legal_risk:* Low — licensed. *product_risk:* Low. *replacement_path:* n/a (this *is* the replacement). *status:* 🟢. *est_prod_cost:* $995/mo published web plan ([plans](https://builtwith.com/plans)); Enterprise API feed custom-quoted (~"2,000 calls/$100" reference) — **flat, does not scale with company count**. *buyer_language:* "Production technographics are a licensed BuiltWith feed with historical change tracking."

**15. Crunchbase (licensed)** — *sample_use:* (not in sample; upgrade for #3 funding data). *legal_risk:* Low. *product_risk:* Low. *replacement_path:* n/a. *status:* 🟢. *est_prod_cost:* Enterprise/Applications API custom, reported $50K+/yr ([Vendr](https://www.vendr.com/marketplace/crunchbase)) — **flat**. *buyer_language:* "Structured funding and firmographic data is a licensed Crunchbase Enterprise feed."

**16. G2 Partner Program / Buyer Intent API (licensed)** — *sample_use:* (not in sample; the compliant replacement for #8). *legal_risk:* Low — licensed/compliant. *product_risk:* Low — removes partner conflict. *replacement_path:* n/a. *status:* 🟢. *est_prod_cost:* ~$10K–$40K/yr, bundles to ~$87K/yr ([Vendr](https://www.vendr.com/marketplace/g2)) — **flat-ish, plan-gated**. *buyer_language:* "Production review intelligence is a licensed G2 partner feed — the same data, sourced compliantly."

## Demo-safety summary

For the 250-company **sample**, only 🟢/🟡 sources are used, and the two 🔴 review sources (G2, Capterra) are used **for a one-time sample only, clearly flagged, with short excerpts**, and are **never represented as production-ready**. Every 🔴/🟡 source has a named licensed replacement above. **No 🔴 source ships inside Amplitude's product** — they exist only to prove the signal in the sample, after which the licensed feed carries it. This is the line we hold in the demo: *public sample today, licensed/permissioned feed in production, identical signal.*
