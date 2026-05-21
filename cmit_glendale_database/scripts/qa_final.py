"""Step 13: QA the final set. The workbook does not ship unless QA passes.

Validates the final records against the hard checks in qa_rules.json and scans
all client-facing text for forbidden methodology terms. Writes qa_results.json
(consumed by build_workbook). Returns pass/fail; the orchestrator gates on it.
"""
import argparse

import common as c

CLIENT_TEXT_FIELDS = [
    "managed_it_trigger", "specific_visible_risk", "compliance_angle",
    "why_cmit_should_call", "recommended_opening_line", "suggested_discovery_question",
    "source_evidence", "security_posture_summary", "email_security_summary",
    "website_security_summary",
]


def run_qa(week):
    log = c.get_logger("qa_final", week)
    rules = c.load_config("qa_rules.json")
    cities_cfg = c.load_config("la_county_cities.json")
    title_cfg = c.load_config("title_filters.json")
    excl = c.load_json(c.processed_path(week, "exclusions_active.json"), {}) or {}
    final = c.load_json(c.processed_path(week, "accounts_final.json"), []) or []

    allow_cities = {x.lower() for x in cities_cfg["cities"]}
    accepted_titles = [t.lower() for t in title_cfg["accepted_titles"]]
    info_parts = set(rules["info_email_local_parts"])
    forbidden = [t.lower() for t in rules["forbidden_workbook_terms"]]
    target = rules["required_final_count"]

    domains = [c.normalize_domain(a.get("domain")) for a in final]
    emails = [(a.get("verified_email") or "").lower() for a in final]

    def all_true(pred):
        return all(pred(a) for a in final) if final else False

    def is_real_person(a):
        nm = (a.get("decision_maker") or "").strip()
        return bool(nm) and len(nm.split()) >= 2 and c.normalize_company(nm) != c.normalize_company(a.get("company_name"))

    def has_title(a):
        t = (a.get("decision_maker_title") or "").lower()
        return bool(t) and any(acc in t for acc in accepted_titles)

    def is_la(a):
        return (a.get("county") == "Los Angeles County") or ((a.get("city") or "").lower() in allow_cities)

    def email_ok(a):
        e = (a.get("verified_email") or "").lower()
        if "@" not in e:
            return False
        local = e.split("@")[0]
        return local not in info_parts and a.get("email_status") in ("verified", "likely to engage")

    def not_info(a):
        return (a.get("verified_email") or "").split("@")[0].lower() not in info_parts

    def not_business_listing(a):
        e = (a.get("verified_email") or "").lower()
        return e not in {x.lower() for x in (a.get("emails_found") or [])} or not_info(a)

    def not_company_name(a):
        return c.normalize_company(a.get("decision_maker")) != c.normalize_company(a.get("company_name"))

    def not_solo(a):
        return (a.get("estimated_employees_max") or 0) >= 3 and is_real_person(a)

    def not_prior_dup(a):
        d = c.normalize_domain(a.get("domain"))
        e = (a.get("verified_email") or "").lower()
        return d not in set(excl.get("domains", [])) and e not in set(excl.get("emails", []))

    def no_methodology(a):
        blob = " ".join(str(a.get(f, "")) for f in CLIENT_TEXT_FIELDS).lower()
        return not any(term in blob for term in forbidden)

    checks = [
        ("Exactly {} final records".format(target), len(final) == target, f"{len(final)} records"),
        ("All real people", all_true(is_real_person), ""),
        ("All verified emails", all_true(email_ok), ""),
        ("All decision-maker titles", all_true(has_title), ""),
        ("All LA County accounts", all_true(is_la), ""),
        ("All have a website", all_true(lambda a: bool(a.get("website"))), ""),
        ("Unique domains", len(domains) == len(set(domains)) and "" not in domains, f"{len(set(domains))} unique"),
        ("Unique emails", len(emails) == len(set(emails)) and "" not in emails, f"{len(set(emails))} unique"),
        ("Zero info-only contacts", all_true(not_info), ""),
        ("Zero business-listing-only contacts", all_true(not_business_listing), ""),
        ("Zero company-name contacts", all_true(not_company_name), ""),
        ("Zero obvious solo operators", all_true(not_solo), ""),
        ("Zero prior-run duplicates", all_true(not_prior_dup), ""),
        ("Zero methodology exposure", all_true(no_methodology), ""),
        ("Every account has a managed IT trigger", all_true(lambda a: bool(a.get("managed_it_trigger"))), ""),
        ("Every account has an opening line", all_true(lambda a: bool(a.get("recommended_opening_line"))), ""),
        ("Every account has source evidence", all_true(lambda a: bool(a.get("source_evidence"))), ""),
    ]

    results = [{"name": n, "passed": bool(p), "detail": d} for n, p, d in checks]
    status = "pass" if all(r["passed"] for r in results) else "fail"
    qa = {"week": week, "status": status, "final_count": len(final), "checks": results, "generated_at": c.now_iso()}
    c.save_json(c.processed_path(week, "qa_results.json"), qa)

    for r in results:
        log.info("[%s] %s %s", "PASS" if r["passed"] else "FAIL", r["name"], f"({r['detail']})" if r["detail"] else "")
    log.info("QA overall: %s (%d/%d final)", status.upper(), len(final), target)
    if status != "pass":
        log.warning("QA FAILED - do not ship. Move failed records to backup; return to Apollo queue or scrape more.")
    return qa


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    run_qa(args.week)
