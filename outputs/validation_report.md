# Validation Report — Phase 1

Generated 2026-05-21. Sample: 25 companies. Sources: SAFE PUBLIC /
first-party only (no feedback/competitive scraping).

## Headline metrics

| Metric | Value | Target | Result |
|---|---|---|---|
| Technographic **precision** (evidence re-verified) | **1.00** (34/34) | >= 0.75 | PASS |
| Product-motion **precision** (positives re-verified) | **1.00** (64/64) | >= 0.75 | PASS |
| Self-detection **recall** (vendors on own site) | **1.00** (6/6) | informational | strong |

## What "precision" means here
Every exported technographic and product-motion fact was re-checked against the
saved page source (a 100% claim audit, rule R5). Precision = facts whose literal
signature/token is still present in the source. High precision => exported facts
are trustworthy and evidence-backed (success criteria #2, #3).

**Caveat (signature-presence vs installed-tool).** This precision measures that
the signature string is genuinely present in the page source. Hard signatures
(CDN hosts like `cdn.amplitude.com`, init calls like `posthog.init`) reliably mean
the tool is installed. Bare-domain signatures (e.g. `contentsquare.com`) can also
match brand/ownership banners or footer links: on heap.io the `contentsquare.com`
hit is a "by Contentsquare" brand-banner link, not an installed Contentsquare
analytics tag. The string is real (so it passes re-verification), but the
*interpretation* needs care - a Phase-2 refinement is to separate "brand/ownership
link" from "installed tag" for domain-only signatures.

## Technographic precision detail
- Detected (>= 0.6) technographic facts: 34; re-verified: 34.
- Unverified on re-check: none

## Self-detection recall (independent ground truth)
- Amplitude: DETECTED own amplitude
- Mixpanel: DETECTED own mixpanel
- PostHog: DETECTED own posthog
- Pendo: DETECTED own pendo
- Heap: DETECTED own heap
- Hotjar: DETECTED own hotjar

## Recall gap (known, honest limitation)
- 8/25 companies returned **zero** technographic detections
  at/above the confidence floor.
- Root cause: modern sites load analytics via server-side tagging, first-party
  proxies, or consent managers, which are invisible to page-source detection.
  Example: Notion self-discloses Amplitude usage on its engineering blog, but its
  homepage serves analytics first-party (a `Track` endpoint + `analytics-*` data
  attributes), so page-source detection cannot see the vendor. The lone "amplitude"
  string on Notion's homepage is an SVG icon filename (conf 0.4) correctly nulled
  by the confidence floor (R1) - a suppressed false positive.
- Production fix (per docs/data_rights_matrix.md): a licensed **BuiltWith
  Enterprise** feed for recall + historical technographic shifts.

## Product-motion precision detail
- Positive product-motion facts: 64; re-verified: 64.
- Unverified on re-check: none
