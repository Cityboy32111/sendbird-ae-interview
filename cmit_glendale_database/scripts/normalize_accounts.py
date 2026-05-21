"""Step 4: Normalize raw Apify records into one account schema.

Maps the Google Maps actor output into the canonical account schema and merges
records that resolve to the same account_id (company + domain + city).
"""
import argparse

import common as c

VERTICAL_SUBMAP = None


def _sub_vertical(category, vertical, verticals_cfg):
    cat = (category or "").lower()
    info = verticals_cfg["keep_verticals"].get(vertical, {})
    for sub in info.get("sub_verticals", []):
        if sub.lower() in cat:
            return sub
    subs = info.get("sub_verticals", [])
    return subs[0] if subs else ""


def _socials(rec):
    links = []
    for key in ("facebooks", "instagrams", "twitters", "youtubes", "tiktoks", "socials"):
        v = rec.get(key)
        if isinstance(v, list):
            links.extend(v)
        elif isinstance(v, str) and v:
            links.append(v)
    return sorted(set(links))


def _linkedin(rec):
    for key in ("linkedIns", "linkedin", "linkedins"):
        v = rec.get(key)
        if isinstance(v, list) and v:
            return v[0]
        if isinstance(v, str) and v:
            return v
    for s in _socials(rec):
        if "linkedin.com/company" in s.lower():
            return s
    return ""


def _emails(rec):
    out = []
    v = rec.get("emails")
    if isinstance(v, list):
        out.extend(v)
    elif isinstance(v, str) and v:
        out.append(v)
    return sorted({e.strip().lower() for e in out if e and "@" in e})


def normalize(week):
    log = c.get_logger("normalize_accounts", week)
    verticals_cfg = c.load_config("target_verticals.json")
    raw = c.load_json(c.processed_path(week, "apify_combined_raw.json"), []) or []

    accounts = {}
    for rec in raw:
        company = (rec.get("title") or "").strip()
        if not company:
            continue
        website = rec.get("website") or ""
        domain = c.normalize_domain(website)
        city = c.normalize_city(rec.get("city") or "")
        acc_id = c.make_account_id(company, domain, city)
        category = rec.get("categoryName") or (rec.get("categories") or [""])[0]
        vertical = rec.get("_vertical", "")
        phone = c.normalize_phone(rec.get("phone") or rec.get("phoneUnformatted") or "")

        if acc_id not in accounts:
            accounts[acc_id] = {
                "account_id": acc_id,
                "company_name": company,
                "domain": domain,
                "website": website,
                "address": rec.get("address") or "",
                "city": city,
                "state": rec.get("state") or "CA",
                "zip": str(rec.get("postalCode") or ""),
                "county": "",
                "vertical": vertical,
                "sub_vertical": _sub_vertical(category, vertical, verticals_cfg),
                "category": category,
                "main_phone": phone,
                "google_maps_url": rec.get("url") or "",
                "place_id": rec.get("placeId") or "",
                "rating": rec.get("totalScore"),
                "review_count": rec.get("reviewsCount") or 0,
                "business_description": rec.get("description") or "",
                "linkedin_company_url": _linkedin(rec),
                "emails_found": _emails(rec),
                "social_links": _socials(rec),
                "source_urls": [],
                "source_run_ids": [],
                "scrape_timestamp": rec.get("_scrape_timestamp", c.now_iso()),
            }
        acc = accounts[acc_id]
        # merge provenance and fill gaps from duplicate listings
        if rec.get("_source_url"):
            acc["source_urls"] = sorted(set(acc["source_urls"]) | {rec["_source_url"]})
        if rec.get("_source_run_id"):
            acc["source_run_ids"] = sorted(set(acc["source_run_ids"]) | {rec["_source_run_id"]})
        acc["emails_found"] = sorted(set(acc["emails_found"]) | set(_emails(rec)))
        acc["social_links"] = sorted(set(acc["social_links"]) | set(_socials(rec)))
        if not acc["linkedin_company_url"]:
            acc["linkedin_company_url"] = _linkedin(rec)
        if not acc["main_phone"] and phone:
            acc["main_phone"] = phone
        if (rec.get("reviewsCount") or 0) > (acc["review_count"] or 0):
            acc["review_count"] = rec.get("reviewsCount") or 0

    out_list = list(accounts.values())
    out = c.processed_path(week, "accounts_normalized.json")
    c.save_json(out, out_list)
    log.info("normalized %d raw records into %d unique accounts -> %s", len(raw), len(out_list), out)
    return out_list


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    normalize(args.week)
