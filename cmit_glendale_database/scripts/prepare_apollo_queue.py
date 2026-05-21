"""Step 10: Prepare the Apollo queue.

Selects the top-scored accounts (default top 100 buffer to reach 50 final
verified contacts), preferring the 8-30 employee band, and writes a queue with
the search keys (domain, company, city, state) and accepted title filters.
"""
import argparse

import common as c


def _emp_mid(acc):
    return (acc.get("estimated_employees_min", 0) + acc.get("estimated_employees_max", 0)) / 2


def prepare(week):
    log = c.get_logger("prepare_apollo_queue", week)
    rules = c.load_config("scoring_rules.json")
    titles = c.load_config("title_filters.json")
    accounts = c.load_json(c.processed_path(week, "accounts_scored.json"), []) or []
    queue_size = rules.get("apollo_queue_size", 100)

    # prefer accounts in the ideal employee band, then by score
    def sort_key(a):
        mid = _emp_mid(a)
        in_band = 1 if 8 <= mid <= 30 else 0
        return (in_band, a.get("total_score", 0))

    ranked = sorted(accounts, key=sort_key, reverse=True)
    queue = []
    for acc in ranked[:queue_size]:
        queue.append({
            "account_id": acc["account_id"],
            "company_name": acc["company_name"],
            "domain": acc["domain"],
            "city": acc["city"],
            "state": acc["state"],
            "total_score": acc["total_score"],
            "priority_tier": acc["priority_tier"],
            "title_filters": titles["accepted_titles"],
        })
    c.save_json(c.processed_path(week, "apollo_queue.json"), queue)
    log.info("apollo queue prepared: %d accounts (of %d scored)", len(queue), len(accounts))
    return queue


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    prepare(args.week)
