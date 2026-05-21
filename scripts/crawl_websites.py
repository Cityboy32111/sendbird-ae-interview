"""Phase 2 — code-first crawl of public pages + product-motion extraction.

SAFE PUBLIC / first-party only. Fetches homepage, pricing, product, integrations,
api-docs, changelog, blog, press, careers. Stores raw HTML in data/raw and a
raw_pages row per fetch. Extracts product-motion facts with evidence spans (R3).
Only positive observations are stored; absent signals stay null (R6).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E
from bs4 import BeautifulSoup

# page_type -> (href/text keywords, candidate path guesses)
PAGE_SPECS = {
    "pricing": (["pricing", "plans"], ["/pricing", "/plans", "/pricing-plans"]),
    "product": (["product", "platform", "features"], ["/product", "/platform", "/features"]),
    "integrations": (["integration", "marketplace", "apps", "connect"], ["/integrations", "/apps", "/marketplace"]),
    "api_docs": (["developer", "api", "docs"], ["/docs", "/developers", "/api", "/docs/api"]),
    "changelog": (["changelog", "release", "what's new", "whats new", "updates"], ["/changelog", "/releases", "/whats-new", "/release-notes"]),
    "blog": (["blog", "news"], ["/blog", "/news"]),
    "press": (["press", "newsroom"], ["/press", "/newsroom", "/news"]),
    "careers": (["career", "jobs", "join", "hiring"], ["/careers", "/jobs", "/company/careers"]),
}

PRICE_SIGNALS = ["$", "/mo", "/month", "per month", "per user", "/year", "per year",
                 "billed annually", "billed monthly", "/seat", "per seat"]
FREE_TRIAL = ["free trial", "start free", "start for free", "try it free", "try for free",
              "14-day", "14 day", "30-day", "30 day", "free for 14"]
FREEMIUM = ["free plan", "free forever", "forever free", "free tier", "$0", "free for individuals",
            "free for personal", "free version"]


def _best_url(ptype, urls):
    """Prefer short, exact-segment paths (e.g. /integrations over
    /changelog/2026-04-23-linear-agent-mcp-support)."""
    keys = [k.replace("'", "").replace(" ", "-") for k in PAGE_SPECS[ptype][0]]

    def score(u):
        path = E.urlparse(u).path.rstrip("/").lower()
        segs = [s for s in path.split("/") if s]
        s = 0.0
        if segs and segs[-1] in keys:
            s += 100
        if any(path == "/" + k for k in keys):
            s += 100
        s -= len(segs) * 5      # prefer shallow
        s -= len(path) * 0.1    # prefer short
        return s

    return max(urls, key=score)


def discover(homepage_html, base_url):
    """Map page_type -> best candidate URL from homepage nav links."""
    soup = BeautifulSoup(homepage_html, "lxml")
    cands = {ptype: [] for ptype in PAGE_SPECS}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(" ").strip().lower()
        if href.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        full = href if href.startswith("http") else E.urljoin(base_url, href)
        if E.urlparse(full).netloc and E.urlparse(base_url).netloc.split(".")[-2:] != E.urlparse(full).netloc.split(".")[-2:]:
            continue
        low = (href + " " + text).lower()
        for ptype, (keywords, _) in PAGE_SPECS.items():
            if any(k in low for k in keywords):
                cands[ptype].append(full)
    return {p: _best_url(p, u) for p, u in cands.items() if u}


def fetch_and_store(conn, cid, domain, page_type, url):
    status, text = E.fetch(url)
    if status == 200 and text:
        path = E.save_raw(cid, domain, page_type, text)
        conn.execute(
            "INSERT INTO raw_pages(company_id,page_type,url,http_status,fetched_at,content_path,content_len,error)"
            " VALUES(?,?,?,?,?,?,?,?)",
            (cid, page_type, url, 200, E.dt.datetime.now().isoformat(timespec="seconds"), path, len(text), None),
        )
        conn.commit()
        return text
    conn.execute(
        "INSERT INTO raw_pages(company_id,page_type,url,http_status,fetched_at,content_path,content_len,error)"
        " VALUES(?,?,?,?,?,?,?,?)",
        (cid, page_type, url, None, E.dt.datetime.now().isoformat(timespec="seconds"), None, 0, str(status)),
    )
    conn.commit()
    return None


def crawl_company(conn, row):
    cid, name, domain, website = row["id"], row["company_name"], row["domain"], row["website"]
    pages = {}
    # 1) homepage
    home = fetch_and_store(conn, cid, domain, "homepage", website)
    if home:
        pages["homepage"] = (website, home)
    # 2) discover from nav, else guess common paths
    discovered = discover(home, website) if home else {}
    for ptype, (_, guesses) in PAGE_SPECS.items():
        url = discovered.get(ptype)
        text = None
        if url:
            text = fetch_and_store(conn, cid, domain, ptype, url)
        if not text:  # fall back to one common path guess
            for g in guesses:
                cand = website.rstrip("/") + g
                if cand == url:
                    continue
                text = fetch_and_store(conn, cid, domain, ptype, cand)
                if text:
                    url = cand
                    break
        if text:
            pages[ptype] = (url, text)

    extract_product_motion(conn, cid, name, pages)
    n_ok = len(pages)
    E.log(conn, "phase2.crawl", "ok", f"{name}: {n_ok} pages fetched", cid)
    return n_ok


def _find_signal(pages, signals, page_priority):
    for ptype in page_priority:
        if ptype in pages:
            url, html = pages[ptype]
            txt = E.visible_text(html)
            low = txt.lower()
            for s in signals:
                if s in low:
                    return url, E.snippet(txt, s)
    return None, None


def extract_product_motion(conn, cid, name, pages):
    # has_public_pricing
    if "pricing" in pages:
        url, html = pages["pricing"]
        txt = E.visible_text(html)
        hit = next((s for s in PRICE_SIGNALS if s in txt.lower()), None)
        if hit:
            E.store_fact(conn, cid, "has_public_pricing", True, "pricing_page", url,
                         E.snippet(txt, hit), 0.85)
            E.store_fact(conn, cid, "pricing_url", url, "pricing_page", url,
                         E.snippet(txt, hit), 0.9)
    # has_free_trial
    url, sn = _find_signal(pages, FREE_TRIAL, ["pricing", "homepage", "product"])
    if url:
        E.store_fact(conn, cid, "has_free_trial", True, "website", url, sn, 0.8)
    # has_freemium
    url, sn = _find_signal(pages, FREEMIUM, ["pricing", "homepage", "product"])
    if url:
        E.store_fact(conn, cid, "has_freemium", True, "website", url, sn, 0.75)
    # presence-of-page booleans
    for field, ptype, conf in [
        ("has_api_docs", "api_docs", 0.8),
        ("has_changelog", "changelog", 0.85),
        ("has_integrations_page", "integrations", 0.85),
    ]:
        if ptype in pages:
            url, html = pages[ptype]
            txt = E.visible_text(html)[:200]
            E.store_fact(conn, cid, field, True, ptype + "_page", url, txt or url, conf)
            urlfield = {"has_api_docs": "api_docs_url", "has_changelog": "changelog_url",
                        "has_integrations_page": "integrations_url"}[field]
            E.store_fact(conn, cid, urlfield, url, ptype + "_page", url, url, 0.9)


def main():
    conn = E.connect()
    E.init_db(conn)
    only = sys.argv[1] if len(sys.argv) > 1 else None  # optional domain filter / limit
    rows = conn.execute("SELECT * FROM companies ORDER BY id").fetchall()
    if only and only.isdigit():
        rows = rows[: int(only)]
    elif only:
        rows = [r for r in rows if r["domain"] == only]
    total = 0
    for row in rows:
        try:
            n = crawl_company(conn, row)
            total += n
            print(f"  [{row['id']:>2}] {row['company_name']:<12} {n} pages")
        except Exception as e:
            E.log(conn, "phase2.crawl", "error", f"{row['company_name']}: {e}", row["id"])
            print(f"  [{row['id']:>2}] {row['company_name']:<12} ERROR {e}")
    print(f"Crawl complete: {len(rows)} companies, {total} pages fetched.")


if __name__ == "__main__":
    main()
