"""Step 8: Domain and website checks -> client-safe posture fields.

Performs HTTPS/SSL, mail provider, hosting platform, and security-header checks.
Internal technical detail stays in data/raw; only client-safe summary phrasing is
attached to the account for the workbook. No methodology terms leak downstream.
"""
import argparse
import socket
import ssl

import requests

import common as c

try:
    import dns.resolver
    HAVE_DNS = True
except Exception:
    HAVE_DNS = False

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CMIT-Research/1.0)"}
SECURITY_HEADERS = ["strict-transport-security", "content-security-policy", "x-frame-options", "x-content-type-options"]

# client-safe phrasing (no methodology terms)
SAFE = {
    "email_incomplete": "Email authentication appears incomplete",
    "email_ok": "Email authentication appears configured",
    "web_review": "Website security posture may need review",
    "web_ok": "Website security posture appears current",
    "sensitive": "The business appears to handle sensitive client information",
    "cloud": "The company appears to rely on cloud based workflows",
    "forms": "The website includes forms or portals that may need stronger protection",
    "benefit": "The account may benefit from proactive backup, email security, and endpoint management",
}


def _mx_provider(domain):
    if not HAVE_DNS or not domain:
        return "", False, False
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=8)
        hosts = " ".join(str(r.exchange).lower() for r in answers)
        if "google" in hosts or "googlemail" in hosts:
            return "Google Workspace", True, False
        if "outlook" in hosts or "microsoft" in hosts or "office365" in hosts:
            return "Microsoft 365", False, True
        if "secureserver" in hosts:
            return "GoDaddy email", False, False
        return "Other provider", False, False
    except Exception:
        return "", False, False


def _email_auth_complete(domain):
    """Internal only. True if TXT auth records look present. Never surfaced verbatim."""
    if not HAVE_DNS or not domain:
        return None
    try:
        txt = " ".join(str(r).lower() for r in dns.resolver.resolve(domain, "TXT", lifetime=8))
        has_spf = "v=spf1" in txt
        has_dmarc = False
        try:
            dmarc = " ".join(str(r).lower() for r in dns.resolver.resolve("_dmarc." + domain, "TXT", lifetime=8))
            has_dmarc = "v=dmarc1" in dmarc
        except Exception:
            has_dmarc = False
        return has_spf and has_dmarc
    except Exception:
        return None


def _ssl_ok(domain):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain):
                return True
    except Exception:
        return False


def _web_headers(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        present = [h for h in SECURITY_HEADERS if h in {k.lower() for k in r.headers}]
        server = r.headers.get("Server", "")
        powered = r.headers.get("X-Powered-By", "")
        gen = ""
        try:
            from bs4 import BeautifulSoup
            m = BeautifulSoup(r.text, "html.parser").find("meta", attrs={"name": "generator"})
            gen = m.get("content", "") if m else ""
        except Exception:
            pass
        https = r.url.startswith("https")
        platform = gen or powered or server
        return https, present, platform
    except requests.RequestException:
        return False, [], ""


def scan_one(acc):
    domain = c.normalize_domain(acc.get("domain"))
    url = acc.get("website") or ("https://" + domain)
    if not url.startswith("http"):
        url = "https://" + url

    mx_provider, is_gws, is_m365 = _mx_provider(domain)
    auth_complete = _email_auth_complete(domain)
    ssl_ok = _ssl_ok(domain)
    https, sec_headers, platform = _web_headers(url)
    sig = acc.get("website_signals", {})

    internal = {
        "https": https, "ssl_valid": ssl_ok, "mx_provider": mx_provider,
        "google_workspace": is_gws, "microsoft_365": is_m365,
        "email_auth_complete": auth_complete, "platform": platform,
        "security_headers_present": sec_headers,
        "weak_security_headers": len(sec_headers) < 2,
    }
    acc["domain_scan_internal"] = internal

    # client-safe fields
    handles_sensitive = acc.get("vertical") in ("Legal", "Dental", "Medical", "CPA and Accounting", "Insurance and Financial")
    cloud = is_gws or is_m365 or bool(sig.get("cloud_tool_keywords"))
    has_forms = sig.get("forms_detected") or sig.get("portal_detected") or sig.get("payment_detected")

    email_summary = SAFE["email_incomplete"] if auth_complete is False else (
        SAFE["email_ok"] if auth_complete else SAFE["email_incomplete"])
    web_summary = SAFE["web_ok"] if (https and ssl_ok and not internal["weak_security_headers"]) else SAFE["web_review"]

    risk_bits = []
    if auth_complete is False or auth_complete is None:
        risk_bits.append(SAFE["email_incomplete"])
    if not https or not ssl_ok or internal["weak_security_headers"]:
        risk_bits.append(SAFE["web_review"])
    if has_forms:
        risk_bits.append(SAFE["forms"])

    posture = []
    if handles_sensitive:
        posture.append(SAFE["sensitive"])
    if cloud:
        posture.append(SAFE["cloud"])
    posture.append(SAFE["benefit"])

    acc["email_security_summary"] = email_summary
    acc["website_security_summary"] = web_summary
    acc["security_posture_summary"] = ". ".join(posture)
    acc["specific_visible_risk"] = risk_bits[0] if risk_bits else SAFE["web_review"]
    acc["managed_it_relevance"] = SAFE["benefit"]
    return acc


def scan_all(week, limit=None):
    log = c.get_logger("scan_domains", week)
    if not HAVE_DNS:
        log.warning("dnspython not available; mail/auth checks degraded")
    accounts = c.load_json(c.processed_path(week, "accounts_enriched.json"), []) or []
    if limit:
        accounts = accounts[:limit]
    for i, acc in enumerate(accounts, 1):
        try:
            scan_one(acc)
        except Exception as e:  # noqa: BLE001 - one bad domain must not abort the run
            acc.setdefault("domain_scan_internal", {})
            acc["domain_scan_status"] = "failed"
            acc["domain_scan_error"] = f"{type(e).__name__}: {e}"
            log.warning(
                "domain scan failed | company=%r domain=%r error=%s",
                acc.get("company_name"), acc.get("domain"), f"{type(e).__name__}: {e}",
            )
        if i % 10 == 0:
            log.info("scanned %d/%d domains", i, len(accounts))
    c.save_json(c.processed_path(week, "accounts_scanned.json"), accounts)
    log.info("domain scan complete for %d accounts", len(accounts))
    return accounts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    c.load_env()
    scan_all(args.week, args.limit)
