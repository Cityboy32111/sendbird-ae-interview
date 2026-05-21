# External Account Signal Graph — Buyer Summary

*One-page overview for VP Product, VP AI, VP Partnerships, and VP Customer Success.*
*(Internal codename: External Product Intelligence Graph. Prepared 2026-05-21.)*

## The one-sentence pitch
We turn the **public web outside a company's own website** — review sites, community
forums, app stores, hiring boards, launch pages — into **account-level signals you can
act on inside Amplitude**: who is about to churn, who is shopping for a switch, and why.

## The problem
Traditional account data (ZoomInfo, Clearbit, 6sense) tells you a company's size, stack,
and intent *category*. It does **not** tell you that an account just quietly lost trust in
its current vendor, is reacting badly to a new pricing model, or is being actively courted
by a competitor this month. That signal exists — but it lives in forums, reviews, and
launch threads that a company's own website will never reveal.

## What we built (and proved)
A code-first pipeline over **25 leading B2B SaaS companies**:
- **214 public pages** crawled; **733 evidence-backed facts**; **every fact carries a source
  URL, a short evidence quote, a confidence score, and an extraction date.**
- **Accuracy is real:** technographic detection **100% precision (34/34)**, product-motion
  detection **100% precision (64/64)**, and a clean control test — **6 of 6 analytics vendors
  detect their own product on their own site.**
- Then a **unique-signal sample** on 10 priority accounts pulled **49 external signals** from
  reviews, forums, app stores, Product Hunt, and discussion sites.

## Why it's differentiated — three real findings
- **Retool** silently moved self-hosting behind its Enterprise tier (Feb 2026). The churn
  trigger appeared **only in a community forum** ("the most severe breach of trust ever from
  Retool"). Retool's own site still markets self-hosting. *Owned-site crawling cannot see this.*
- **Brex** was acquired by Capital One. Brex announced **zero** product changes — yet finance
  buyers are pre-emptively shortlisting competitors out of distrust, and rivals are running
  "Brex alternatives after the acquisition" capture content. *Anticipatory churn, invisible on brex.com.*
- **Heap** shows post-Contentsquare erosion confirmed by **two independent layers** of our own
  data: we detected Contentsquare's tags in Heap's page source **and** found ~28% active-domain
  decline plus "buggy since the acquisition" sentiment.

## How it plugs into Amplitude
Every signal maps to an action you already take: an **account property** (e.g.
`acquisition_uncertainty = high`), an **audience trigger** (e.g. "on a competitor at its
repricing moment"), **context for an AI Agent** ("which accounts have an emerging trust
backlash?"), and a **CS / expansion play** timed to the moment of pain.

## What we are explicitly NOT doing
No personal-data scraping, no contact harvesting, no LinkedIn profiles, no logged-in or
paywalled content, no production-database writes. Risky sources (G2, Capterra) are used in
the demo only and are flagged for licensed replacement before any shipped product.

## The ask
This is a working, evidence-backed sample — not a mockup. The next step is to (a) prove the
feedback layer at slightly larger scale and (b) agree which packaging fits Amplitude:
a **Signal Feed**, a **Signal Feed + Activation Layer**, or an **embedded API / partnership**.
