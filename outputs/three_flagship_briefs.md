# Three Flagship Account Briefs

*Buyer-facing. Built from the Phase 1.5 unique-signal sample (2026-05-21). Every claim is
evidence-backed with a source URL, a short quote, and a confidence score. G2/Capterra are
demo-only (SCRAPED RISKY); production replacement paths are listed per brief.*

---

## 1. Retool — a churn trigger that lives only in a community forum

**Account signal.** Retool silently moved **self-hosting behind the Enterprise tier (Feb 2026)**,
triggering a public trust backlash among data-residency / GDPR-sensitive customers.

**Evidence.**
- "self-hosting silently moved to Enterprise-only… most severe breach of trust ever from Retool" — [community.retool.com](https://community.retool.com/t/self-hosting-enterprise-only/64586) *(forum, direct read, conf 0.85)*
- "I can no longer trust the stability of the company" (GDPR/residency fallout) — same thread *(conf 0.85)*
- "5x price jump from Team to Business"; "cannot be exported as portable code" — G2 *(demo-only snippet, conf 0.55)*

**Why company-owned crawling would miss it.** retool.com's `/self-hosted` page still markets
self-hosting. The change was a quiet docs edit; the *reaction* exists only in a public forum.

**Why it matters.** This is a live, dated churn/displacement trigger hitting a specific,
high-value segment (self-hosters with compliance needs) — the exact accounts a competitor wins.

**How it maps to Amplitude.** Converts an invisible packaging change into a targetable
displacement cohort with citable evidence for the AI Agent and the CS team.

- **Recommended account property:** `vendor_trust_event = "retool_selfhost_enterprise_2026Q1"`
- **Recommended audience trigger:** accounts on Retool **and** flagged data-residency/self-host need → "displacement-ready."
- **Recommended AI Agent context:** "Which accounts face an emerging packaging/trust backlash with their current internal-tools vendor, and what is the evidence?"
- **Recommended CS / expansion action:** proactive migration outreach citing code-ownership and self-host parity; arm reps with the forum-sourced objection.
- **Source risk & production path:** forum = safe public (keep, first-party crawl). G2 line = demo-only → replace via **G2 Partner / Buyer Intent API**.

---

## 2. Brex — anticipatory churn manufactured purely by an acquisition

**Account signal.** After the **Capital One acquisition (completed 2026-04-07)**, finance buyers
are **pre-emptively shortlisting Ramp/BILL/Navan** on acquisition distrust — despite Brex
announcing no product or pricing changes.

**Evidence.**
- "bank-owned product anxiety… being prudent, not reactive"; teams evaluating alternatives — [receiptor.ai](https://receiptor.ai/blog/brex-alternatives-after-the-capital-one-acquisition-2026) *(news, direct read, conf 0.8)*
- Trustpilot 3.0/5: "freeze accounts without prior notice" — [trustpilot.com/review/brex.com](https://www.trustpilot.com/review/brex.com) *(direct read, conf 0.8)*
- iOS app 4.8/5 (8.8K) but "5-6 tries… force quitting the app" (reimbursement bug) — [Apple App Store](https://apps.apple.com/us/app/brex/id1472905508) *(direct read, conf 0.85)*

**Why company-owned crawling would miss it.** brex.com signals business-as-usual. The churn
*intent* lives entirely in third-party reaction content, review sites, and competitor capture pages.

**Why it matters.** Acquisition-driven distrust is a rare, time-boxed window where even
satisfied customers actively evaluate alternatives — the highest-leverage moment to win or save.

**How it maps to Amplitude.** Flags accounts whose risk has nothing to do with their own usage
curve, so CS can intervene before a renewal conversation is lost.

- **Recommended account property:** `external_acquisition_uncertainty = high`
- **Recommended audience trigger:** acquisition-uncertainty **∩** flat/declining usage → "at-risk despite healthy logins."
- **Recommended AI Agent context:** "Which of my accounts are absorbing an acquisition or ownership change, and how is the market reacting?"
- **Recommended CS / expansion action:** pre-renewal retention play; reassurance + roadmap continuity; for competitive reps, a timed displacement campaign.
- **Source risk & production path:** Trustpilot/App Store/news = sample-tolerable → **Trustpilot Business API**, **App Store Connect / licensed app-intelligence**. No demo-only sources required for the core signal.

---

## 3. Heap — post-acquisition erosion, corroborated across two independent layers

**Account signal.** Heap is eroding since its Contentsquare acquisition — the only finding
confirmed by **both** our technographic layer **and** our external-signal layer.

**Evidence.**
- Phase 1: **Contentsquare tags detected in heap.io's own page source** (ownership corroboration) — `outputs/source_evidence.json` *(conf 0.8)*
- "active domains declined ~28% by mid-2025" — [openpanel.dev/compare/heap-alternative](https://openpanel.dev/compare/heap-alternative) *(conf 0.55)*
- "gone downhill since the acquisition; buggy" — G2 *(demo-only snippet, conf 0.6)*
- "if you can't afford over $2k/mo, don't bother" — [Capterra](https://www.capterra.com/p/147216/Heap/reviews/) *(direct read, conf 0.85)*

**Why company-owned crawling would miss it.** heap.io frames the deal as "joined forces" and
shows no churn signal. Erosion only emerges by combining ownership data + adoption trend + sentiment.

**Why it matters.** A declining, more-expensive, lower-support analytics incumbent is a direct
displacement opportunity for Amplitude — with multi-source proof, not a hunch.

**How it maps to Amplitude.** A ready-made "win Heap accounts" cohort backed by independent
evidence, ideal for both competitive sales and CS expansion.

- **Recommended account property:** `competitor_in_use = "Heap"`, `competitor_health = "declining"`
- **Recommended audience trigger:** uses Heap **and** shows cost/quality complaints → "displacement target."
- **Recommended AI Agent context:** "Which competitors in my accounts are showing post-acquisition decline, and what's the evidence?"
- **Recommended CS / expansion action:** competitive displacement play; migration offer timed to Heap renewal; lead with reliability + cost-predictability.
- **Source risk & production path:** technographic + Capterra usable; G2 line demo-only → **G2 Partner / Buyer Intent API**; adoption-trend → **licensed web-traffic/technographic feed**.

---

*Compliance footer: company/product-level signals only. No personal data, names, contacts, or
usernames. No login/paywalled content. Short evidence spans only. Nothing fabricated; blocked
sources were recorded as inaccessible, not invented.*
