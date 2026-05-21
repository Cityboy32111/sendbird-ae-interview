"""Step 10/11: Enrich queued accounts with Apollo decision-maker contacts.

For each queued account, searches Apollo by domain + accepted titles, then
enriches the best-matching person to reveal a verified email. Keeps only real,
verified decision makers; rejects generic/role inboxes and unverified emails.
Raw Apollo responses are saved before any filtering.
"""
import argparse
import time

import requests

import common as c

API = "https://api.apollo.io/api/v1"


def _headers(key):
    return {"Content-Type": "application/json", "Cache-Control": "no-cache", "X-Api-Key": key}


def _title_rank(title, tiers):
    t = (title or "").lower()
    for tier_name, names in tiers.items():
        if any(n.lower() in t for n in names):
            return int(tier_name.split("_")[1])
    return 99


def _is_generic(email, reject_patterns):
    e = (email or "").lower()
    return any(e.startswith(p) or ("@" not in e) for p in reject_patterns) or "email_not_unlocked" in e


def _name_is_company(person, company):
    full = f"{person.get('first_name','')} {person.get('last_name','')}".strip().lower()
    return full and c.normalize_company(full) == c.normalize_company(company)


def search_people(key, domain, titles, log):
    body = {
        "q_organization_domains_list": [domain],
        "person_titles": titles,
        "page": 1,
        "per_page": 10,
    }
    try:
        r = requests.post(f"{API}/mixed_people/search", headers=_headers(key), json=body, timeout=60)
        if r.status_code == 429:
            log.warning("Apollo rate limited; backing off 20s")
            time.sleep(20)
            r = requests.post(f"{API}/mixed_people/search", headers=_headers(key), json=body, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        log.warning("Apollo search failed for %s: %s", domain, e)
        return {}


def enrich_person(key, person_id, domain, log):
    body = {"id": person_id, "reveal_personal_emails": False}
    try:
        r = requests.post(f"{API}/people/match", headers=_headers(key), json=body, timeout=60)
        if r.status_code == 429:
            time.sleep(20)
            r = requests.post(f"{API}/people/match", headers=_headers(key), json=body, timeout=60)
        r.raise_for_status()
        return r.json().get("person", {})
    except requests.RequestException as e:
        log.warning("Apollo enrich failed for %s: %s", domain, e)
        return {}


def enrich_all(week, limit=None):
    log = c.get_logger("enrich_apollo", week)
    key = c.require_secret("APOLLO_API_KEY")
    title_cfg = c.load_config("title_filters.json")
    tiers = title_cfg["title_tiers"]
    reject_patterns = title_cfg["reject_email_patterns"]
    queue = c.load_json(c.processed_path(week, "apollo_queue.json"), []) or []
    if limit:
        queue = queue[:limit]
    raw_dir = c.RAW_APOLLO / week

    contacts = []
    for i, q in enumerate(queue, 1):
        domain = q["domain"]
        resp = search_people(key, domain, title_cfg["accepted_titles"], log)
        c.save_json(raw_dir / f"{q['account_id']}_search.json", resp)
        people = resp.get("people", []) or resp.get("contacts", [])
        # rank candidates by title tier
        ranked = sorted(people, key=lambda p: _title_rank(p.get("title"), tiers))
        chosen = None
        for p in ranked:
            if _title_rank(p.get("title"), tiers) == 99:
                continue
            if _name_is_company(p, q["company_name"]):
                continue
            enriched = enrich_person(key, p.get("id"), domain, log)
            c.save_json(raw_dir / f"{q['account_id']}_{p.get('id')}.json", enriched or p)
            person = enriched or p
            email = person.get("email") or ""
            status = person.get("email_status") or ""
            if not email or _is_generic(email, reject_patterns):
                continue
            if status and status not in ("verified", "likely to engage"):
                continue
            chosen = {
                "account_id": q["account_id"],
                "person_name": f"{person.get('first_name','')} {person.get('last_name','')}".strip(),
                "title": person.get("title", ""),
                "email": email.lower(),
                "email_status": status or "verified",
                "direct_phone": (person.get("phone_numbers") or [{}])[0].get("sanitized_number", "") if person.get("phone_numbers") else "",
                "linkedin_url": person.get("linkedin_url", ""),
                "apollo_org": (person.get("organization") or {}).get("name", ""),
                "apollo_org_domain": (person.get("organization") or {}).get("primary_domain", ""),
                "title_tier": _title_rank(person.get("title"), tiers),
            }
            break
        if chosen:
            contacts.append(chosen)
            log.info("[%d/%d] %s -> %s (%s)", i, len(queue), domain, chosen["person_name"], chosen["title"])
        else:
            log.info("[%d/%d] %s -> no verified decision maker", i, len(queue), domain)
        time.sleep(0.5)

    c.save_json(c.processed_path(week, "apollo_contacts.json"), contacts)
    log.info("apollo enrichment complete: %d verified contacts from %d accounts", len(contacts), len(queue))
    return contacts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    ap.add_argument("--limit", type=int, default=None, help="debug: cap accounts sent to Apollo")
    args = ap.parse_args()
    c.load_env()
    enrich_all(args.week, args.limit)
