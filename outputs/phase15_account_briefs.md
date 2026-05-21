# Phase 1.5 — Mini Account Briefs (strongest new insights)

**Product:** External Product Intelligence Graph · **Buyer:** Amplitude · **Date:** 2026-05-21
**Scope:** controlled external-signal sample, 10 companies, local SQLite, no production writes.

Each brief states a **multi-source narrative**, **why it is invisible from company-owned
sources**, the **evidence** (with source + confidence; G2/Capterra are demo-only / SCRAPED
RISKY), and the **Amplitude use-case mapping**. Full provenance in
`outputs/external_feedback_sample.json` and `outputs/source_evidence.json`.

---

## Brief 1 (FLAGSHIP) — Heap: post-Contentsquare erosion, corroborated across owned + external sources

**The narrative.** Heap is showing measurable decline since its Contentsquare acquisition.
This is the only finding in the sample confirmed by **two independent layers of our own
pipeline**: Phase 1 detected **Contentsquare tags in heap.io's own page source** (technographic
ownership corroboration), and Phase 1.5 found **post-acquisition sentiment erosion** plus a
third-party signal that Heap's **active domains fell ~28%** (late-2024 → mid-2025), alongside
**">$2k/mo floor"** cost complaints and "buggy / support declined since the acquisition."

**Why it's invisible from owned sources.** heap.io frames the acquisition as "joined forces"
and shows no churn signal. The erosion only appears when you combine technographic ownership
data, third-party adoption trends, and review/forum sentiment.

**Evidence.**
- Phase 1 (page source): `contentsquare` signature on heap.io — `outputs/source_evidence.json` (conf 0.8).
- ~28% active-domain decline — [openpanel.dev/compare/heap-alternative](https://openpanel.dev/compare/heap-alternative) (conf 0.55).
- "gone downhill since the acquisition; buggy" — G2 *(demo-only, snippet)* (conf 0.6).
- "if you can't afford over $2k/mo, don't bother" — [Capterra](https://www.capterra.com/p/147216/Heap/reviews/) (conf 0.85, direct read).

**Amplitude mapping.** **Audiences** → a "Heap displacement / win-target" cohort joined on
account domain; **Activation AI / customer health** → churn-risk flag on accounts still on Heap;
**expansion action** → time outreach to Heap accounts now, with evidence.

---

## Brief 2 — Brex: anticipatory churn manufactured purely by the Capital One acquisition

**The narrative.** Brex was acquired by Capital One (completed 2026-04-07). Brex has announced
**zero** product or pricing changes — yet finance buyers are **pre-emptively shortlisting
Ramp/BILL/Navan on acquisition-driven distrust** ("thought they were getting a nimble fintech and
wound up with a legacy bank"), and competitors are already running **"Brex alternatives after the
Capital One acquisition"** capture content. Trustpilot (3.0/5) shows account-freeze complaints;
the iOS app (4.8/5, 8.8K) has a reimbursement-submit bug.

**Why it's invisible from owned sources.** brex.com signals business-as-usual. The churn *intent*
lives entirely in third-party comparison content, review sites, and acquisition-reaction articles.

**Evidence.**
- Post-acquisition uncertainty, teams evaluating alternatives — [receiptor.ai/blog/brex-alternatives…](https://receiptor.ai/blog/brex-alternatives-after-the-capital-one-acquisition-2026) (conf 0.8).
- Account freezes without notice — [Trustpilot](https://www.trustpilot.com/review/brex.com) (conf 0.8, direct read).
- Reimbursement submit bug / force-quits — [Apple App Store](https://apps.apple.com/us/app/brex/id1472905508) (conf 0.85, direct read).

**Amplitude mapping.** **Account property** `external_acquisition_uncertainty = high`;
**Audience trigger** (acquisition-uncertainty ∩ usage dip) → **CS retention play** before renewal.

---

## Brief 3 — Retool: a churn trigger that exists ONLY in a community forum

**The narrative.** Retool **silently moved self-hosting behind the Enterprise wall (Feb 2026)** —
documented only via a quiet docs edit and surfaced in a **community-forum thread** reading "the
most severe breach of trust ever from Retool," with GDPR/data-residency users openly reconsidering.
Reinforced by review-site complaints about a **5x Team→Business price jump** and **non-exportable
proprietary JSON** (lock-in).

**Why it's invisible from owned sources.** retool.com's /self-hosted page still markets
self-hosting. This is the cleanest proof of the thesis: the single highest-leverage churn signal
existed **nowhere except a public community forum** — exactly the source company-owned crawling
(Phase 1) cannot reach.

**Evidence.**
- "self-hosting silently moved to Enterprise-only; most severe breach of trust" — [community.retool.com](https://community.retool.com/t/self-hosting-enterprise-only/64586) (conf 0.85, direct read).
- "5x price jump from Team to Business"; "cannot be exported as portable code" — G2 *(demo-only, snippet)* (conf 0.55).
- SSO gated behind enterprise; cost pain — [Capterra](https://www.capterra.com/p/186115/Retool/reviews/) (conf 0.6).

**Amplitude mapping.** **AI Agent context** → the Global Agent can answer "which accounts have an
emerging trust/packaging backlash?" citing the forum evidence; **Audiences** → displacement cohort
for win-back/expansion.

---

*Honesty note: G2 review pages were 403-blocked to direct fetch across all companies (snippet-only,
demo-only). The highest-confidence external reads were Capterra, Product Hunt, Apple App Store, and
public community forums (0.8–0.85). Reddit was captured via public secondary aggregators (≤0.65).
All claims carry source URL + evidence span + confidence + extraction date; unsupported items are null.*
