"""Phase 4 — hiring signals from first-party careers pages / public ATS APIs.

Detects the company's ATS (Greenhouse / Lever / Ashby) from its careers/homepage
HTML and reads the PUBLIC job-board API (the company's own postings — SAFE PUBLIC,
first-party). Classifies roles into buckets and stores counts with evidence (R3:
sample titles + board URL). No LinkedIn / aggregator scraping. If no ATS is found
or reachable, hiring fields stay null (R6).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E

ATS_PATTERNS = {
    "greenhouse": [r"boards\.greenhouse\.io/(?:embed/job_board\?for=)?([a-zA-Z0-9_-]+)",
                   r"job_board\?for=([a-zA-Z0-9_-]+)",
                   r"boards-api\.greenhouse\.io/v1/boards/([a-zA-Z0-9_-]+)"],
    "lever": [r"jobs\.lever\.co/([a-zA-Z0-9_-]+)", r"api\.lever\.co/v0/postings/([a-zA-Z0-9_-]+)"],
    "ashby": [r"jobs\.ashbyhq\.com/([a-zA-Z0-9_-]+)", r"ashbyhq\.com/([a-zA-Z0-9_-]+)"],
}

BUCKETS = {
    "product_jobs_count": ["product manager", "product management", "head of product",
                            "product lead", "group product manager", "principal product",
                            "director, product", "director of product", "vp product", "vp, product"],
    "analytics_jobs_count": ["product analyst", "data analyst", "analytics engineer",
                              "business analyst", "bi analyst", "analytics"],
    "data_jobs_count": ["data scientist", "data engineer", "machine learning", "ml engineer",
                         "data platform", "analytics engineer", "data infrastructure"],
    "growth_jobs_count": ["growth"],
    "ai_jobs_count": ["ai ", " ai", "a.i.", "machine learning", "ml ", "llm", "applied scientist",
                      "gen ai", "genai", "agent"],
    "customer_success_jobs_count": ["customer success", "customer experience", "onboarding specialist"],
    "product_ops_jobs_count": ["product operations", "product ops"],
}


def find_token(html, ats):
    for pat in ATS_PATTERNS[ats]:
        m = re.search(pat, html, re.I)
        if m:
            tok = m.group(1)
            if tok.lower() not in ("embed", "v0", "v1", "postings", "boards", "job"):
                return tok
    return None


def fetch_jobs(ats, token):
    """Return list of (title, location, url) from the public board API, or []."""
    if ats == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        st, txt = E.fetch(url)
        if st == 200 and txt:
            data = json.loads(txt)
            return url, [(j.get("title", ""), (j.get("location") or {}).get("name", ""),
                         j.get("absolute_url", "")) for j in data.get("jobs", [])]
    elif ats == "lever":
        url = f"https://api.lever.co/v0/postings/{token}?mode=json"
        st, txt = E.fetch(url)
        if st == 200 and txt:
            data = json.loads(txt)
            return url, [(j.get("text", ""), (j.get("categories") or {}).get("location", ""),
                         j.get("hostedUrl", "")) for j in data]
    elif ats == "ashby":
        url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
        st, txt = E.fetch(url)
        if st == 200 and txt:
            data = json.loads(txt)
            return url, [(j.get("title", ""), j.get("location", ""),
                         j.get("jobUrl", "")) for j in data.get("jobs", [])]
    return None, []


def classify(titles):
    counts = {b: 0 for b in BUCKETS}
    examples = {b: [] for b in BUCKETS}
    for t in titles:
        low = " " + t.lower() + " "
        for b, kws in BUCKETS.items():
            if any(k in low for k in kws):
                counts[b] += 1
                if len(examples[b]) < 4:
                    examples[b].append(t)
    return counts, examples


def guess_tokens(domain, name):
    """Candidate public-board tokens when none is embedded in the HTML. Restricted
    to the company's own identifiers (first-party board), e.g. figma.com -> 'figma'."""
    label = domain.split(".")[0]
    nm = re.sub(r"[^a-z0-9]", "", name.lower())
    cands = []
    for t in (label, nm, label.replace("-", "")):
        if t and t not in cands:
            cands.append(t)
    return cands


def enrich_company(conn, cid, name):
    # gather careers + homepage html
    html = ""
    for r in conn.execute(
        "SELECT content_path FROM raw_pages WHERE company_id=? AND http_status=200"
        " AND page_type IN ('careers','homepage')", (cid,)):
        if r["content_path"]:
            try:
                with open(os.path.join(E.ROOT, r["content_path"]), encoding="utf-8", errors="ignore") as f:
                    html += f.read()
            except OSError:
                pass
    domain = conn.execute("SELECT domain FROM companies WHERE id=?", (cid,)).fetchone()["domain"]
    ats = token = board_url = None
    jobs = []
    confidence = 0.85
    # 1) token embedded in HTML (high confidence)
    for a in ATS_PATTERNS:
        token = find_token(html, a)
        if token:
            ats = a
            board_url, jobs = fetch_jobs(a, token)
            if jobs:
                break
            token = None
    # 2) fallback: guess own-name token against each ATS (lower confidence, logged)
    if not jobs:
        for cand in guess_tokens(domain, name):
            for a in ("greenhouse", "ashby", "lever"):
                bu, jj = fetch_jobs(a, cand)
                if jj:
                    ats, token, board_url, jobs = a, cand, bu, jj
                    confidence = 0.75
                    break
            if jobs:
                break
    if not token or not jobs:
        E.log(conn, "phase4.jobs", "null", f"{name}: no public ATS detected/reachable", cid)
        return None
    titles = [t for t, _, _ in jobs if t]
    counts, examples = classify(titles)
    total = len(titles)
    src = f"ats:{ats}" + ("" if confidence >= 0.85 else "(guessed-token)")
    E.store_fact(conn, cid, "open_jobs_count", total, src, board_url,
                 f"{total} roles via {ats}/{token}; e.g. " + "; ".join(titles[:5]), confidence)
    for b, n in counts.items():
        if n > 0:
            E.store_fact(conn, cid, b, n, src, board_url,
                         "; ".join(examples[b]) or str(n), confidence)
    E.log(conn, "phase4.jobs", "ok", f"{name}: {ats}/{token} {total} roles (conf {confidence})", cid)
    return total, ats, counts


def main():
    conn = E.connect()
    rows = conn.execute("SELECT id, company_name FROM companies ORDER BY id").fetchall()
    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only and only.isdigit():
        rows = rows[: int(only)]
    for r in rows:
        res = enrich_company(conn, r["id"], r["company_name"])
        if res:
            total, ats, counts = res
            print(f"  [{r['id']:>2}] {r['company_name']:<12} {total:>4} roles ({ats})  "
                  f"prod={counts['product_jobs_count']} data={counts['data_jobs_count']} ai={counts['ai_jobs_count']}")
        else:
            print(f"  [{r['id']:>2}] {r['company_name']:<12}  no public ATS (null)")
    print("Hiring enrichment complete.")


if __name__ == "__main__":
    main()
