"""Phase 1.5 — load curated external-signal sample into local SQLite + emit outputs.

Phase 1.5 is a CONTROLLED SAMPLE, not bulk scraping. Signals are gathered by
single-URL public-page research (WebSearch + WebFetch) with strict compliance
(company/product-level only; no personal data/contacts; no login/paywalled;
short evidence spans only), then curated into config/phase15_signals.json with
full provenance. This loader ingests them into the external_signals table and
also stores each as a fact+evidence row, then writes:
  outputs/external_feedback_sample.csv
  outputs/external_feedback_sample.json
  refreshes outputs/source_evidence.json to include external signals.

Rules: G2/Capterra flagged demo_only (SCRAPED RISKY). Every signal carries
source_url, source_type, extraction_date, confidence, evidence_span. No fabrication.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E

SIGNALS_FILE = os.path.join(E.ROOT, "config", "phase15_signals.json")
DEMO_ONLY_SOURCES = {"g2", "capterra"}


def main():
    conn = E.connect()
    E.init_db(conn)
    if not os.path.exists(SIGNALS_FILE):
        print(f"Missing {SIGNALS_FILE}; nothing to load.")
        return
    data = json.load(open(SIGNALS_FILE))
    signals = data.get("signals", [])

    # reset prior Phase-1.5 load (idempotent re-run)
    conn.execute("DELETE FROM external_signals")
    conn.execute("DELETE FROM facts WHERE source_name LIKE 'ext:%'")
    conn.commit()

    name_to_id = {r["company_name"]: r["id"] for r in conn.execute("SELECT id,company_name FROM companies")}
    loaded = 0
    for s in signals:
        cid = name_to_id.get(s["company"])
        if cid is None:
            E.log(conn, "phase1_5.feedback", "warn", f"unknown company {s['company']}")
            continue
        demo = 1 if (s["source_type"] in DEMO_ONLY_SOURCES or s.get("demo_only")) else 0
        conn.execute(
            "INSERT INTO external_signals(company_id,source_type,source_url,theme,sentiment,"
            "evidence_span,confidence,extraction_date,demo_only,maps_to_amplitude)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)",
            (cid, s["source_type"], s["source_url"], s["theme"], s.get("sentiment", ""),
             s["evidence_span"][:240], float(s["confidence"]), s.get("extraction_date", E.TODAY),
             demo, s.get("maps_to_amplitude")))
        # also store as fact+evidence for unified provenance
        E.store_fact(conn, cid, f"ext:{s['source_type']}:{_slug(s['theme'])}", s["sentiment"],
                     f"ext:{s['source_type']}" + ("(demo-only)" if demo else ""), s["source_url"],
                     s["evidence_span"][:240], float(s["confidence"]),
                     inference_flag=0)
        loaded += 1
    conn.commit()
    E.log(conn, "phase1_5.feedback", "ok", f"loaded {loaded} external signals")

    _export(conn)
    print(f"Loaded {loaded} external signals across "
          f"{len({s['company'] for s in signals})} companies.")


def _slug(t):
    return "".join(ch if ch.isalnum() else "_" for ch in t.lower())[:40]


def _export(conn):
    out_dir = os.path.join(E.ROOT, "outputs")
    rows = []
    for r in conn.execute(
        "SELECT c.company_name, c.website, s.* FROM external_signals s "
        "JOIN companies c ON c.id=s.company_id ORDER BY c.company_name, s.source_type"):
        rows.append(dict(
            company=r["company_name"], website=r["website"], source_type=r["source_type"],
            source_url=r["source_url"], theme=r["theme"], sentiment=r["sentiment"],
            evidence_span=r["evidence_span"], confidence=r["confidence"],
            extraction_date=r["extraction_date"],
            demo_only=("yes" if r["demo_only"] else "no"),
            maps_to_amplitude=r["maps_to_amplitude"] or ""))

    csv_path = os.path.join(out_dir, "external_feedback_sample.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["company", "website", "source_type", "source_url",
            "theme", "sentiment", "evidence_span", "confidence", "extraction_date",
            "demo_only", "maps_to_amplitude"])
        w.writeheader()
        w.writerows(rows)

    # nested per-company
    by_co = {}
    for r in rows:
        by_co.setdefault(r["company"], {"company": r["company"], "website": r["website"], "signals": []})
        by_co[r["company"]]["signals"].append({k: r[k] for k in
            ("source_type", "source_url", "theme", "sentiment", "evidence_span",
             "confidence", "extraction_date", "demo_only", "maps_to_amplitude")})
    json_path = os.path.join(out_dir, "external_feedback_sample.json")
    with open(json_path, "w") as f:
        json.dump({"generated": E.TODAY, "phase": "1.5", "n_signals": len(rows),
                   "note": "Controlled external-signal sample. G2/Capterra are demo_only "
                           "(SCRAPED RISKY) - see docs/data_rights_matrix.md for production "
                           "replacement paths.",
                   "companies": list(by_co.values())}, f, indent=2)

    # refresh source_evidence.json to include BOTH phase-1 facts and phase-1.5 signals
    ev = []
    for r in conn.execute(
        "SELECT c.company_name, f.field_name, f.value, f.confidence, e.source_url, "
        "e.evidence_span, e.extraction_date, f.inference_flag, f.source_name FROM facts f "
        "JOIN evidence e ON f.evidence_id=e.id JOIN companies c ON c.id=f.company_id "
        "WHERE f.confidence>=? ORDER BY c.company_name", (E.CONFIDENCE_FLOOR,)):
        ev.append(dict(company=r["company_name"], field=r["field_name"], value=r["value"],
                       confidence=r["confidence"], source_name=r["source_name"],
                       source_url=r["source_url"], evidence_span=r["evidence_span"],
                       extraction_date=r["extraction_date"], inference_flag=r["inference_flag"]))
    with open(os.path.join(out_dir, "source_evidence.json"), "w") as f:
        json.dump({"generated": E.TODAY, "count": len(ev), "evidence": ev}, f, indent=2)
    print(f"  -> {csv_path}\n  -> {json_path}\n  -> outputs/source_evidence.json ({len(ev)} rows incl. external)")


if __name__ == "__main__":
    main()
