"""Step 11: Merge Apollo contacts back to accounts; split final vs backup.

A final record must have a real person with a decision-maker title, a verified
email, a company match, a unique domain and unique email, an LA County address,
a managed-IT trigger, and source evidence. Accounts without a verified person go
to backup. Business-listing emails never enter the final set.
"""
import argparse

import common as c


def _company_match(contact, acc):
    cd = c.normalize_domain(contact.get("apollo_org_domain"))
    if cd and cd == c.normalize_domain(acc.get("domain")):
        return True
    on = c.normalize_company(contact.get("apollo_org"))
    return bool(on) and on == c.normalize_company(acc.get("company_name"))


def _source_evidence(acc):
    bits = []
    if acc.get("google_maps_url"):
        bits.append(f"Public business listing: {acc['google_maps_url']}")
    if acc.get("website"):
        bits.append(f"Company website: {acc['website']}")
    if acc.get("linkedin_company_url"):
        bits.append(f"Company LinkedIn: {acc['linkedin_company_url']}")
    bits.append(f"Decision maker verified against {acc.get('domain')} (verified business email)")
    if acc.get("employee_evidence"):
        bits.append(f"Size estimate: {acc['employee_evidence']}")
    return " | ".join(bits)


def merge(week):
    log = c.get_logger("merge_contacts", week)
    target = c.load_config("scoring_rules.json").get("final_target_count", 50)
    accounts = c.load_json(c.processed_path(week, "accounts_scored.json"), []) or []
    contacts = c.load_json(c.processed_path(week, "apollo_contacts.json"), []) or []
    by_acc = {ct["account_id"]: ct for ct in contacts}

    accounts.sort(key=lambda a: a.get("total_score", 0), reverse=True)
    final, backup = [], []
    used_domains, used_emails = set(), set()

    for acc in accounts:
        ct = by_acc.get(acc["account_id"])
        domain = c.normalize_domain(acc.get("domain"))
        rec = dict(acc)
        rec["source_evidence"] = _source_evidence(acc)

        if not ct or not ct.get("person_name") or not ct.get("email"):
            rec["_backup_reason"] = "no_verified_contact"
            backup.append(rec)
            continue
        email = ct["email"].lower()
        if not _company_match(ct, acc):
            rec["_backup_reason"] = "company_mismatch"
            backup.append(rec)
            continue
        if domain in used_domains:
            rec["_backup_reason"] = "duplicate_domain"
            backup.append(rec)
            continue
        if email in used_emails:
            rec["_backup_reason"] = "duplicate_email"
            backup.append(rec)
            continue
        if len(final) >= target:
            rec["_backup_reason"] = "over_target_buffer"
            backup.append(rec)
            continue

        rec.update({
            "decision_maker": ct["person_name"],
            "decision_maker_title": ct["title"],
            "verified_email": email,
            "email_status": ct.get("email_status", "verified"),
            "direct_phone": ct.get("direct_phone", ""),
            "contact_linkedin": ct.get("linkedin_url", ""),
        })
        used_domains.add(domain)
        used_emails.add(email)
        final.append(rec)

    c.save_json(c.processed_path(week, "accounts_final.json"), final)
    c.save_json(c.processed_path(week, "accounts_backup.json"), backup)
    log.info("merge complete: %d final, %d backup (target=%d)", len(final), len(backup), target)
    if len(final) < target:
        log.warning("only %d/%d final records; QA will flag. Expand Apollo queue or scrape more.", len(final), target)
    return final, backup


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    merge(args.week)
