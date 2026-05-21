# Commercial Product Schema — External Account Signal Graph

*The shape of the shipped product. Account-keyed. Every signal carries evidence, confidence,
and a recommended action. The contact/activation layer is optional and permission-gated.*

## Design principles
1. **Account-level by default.** The core product stores company/product-level signals only.
2. **Evidence or it doesn't ship.** Every signal has a source URL, short evidence span, source
   type, extraction date, and confidence. Unsupported inferences stay null.
3. **Action-oriented.** Each signal resolves to an Amplitude-native recommendation.
4. **Source tier is a first-class field** (safe / demo-only / licensed) so risky data can never
   leak into a production export by accident.

---

## Layer 1 — Account (firmographic core)
| field | type | example |
|---|---|---|
| account_id | string (domain) | `retool.com` |
| company_name | string | Retool |
| industry / segment | string | Internal tools / dev platform |
| employee_band, hq_region | string | 501–1000, US |
| primary_motion | enum | PLG / sales-led / hybrid |

## Layer 2 — Account Signals (the differentiator)
| field | type | notes |
|---|---|---|
| signal_id | string | stable id |
| account_id | string (FK) | |
| signal_type | enum | `vendor_trust_event`, `pricing_backlash`, `acquisition_uncertainty`, `displacement_intent`, `competitor_decline`, `hiring_surge`, `launch_event`, `ai_investment` |
| theme | string | short human label |
| sentiment | enum | positive / negative / neutral / mixed |
| **confidence** | float 0–1 | drives inclusion + display |
| **evidence_span** | string (short) | ≤ ~20 words, no over-quoting |
| **source_url** | string | the public page |
| **source_type** | enum | forum / appstore / producthunt / reddit / news / g2 / capterra / ats / pagesource |
| **source_tier** | enum | `safe_public` / `demo_only` / `licensed` |
| extraction_date | date | freshness |
| first_seen / last_seen | date | trend + decay |

## Layer 3 — Derived Account State (rolled up from signals)
| field | type | example |
|---|---|---|
| churn_risk_score | float | high when trust/pricing/acquisition signals stack |
| displacement_opportunity | float | competitor-in-use + competitor decline |
| ai_momentum | float | AI hiring + AI launches (from Phase 1 hiring/launch facts) |
| renewal_window_flag | bool | competitor at repricing/renewal moment |

## Layer 4 — Recommended Action (Amplitude-native)
| field | type | example |
|---|---|---|
| recommended_account_property | string | `external_acquisition_uncertainty = high` |
| recommended_audience_trigger | string | "on competitor X at repricing moment" |
| recommended_agent_context | string | "which accounts show a trust backlash + evidence" |
| recommended_cs_or_expansion_action | string | "pre-renewal retention call citing forum evidence" |

## Layer 5 — Activation / Contact Layer (OPTIONAL, OFF BY DEFAULT)
*Not part of the core signal product. Enabled only with a customer's explicit configuration and
a documented legal basis.*
| field | type | notes |
|---|---|---|
| routing_role | enum | role/title for routing only (e.g. "VP Product") — **role, not person, by default** |
| contact_source | enum | **licensed/permissioned only** (e.g. ZoomInfo, Apollo) — never scraped |
| legal_basis | enum | consent / legitimate-interest (required to populate) |
| suppression_flags | bool | GDPR/CCPA opt-out, do-not-contact honored |

**Hard rules for Layer 5:** no mass extraction, no cold-outreach lists without legal basis, no
data resale, company-level routing preferred over named individuals, full suppression honored.
This layer is a *connector* to licensed providers, not a scraper.

---

### Example record (Retool, abbreviated)
```json
{
  "account_id": "retool.com",
  "signal": {
    "signal_type": "vendor_trust_event",
    "theme": "self-hosting moved to Enterprise-only (Feb 2026)",
    "sentiment": "negative",
    "confidence": 0.85,
    "evidence_span": "most severe breach of trust ever from Retool",
    "source_url": "https://community.retool.com/t/self-hosting-enterprise-only/64586",
    "source_type": "forum",
    "source_tier": "safe_public",
    "extraction_date": "2026-05-21"
  },
  "recommended_action": {
    "account_property": "vendor_trust_event = retool_selfhost_enterprise_2026Q1",
    "audience_trigger": "on Retool AND self-host/residency need",
    "agent_context": "which accounts face a packaging/trust backlash + evidence",
    "cs_or_expansion_action": "migration outreach citing code-ownership + self-host parity"
  },
  "activation_layer": { "enabled": false }
}
```
