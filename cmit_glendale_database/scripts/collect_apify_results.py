"""Step 3: Collect all per-term Apify raw outputs into one combined raw file.

Reads every data/raw/apify/<week>/*.json discovery file and concatenates the
records (provenance fields already attached) into a single combined raw list.
"""
import argparse

import common as c


def collect(week):
    log = c.get_logger("collect_apify_results", week)
    src_dir = c.RAW_APIFY / week
    combined = []
    files = sorted(p for p in src_dir.glob("*.json") if p.name != "runs_index.json")
    for f in files:
        items = c.load_json(f, []) or []
        combined.extend(items)
        log.info("collected %d from %s", len(items), f.name)
    out = c.processed_path(week, "apify_combined_raw.json")
    c.save_json(out, combined)
    log.info("combined %d raw Apify records -> %s", len(combined), out)
    return combined


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    args = ap.parse_args()
    c.load_env()
    collect(args.week)
