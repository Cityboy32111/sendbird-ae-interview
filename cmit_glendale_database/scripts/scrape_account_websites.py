"""Steps 6 & 7: Scrape each qualified website and estimate employee count.

Fetches the home page plus discovered key pages (about, team, staff, attorneys,
providers, services, contact, careers, privacy, forms), extracts operational and
data-sensitivity signals, then estimates an employee range with a confidence and
human-readable evidence string.
"""
import argparse
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

import common as c

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CMIT-Research/1.0)"}
PAGE_KEYWORDS = {
    "about": ["about"], "team": ["team", "our-team", "meet"], "staff": ["staff"],
    "attorneys": ["attorney", "attorneys", "lawyers"], "providers": ["provider", "providers"],
    "doctors": ["doctor", "doctors", "physicians"], "dentists": ["dentist", "dentists"],
    "services": ["service", "services", "practice-areas"], "contact": ["contact"],
    "careers": ["career", "careers", "jobs", "join"], "privacy": ["privacy"],
    "forms": ["form", "forms", "new-patient", "intake"],
}
KEYWORD_GROUPS = {
    "hiring_keywords": ["we're hiring", "we are hiring", "now hiring", "open position", "join our team", "job opening"],
    "client_data_keywords": ["client portal", "client login", "confidential", "case management"],
    "patient_data_keywords": ["patient portal", "patient login", "new patient", "medical record", "hipaa"],
    "tax_data_keywords": ["tax return", "secure file", "client documents", "1040", "irs"],
    "legal_data_keywords": ["case", "matter", "litigation", "retainer", "privileged"],
    "financial_data_keywords": ["investment", "portfolio", "wealth", "financial plan", "premium", "policy"],
    "cloud_tool_keywords": ["office 365", "microsoft 365", "google workspace", "g suite", "quickbooks online", "salesforce", "dropbox", "sharepoint"],
}
PORTAL_HINTS = ["portal", "client login", "patient login", "secure login", "/login"]
BOOKING_HINTS = ["book online", "schedule", "appointment", "booking", "calendly", "acuity"]
PAYMENT_HINTS = ["pay online", "pay now", "make a payment", "bill pay", "/payment"]
# Count distinct named professionals (Name + credential, or title + Name),
# not raw keyword occurrences which over-count a solo practitioner's site.
NAME_CRED_RX = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)\s*,?\s*(?:Esq\.?|CPA|M\.?D\.?|DDS|DMD|DO|J\.?D\.?|Ph\.?D\.?|RN|NP|PA-C)\b")
TITLE_NAME_RX = re.compile(r"\b(?:Attorney|Dr\.?|Partner|Founder|Principal|Dentist|Physician)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b")
ZIP_RX = re.compile(r"\bca\s+(\d{5})\b")


def _fetch(url, log):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            return r.text
    except requests.RequestException as e:
        log.info("fetch failed %s: %s", url, e)
    return ""


def _discover_pages(base_url, home_html):
    soup = BeautifulSoup(home_html, "html.parser")
    found = {}
    try:
        base_netloc = urlparse(base_url).netloc
    except ValueError:
        return found
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        for label, kws in PAGE_KEYWORDS.items():
            if label in found:
                continue
            if any(k in href for k in kws):
                # Malformed hrefs (e.g. WordPress shortcodes rendered into a
                # link) can raise ValueError inside urljoin/urlparse; skip them.
                try:
                    full = urljoin(base_url, a["href"])
                    if urlparse(full).netloc == base_netloc:
                        found[label] = full
                except ValueError:
                    continue
    return found


