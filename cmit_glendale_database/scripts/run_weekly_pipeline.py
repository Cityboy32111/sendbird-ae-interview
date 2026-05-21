"""Weekly pipeline orchestrator for the CMIT Glendale sales-ready database.

Run the whole pipeline:
    python scripts/run_weekly_pipeline.py --week week_21

Step-by-step debugging:
    python scripts/run_weekly_pipeline.py --week week_21 --steps normalize,filter,score
    python scripts/run_weekly_pipeline.py --week week_21 --from websites
    python scripts/run_weekly_pipeline.py --week week_21 --list-steps

Each step writes a JSON artifact to data/processed/<week>/, so steps can be run
independently as long as the previous artifact exists. Apify runs first, Apollo
last. update_exclusions only runs when QA passes.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common as c
import build_exclusions
import run_apify_scrapes
import collect_apify_results
import normalize_accounts
import filter_icp
import scrape_account_websites
import scan_domains
import score_accounts
import prepare_apollo_queue
import enrich_apollo
import merge_contacts
import qa_final
import build_workbook
import update_exclusions

# QA runs before workbook so the QA Report tab is embedded and we can gate exclusions.
STEP_ORDER = [
    "exclusions", "apify", "collect", "normalize", "filter", "websites",
    "domains", "score", "queue", "apollo", "merge", "qa", "workbook",
    "update_exclusions",
]


def run_step(name, week, args, log):
    log.info("=== STEP: %s ===", name)
    if name == "exclusions":
        build_exclusions.build(week)
    elif name == "apify":
        run_apify_scrapes.run(week, args.limit_terms)
    elif name == "collect":
        collect_apify_results.collect(week)
    elif name == "normalize":
        normalize_accounts.normalize(week)
    elif name == "filter":
        filter_icp.filter_accounts(week)
    elif name == "websites":
        scrape_account_websites.scrape_all(week, args.limit)
    elif name == "domains":
        scan_domains.scan_all(week, args.limit)
    elif name == "score":
        score_accounts.score_all(week)
    elif name == "queue":
        prepare_apollo_queue.prepare(week)
    elif name == "apollo":
        enrich_apollo.enrich_all(week)
    elif name == "merge":
        merge_contacts.merge(week)
    elif name == "qa":
        qa_final.run_qa(week)
    elif name == "workbook":
        build_workbook.build(week)
    elif name == "update_exclusions":
        qa = c.load_json(c.processed_path(week, "qa_results.json"), {}) or {}
        if qa.get("status") == "pass":
            update_exclusions.update(week)
        else:
            log.warning("QA status '%s' - skipping exclusion update (nothing shipped).", qa.get("status"))
    else:
        log.error("unknown step: %s", name)


def main():
    ap = argparse.ArgumentParser(description="CMIT Glendale weekly pipeline")
    ap.add_argument("--week", required=True, help="e.g. week_21")
    ap.add_argument("--steps", help="comma-separated subset of steps to run")
    ap.add_argument("--from", dest="from_step", help="run from this step to the end")
    ap.add_argument("--limit-terms", type=int, default=None, help="debug: cap Apify search terms")
    ap.add_argument("--limit", type=int, default=None, help="debug: cap accounts in website/domain steps")
    ap.add_argument("--list-steps", action="store_true")
    args = ap.parse_args()

    if args.list_steps:
        print("Pipeline steps (in order):")
        for i, s in enumerate(STEP_ORDER, 1):
            print(f"  {i:2d}. {s}")
        return

    c.load_env()
    log = c.get_logger("pipeline", args.week)

    if args.steps:
        steps = [s.strip() for s in args.steps.split(",") if s.strip()]
    elif args.from_step:
        if args.from_step not in STEP_ORDER:
            raise SystemExit(f"unknown --from step: {args.from_step}")
        steps = STEP_ORDER[STEP_ORDER.index(args.from_step):]
    else:
        steps = STEP_ORDER

    log.info("running pipeline for %s: %s", args.week, " -> ".join(steps))
    for name in steps:
        try:
            run_step(name, args.week, args, log)
        except SystemExit:
            raise
        except Exception as e:
            log.exception("step '%s' failed: %s", name, e)
            raise
    log.info("pipeline complete for %s", args.week)


if __name__ == "__main__":
    main()
