# Phase 1 Findings & Recommendation

**Product:** External Product Intelligence Graph · **Buyer:** Amplitude · **Date:** 2026-05-21
**Scope:** 25 companies · SAFE PUBLIC / first-party sources only · local SQLite · no production DB · no risky scraped sources.

## 1. What ran

A code-first pipeline crawled 25 B2B SaaS companies (214 public pages: homepage,
pricing, product, integrations, api-docs, changelog, blog, press, careers) and ran:
page-source technographic detection, product-motion extraction, first-party
hiring-signal collection (public Greenhouse/Lever/Ashby boards), and recent-launch
detection from owned changelog/blog/press. Everything is stored in
`data/processed/epig.db` with field-level facts + evidence spans. Outputs:
`outputs/external_product_intelligence_graph.{csv,json}`, `source_evidence.json`,
`validation_report.md`.

- 25 companies · **684 non-null exported fields** (~62% cell coverage) · **702 evidence rows**.
- **Every evidence row has a source URL + extraction date** (0 missing) and every
  exported fact carries confidence ≥ 0.6 (R1). Below-floor values retained in DB, nulled in deliverables.

## 2. Accuracy read (success criterion #1)

| Metric | Result | Target |
|---|---|---|
| Technographic precision (evidence re-verified, 100% claim audit) | **1.00 (34/34)** | ≥ 0.75 PASS |
| Product-motion precision (positives re-verified) | **1.00 (64/64)** | ≥ 0.75 PASS |
| Self-detection recall (analytics vendors detect own tool on own site) | **1.00 (6/6)** | strong |
| Technographic recall gap | 8/25 returned zero detections | known limitation |

"Precision" = the claimed signature/token is genuinely present in the saved page
source. **Caveat:** hard signatures (CDN hosts, init calls) reliably mean the tool
is installed; bare-domain signatures (e.g. `contentsquare.com`) can match
brand/ownership banners — see §4. Self-detection recall is the cleanest independent
ground truth: **Amplitude, Mixpanel, PostHog, Pendo, Heap, and Hotjar each correctly
detect their own product on their own site.**

## 3. Wow-finding leg CONFIRMED (success criterion #4)

**Contentsquare ↔ Heap ↔ Hotjar corporate relationship, corroborated from page source.**
- `heap.io` serves a **"by Contentsquare" brand banner** (`<a href="https://contentsquare.com">`) — evidence in `source_evidence.json`.
- `hotjar.com` analytics config shares domains across `contentsquare.com` + `heapanalytics.com` (`heap.load(... supporteddomains:["contentsquare.com","heapanalytics.com"...]`).
- This independently corroborates (from a *second* source type beyond the
  [Dec-2023 Contentsquare/Heap press release](https://contentsquare.com/press/contentsquare-completes-acquisition-heap/)) that Heap and Hotjar are now Contentsquare properties — the foundation of the **Rank-1 wow narrative** (Heap-customer displacement post-acquisition; see `docs/wow_finding_targets.md`).

**Bonus confirmed signal:** **Loom uses Amplitude** — detected at confidence 0.95
from `loom.com` page source (`cdn.amplitude.com`). A verifiable Amplitude customer
discovered directly, independent of any logo list.

**Other notable page-source findings (precision-verified):** Mixpanel runs
Optimizely (experimentation); Pendo's site carries a Gainsight PX (`aptrinsic`)
signature — flagged for Phase-2 verification (could be an embed or comparison
content). Datadog (414 roles, 35 AI), Brex (231 roles, 22 product), and Intercom
(168 roles, 39 AI) show the heaviest AI/product hiring in the sample.

## 4. Limitations (honest)

1. **Technographic recall (8/25 zero detections).** Modern sites load analytics via
   server-side tagging, first-party proxies, or consent managers, invisible to
   page-source detection. Clearest case: **Notion self-discloses Amplitude on its
   eng blog, but its homepage serves analytics first-party** (a `Track` endpoint +
   `analytics-*` data attributes), so we cannot see the vendor. The lone "amplitude"
   string on Notion's homepage is an SVG icon filename (conf 0.4) correctly nulled
   by the floor — a *suppressed* false positive. **Production fix:** licensed
   BuiltWith Enterprise feed (per `docs/data_rights_matrix.md`).
2. **Bare-domain signature interpretation.** `contentsquare.com` on heap.io is a
   brand banner, not an installed tag. Phase-2 fix: separate "brand/ownership link"
   from "installed tag" for domain-only signatures.
3. **Hiring recall (6/25 null).** Companies on Workday/SmartRecruiters/custom boards
   aren't covered by the Greenhouse/Lever/Ashby readers (Retool, monday.com, Miro,
   Loom, Heap, Hotjar). Honest nulls (R6).
4. **Recent-events recall.** Changelog/blog dates are only parsed when present in
   static HTML; JS-rendered or dateless feeds yield nulls (Datadog, Ramp, Brex,
   Calendly, several others).
5. **The core thesis layer is still untested.** External *feedback* synthesis
   (G2/Reddit/app-store) — the actual proprietary differentiator — was off-limits
   this phase, so the most important product claim has not yet been demonstrated.

## 5. Recommendation

**Proceed to 100 companies AND add one tightly-scoped sample of the feedback layer — do not revise the thesis.**

- **The thesis holds.** Precision is excellent, evidence discipline works end-to-end,
  and we already surfaced a genuine multi-source signal (Contentsquare/Heap/Hotjar)
  and a real Amplitude customer (Loom) from public pages alone.
- **Expand to 100 companies** to build a meaningful sample and stress dedup/normalization.
- **Add a tightly-scoped, one-time external-feedback sample (≈10 companies)** — the
  G2/Reddit/app-store synthesis is the product's actual differentiator and is the
  one untested leg. I recommend you explicitly authorize a small, clearly-flagged
  SAMPLE-only pull (SAMPLE_TOLERABLE / one-time, never shipped, replacement path
  documented) so Phase 2 can prove the feedback-synthesis → Amplitude-fit story end
  to end. **This requires your explicit approval and stays within the demo-safety
  rules in `docs/data_rights_matrix.md`.**
- **Before any production claim**, plan a licensed BuiltWith trial to quantify the
  technographic recall lift over code-first detection.

**Net:** Phase 1 met every success criterion (precision ≥ 0.75 on both critical
field families; full evidence on every fact; nulls preserved; ≥1 wow leg confirmed;
no production DB changes; no risky sources). The signal is high-quality. The
recommended next step is breadth (100) plus a guarded test of the differentiating
feedback layer.
