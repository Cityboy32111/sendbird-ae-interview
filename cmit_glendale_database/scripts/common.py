"""Shared utilities for the CMIT Glendale pipeline.

Loads credentials from .env (never hardcoded, never logged), exposes project
paths, JSON helpers, normalization helpers, and a logger that redacts secrets.
"""
import json
import logging
import os
import re
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_APIFY = RAW_DIR / "apify"
RAW_APOLLO = RAW_DIR / "apollo"
RAW_WEBSITES = RAW_DIR / "websites"
PROCESSED_DIR = DATA_DIR / "processed"
EXCLUSIONS_DIR = DATA_DIR / "exclusions"
FINAL_DIR = DATA_DIR / "final"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = PROJECT_ROOT / "logs"

_SECRETS = {}


def load_env():
    """Load .env into os.environ and return the secret values (for redaction).

    Returns a dict with APIFY_TOKEN and APOLLO_API_KEY. Values are never logged.
    """
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
    secrets = {
        "APIFY_TOKEN": os.environ.get("APIFY_TOKEN", ""),
        "APOLLO_API_KEY": os.environ.get("APOLLO_API_KEY", ""),
    }
    for v in secrets.values():
        if v:
            _SECRETS[v] = True
    return secrets


def require_secret(name):
    val = os.environ.get(name, "")
    if not val:
        raise SystemExit(
            f"Missing {name}. Copy .env.example to .env and fill it in."
        )
    return val


class _RedactFilter(logging.Filter):
    """Strip any known secret value out of log records as a safety net."""

    def filter(self, record):
        try:
            msg = record.getMessage()
        except Exception:
            return True
        for secret in _SECRETS:
            if secret and secret in msg:
                msg = msg.replace(secret, "***REDACTED***")
                record.msg = msg
                record.args = ()
        return True


def get_logger(name, week="week"):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh = logging.FileHandler(LOGS_DIR / f"{week}.log")
    fh.setFormatter(fmt)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    redact = _RedactFilter()
    fh.addFilter(redact)
    ch.addFilter(redact)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_config(name):
    return load_json(CONFIG_DIR / name)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def week_dir(week):
    d = OUTPUTS_DIR / week
    d.mkdir(parents=True, exist_ok=True)
    return d


def processed_path(week, name):
    d = PROCESSED_DIR / week
    d.mkdir(parents=True, exist_ok=True)
    return d / name


# ---- normalization helpers ----

def normalize_domain(value):
    if not value:
        return ""
    v = value.strip().lower()
    v = re.sub(r"^https?://", "", v)
    v = re.sub(r"^www\.", "", v)
    v = v.split("/")[0].split("?")[0].split("#")[0]
    return v.strip()


def normalize_phone(value):
    if not value:
        return ""
    digits = re.sub(r"\D", "", str(value))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits if len(digits) == 10 else re.sub(r"\D", "", str(value))


def normalize_city(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip()).title()


def normalize_company(value):
    if not value:
        return ""
    v = value.lower().strip()
    v = re.sub(r"[,\.]", "", v)
    v = re.sub(r"\b(llc|inc|incorporated|llp|lp|pc|apc|corp|corporation|co|ltd|pllc|group|associates|assoc)\b", "", v)
    v = re.sub(r"\s+", " ", v).strip()
    return v


def normalize_address(value):
    if not value:
        return ""
    v = value.lower().strip()
    v = re.sub(r"\b(suite|ste|unit|apt|fl|floor|#)\b\.?\s*\w*", "", v)
    v = re.sub(r"[,\.]", "", v)
    v = re.sub(r"\s+", " ", v).strip()
    return v


def make_account_id(company, domain, city):
    basis = f"{normalize_company(company)}|{normalize_domain(domain)}|{normalize_city(city)}"
    h = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"acc_{h}"


def slugify(value):
    v = re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")
    return v[:60]