def _count_staff(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    names = set()
    for rx in (NAME_CRED_RX, TITLE_NAME_RX):
        for m in rx.findall(text):
            names.add(m.strip().lower())
    cards = len(soup.select(".team-member, .staff-member, .attorney, .provider, .doctor, .bio, .profile, .person, .team__member"))
    return max(len(names), cards)


def _count_locations(blob):
    zips = set(ZIP_RX.findall(blob))
    return max(1, min(len(zips), 6))


def scrape_one(acc, log):
    base = acc.get("website") or ""
    if not base.startswith("http"):
        base = "https://" + base
    home = _fetch(base, log)
    site = {
        "account_id": acc["account_id"], "base_url": base, "fetched": bool(home),
        "pages": {}, "signals": {}, "important_page_urls": {},
    }
    blob = home.lower()
    pages = {"home": base}
    if home:
        pages.update(_discover_pages(base, home))
    site["important_page_urls"] = pages

    staff_count = _count_staff(home) if home else 0
    services_count = 0
    htmls = {"home": home}
    for label, url in list(pages.items())[:8]:
        if label == "home":
            continue
        time.sleep(0.3)
        h = _fetch(url, log)
        htmls[label] = h
        blob += " " + h.lower()
        if label in ("team", "staff", "attorneys", "providers", "doctors", "dentists"):
            staff_count = max(staff_count, _count_staff(h))
        if label == "services" and h:
            ssoup = BeautifulSoup(h, "html.parser")
            services_count = len(ssoup.select("li, .service, .practice-area, h3, h4"))

    sig = {
        "staff_count": staff_count,
        "provider_count": staff_count,
        "professional_count": staff_count,
        "num_locations": _count_locations(blob),
        "services_count": services_count,
        "forms_detected": "forms" in pages or "<form" in blob,
        "portal_detected": any(h in blob for h in PORTAL_HINTS),
        "booking_detected": any(h in blob for h in BOOKING_HINTS),
        "payment_detected": any(h in blob for h in PAYMENT_HINTS),
        "privacy_detected": "privacy" in pages or "privacy policy" in blob,
        "careers_detected": "careers" in pages,
    }
    for group, kws in KEYWORD_GROUPS.items():
        sig[group] = sorted({k for k in kws if k in blob})
    site["signals"] = sig
    site["pages"] = {k: bool(v) for k, v in htmls.items()}

    _estimate_employees(acc, sig)
    acc["website_signals"] = sig
    acc["important_page_urls"] = pages
    return site


def _estimate_employees(acc, sig):
    staff = sig.get("staff_count", 0)
    reviews = acc.get("review_count") or 0
    services = sig.get("services_count", 0)
    locations = sig.get("num_locations", 1)
    evidence = []
    if staff >= 3:
        lo, hi = staff, max(staff + 5, int(staff * 1.6))
        conf = "high"
        evidence.append(f"{staff} staff/provider profiles found on website")
    elif staff in (1, 2):
        lo, hi = max(staff * 2, 4), staff * 2 + 8
        conf = "medium"
        evidence.append(f"{staff} named professional(s) on site; staff inferred from supporting roles")
    else:
        if reviews >= 200:
            lo, hi, conf = 12, 30, "low"
        elif reviews >= 60:
            lo, hi, conf = 8, 20, "low"
        elif reviews >= 15:
            lo, hi, conf = 5, 15, "low"
        else:
            lo, hi, conf = 3, 12, "low"
        evidence.append(f"estimated from {reviews} reviews and business profile (no staff page parsed)")
    if locations > 1:
        hi += locations * 3
        evidence.append(f"{locations} locations detected")
    if services >= 8:
        evidence.append(f"{services} service lines listed")
        conf = "high" if conf == "medium" else conf
    acc["estimated_employees_min"] = lo
    acc["estimated_employees_max"] = hi
    acc["estimated_employees_display"] = f"{lo}-{hi}"
    acc["employee_confidence"] = conf
    acc["employee_evidence"] = "; ".join(evidence)


def scrape_all(week, limit=None):
    log = c.get_logger("scrape_account_websites", week)
    accounts = c.load_json(c.processed_path(week, "accounts_filtered.json"), []) or []
    if limit:
        accounts = accounts[:limit]
    site_dir = c.RAW_WEBSITES / week
    attempted = succeeded = failed = 0
    for i, acc in enumerate(accounts, 1):
        attempted += 1
        # Per-account isolation: no single broken site (malformed href, bad SSL,
        # timeout, redirect loop, invalid URL, unparseable HTML) may abort the run.
        try:
            site = scrape_one(acc, log)
            c.save_json(site_dir / f"{acc['account_id']}.json", site)
            if site.get("fetched"):
                acc["website_scrape_status"] = "success"
                succeeded += 1
            else:
                acc["website_scrape_status"] = "failed"
                acc["website_scrape_error"] = "site unreachable (no HTML fetched)"
                failed += 1
                log.warning(
                    "website unreachable | company=%r domain=%r url=%r",
                    acc.get("company_name"), acc.get("domain"), acc.get("website"),
                )
        except Exception as e:  # noqa: BLE001 - deliberately catch-all per account
            failed += 1
            acc["website_scrape_status"] = "failed"
            acc["website_scrape_error"] = f"{type(e).__name__}: {e}"
            # Guarantee downstream steps (scoring, briefing) still have usable
            # fields so the account survives in the backup pool.
            acc.setdefault("website_signals", {})
            try:
                _estimate_employees(acc, acc["website_signals"])
            except Exception:  # noqa: BLE001
                acc.setdefault("estimated_employees_min", 0)
                acc.setdefault("estimated_employees_max", 0)
            log.warning(
                "website scrape failed | company=%r domain=%r url=%r error=%s",
                acc.get("company_name"), acc.get("domain"), acc.get("website"),
                f"{type(e).__name__}: {e}",
            )
        if i % 25 == 0:
            log.info("scraped %d/%d websites (ok=%d failed=%d)", i, len(accounts), succeeded, failed)
    c.save_json(c.processed_path(week, "accounts_enriched.json"), accounts)
    c.save_json(
        c.processed_path(week, "website_scrape_summary.json"),
        {"attempted": attempted, "succeeded": succeeded, "failed": failed},
    )
    log.info(
        "website scrape complete: attempted=%d succeeded=%d failed=%d",
        attempted, succeeded, failed,
    )
    return accounts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    c.load_env()
    scrape_all(args.week, args.limit)
