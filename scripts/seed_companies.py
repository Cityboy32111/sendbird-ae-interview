"""Phase 1 — seed ~25 B2B SaaS companies into the local DB + companies_seed.csv.

Selection: the validation cohort (10) + wow-finding-relevant analytics vendors and
PLG SaaS with strong public pricing/changelog/careers presence. SAFE PUBLIC only.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E

SEED = [
    # (name, domain, category)
    ("Linear", "linear.app", "dev-tooling / cohort"),
    ("Notion", "notion.com", "productivity / cohort / amplitude-customer"),
    ("Vercel", "vercel.com", "dev-platform / cohort"),
    ("Webflow", "webflow.com", "no-code / cohort"),
    ("Retool", "retool.com", "internal-tools / cohort"),
    ("monday.com", "monday.com", "work-mgmt / cohort"),
    ("Datadog", "datadoghq.com", "observability / cohort"),
    ("Ramp", "ramp.com", "fintech / cohort"),
    ("Brex", "brex.com", "fintech / cohort / wow-candidate"),
    ("Intercom", "intercom.com", "support / cohort / wow-candidate"),
    ("Figma", "figma.com", "design / PLG"),
    ("Airtable", "airtable.com", "no-code db / PLG"),
    ("Calendly", "calendly.com", "scheduling / PLG"),
    ("Miro", "miro.com", "whiteboard / PLG"),
    ("ClickUp", "clickup.com", "work-mgmt / PLG"),
    ("Asana", "asana.com", "work-mgmt / PLG"),
    ("Loom", "loom.com", "video / PLG"),
    ("Amplitude", "amplitude.com", "analytics / self-detect-control"),
    ("Mixpanel", "mixpanel.com", "analytics / wow-candidate"),
    ("PostHog", "posthog.com", "analytics / wow-candidate"),
    ("Pendo", "pendo.io", "analytics / wow-candidate"),
    ("Heap", "heap.io", "analytics / wow-candidate"),
    ("Hotjar", "hotjar.com", "analytics / PLG"),
    ("Sentry", "sentry.io", "observability / PLG"),
    ("Postman", "postman.com", "api-tooling / PLG"),
]


def main():
    conn = E.connect()
    E.init_db(conn)
    seed_csv = os.path.join(E.ROOT, "config", "companies_seed.csv")
    rows = []
    for name, domain, category in SEED:
        website = f"https://{domain}"
        cid = E.add_company(conn, name, domain, website, "seed_companies.py", category)
        rows.append([name, domain, website, "", "seed_companies.py", category, ""])
        print(f"  seeded #{cid:>2} {name} ({domain})")
    with open(seed_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["company_name", "domain", "website", "linkedin_url",
                    "seed_source", "seed_category", "notes"])
        w.writerows(rows)
    E.log(conn, "phase1.seed", "ok", f"seeded {len(SEED)} companies")
    print(f"Seeded {len(SEED)} companies -> {E.DB_PATH}")


if __name__ == "__main__":
    main()
