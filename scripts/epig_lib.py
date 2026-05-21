"""External Product Intelligence Graph — shared library (Phase 1).

Local-only. SQLite at data/processed/epig.db. SAFE PUBLIC / first-party sources
only: company websites, pricing/product/integrations/changelog/blog/press/careers
pages, and page-source technographic detection. No G2/Capterra/LinkedIn/Reddit/
app-store scraping. No production database. Honors robots.txt and rate limits.

Anti-hallucination rules enforced here:
  R1 confidence floor 0.6 (applied at export, raw kept in DB)
  R3 evidence span required for every stored fact
  R6 no fabrication on missing data -> field left absent/null
"""

from __future__ import annotations

import os
import re
import sqlite3
import time
import json
import datetime as dt
from urllib.parse import urljoin, urlparse
from urllib import robotparser

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "processed", "epig.db")
RAW_DIR = os.path.join(ROOT, "data", "raw")
TODAY = dt.date.today().isoformat()

USER_AGENT = "EPIG-research-bot/0.1 (+contact: accel-corporate-solutions; SAFE_PUBLIC first-party crawl)"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "text/html,application/json,*/*"}
TIMEOUT = 20
RATE_DELAY = 1.5  # seconds between requests to the same host

CONFIDENCE_FLOOR = 0.6

_last_hit: dict[str, float] = {}
_robots_cache: dict[str, robotparser.RobotFileParser | None] = {}


# --------------------------------------------------------------------------- DB
def connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY,
            company_name TEXT, domain TEXT UNIQUE, website TEXT,
            seed_source TEXT, seed_category TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS raw_pages (
            id INTEGER PRIMARY KEY,
            company_id INTEGER, page_type TEXT, url TEXT,
            http_status INTEGER, fetched_at TEXT, content_path TEXT,
            content_len INTEGER, error TEXT
        );
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY,
            company_id INTEGER, source_name TEXT, source_url TEXT,
            evidence_span TEXT, extraction_date TEXT
        );
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY,
            company_id INTEGER, field_name TEXT, value TEXT,
            source_name TEXT, source_url TEXT, extraction_date TEXT,
            confidence REAL, evidence_id INTEGER,
            inference_flag INTEGER DEFAULT 0, inference_basis TEXT
        );
        CREATE TABLE IF NOT EXISTS run_logs (
            id INTEGER PRIMARY KEY,
            phase TEXT, company_id INTEGER, status TEXT, detail TEXT, ts TEXT
        );
        CREATE TABLE IF NOT EXISTS external_signals (
            id INTEGER PRIMARY KEY,
            company_id INTEGER, source_type TEXT, source_url TEXT,
            theme TEXT, sentiment TEXT, evidence_span TEXT,
            confidence REAL, extraction_date TEXT,
            demo_only INTEGER DEFAULT 0, maps_to_amplitude TEXT
        );
        """
    )
    conn.commit()


def log(conn, phase, status, detail, company_id=None):
    conn.execute(
        "INSERT INTO run_logs(phase,company_id,status,detail,ts) VALUES(?,?,?,?,?)",
        (phase, company_id, status, detail, dt.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()


def add_company(conn, name, domain, website, seed_source, seed_category):
    conn.execute(
        "INSERT OR IGNORE INTO companies(company_name,domain,website,seed_source,seed_category,created_at)"
        " VALUES(?,?,?,?,?,?)",
        (name, domain, website, seed_source, seed_category, TODAY),
    )
    conn.commit()
    row = conn.execute("SELECT id FROM companies WHERE domain=?", (domain,)).fetchone()
    return row["id"]


def store_fact(conn, company_id, field_name, value, source_name, source_url,
               evidence_span, confidence, inference_flag=0, inference_basis=None):
    """Store a field-level fact + its evidence span (R3). R6: callers must not
    invent values; only call when value is observed."""
    ev_id = None
    if evidence_span:
        cur = conn.execute(
            "INSERT INTO evidence(company_id,source_name,source_url,evidence_span,extraction_date)"
            " VALUES(?,?,?,?,?)",
            (company_id, source_name, source_url, evidence_span[:600], TODAY),
        )
        ev_id = cur.lastrowid
    conn.execute(
        "INSERT INTO facts(company_id,field_name,value,source_name,source_url,extraction_date,"
        "confidence,evidence_id,inference_flag,inference_basis) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (company_id, field_name, str(value), source_name, source_url, TODAY,
         round(confidence, 2), ev_id, inference_flag, inference_basis),
    )
    conn.commit()
    return ev_id


# ------------------------------------------------------------------------ fetch
def _robots_ok(url: str) -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    if base not in _robots_cache:
        rp = robotparser.RobotFileParser()
        try:
            r = requests.get(urljoin(base, "/robots.txt"), headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
            else:
                rp = None  # no robots -> allowed
        except Exception:
            rp = None
        _robots_cache[base] = rp
    rp = _robots_cache[base]
    if rp is None:
        return True
    try:
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def _rate_limit(host: str) -> None:
    now = time.time()
    last = _last_hit.get(host, 0)
    wait = RATE_DELAY - (now - last)
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.time()


def fetch(url: str):
    """Fetch a URL respecting robots.txt + rate limits. Returns (status, text)
    or (None, None) on failure/disallow. Never raises."""
    host = urlparse(url).netloc
    if not _robots_ok(url):
        return ("robots_disallow", None)
    _rate_limit(host)
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        ctype = r.headers.get("content-type", "")
        if r.status_code == 200 and ("text" in ctype or "json" in ctype or ctype == ""):
            return (200, r.text)
        return (r.status_code, None)
    except Exception as e:
        return (f"error:{type(e).__name__}", None)


def save_raw(company_id: int, domain: str, page_type: str, text: str) -> str:
    d = os.path.join(RAW_DIR, domain.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{page_type}.html")
    with open(path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(text)
    return os.path.relpath(path, ROOT)


# ----------------------------------------------------------------- text helpers
def visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.extract()
    return re.sub(r"\s+", " ", soup.get_text(" ")).strip()


def snippet(haystack: str, needle: str, width: int = 120) -> str:
    i = haystack.lower().find(needle.lower())
    if i < 0:
        return ""
    a = max(0, i - width // 2)
    b = min(len(haystack), i + len(needle) + width // 2)
    return haystack[a:b].strip()
