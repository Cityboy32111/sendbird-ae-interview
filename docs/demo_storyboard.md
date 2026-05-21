# Demo Storyboard — Two-Minute Buyer Narrative (Phase 0 First Draft)

**Product:** External Product Intelligence Graph · **Buyer:** Amplitude · **Date:** 2026-05-21

> **STATUS: ILLUSTRATIVE FIRST DRAFT.** Per the engagement plan, this uses a *hypothesized* flagship narrative drawn from `docs/wow_finding_targets.md` (Rank 1: Heap-customer displacement). The **market dynamic is real and cited**; the **specific account ("Northwind Analytics") is an explicitly illustrative placeholder** standing in for the named, confirmed account that Phase 1 will identify. We do **not** assert unverified signals about a real company. **This storyboard is refreshed in Phase 10 with the actual flagship account and its evidence.** Every bracketed `[CONFIRM P1]` is a leg to verify before this goes in front of a buyer.

---

## Open — the flagship narrative (60 seconds)

*"Heap was acquired by Contentsquare ([completed Dec 2023](https://contentsquare.com/press/contentsquare-completes-acquisition-heap/)), and the market has been voting with its feet — roughly **3 companies leaving Heap for every 1 joining** ([OpenPanel](https://openpanel.dev/compare/heap-alternative)). That migration is invisible inside any single product's analytics. It's only visible from the **outside.***

*"Take **Northwind Analytics** — a mid-market B2B SaaS, ~400 employees. Here's what the External Product Intelligence Graph saw, from the outside, in one quarter:*
- *In **March**, Northwind **removed Heap from its public integrations page** `[CONFIRM P1]`.*
- *In **April**, it opened **three product-analyst roles** whose descriptions mention experimentation and 'modern product analytics' `[CONFIRM P1]`.*
- *Across its **last 30 G2 reviews**, 'switching away from our old analytics tool' and competitor-comparison language is rising `[CONFIRM P1]`.*

*"Three independent public sources — a website change, a hiring pattern, and customer reviews — that together say: **this account is mid-migration and in-market for product analytics, right now.** No CRM, no intent vendor, no internal Amplitude data would have told you that."*

---

## Then — the same signal, flowing into Amplitude in four shapes (60 seconds)

**1. An Amplitude account property.**
A new field on the Northwind account: `external_competitive_pressure = High (84/100)`, joined on the company's account identifier, backed by the three sources above. The product manager opening that account in Amplitude now sees *market context* sitting next to product usage — they know the account is in motion before the usage data shows it.

**2. An Audience trigger.**
A rule fires: *external competitive-pressure score ≥ 80* **AND** *in-product weekly active usage flat-or-declining*. That combination assembles a **"Displacement-Risk / Win-Back" audience** automatically. Northwind drops into it the week the external signal appears — and the audience syncs to the CS team's Slack and the CRM. The action is enabled before a human noticed anything.

**3. AI Agent context.**
*Exact prompt a CS leader types into the Amplitude Global Agent:*
> "Which of my accounts show rising external competitive pressure this quarter, and why?"

*Exact answer the agent can now produce (and could not before):*
> "Northwind Analytics is your top flag. Its external competitive-pressure score rose to 84 this quarter. Evidence: it removed Heap from its integrations page in March, opened three product-analyst roles in April referencing experimentation, and its last 30 G2 reviews show rising vendor-switching language. Recommended play: expansion conversation around experimentation and session replay."

The agent answers with **named, dated, sourced evidence** — grounded, not guessed.

**4. A customer-success / expansion recommendation.**
The CS team gets one concrete action: *reach out to Northwind this week with an experimentation + session-replay expansion offer, referencing their analytics migration.* Expected outcome: a timed, evidence-led expansion conversation at the exact moment the account is choosing tools — instead of finding out a quarter later in a renewal call.

---

## Close — the one line we want repeated

> **"Amplitude already knows what's happening inside the product — now it knows what's happening in the market, account by account, with the receipts to prove it."**

---

*Phase 10 refresh checklist: replace "Northwind Analytics" with the confirmed flagship account; replace each `[CONFIRM P1]` with the verified signal, its source URL, and its date; confirm the account property name and Audience-trigger mechanics against Amplitude's account/cohort model (see open questions in `docs/integration_architecture.md`).*
