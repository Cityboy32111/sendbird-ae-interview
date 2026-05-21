# Risk & Production Path — Enterprise-Safe Source Strategy

*Makes the source strategy enterprise-safe by sorting every source into three tiers:
**safe public**, **demo-only (risky)**, and **licensed / permissioned (production)**. The shipped
product ships only Tier-A and Tier-C. Tier-B is for demos and is never sold un-licensed.*

## The rule that governs everything
> Risky data may be used **once**, in a **clearly-flagged demo sample**, with **short evidence
> spans** and **no personal data** — and must be **replaced by a licensed/permissioned source
> before it enters any paid product.** Source tier is stored on every signal so this is enforced,
> not just promised.

---

## Tier A — Safe Public (ship as-is)
First-party or clearly public sources, company/product-level, low legal risk.

| Source | What it gives | Notes |
|---|---|---|
| Company websites (homepage, pricing, docs, changelog, blog, press) | technographics, product motion, launches | Phase 1 core; 100% precision on verified fields |
| First-party hiring boards (Greenhouse / Lever / Ashby public APIs) | AI/data/product hiring momentum | Phase 1; 19/25 companies |
| Public community / support forums | trust events, churn triggers (Retool!) | highest-value off-site signal; direct-readable |
| Public news / vendor-comparison pages | acquisition reactions, positioning | corroboration |

**Production stance:** keep, first-party crawl with robots/rate-limit discipline. **This is the
differentiating core.**

## Tier B — Demo-Only / SCRAPED RISKY (never sold un-licensed)
Used once in the Phase 1.5 sample, flagged `demo_only`, snippet-length evidence only.

| Source | Why risky | Demo handling |
|---|---|---|
| **G2** | ToS/anti-scraping; **403-blocked to direct fetch everywhere**; partner-conflict | snippet-only, conf ≤0.6, flagged |
| **Capterra** | ToS; Gartner-owned; licensing friction | direct-read in sample only, flagged |

**Production stance:** **do not ship scraped.** Replace before any paid feed (see Tier C).

## Tier C — Licensed / Permissioned (production replacements)
The same signal, obtained compliantly. This is how Tier-B value reaches the shipped product.

| Need | Production source | Replaces |
|---|---|---|
| Review sentiment / buyer intent | **G2 Partner Program / Buyer Intent API** | G2 scraping |
| Review corpus | **Gartner Digital Markets / Capterra partner** | Capterra scraping |
| Social discussion | **Official Reddit Data API** | Reddit (sample used aggregators) |
| Launch / positioning | **Product Hunt official API** | PH direct read |
| App reviews | **App Store Connect / Play Developer API** (own apps) + **licensed app-intelligence feed** (competitors) | store scraping |
| Trust/review aggregate | **Trustpilot Business API** | Trustpilot direct read |
| Adoption / traffic trend | **Licensed web-traffic / technographic feed** (e.g. BuiltWith Enterprise) | page-source recall gap |
| Contact / activation (optional) | **ZoomInfo / Apollo** under their AUP, legal basis required | never scraped |

---

## Hard compliance lines (apply to all tiers)
- **No personal data, no contact harvesting, no LinkedIn profile scraping** in the core product.
- **No login-protected, private, or paywalled content.** Public only.
- **No mass extraction / database-building** from any licensed provider (violates ZoomInfo/Apollo AUP).
- **No cold-outreach lists without a documented legal basis;** honor all GDPR/CCPA/CAN-SPAM opt-outs.
- **Short evidence spans only** — paraphrase themes, never republish review/forum text at length.
- **Every signal stores its `source_tier`,** so a Tier-B item cannot silently enter a paid export.

## One-line summary for security review
*"The product's differentiating signal comes from safe, public, company/product-level sources
(forums, app stores, launch pages, hiring boards) and licensed APIs. Risky review-site scraping
was used only in a flagged one-time demo and is replaced by partner/licensed feeds before sale.
No personal data, no scraping of contacts, no production-database writes."*
