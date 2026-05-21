"""Step 14: Update master exclusion lists. Runs only after QA passes.

Appends the shipped final accounts' domains, emails, companies, LinkedIn URLs,
addresses, and phones to the six master exclusion files so future weekly runs
never re-surface the same accounts.
"""
import argparse

import common as c

MASTERS = {
    "domains": "exclusion_domains_master.json",
    "emails": "exclusion_emails_master.json",
    "companies": "exclusion_companies_master.json",
    "linkedin": "exclusion_linkedin_master.json",
    "addresses": "exclusion_addresses_master.json",
    "phones": "exclusion_phones_master.json",
}


def update(week, force=False):
    log = c.get_logger("update_exclusions", week)
    qa = c.load_json(c.processed_path(week, "qa_results.json"), {}) or {}
    if qa.get("status") != "pass" and not force:
        log.warning("QA status is '%s'; refusing to update exclusions. Use --force to override.", qa.get("status"))
        return False

    final = c.load_json(c.processed_path(week, "accounts_final.json"), []) or []
    additions = {k: [] for k in MASTERS}
    for a in final:
        if a.get("domain"):
            additions["domains"].append(a["domain"])
        if a.get("verified_email"):
            additions["emails"].append(a["verified_email"])
        if a.get("company_name"):
            additions["companies"].append(a["company_name"])
        if a.get("contact_linkedin") or a.get("linkedin_company_url"):
            additions["linkedin"].append(a.get("contact_linkedin") or a.get("linkedin_company_url"))
        if a.get("address"):
            additions["addresses"].append(a["address"])
        if a.get("main_phone"):
            additions["phones"].append(a["main_phone"])

    for key, fname in MASTERS.items():
        path = c.EXCLUSIONS_DIR / fname
        data = c.load_json(path, {}) or {}
        existing = data.get(key, [])
        merged = sorted(set(existing) | set(additions[key]))
        added = len(merged) - len(set(existing))
        data[key] = merged
        c.save_json(path, data)
        log.info("%s: +%d (total %d)", fname, added, len(merged))

    log.info("master exclusion lists updated for %s", week)
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    ap.add_argument("--force", action="store_true", help="update even if QA did not pass")
    args = ap.parse_args()
    c.load_env()
    update(args.week, args.force)
