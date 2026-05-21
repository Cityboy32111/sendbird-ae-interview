# Data Dictionary

**Status: Phase 11 deliverable — not produced in Phase 0.**

The per-company schema and the database schema (tables: companies, sources,
raw_pages, jobs, reviews, feedback_items, technographics, market_events,
competitors, scores, briefs, run_logs, evidence) are defined in the engagement
spec. Every stored data point carries: company_id, field_name, value,
source_name, source_url, extraction_date, confidence (0.0-1.0), evidence_id,
inference_flag. This document will enumerate every field with type, source
category, and example once the schema is implemented in Phase 1+.
