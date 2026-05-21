# Runbook

**Status: living document. Phase 1 implemented (25-company sample).**

## Dependencies
`pip install requests beautifulsoup4 lxml` (requests usually present). No API keys
needed for Phase 1 (detection is rule-based, not LLM). All scripts import the shared
library `scripts/epig_lib.py` (SQLite at `data/processed/epig.db`, raw HTML in
`data/raw/`; both are git-ignored and regenerable).

## Phase 1 re-run (implemented, SAFE PUBLIC / first-party only)
```
python3 scripts/seed_companies.py          # seed 25 companies -> DB + companies_seed.csv
python3 scripts/crawl_websites.py          # crawl 8 page types/company (robots + rate-limited)
python3 scripts/detect_technographics.py   # page-source detection (homepage+pricing only)
python3 scripts/enrich_jobs.py             # first-party Greenhouse/Lever/Ashby boards
python3 scripts/collect_market_events.py   # recent launches from changelog/blog/press
python3 scripts/score_companies.py         # Phase-1 partial scores
python3 scripts/export_outputs.py          # confidence-filtered CSV/JSON + source_evidence.json
python3 scripts/validate_accuracy.py       # precision read -> outputs/validation_report.md
```
Each script accepts an optional integer arg to limit to the first N companies
(e.g. `python3 scripts/crawl_websites.py 3` for a smoke test). To rebuild from
scratch: `rm -f data/processed/epig.db && rm -rf data/raw/*` then re-run.

## Full pipeline (Phase 2+ once approved)
... `collect_feedback.py` (Phase 5, needs explicit sample approval) ->
`collect_competitive_intel.py` (Phase 6) -> `normalize_entities.py` ->
`generate_briefs.py` (Phase 10) -> `claim_audit.py` (R5, 10% sample).

Anti-hallucination rules R1-R7 and the data-rights tiers in
`docs/data_rights_matrix.md` are enforced throughout.
