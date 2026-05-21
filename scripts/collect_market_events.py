"""Phase 7 (subset) — recent product launches from owned changelog/blog/press.

Code-first over first-party pages only. Extracts dates within the last 90 days
and stores recent_product_launch_90d / recent_product_launches / most_recent_
launch_date with the literal dated snippet as evidence (R3). Also flags
recent_ai_announcement when a recent entry mentions AI/agent/MCP/LLM. No external
search APIs in Phase 1 (funding/exec-change detection deferred to a licensed feed).
"""
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E

WINDOW_DAYS = 90
CUTOFF = dt.date.today() - dt.timedelta(days=WINDOW_DAYS)

MONTHS = {m.lower(): i for i, m in enumerate(
    ["", "January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=0)}
MONTHS.update({m[:3].lower(): i for m, i in list(MONTHS.items()) if m})

ISO = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
MDY = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2}),?\s+(20\d{2})\b", re.I)
DMY = re.compile(r"\b(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(20\d{2})\b", re.I)
AI_TERMS = ["ai ", " ai", "agent", "mcp", "llm", "genai", "gen ai", "machine learning"]


def extract_dates(text):
    """Return list of (date, position)."""
    out = []
    for m in ISO.finditer(text):
        try:
            out.append((dt.date(int(m[1]), int(m[2]), int(m[3])), m.start()))
        except ValueError:
            pass
    for m in MDY.finditer(text):
        mo = MONTHS.get(m[1][:3].lower())
        if mo:
            try:
                out.append((dt.date(int(m[3]), mo, int(m[2])), m.start()))
            except ValueError:
                pass
    for m in DMY.finditer(text):
        mo = MONTHS.get(m[2][:3].lower())
        if mo:
            try:
                out.append((dt.date(int(m[3]), mo, int(m[1])), m.start()))
            except ValueError:
                pass
    return out


def collect_company(conn, cid, name):
    sources = []  # (page_type, url, text)
    for r in conn.execute(
        "SELECT page_type,url,content_path FROM raw_pages WHERE company_id=? AND http_status=200"
        " AND page_type IN ('changelog','blog','press')", (cid,)):
        if r["content_path"]:
            try:
                with open(os.path.join(E.ROOT, r["content_path"]), encoding="utf-8", errors="ignore") as f:
                    sources.append((r["page_type"], r["url"], E.visible_text(f.read())))
            except OSError:
                pass
    # also mine date in the changelog URL slug itself (e.g. /changelog/2026-05-14-...)
    for r in conn.execute("SELECT url FROM raw_pages WHERE company_id=? AND page_type='changelog'", (cid,)):
        sources.append(("changelog_url", r["url"], r["url"]))

    recent = []  # (date, url, snippet, page_type)
    today = dt.date.today()
    for ptype, url, text in sources:
        for d, pos in extract_dates(text):
            if CUTOFF <= d <= today:
                sn = text[max(0, pos - 80): pos + 80].strip()
                recent.append((d, url, sn, ptype))
    if not recent:
        E.log(conn, "phase7.events", "null", f"{name}: no dated launch in last {WINDOW_DAYS}d", cid)
        return 0
    recent.sort(reverse=True)
    most_recent, url0, sn0, _ = recent[0]
    distinct_dates = sorted({d for d, _, _, _ in recent}, reverse=True)
    E.store_fact(conn, cid, "recent_product_launch_90d", True, "changelog/blog", url0,
                 f"{most_recent.isoformat()}: {sn0}", 0.8)
    E.store_fact(conn, cid, "most_recent_launch_date", most_recent.isoformat(), "changelog/blog",
                 url0, sn0, 0.8)
    E.store_fact(conn, cid, "recent_product_launches", len(distinct_dates), "changelog/blog",
                 url0, f"{len(distinct_dates)} distinct dated entries in last {WINDOW_DAYS}d", 0.7)
    # AI announcement flag
    ai_hit = next(((d, u, s) for d, u, s, _ in recent
                   if any(t in s.lower() for t in AI_TERMS)), None)
    if ai_hit:
        E.store_fact(conn, cid, "recent_ai_announcement", True, "changelog/blog", ai_hit[1],
                     f"{ai_hit[0].isoformat()}: {ai_hit[2]}", 0.65)
    E.log(conn, "phase7.events", "ok",
          f"{name}: {len(distinct_dates)} recent dates, latest {most_recent}", cid)
    return len(distinct_dates)


def main():
    conn = E.connect()
    rows = conn.execute("SELECT id, company_name FROM companies ORDER BY id").fetchall()
    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only and only.isdigit():
        rows = rows[: int(only)]
    for r in rows:
        n = collect_company(conn, r["id"], r["company_name"])
        print(f"  [{r['id']:>2}] {r['company_name']:<12} {n} recent dated entries (<= {WINDOW_DAYS}d)")
    print("Market-events collection complete.")


if __name__ == "__main__":
    main()
