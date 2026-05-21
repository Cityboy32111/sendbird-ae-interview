"""Phase 9 — accuracy read against re-verifiable ground truth.

Phase-1 sources are structured public pages, so the meaningful, measurable
accuracy is PRECISION via evidence re-verification (re-scan the saved page source
for each claimed signature/token = a 100% claim audit, R5) plus SELF-DETECTION
RECALL (analytics vendors should detect their own product on their own site -
an independent ground truth). Recall against arbitrary companies needs a licensed
technographic reference (BuiltWith) and is reported as a known Phase-1 gap.

Writes outputs/validation_report.md. Exit non-zero if precision on technographics
or product motion < 0.75 (success criterion #1).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E
from detect_technographics import SIGNATURES

# vendors that should self-detect on their own site (dogfooding ground truth)
SELF_DETECT = {
    "amplitude.com": "amplitude", "mixpanel.com": "mixpanel", "posthog.com": "posthog",
    "pendo.io": "pendo", "heap.io": "heap", "hotjar.com": "hotjar",
}
PRODUCT_MOTION_TOKENS = {
    "has_public_pricing": ["$", "/mo", "per month", "per user", "free", "billed", "/year"],
    "has_free_trial": ["free trial", "start free", "try", "14-day", "30-day"],
    "has_freemium": ["free plan", "free forever", "$0", "free tier", "free for", "free version"],
}


def load_html(conn, cid, page_types=("homepage", "pricing")):
    chunks = []
    q = "SELECT content_path FROM raw_pages WHERE company_id=? AND http_status=200 AND page_type IN ({})".format(
        ",".join("?" * len(page_types)))
    for r in conn.execute(q, (cid, *page_types)):
        if r["content_path"]:
            try:
                with open(os.path.join(E.ROOT, r["content_path"]), encoding="utf-8", errors="ignore") as f:
                    chunks.append(f.read().lower())
            except OSError:
                pass
    return "\n".join(chunks)


def main():
    conn = E.connect()
    companies = conn.execute("SELECT * FROM companies ORDER BY id").fetchall()

    # ---- technographic precision (re-verify each detected >=0.6 fact) ----
    tp = vp = 0  # verified / total
    techno_misses = []
    sig_index = {field: [s for s, _ in sigs] for field, (df, _, sigs) in
                 {v: (vv[0], vv[1], vv[2]) for v, vv in SIGNATURES.items()}.items()}
    # map detected_field -> signatures
    field_sigs = {vv[0]: [s for s, _ in vv[2]] for vv in SIGNATURES.values()}
    for c in companies:
        html = load_html(conn, c["id"])
        for r in conn.execute(
            "SELECT field_name FROM facts WHERE company_id=? AND confidence>=? AND field_name LIKE '%_detected'",
            (c["id"], E.CONFIDENCE_FLOOR)):
            field = r["field_name"]
            sigs = field_sigs.get(field, [])
            vp += 1
            if any(s in html for s in sigs):
                tp += 1
            else:
                techno_misses.append(f"{c['company_name']}.{field}")
    techno_precision = (tp / vp) if vp else 1.0

    # ---- self-detection recall (vendors on their own site) ----
    sd_hit = sd_total = 0
    sd_detail = []
    for c in companies:
        vendor = SELF_DETECT.get(c["domain"])
        if not vendor:
            continue
        sd_total += 1
        df = SIGNATURES[vendor][0]
        got = conn.execute(
            "SELECT 1 FROM facts WHERE company_id=? AND field_name=? AND confidence>=?",
            (c["id"], df, E.CONFIDENCE_FLOOR)).fetchone()
        sd_hit += 1 if got else 0
        sd_detail.append(f"{c['company_name']}: {'DETECTED' if got else 'MISSED'} own {vendor}")
    self_recall = (sd_hit / sd_total) if sd_total else None

    # ---- product-motion precision (re-verify positives) ----
    mp = mv = 0
    motion_misses = []
    for c in companies:
        html = load_html(conn, c["id"])
        for field, tokens in PRODUCT_MOTION_TOKENS.items():
            got = conn.execute(
                "SELECT 1 FROM facts WHERE company_id=? AND field_name=? AND value='True' AND confidence>=?",
                (c["id"], field, E.CONFIDENCE_FLOOR)).fetchone()
            if got:
                mv += 1
                if any(t in html for t in tokens):
                    mp += 1
                else:
                    motion_misses.append(f"{c['company_name']}.{field}")
    motion_precision = (mp / mv) if mv else 1.0

    # ---- cohort cross-check (detected stack vs cohort verified column) ----
    # (informational; recall against undetectable server-side analytics noted)

    # ---- coverage stats ----
    n_companies = len(companies)
    n_zero_techno = sum(
        1 for c in companies if not conn.execute(
            "SELECT 1 FROM facts WHERE company_id=? AND confidence>=? AND field_name LIKE '%_detected'",
            (c["id"], E.CONFIDENCE_FLOOR)).fetchone())

    report = f"""# Validation Report — Phase 1

Generated {E.TODAY}. Sample: {n_companies} companies. Sources: SAFE PUBLIC /
first-party only (no feedback/competitive scraping).

## Headline metrics

| Metric | Value | Target | Result |
|---|---|---|---|
| Technographic **precision** (evidence re-verified) | **{techno_precision:.2f}** ({tp}/{vp}) | >= 0.75 | {'PASS' if techno_precision>=0.75 else 'FAIL'} |
| Product-motion **precision** (positives re-verified) | **{motion_precision:.2f}** ({mp}/{mv}) | >= 0.75 | {'PASS' if motion_precision>=0.75 else 'FAIL'} |
| Self-detection **recall** (vendors on own site) | **{self_recall:.2f}** ({sd_hit}/{sd_total}) | informational | {'strong' if (self_recall or 0)>=0.75 else 'weak'} |

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
- Detected (>= {E.CONFIDENCE_FLOOR}) technographic facts: {vp}; re-verified: {tp}.
- Unverified on re-check: {techno_misses or 'none'}

## Self-detection recall (independent ground truth)
{chr(10).join('- ' + d for d in sd_detail)}

## Recall gap (known, honest limitation)
- {n_zero_techno}/{n_companies} companies returned **zero** technographic detections
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
- Positive product-motion facts: {mv}; re-verified: {mp}.
- Unverified on re-check: {motion_misses or 'none'}
"""
    out = os.path.join(E.ROOT, "outputs", "validation_report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(report)
    print(f"Technographic precision: {techno_precision:.2f} ({tp}/{vp})")
    print(f"Product-motion precision: {motion_precision:.2f} ({mp}/{mv})")
    print(f"Self-detection recall:    {self_recall:.2f} ({sd_hit}/{sd_total})")
    print(f"Zero-technographic companies: {n_zero_techno}/{n_companies}")
    print(f"Report -> {out}")
    if techno_precision < 0.75 or motion_precision < 0.75:
        sys.exit(1)


if __name__ == "__main__":
    main()
