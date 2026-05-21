"""Phase 11 (Phase-1 subset) — confidence-filtered exports + evidence file.

R1: only facts with confidence >= 0.6 appear in deliverables; below-floor values
remain in the DB but are nulled here. R6: fields with no qualifying fact are null.
Writes:
  outputs/external_product_intelligence_graph.csv  (flat, confidence-filtered)
  outputs/external_product_intelligence_graph.json (nested w/ evidence refs)
  outputs/source_evidence.json                     (every evidence span + URL + date)
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E

FIELDS = [
    "has_public_pricing", "pricing_url", "has_free_trial", "has_freemium",
    "has_api_docs", "api_docs_url", "has_changelog", "changelog_url",
    "has_integrations_page", "integrations_url",
    "detected_analytics_tools", "detected_product_analytics_tools", "technographic_confidence",
    "amplitude_detected", "mixpanel_detected", "posthog_detected", "heap_detected",
    "pendo_detected", "segment_detected", "ga4_detected", "fullstory_detected", "hotjar_detected",
    "open_jobs_count", "product_jobs_count", "analytics_jobs_count", "data_jobs_count",
    "growth_jobs_count", "ai_jobs_count", "customer_success_jobs_count", "product_ops_jobs_count",
    "recent_product_launch_90d", "most_recent_launch_date", "recent_product_launches",
    "recent_ai_announcement",
    "product_led_growth_score", "product_maturity_score", "hiring_signal_score",
    "ai_readiness_hiring_score", "market_event_score", "freshness_score",
    "product_analytics_fit_score", "global_agent_fit_score", "expansion_intelligence_fit_score",
    "overall_amplitude_fit_score_partial",
]


def filtered_facts(conn, cid):
    """field -> dict(value, confidence, source_url, evidence_id, extraction_date,
    inference_flag) for the highest-confidence fact >= floor."""
    out = {}
    for r in conn.execute(
        "SELECT field_name,value,confidence,source_url,evidence_id,extraction_date,inference_flag"
        " FROM facts WHERE company_id=? AND confidence>=? ORDER BY confidence DESC",
        (cid, E.CONFIDENCE_FLOOR)):
        out.setdefault(r["field_name"], dict(
            value=r["value"], confidence=r["confidence"], source_url=r["source_url"],
            evidence_id=r["evidence_id"], extraction_date=r["extraction_date"],
            inference_flag=r["inference_flag"]))
    return out


def main():
    conn = E.connect()
    out_dir = os.path.join(E.ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    companies = conn.execute("SELECT * FROM companies ORDER BY id").fetchall()

    flat_rows, nested, n_nonnull = [], [], 0
    for c in companies:
        ff = filtered_facts(conn, c["id"])
        row = {"company_name": c["company_name"], "website": c["website"],
               "seed_category": c["seed_category"]}
        node = {"company_name": c["company_name"], "website": c["website"], "fields": {}}
        for field in FIELDS:
            if field in ff:
                row[field] = ff[field]["value"]
                node["fields"][field] = ff[field]
                n_nonnull += 1
            else:
                row[field] = ""  # null per R1/R6
        flat_rows.append(row)
        nested.append(node)

    csv_path = os.path.join(out_dir, "external_product_intelligence_graph.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["company_name", "website", "seed_category"] + FIELDS)
        w.writeheader()
        w.writerows(flat_rows)

    json_path = os.path.join(out_dir, "external_product_intelligence_graph.json")
    with open(json_path, "w") as f:
        json.dump({"generated": E.TODAY, "phase": "1",
                   "confidence_floor": E.CONFIDENCE_FLOOR,
                   "note": "Phase-1 sample (25 companies). Feedback & competitive-pressure "
                           "fields intentionally absent (sources off-limits in Phase 1).",
                   "companies": nested}, f, indent=2)

    # evidence file
    ev = []
    for r in conn.execute(
        "SELECT f.company_id,c.company_name,f.field_name,f.value,f.confidence,e.source_url,"
        "e.evidence_span,e.extraction_date,f.inference_flag FROM facts f "
        "JOIN evidence e ON f.evidence_id=e.id JOIN companies c ON c.id=f.company_id "
        "WHERE f.confidence>=? ORDER BY f.company_id", (E.CONFIDENCE_FLOOR,)):
        ev.append(dict(company=r["company_name"], field=r["field_name"], value=r["value"],
                       confidence=r["confidence"], source_url=r["source_url"],
                       evidence_span=r["evidence_span"], extraction_date=r["extraction_date"],
                       inference_flag=r["inference_flag"]))
    ev_path = os.path.join(out_dir, "source_evidence.json")
    with open(ev_path, "w") as f:
        json.dump({"generated": E.TODAY, "count": len(ev), "evidence": ev}, f, indent=2)

    print(f"Exported {len(companies)} companies, {n_nonnull} non-null fields (>= {E.CONFIDENCE_FLOOR}).")
    print(f"  {csv_path}\n  {json_path}\n  {ev_path} ({len(ev)} evidence rows)")


if __name__ == "__main__":
    main()
