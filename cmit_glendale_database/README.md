# CMIT Glendale Sales-Ready Database Pipeline

A repeatable weekly pipeline that produces **50 sales-ready LA County SMB
accounts** for CMIT Solutions of Glendale. This is a *managed IT opportunity
database*, not a scraped contact list: every final record has a real decision
maker, a verified email, an LA County location, an estimated 8-30 employee size,
a specific managed-IT reason to call, source evidence, an opening line, and a
discovery question.

**Apify comes first** (account discovery). **Apollo comes last** (decision-maker
verification), and only the top-scored accounts are ever sent to Apollo.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your two keys
```

`.env` holds the only secrets and is git-ignored. Keys are never hardcoded in
Python, never printed in logs (a redaction filter strips them), never written to
the workbook, and never written to any output file.

```
APIFY_TOKEN=...
APOLLO_API_KEY=...
```

## Run the whole pipeline

```bash
python scripts/run_weekly_pipeline.py --week week_21
```

Output workbook: `outputs/week_21/CMIT_Glendale_Sales_Ready_Database_Week21.xlsx`

## Step-by-step debugging

```bash
python scripts/run_weekly_pipeline.py --week week_21 --list-steps
python scripts/run_weekly_pipeline.py --week week_21 --from websites
python scripts/run_weekly_pipeline.py --week week_21 --steps normalize,filter,score
# debug caps
python scripts/run_weekly_pipeline.py --week week_21 --limit-terms 2   # fewer Apify terms
python scripts/run_weekly_pipeline.py --week week_21 --steps websites --limit 5
```

Each step can also be run directly, e.g. `python scripts/score_accounts.py --week week_21`.

## Pipeline steps

| # | Step | Script | Output |
|---|------|--------|--------|
| 1 | Build exclusions | `build_exclusions.py` | `exclusions_active.json` |
| 2 | Apify discovery (per vertical) | `run_apify_scrapes.py` | `data/raw/apify/<week>/*.json` + `runs_index.json` |
| 3 | Collect Apify results | `collect_apify_results.py` | `apify_combined_raw.json` |
| 4 | Normalize to account schema | `normalize_accounts.py` | `accounts_normalized.json` |
| 5 | Hard ICP filter | `filter_icp.py` | `accounts_filtered.json` |
| 6 | Scrape websites + size signals | `scrape_account_websites.py` | `accounts_enriched.json` |
| 7 | Domain/website checks | `scan_domains.py` | `accounts_scanned.json` |
| 8 | Internal scoring + briefings | `score_accounts.py` | `accounts_scored.json` |
| 9 | Prepare Apollo queue (top 100) | `prepare_apollo_queue.py` | `apollo_queue.json` |
| 10 | Apollo decision-maker enrichment | `enrich_apollo.py` | `apollo_contacts.json` |
| 11 | Merge contacts; final vs backup | `merge_contacts.py` | `accounts_final.json`, `accounts_backup.json` |
| 12 | QA gate | `qa_final.py` | `qa_results.json` |
| 13 | Build workbook | `build_workbook.py` | `outputs/<week>/*.xlsx` |
| 14 | Update exclusions (only if QA passes) | `update_exclusions.py` | master exclusion files |

> Employee estimation (the 8-30 band) is produced in step 6 from website staff/
> provider counts, locations, services, and review volume.
>
> QA runs *before* the workbook is assembled so the QA Report tab is embedded and
> exclusions are only updated when the run actually passes. If QA fails, the run
> does not ship: failed records stay in backup and you re-run Apollo / discover
> more accounts.

## Configuration (`config/`)

- `search_terms.json` - Google Maps discovery terms grouped by vertical
- `target_verticals.json` - ICP verticals, reject categories, franchise names
- `la_county_cities.json` - LA County city allowlist + ZIP prefixes
- `title_filters.json` - accepted decision-maker titles, rejected email patterns
- `scoring_rules.json` - internal scoring weights and tiers (never shown to client)
- `qa_rules.json` - hard QA checks and forbidden workbook terms

## Client-safe language

The workbook never exposes methodology. Technical findings are translated into
client-safe phrasing such as *"Email authentication appears incomplete"* and
*"The website includes forms or portals that may need stronger protection."* QA
fails the run if any forbidden term (Apify, scraper, SPF/DMARC/DKIM, formula,
etc.) appears in client-facing text.

## Workbook tabs

1. Executive Summary
2. Final Sales Ready Accounts
3. Account Briefings (account-specific, not vertical templates)
4. Contact Details
5. Verification Sources
6. Backup Accounts
7. QA Report
