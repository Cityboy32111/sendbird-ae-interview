"""Step 2: Run small Google Maps discovery jobs by vertical via Apify.

Rules enforced:
- one small job per search term (no single huge scrape)
- 25-50 results per term
- every run ID, dataset ID, and actor are recorded
- raw output saved before any filtering
- failed run -> retry once with fewer results
- timed-out run -> split into smaller jobs
- each raw record keeps source actor, run ID, source URL, scrape timestamp
"""
import argparse
import time

import requests

import common as c

ACTOR = "compass~crawler-google-places"
API = "https://api.apify.com/v2"
POLL_INTERVAL = 10
RUN_TIMEOUT_SECS = 420


def _start_run(token, search_term, max_results, log):
    payload = {
        "searchStringsArray": [search_term],
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
        "skipClosedPlaces": True,
        "scrapeContacts": True,
    }
    r = requests.post(
        f"{API}/acts/{ACTOR}/runs",
        params={"token": token},
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()["data"]
    log.info("started run %s for term '%s' (max=%d)", data["id"], search_term, max_results)
    return data["id"]


def _wait_run(token, run_id, log):
    deadline = time.time() + RUN_TIMEOUT_SECS + 120
    while True:
        r = requests.get(f"{API}/actor-runs/{run_id}", params={"token": token}, timeout=60)
        r.raise_for_status()
        data = r.json()["data"]
        status = data["status"]
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            return status, data.get("defaultDatasetId")
        if time.time() > deadline:
            return "TIMED-OUT", data.get("defaultDatasetId")
        time.sleep(POLL_INTERVAL)


def _fetch_items(token, dataset_id, log):
    r = requests.get(
        f"{API}/datasets/{dataset_id}/items",
        params={"token": token, "clean": "true", "format": "json"},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def _tag(items, term, vertical, sub_group, run_id, max_results):
    ts = c.now_iso()
    for it in items:
        it["_source_actor"] = ACTOR
        it["_source_run_id"] = run_id
        it["_source_url"] = f"https://api.apify.com/v2/actor-runs/{run_id}"
        it["_scrape_timestamp"] = ts
        it["_search_term"] = term
        it["_vertical"] = vertical
        it["_sub_group"] = sub_group
        it["_max_results"] = max_results
    return items


def run_term(token, term, vertical, sub_group, max_results, log):
    """Run one term. Retry once smaller on failure; split on timeout."""
    try:
        run_id = _start_run(token, term, max_results, log)
        status, ds = _wait_run(token, run_id, log)
        if status == "SUCCEEDED" and ds:
            items = _tag(_fetch_items(token, ds, log), term, vertical, sub_group, run_id, max_results)
            return items, [{"run_id": run_id, "dataset_id": ds, "status": status, "term": term, "max": max_results}]
        if status == "TIMED-OUT":
            log.warning("run %s timed out; splitting term '%s' into smaller jobs", run_id, term)
            half = max(12, max_results // 2)
            items, runs = [], [{"run_id": run_id, "dataset_id": ds, "status": status, "term": term, "max": max_results}]
            for _ in range(2):
                rid = _start_run(token, term, half, log)
                st, d2 = _wait_run(token, rid, log)
                runs.append({"run_id": rid, "dataset_id": d2, "status": st, "term": term, "max": half})
                if st == "SUCCEEDED" and d2:
                    items += _tag(_fetch_items(token, d2, log), term, vertical, sub_group, rid, half)
            return items, runs
        log.warning("run %s status=%s; retrying once with fewer results", run_id, status)
    except requests.RequestException as e:
        log.warning("error on term '%s': %s; retrying once with fewer results", term, e)

    # single retry with fewer results
    try:
        smaller = max(15, max_results // 2)
        rid = _start_run(token, term, smaller, log)
        st, ds = _wait_run(token, rid, log)
        runs = [{"run_id": rid, "dataset_id": ds, "status": st, "term": term, "max": smaller, "retry": True}]
        if st == "SUCCEEDED" and ds:
            return _tag(_fetch_items(token, ds, log), term, vertical, sub_group, rid, smaller), runs
        return [], runs
    except requests.RequestException as e:
        log.error("retry failed on term '%s': %s", term, e)
        return [], [{"run_id": None, "status": "ERROR", "term": term, "error": str(e)}]


def run(week, limit_terms=None):
    log = c.get_logger("run_apify_scrapes", week)
    token = c.require_secret("APIFY_TOKEN")
    cfg = c.load_config("search_terms.json")
    max_results = cfg.get("results_per_term_max", 50)

    runs_index = []
    total_terms = 0
    for group_key, group in cfg["vertical_groups"].items():
        vertical = group["vertical"]
        for term in group["terms"]:
            if limit_terms and total_terms >= limit_terms:
                log.info("reached debug term limit (%d)", limit_terms)
                break
            total_terms += 1
            items, runs = run_term(token, term, vertical, group_key, max_results, log)
            out = c.RAW_APIFY / week / f"{group_key}__{c.slugify(term)}.json"
            c.save_json(out, items)
            log.info("term '%s' -> %d records saved to %s", term, len(items), out.name)
            for rmeta in runs:
                rmeta.update({"vertical": vertical, "sub_group": group_key, "output_file": str(out)})
                runs_index.append(rmeta)
        if limit_terms and total_terms >= limit_terms:
            break

    c.save_json(c.RAW_APIFY / week / "runs_index.json", {
        "week": week, "actor": ACTOR, "generated_at": c.now_iso(), "runs": runs_index,
    })
    log.info("apify discovery complete: %d terms, %d runs", total_terms, len(runs_index))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    ap.add_argument("--limit-terms", type=int, default=None, help="debug: cap number of terms")
    args = ap.parse_args()
    c.load_env()
    run(args.week, args.limit_terms)
