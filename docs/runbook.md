# Runbook

**Status: living document — skeleton only in Phase 0.**

Execution order (no step before Phase 0 approval):
1. Configure `.env` from `config/.env.example`.
2. Phase 1 `scripts/seed_companies.py` -> Phase 2 `crawl_websites.py` ->
   Phase 3 `detect_technographics.py` -> Phase 4 `enrich_jobs.py` ->
   Phase 5 `collect_feedback.py` -> Phase 6 `collect_competitive_intel.py` ->
   Phase 7 `collect_market_events.py` -> `normalize_entities.py` ->
   Phase 8 `score_companies.py` -> Phase 9 `validate_accuracy.py` ->
   Phase 10 `generate_briefs.py` -> Phase 11 `export_outputs.py`.
3. `claim_audit.py` runs on a 10% sample (rule R5).
Anti-hallucination rules R1-R7 and the data-rights tiers in
`docs/data_rights_matrix.md` are enforced throughout. Full re-run instructions
land here as each phase is built.
