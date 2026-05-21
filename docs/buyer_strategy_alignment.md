# Buyer Strategy Alignment — Amplitude (NASDAQ: AMPL)

**Product:** External Product Intelligence Graph
**Buyer:** Amplitude
**Prepared by:** Accel Corporate Solutions
**Date:** 2026-05-21
**Test applied to every design choice:** *Does this make Amplitude's product better?*

> **Sourcing note (anti-hallucination).** Quotes below are split into **VERIFIED VERBATIM** (independently confirmed against an accessible transcript or official page) and **PARAPHRASE / SUBSTANCE-CONFIRMED** (the event and meaning are confirmed from an official source, but exact wording was retrieved via summarized fetch and is *not* placed in quotation marks). We do not present unverified wording as a quote.
>
> **Correction on the brief.** The engagement brief referenced an Amplitude *"West acquisition."* A targeted search found **no evidence that any "West"/"WEST" acquisition exists.** It does not appear in Amplitude blogs, press releases, SEC filings, or news coverage. We have replaced it below with Amplitude's *actual* recent inorganic moves: the **Command AI** acquisition (Oct 2024), **Kraftful** (Aug 2025), **InfiniGrow** (Jan 2026), and the **Statsig** partnership (May 2026). Please confirm whether "West" was a mistaken reference before we anchor any pitch language to it.

---

## 1. Where Amplitude is going (verified)

Amplitude has, over the last two quarters, repositioned from "digital analytics platform" to **agentic AI analytics platform**. The throughline of every public statement is the same: behavioral data is the fuel, and **AI agents are the new consumption layer** on top of it.

### Verified verbatim quotes

