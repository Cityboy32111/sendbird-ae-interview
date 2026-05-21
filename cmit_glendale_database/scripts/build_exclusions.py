"""Step 1: Build the active exclusion set from the master lists.

Consolidates the six master exclusion files into a single normalized lookup
written to data/processed/<week>/exclusions_active.json, used by filter_icp.
"""
import argparse

import common as c


def build(week):
    log = c.get_logger("build_exclusions", week)
    masters = {
        "domains": "exclusion_domains_master.json",
        "emails": "exclusion_emails_master.json",
        "companies": "exclusion_companies_master.json",
        "linkedin": "exclusion_linkedin_master.json",
        "addresses": "exclusion_addresses_master.json",
        "phones": "exclusion_phones_master.json",
    }
    active = {}
    for key, fname in masters.items():
        data = c.load_json(c.EXCLUSIONS_DIR / fname, {}) or {}
        raw = data.get(key, [])
        if key == "domains":
            norm = {c.normalize_domain(x) for x in raw}
        elif key == "emails":
            norm = {str(x).strip().lower() for x in raw}
        elif key == "companies":
            norm = {c.normalize_company(x) for x in raw}
        elif key == "phones":
            norm = {c.normalize_phone(x) for x in raw}
        elif key == "addresses":
            norm = {c.normalize_address(x) for x in raw}
        else:
            norm = {str(x).strip().lower().rstrip("/") for x in raw}
        active[key] = sorted(x for x in norm if x)
        log.info("loaded %d %s exclusions", len(active[key]), key)

    out = c.processed_path(week, "exclusions_active.json")
    c.save_json(out, active)
    log.info("wrote active exclusions -> %s", out)
    return active


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    build(args.week)
