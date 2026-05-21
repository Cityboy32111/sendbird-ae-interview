# Phase 1.5 — Source Risk Note & Roadmap Recommendation

**Product:** External Product Intelligence Graph · **Buyer:** Amplitude · **Date:** 2026-05-21

Separates **demo-acceptable** sources (used in this sample) from **production** sources
(licensed/permissioned), and recommends which to keep in the product roadmap. Cross-reference
`docs/data_rights_matrix.md` for full tiering and cost. **G2 and Capterra are SCRAPED RISKY /
demo-only and must NOT be presented as production-ready.**

## What we actually accessed (honest)

| Source | Accessed how | Confidence | Demo status |
|---|---|---|---|
| **G2** | 403-blocked to direct fetch → **search-snippet only** | 0.55–0.6 | 🔴 demo-only / SCRAPED RISKY |
| **Capterra** | Direct read (review pages) | 0.6–0.85 | 🔴 demo-only / SCRAPED RISKY |
| **Reddit** | Via public secondary aggregators (no direct thread fetch) | 0.5–0.65 | 🟡 sample-tolerable |
| **Product Hunt** | Direct read (public launch/review pages) | 0.8–0.85 | 🟡 sample-tolerable |
| **Apple App Store** | Direct read (public listing/reviews) | 0.85 | 🟡 sample-tolerable |
| **Trustpilot** | Direct read (public reviews) | 0.8 | 🟡 sample-tolerable |
| **Community/support forums** | Direct read (public threads) | 0.85 | 🟢 safe public |
| **News / vendor comparison pages** | Direct read | 0.75–0.8 | 🟢 safe public |
| **First-party job boards (Phase 1)** | Direct public ATS APIs | 0.85 | 🟢 safe public |

**No LinkedIn profile scraping, no contact extraction, no personal data, no login/paywalled
content** was performed. G2 direct fetch was blocked everywhere — confirming in practice why it
cannot be a production scraping target.

## Demo-acceptable vs production sources

| Source | Demo-acceptable? | Production replacement path | Production status |
|---|---|---|---|
| G2 | one-time sample, snippet only, flagged | **G2 Partner Program / Buyer Intent API** (licensed) | 🔴 must not ship scraped |
| Capterra | one-time sample, flagged | **Gartner Digital Markets / Capterra partner** (licensed) | 🔴 must not ship scraped |
| Reddit | yes (short excerpts) | **Official Reddit Data API** (licensed tier) | 🟡 replace before scale |
| Product Hunt | yes | **Product Hunt official API** (GraphQL) | 🟡 → 🟢 once on API |
| Apple App Store | yes | **App Store Connect API** (own apps) + **licensed app-intelligence feed** for competitor apps | 🟡 |
| Google Play | yes | **Play Developer API** (own apps) + licensed feed for competitors | 🟡 |
| Trustpilot | yes | **Trustpilot Business API** | 🟡 → 🟢 |
| Community/support forums | yes | first-party crawl (stays safe public) | 🟢 |
| First-party job boards | yes | stays first-party (Greenhouse/Lever/Ashby public APIs); LinkedIn Talent Insights optional | 🟢 |

## Roadmap recommendation — which sources to keep

**KEEP (high value, clean production path):**
1. **Community / support forums — KEEP, top priority.** Highest-confidence reads in the sample
   *and* the single biggest "wow" (Retool self-hosting churn lived only here). Safe public,
   first-party crawlable. This is the differentiator.
2. **App stores (Apple/Google) — KEEP** for accounts with mobile apps. Directly readable; clean
   own-app APIs + a licensed app-intelligence feed for competitor coverage.
3. **Product Hunt — KEEP** (launch/positioning signal + early sentiment); clean official API.
4. **First-party job boards — KEEP** (already proven in Phase 1; pure first-party).
5. **Trustpilot / news / vendor-comparison content — KEEP** as corroboration; mostly safe public.

**KEEP-BUT-LICENSE (high value, must replace the access method):**
6. **G2 — KEEP THE SIGNAL, REPLACE THE METHOD.** Richest review/displacement signal, but direct
   scraping is **blocked and non-compliant** (403 everywhere). Production = **G2 Partner Program /
   Buyer Intent API**. Never ship scraped G2.
7. **Reddit — KEEP, move to official API.** Real displacement/pricing-pain signal, but only
   sample-tolerable when scraped; production = official Reddit Data API.

**DEPRIORITIZE:**
8. **Capterra — LOWER priority.** Largely duplicates G2's signal at higher licensing friction
   (Gartner Digital Markets). Keep only if a customer needs that specific corpus.
9. **LinkedIn (beyond jobs) — DO NOT pursue profile scraping.** Personal-data + ToS risk. Jobs
   stay via first-party ATS / Talent Insights only.

**Net:** the production roadmap should lead with **forums + app stores + Product Hunt + first-party
jobs** (clean, defensible, differentiating) and treat **G2 + Reddit** as high-value signals sourced
through **licensed/official APIs** — never scraped in the shipped product.
