"""Step 5: Apply hard ICP filtering.

Removes accounts that are out of LA County, have no website, are duplicates
(domain/company/phone/address), match a prior exclusion, are in a rejected
category, are national franchises, or look like solo operators. Numeric
employee-range filtering happens after estimation (score step).
"""
import argparse
import re

import common as c

SOLO_HINTS = [
    "law office of", "law offices of", "dds", "md", "cpa,", ", cpa",
    "attorney at law", "esq", "solo", "& associates",
]


def _is_la_county(acc, cities_cfg):
    city = (acc.get("city") or "").strip().lower()
    allow = {x.lower() for x in cities_cfg["cities"]}
    if city and city in allow:
        return True
    zp = str(acc.get("zip") or "")[:3]
    if zp and zp in set(cities_cfg.get("zip_prefixes", [])):
        return True
    return False


def _category_rejected(acc, verticals_cfg):
    cat = (acc.get("category") or "").lower()
    desc = (acc.get("business_description") or "").lower()
    blob = f"{cat} {desc}"
    for bad in verticals_cfg["reject_categories"]:
        if bad in blob:
            return bad
    return None


def _is_franchise(acc, verticals_cfg):
    name = (acc.get("company_name") or "").lower()
    for f in verticals_cfg["national_franchise_names"]:
        if f in name:
            return f
    return None


def _looks_solo(acc):
    name = (acc.get("company_name") or "").lower()
    return any(h in name for h in SOLO_HINTS)


def filter_accounts(week):
    log = c.get_logger("filter_icp", week)
    cities_cfg = c.load_config("la_county_cities.json")
    verticals_cfg = c.load_config("target_verticals.json")
    excl = c.load_json(c.processed_path(week, "exclusions_active.json"), {}) or {}
    accounts = c.load_json(c.processed_path(week, "accounts_normalized.json"), []) or []

    seen = {"domain": set(), "company": set(), "phone": set(), "address": set()}
    kept, removed = [], []

    def drop(acc, reason):
        acc = dict(acc)
        acc["_removed_reason"] = reason
        removed.append(acc)

    for acc in accounts:
        domain = c.normalize_domain(acc.get("domain"))
        ncompany = c.normalize_company(acc.get("company_name"))
        nphone = c.normalize_phone(acc.get("main_phone"))
        naddr = c.normalize_address(acc.get("address"))

        if not acc.get("website") or not domain:
            drop(acc, "no_website"); continue
        if not _is_la_county(acc, cities_cfg):
            drop(acc, "outside_la_county"); continue
        if domain in set(excl.get("domains", [])):
            drop(acc, "prior_exclusion_domain"); continue
        if ncompany in set(excl.get("companies", [])):
            drop(acc, "prior_exclusion_company"); continue
        if nphone and nphone in set(excl.get("phones", [])):
            drop(acc, "prior_exclusion_phone"); continue
        rej = _category_rejected(acc, verticals_cfg)
        if rej:
            drop(acc, f"irrelevant_category:{rej}"); continue
        fr = _is_franchise(acc, verticals_cfg)
        if fr:
            drop(acc, f"national_franchise:{fr}"); continue
        if domain in seen["domain"]:
            drop(acc, "duplicate_domain"); continue
        if ncompany in seen["company"]:
            drop(acc, "duplicate_company"); continue
        if nphone and nphone in seen["phone"]:
            drop(acc, "duplicate_phone"); continue
        if naddr and naddr in seen["address"]:
            drop(acc, "duplicate_address"); continue
        if _looks_solo(acc) and (acc.get("review_count") or 0) < 5:
            drop(acc, "likely_solo_operator"); continue

        seen["domain"].add(domain)
        seen["company"].add(ncompany)
        if nphone:
            seen["phone"].add(nphone)
        if naddr:
            seen["address"].add(naddr)
        acc["county"] = "Los Angeles County"
        kept.append(acc)

    c.save_json(c.processed_path(week, "accounts_filtered.json"), kept)
    c.save_json(c.processed_path(week, "accounts_removed.json"), removed)
    log.info("ICP filter: kept %d, removed %d (of %d)", len(kept), len(removed), len(accounts))
    return kept


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    filter_accounts(args.week)