| Quote | Speaker | Source | Date |
|---|---|---|---|
| "Over 90% of the code our team ships today is written by AI." | Spenser Skates, CEO | [Motley Fool — Q1 2026 transcript](https://www.fool.com/earnings/call-transcripts/2026/05/07/amplitude-ampl-q1-2026-earnings-transcript/) | Call 2026-05-06 |
| "We're talking about Statsig as a partnership, not an acquisition." | Spenser Skates, CEO | [Motley Fool — Q1 2026 transcript](https://www.fool.com/earnings/call-transcripts/2026/05/07/amplitude-ampl-q1-2026-earnings-transcript/) | Call 2026-05-06 |
| Margin pressure driven by "growth in inference costs as adoption of our AI tools by our customers outpaced our expectations." | Andrew Casey, CFO | [Motley Fool — Q1 2026 transcript](https://www.fool.com/earnings/call-transcripts/2026/05/07/amplitude-ampl-q1-2026-earnings-transcript/) | Call 2026-05-06 |

The CFO line is the most strategically revealing for Accel: **Amplitude's customers are adopting AI features faster than expected.** Demand for AI-driven answers is real and growing. The constraint on the *quality* of those answers is the context the agents can reach.

### Verified financial trajectory

| Metric | Q4 2025 | Q1 2026 | Source |
|---|---|---|---|
| Revenue | $91.4M (+17% YoY) | $93.5M (+17% YoY) | [8-K / Motley Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/05/07/amplitude-ampl-q1-2026-earnings-transcript/) |
| ARR | $366M (+17% YoY) | $374M (+17% YoY) | same |
| $100K+ ARR customers | 698 (+18% YoY) | 727 (+18% YoY) | same |
| $1M+ ARR customers | 56 (+33% YoY) | — | Q4 2025 call |
| Net dollar retention | 105% | 106% | same |
| Multi-product ARR share | — | 77% | Q1 2026 call |
| FY2026 revenue guidance | — | $397M–$403M (incl. Statsig) | same |

The story these numbers tell: **enterprise and expansion are the growth engine** (NRR ticking up, $100K+ and $1M+ cohorts growing fastest, 77% of ARR now multi-product). Expansion intelligence — knowing *which accounts are ready to grow and why* — maps directly to how Amplitude makes money.

### Amplitude's AI product surface (launched Feb 17, 2026)

Source: [Amplitude press — "Agentic AI Analytics for the Next Era of Product Experiences"](https://amplitude.com/press/amplitude-introduces-agentic-ai-analytics-for-the-next-era-of-product-experiences) (2026-02-17); [AI Agents launch blog](https://amplitude.com/blog/amplitude-ai-agents-launch). *Descriptions paraphrased from official materials.*

- **Global Agent** — a system-wide conversational agent: ask complex questions in plain language; it analyzes data, builds dashboards, investigates root causes, and takes action inside Amplitude.
- **MCP (Model Context Protocol) support** — Amplitude behavioral data is exposed to external tools; named integration partners include Anthropic (Claude), OpenAI (ChatGPT), Cursor, Figma, Lovable, Notion, GitHub, and Slack.
- **AI Feedback Agent** — turns unstructured feedback from surveys, support tickets, and Slack into actionable themes.
- **Session Replay Agent** — continuously reviews sessions to surface friction (rage clicks, dead clicks, JS errors) and quantify revenue impact.
- **Dashboard Monitoring Agent** — detects meaningful metric changes within hours and explains *why*.
- **Web Experimentation Agent** — designs, launches, and analyzes experiments.
- **Agent Analytics** — a distinct product for teams *building* AI agents; sits "between product analytics and LLM observability." ([blog](https://amplitude.com/blog/agent-analytics))

### Inorganic strategy (verified real)

| Move | Date | Source | Strategic read |
|---|---|---|---|
| Acquired **Command AI** (CommandBar) | 2024-10-15 | [blog](https://amplitude.com/blog/amplitude-acquires-command-ai) | In-product AI assistance → make every insight actionable |
| Acquired **Kraftful** | 2025-08-11 | [blog](https://amplitude.com/blog/amplitude-acquires-kraftful) | AI synthesis of **customer feedback / voice** → directly adjacent to Accel's feedback layer |
| Acquired **InfiniGrow** | 2026-01-14 | [press](https://amplitude.com/press/amplitude-acquires-infinigrow) | AI revenue/marketing analytics for marketers |
| **Statsig** partnership | 2026-05-05 | [blog](https://amplitude.com/blog/amplitude-and-statsig-partnership) | Experimentation breadth; ~$16M incremental ARR |

The Kraftful acquisition is the single most important signal for this engagement: **Amplitude is already buying the capability to synthesize customer feedback into themes.** Accel's external-feedback layer is the *supply side* of exactly that capability — it feeds the synthesizer Amplitude just bought.

---

## 2. Strategic gaps this dataset is designed to fill

Each gap is framed as a question Amplitude's product cannot answer today from its own data, and that this dataset answers.

1. **The "why behind the behavior" gap.** Amplitude sees *that* activation dropped or a feature stalled. It cannot see that the same week, 18 new G2 reviews cited a missing integration, or that Reddit threads are comparing the product unfavorably to a competitor. Amplitude's data is endogenous (inside the product); the *cause* is frequently exogenous (the market). **This dataset is the external-signal layer that lets Amplitude's agents explain causation, not just report correlation.**

2. **The expansion-timing gap.** With NRR at 106% and expansion driving growth, Amplitude monetizes by knowing *which accounts are ready to grow*. Amplitude's own data shows in-product usage; it does not show that an account just raised a round, opened five product-analyst roles mentioning experimentation, and launched in a new geography — the leading indicators of expansion readiness. **This dataset turns Audiences and account scoring into forward-looking expansion intelligence.**

3. **The agent-context gap (the CFO's problem).** Amplitude's agents are being adopted faster than expected, and inference cost is rising. The differentiator between Amplitude's agents and a generic LLM is *context the LLM cannot otherwise reach*. Today that context stops at the edge of the customer's own event stream. Once these external signals land in Amplitude's semantic model as **account (group) properties** — via the Group Identify API / warehouse import, *not* MCP, which is outbound-only ([docs](https://amplitude.com/docs/apis/analytics/group-identify)) — the Global Agent can read and cite them when answering customer-health and expansion questions. **This dataset is privileged external context an Amplitude agent can ground its answers in — context a raw model does not have.**

4. **The *external-account* voice gap (distinct from AI Feedback).** Amplitude's AI Feedback Agent already connects G2, Reddit, Trustpilot, and app-store reviews ([ai-feedback](https://amplitude.com/ai-feedback)) — but it synthesizes the *customer's own* voice about the *customer's own* product, tied to the customer's own behavioral data. It does not build a graph of the *market's* voice about the *other companies in the customer's B2B account base*. **This dataset supplies external customer voice at the account-graph level — feedback, pain themes, and competitive language about prospects and accounts — which AI Feedback's own-product VoC pipeline is not designed to source.** It is complementary supply, not a duplicate.

5. **The competitive-pressure gap.** Nothing in Amplitude's product tells a PM that a peer company removed a competitor from its integrations page, or that "switching away from X" language is rising in that company's reviews. **This dataset adds a competitive-pressure signal that maps to displacement and win-back motions.**

---

## 3. Buyer-specific value proposition (in Amplitude's own language)

Amplitude already captures what happens inside the product. The **External Product Intelligence Graph** adds the external market-signal layer so that Amplitude's AI Agents can explain *why* behavior changed, *where* customer pain is emerging, *which* competitors are creating pressure, and *which* accounts are ready to expand — joined to Amplitude's account model on company domain, delivered as account properties, Audience triggers, and agent context. It is the supply side of the customer-voice and expansion-intelligence capabilities Amplitude is already investing in (Kraftful, AI Feedback, Audiences, Global Agent via MCP): a privileged, evidence-backed context layer that makes every agent answer more grounded, every audience more predictive, and every expansion play better-timed — turning Amplitude's agents from "what happened in your product" into "what's happening in your market, and what to do about it."

---

*Every claim above is tied to a named source. Items not independently verifiable to the word are marked paraphrase and excluded from quotation. See `docs/competitive_positioning.md` for why this layer cannot simply be bought off the shelf, and `docs/integration_architecture.md` for how it lands inside Amplitude's surfaces.*
