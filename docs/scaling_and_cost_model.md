# Scaling & Cost Model

**Product:** External Product Intelligence Graph · **Buyer:** Amplitude · **Date:** 2026-05-21

> All figures are **planning estimates** built on public pricing accessed 2026-05-21 (see `docs/competitive_positioning.md` and `docs/data_rights_matrix.md` for sources). Enterprise/licensed-feed prices are negotiation-range estimates, not quotes. Per-company micro-costs use the stated assumptions below; treat them as multipliers to refine against real payloads in Phase 1.

## Cost-driver assumptions

**LLM inference (per company, per full enrichment cycle):** one extraction pass (~150K input + 5K output) + one summarization pass (~30K input + 3K output). At Claude Haiku 4.5 rates ($1/$5 per 1M in/out; [pricing](https://platform.claude.com/docs/en/about-claude/pricing)) ≈ **$0.22/company** standard, **~$0.11** with the Batch API (−50%). We budget **$0.40/company/month** standard (monthly normalization + lighter weekly feedback re-classification) and **~$0.20** with batch.

**Apify usage (sample scraping, per company/month):** feedback (weekly) + jobs (weekly) + search/market-events (weekly) + website/technographics/competitive (monthly), incremental volumes only ≈ **~$0.60/company/month** at sample scale, falling toward **~$0.30** at high volume on discounted CU tiers ($0.13–$0.16/CU; [Apify pricing](https://apify.com/pricing)). Website + technographic detection are **code-first** (compute only); Apify is fallback.

**Refresh cadence (from `config/source_config.json`):** feedback **weekly** · jobs **weekly** · market events **weekly** · website **monthly** · technographics **monthly** · competitive intel **monthly**.

**Licensed feeds are mostly FLAT** (do not scale with company count): BuiltWith Enterprise (~$995–$2,000/mo), G2 Partner/Buyer Intent (~$2,000–$5,000/mo equiv.), Crunchbase Enterprise API (~$4,200–$5,000/mo equiv., $50K+/yr). This flatness is the central economic lever — it makes unit cost fall as N rises.

## Three-scenario model (monthly)

| Component | 250 (sample) | 5,000 (mid-tier) | 50,000 (Amplitude-scale) |
|---|---|---|---|
| Apify platform base | Scale $199 | Business $999 | Enterprise ~$2,000 |
| Apify usage (scraping) | 250 × $0.60 = **$150** | 5,000 × $0.35 = **$1,750** | 50,000 × $0.30 = **$15,000** |
| LLM inference | 250 × $0.40 = **$100** (std) | 5,000 × $0.40 = **$2,000** (std) | 50,000 × $0.20 = **$10,000** (batch) |
| Licensed feeds (flat) | $0 (sample uses scraped) | BuiltWith $995 + G2 ~$2,000 + Crunchbase ~$4,200 = **$7,195** | BuiltWith ~$2,000 + G2 ~$5,000 + Crunchbase ~$5,000 = **$12,000** |
| Storage / DB (Supabase) | Pro **$25** | Pro + overage ~**$50** | Team + overage ~**$1,000** |
| **Total monthly (est.)** | **~$474** | **~$11,994** | **~$40,000** |
| **Unit cost / company / month** | **~$1.90** | **~$2.40** | **~$0.80** |

> Storage note: at 50K companies with evidence excerpts (~3 MB/company structured + excerpts ≈ ~150 GB), Supabase Pro overage ($0.125/GB-mo; [pricing](https://supabase.com/pricing)) is modest; the larger cost is moving to Team tier / a dedicated Postgres. Raw HTML is *not* retained long-term — only evidence spans + source URLs.

## Where Apify gets replaced by licensed feeds

| Source | Sample (250) | 5,000 | 50,000 |
|---|---|---|---|
| G2 reviews | Scraped (one-time, 🔴 flagged) | **G2 Partner API** | G2 Partner API |
| Technographics | Code-first crawl | **BuiltWith Enterprise** | BuiltWith Enterprise |
| Funding/firmographic | Public press (scraped/SERP) | **Crunchbase Enterprise** | Crunchbase Enterprise |
| Reddit | Scraped | Official Reddit Data API | Official Reddit Data API |
| Own-app reviews | Scraped | App Store Connect / Play Developer API | same (+ app-intelligence license for competitor apps) |
| Jobs | Careers crawl + Apify | Careers crawl + Apify | Careers crawl + Apify (LinkedIn Talent Insights optional) |
| Website / blogs / RSS | Code-first | Code-first | Code-first |

## Narrative — the inflection points

**Inflection 1 — the compliance crossover (250 → 5,000).** The sample is cheap (~$1.90/company/mo) precisely because it leans on scraped sources that are *not* production-safe. Crossing into a real product means turning on flat licensed feeds (G2 Partner, BuiltWith, Crunchbase ≈ $7K/mo). At 5,000 companies that flat cost is amortized over relatively few accounts, so **unit cost actually rises to ~$2.40** even as the data becomes safer and better. This is the counter-intuitive point to set expectations on: *going legitimate costs more per unit before scale pays it back.*

**Inflection 2 — flat-feed amortization (5,000 → 50,000).** From 5K to 50K, the ~$12K/mo of licensed feeds barely moves while company count grows 10×. Combined with **Batch-API LLM economics** (halving inference) and **CU volume discounts** on Apify, unit cost **falls to ~$0.80/company/month** — a ~3× improvement. The business gets dramatically more efficient exactly at Amplitude-relevant scale.

**Inflection 3 — batch & cache (any scale).** The single biggest controllable lever is LLM cost: the Batch API (−50%) and prompt caching (cache reads at 0.1× input) can cut the inference line by 50–80% with no quality loss for an offline enrichment workload. At 50K this is the difference between ~$20K and ~$10K/mo.

**Bottom line for the deal:** at Amplitude scale the marginal cost to enrich an account is **well under a dollar per month**, against accounts worth (per Amplitude's own disclosures) $100K+ ARR in the 727-customer cohort. The cost model supports either a flat data-feed price or a per-account API price with healthy margin — see `docs/deal_shape.md`.
