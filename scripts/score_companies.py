"""Phase 8 (Phase-1 subset) — scoring from collected facts.

Computes only the sub-scores supported by Phase-1 data (product motion, maturity,
hiring, AI-readiness, market events, freshness) plus the product-fit scores those
support. Feedback- and competitive-pressure-dependent scores (ai_feedback_fit,
customer_success_fit, external_feedback_*, competitive_pressure) are NOT computed
because those sources are off-limits in Phase 1 -> left null (R6). The composite
is stored as overall_amplitude_fit_score_partial and clearly flagged. Scores are
derived -> inference_flag=1 with inference_basis (R4).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E

COUNT_FIELDS = ["open_jobs_count", "product_jobs_count", "data_jobs_count",
                "analytics_jobs_count", "growth_jobs_count", "product_ops_jobs_count",
                "ai_jobs_count", "recent_product_launches"]


def latest_facts(conn, cid):
    """field -> (value, confidence) using the highest-confidence row per field."""
    out = {}
    for r in conn.execute(
        "SELECT field_name,value,confidence FROM facts WHERE company_id=? ORDER BY confidence DESC", (cid,)):
        out.setdefault(r["field_name"], (r["value"], r["confidence"]))
    return out


def as_bool(facts, field):
    return 1.0 if field in facts and str(facts[field][0]).lower() == "true" else 0.0


def as_num(facts, field):
    try:
        return float(facts[field][0])
    except (KeyError, ValueError):
        return 0.0


def build_norm(conn, cids):
    """Per-field 95th-percentile-capped max for min-max normalization (min=0)."""
    caps = {}
    for f in COUNT_FIELDS:
        vals = []
        for cid in cids:
            row = conn.execute(
                "SELECT value FROM facts WHERE company_id=? AND field_name=? ORDER BY confidence DESC LIMIT 1",
                (cid, f)).fetchone()
            if row:
                try:
                    vals.append(float(row["value"]))
                except ValueError:
                    pass
        if vals:
            vals.sort()
            idx = max(0, int(round(0.95 * (len(vals) - 1))))
            caps[f] = max(1.0, vals[idx])
        else:
            caps[f] = 1.0
    return caps


def norm(facts, field, caps):
    return min(1.0, as_num(facts, field) / caps.get(field, 1.0))


def store_score(conn, cid, field, value, basis, src_url="score://phase1"):
    E.store_fact(conn, cid, field, round(value, 1), "score", src_url,
                 basis, 0.7, inference_flag=1, inference_basis=basis)


def score_company(conn, cid, name, caps):
    f = latest_facts(conn, cid)
    s = {}
    # product_led_growth (drop self-serve input; renormalize over 3)
    s["product_led_growth_score"] = 100 * (
        0.33 * as_bool(f, "has_free_trial") + 0.33 * as_bool(f, "has_freemium")
        + 0.34 * as_bool(f, "has_public_pricing"))
    # product_maturity (drop mobile/integration_breadth; renormalize over 3)
    s["product_maturity_score"] = 100 * (
        0.34 * as_bool(f, "has_api_docs") + 0.33 * as_bool(f, "has_changelog")
        + 0.33 * as_bool(f, "has_integrations_page"))
    # hiring_signal (config weights, renormalized over available count inputs)
    s["hiring_signal_score"] = 100 * (
        0.27 * norm(f, "product_jobs_count", caps) + 0.22 * norm(f, "data_jobs_count", caps)
        + 0.22 * norm(f, "analytics_jobs_count", caps) + 0.16 * norm(f, "growth_jobs_count", caps)
        + 0.13 * norm(f, "product_ops_jobs_count", caps))
    # ai_readiness_hiring
    s["ai_readiness_hiring_score"] = 100 * (
        0.7 * norm(f, "ai_jobs_count", caps) + 0.3 * norm(f, "data_jobs_count", caps))
    # market_event (recent launches + AI announcement)
    s["market_event_score"] = 100 * min(1.0,
        0.7 * norm(f, "recent_product_launches", caps) + 0.3 * as_bool(f, "recent_ai_announcement"))
    # freshness: launch recency if present, else collection-fresh (=100, all today)
    s["freshness_score"] = 100.0  # all facts extracted today

    for k, v in s.items():
        store_score(conn, cid, k, v, f"phase1 inputs: {k}")

    # product-fit scores (partial; only the computable ones)
    paf = (0.40 * s["product_led_growth_score"] + 0.30 * s["product_maturity_score"]
           + 0.30 * (100 if "detected_product_analytics_tools" in f else 0))
    store_score(conn, cid, "product_analytics_fit_score", paf,
                "PLG + maturity + own product-analytics stack detected")
    gaf = (0.4 * s["product_maturity_score"] + 0.2 * 100 * as_bool(f, "has_api_docs")
           + 0.2 * 100 * as_bool(f, "has_integrations_page") + 0.2 * 100 * norm(f, "data_jobs_count", caps))
    store_score(conn, cid, "global_agent_fit_score", gaf,
                "maturity + API docs + integrations + data hiring (partial)")
    eif = (0.4 * s["hiring_signal_score"] + 0.4 * s["market_event_score"]
           + 0.2 * 100 * as_bool(f, "recent_ai_announcement"))
    store_score(conn, cid, "expansion_intelligence_fit_score", eif,
                "hiring + recent launches + AI announcement (funding/exec not yet collected)")

    # PARTIAL composite over available components (feedback/competitive excluded, renormalized)
    comp = {
        "product_led_growth_score": 0.27, "product_maturity_score": 0.20,
        "hiring_signal_score": 0.20, "ai_readiness_hiring_score": 0.13,
        "market_event_score": 0.13, "freshness_score": 0.07,
    }
    overall = sum(s[k] * w for k, w in comp.items())
    store_score(conn, cid, "overall_amplitude_fit_score_partial", overall,
                "PARTIAL: excludes feedback & competitive-pressure signals (off-limits in Phase 1)")
    E.log(conn, "phase8.score", "ok", f"{name}: partial fit {overall:.0f}", cid)
    return overall, s


def main():
    conn = E.connect()
    rows = conn.execute("SELECT id, company_name FROM companies ORDER BY id").fetchall()
    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only and only.isdigit():
        rows = rows[: int(only)]
    cids = [r["id"] for r in rows]
    caps = build_norm(conn, cids)
    for r in rows:
        overall, s = score_company(conn, r["id"], r["company_name"], caps)
        print(f"  [{r['id']:>2}] {r['company_name']:<12} partial_fit={overall:5.1f}  "
              f"plg={s['product_led_growth_score']:.0f} mat={s['product_maturity_score']:.0f} "
              f"hire={s['hiring_signal_score']:.0f} ai={s['ai_readiness_hiring_score']:.0f}")
    print("Scoring complete (Phase-1 partial).")


if __name__ == "__main__":
    main()
