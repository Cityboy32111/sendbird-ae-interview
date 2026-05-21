"""Step 9: Score accounts internally and build account-specific briefings.

Computes a weighted 0-100 score across eight dimensions, assigns a priority
tier, and writes account-specific managed-IT trigger, call rationale, opening
line, and discovery question. Briefings reference the account's own signals, not
generic vertical templates. The scoring formula stays internal.
"""
import argparse

import common as c


def _employee_fit(acc, curve):
    lo = acc.get("estimated_employees_min", 0)
    hi = acc.get("estimated_employees_max", 0)
    mid = (lo + hi) / 2 if hi else 0
    imin, imax = curve["ideal_min"], curve["ideal_max"]
    buf = curve["near_range_buffer"]
    if imin <= mid <= imax:
        return curve["in_range_score"]
    if (imin - buf) <= mid <= (imax + buf):
        return curve["near_range_score"]
    return curve["out_of_range_score"]


def _security_gap(acc, rules):
    sig = acc.get("website_signals", {})
    internal = acc.get("domain_scan_internal", {})
    s = rules["security_gap_signals"]
    score = 0
    if not internal.get("https"):
        score += s["no_https"]
    if internal.get("email_auth_complete") is not True:
        score += s["missing_email_authentication"]
    if internal.get("weak_security_headers"):
        score += s["weak_security_headers"]
    if sig.get("forms_detected") or sig.get("payment_detected"):
        score += s["unprotected_forms"]
    if sig.get("portal_detected"):
        score += s["exposed_portal"]
    return min(score, s["max"])


def _operational(acc, rules):
    sig = acc.get("website_signals", {})
    s = rules["operational_complexity_signals"]
    score = 0
    if sig.get("num_locations", 1) > 1:
        score += s["multiple_locations"]
    if sig.get("portal_detected"):
        score += s["online_portal"]
    if sig.get("booking_detected"):
        score += s["online_booking"]
    if sig.get("payment_detected"):
        score += s["online_payment"]
    if sig.get("services_count", 0) >= 8:
        score += s["many_services"]
    return min(score, s["max"])


def _growth(acc, rules):
    sig = acc.get("website_signals", {})
    s = rules["growth_activity_signals"]
    score = 0
    if sig.get("careers_detected"):
        score += s["careers_page"]
    if sig.get("hiring_keywords"):
        score += s["hiring_keywords"]
    if (acc.get("review_count") or 0) >= 100:
        score += s["high_review_count"]
    return min(score, s["max"])


def _reachability(acc):
    score = 2
    if acc.get("main_phone"):
        score += 1
    if acc.get("linkedin_company_url"):
        score += 1
    if acc.get("emails_found"):
        score += 1
    return min(score, 5)


def _build_briefing(acc, verticals_cfg):
    vert = acc.get("vertical", "")
    sub = acc.get("sub_vertical", "") or vert
    city = acc.get("city", "the area")
    company = acc.get("company_name", "the practice")
    sig = acc.get("website_signals", {})
    vinfo = verticals_cfg["keep_verticals"].get(vert, {})
    compliance = vinfo.get("compliance_angle", "Operates business-critical systems with sensitive records")
    staff = sig.get("staff_count", 0)
    emp = acc.get("estimated_employees_display", "")
    risk = acc.get("specific_visible_risk", "")

    triggers = []
    if sig.get("portal_detected"):
        triggers.append("an online client/patient portal")
    if sig.get("payment_detected"):
        triggers.append("online payments")
    if sig.get("booking_detected"):
        triggers.append("online booking")
    if sig.get("forms_detected"):
        triggers.append("intake forms collecting personal data")
    if sig.get("num_locations", 1) > 1:
        triggers.append(f"{sig['num_locations']} locations to keep in sync")
    if sig.get("careers_detected") or sig.get("hiring_keywords"):
        triggers.append("active hiring/growth")
    if not triggers:
        triggers.append("cloud-based workflows handling sensitive records")
    trigger_text = ", ".join(triggers[:3])

    managed_it_trigger = (
        f"{sub} in {city} ({emp} employees) running {trigger_text}. {risk}."
    )
    why = (
        f"{company} is a {sub.lower()} in {city} with an estimated {emp} staff. "
        f"{compliance}. The business runs {trigger_text}, and {risk.lower()}. "
        f"This is a strong managed IT fit for proactive backup, email security, and endpoint management."
    )
    opening = (
        f"Hi, I work with {sub.lower()} practices around {city} on keeping client data secure and "
        f"systems running without downtime. I noticed {company} {('runs ' + trigger_text) if trigger_text else 'handles sensitive client information'} "
        f"and wanted to ask one quick question."
    )
    discovery_map = {
        "Legal": "How are you currently protecting privileged client files and making sure they're backed up if a device is lost or compromised?",
        "Dental": "How are you handling patient data backup and HIPAA safeguards across your front desk and treatment systems today?",
        "Medical": "How are you currently securing patient records and keeping your scheduling and EHR systems up if something goes down?",
        "CPA and Accounting": "During tax season, how are you protecting client financial documents and meeting the IRS data safeguard requirements?",
        "Insurance and Financial": "How are you protecting client financial and policy data, and who handles it if your email or systems go down?",
        "Commercial SMB": "If your systems or email went down for a day, what would that cost the business, and who handles IT today?",
    }
    discovery = discovery_map.get(vert, discovery_map["Commercial SMB"])

    acc["managed_it_trigger"] = managed_it_trigger
    acc["why_cmit_should_call"] = why
    acc["recommended_opening_line"] = opening
    acc["suggested_discovery_question"] = discovery
    acc["compliance_angle"] = compliance


def score_all(week):
    log = c.get_logger("score_accounts", week)
    rules = c.load_config("scoring_rules.json")
    verticals_cfg = c.load_config("target_verticals.json")
    accounts = c.load_json(c.processed_path(week, "accounts_scanned.json"), []) or []
    dims = rules["dimensions"]
    curve = rules["employee_fit_curve"]

    for acc in accounts:
        vinfo = verticals_cfg["keep_verticals"].get(acc.get("vertical", ""), {})
        raw = {
            "vertical_fit": vinfo.get("base_vertical_fit", 3),
            "employee_fit": _employee_fit(acc, curve),
            "data_sensitivity": vinfo.get("data_sensitivity", 3),
            "security_gap": _security_gap(acc, rules),
            "operational_complexity": _operational(acc, rules),
            "growth_activity": _growth(acc, rules),
            "buyer_reachability": _reachability(acc),
            "local_fit": 5 if acc.get("city", "").lower() in ("glendale", "pasadena", "burbank", "la canada flintridge") else 4,
        }
        weighted = sum(raw[d] / dims[d]["max"] * dims[d]["weight"] for d in dims)
        max_weighted = sum(dims[d]["weight"] for d in dims)
        total = round(weighted / max_weighted * 100, 1)
        acc["score_dimensions"] = raw
        acc["total_score"] = total

        tier = "D"
        for t, info in rules["priority_tiers"].items():
            if total >= info["min_score"]:
                tier = t
                break
        acc["priority_tier"] = tier
        acc["priority_tier_label"] = rules["priority_tiers"][tier]["label"]
        _build_briefing(acc, verticals_cfg)

    accounts.sort(key=lambda a: a["total_score"], reverse=True)
    c.save_json(c.processed_path(week, "accounts_scored.json"), accounts)
    log.info("scored %d accounts; top score=%.1f", len(accounts), accounts[0]["total_score"] if accounts else 0)
    return accounts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    score_all(args.week)
