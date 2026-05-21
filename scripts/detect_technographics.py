"""Phase 3 — technographic detection from page source (direct observation).

Scans the raw HTML saved by crawl_websites.py for vendor signatures (script/CDN
domains, init calls). Hard signatures get high confidence (>=0.6, survive the
export floor); bare name-mentions get low confidence (kept in DB, nulled on
export per R1). Detection is direct observation -> inference_flag = 0.
No BuiltWith / external technographic source in Phase 1 (licensed; out of scope).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epig_lib as E

# vendor -> (detected_field, product_analytics?, [(signature, confidence)])
SIGNATURES = {
    "amplitude": ("amplitude_detected", True, [
        ("cdn.amplitude.com", 0.95), ("api2.amplitude.com", 0.92), ("api.eu.amplitude.com", 0.92),
        ("@amplitude/analytics", 0.9), ("amplitude.getinstance", 0.9), ("amplitude.com/libs", 0.88),
        ("amplitude", 0.4)]),
    "mixpanel": ("mixpanel_detected", True, [
        ("cdn.mxpnl.com", 0.95), ("api.mixpanel.com", 0.9), ("mixpanel.init", 0.9),
        ("mixpanel-2-latest", 0.9), ("mixpanel", 0.4)]),
    "heap": ("heap_detected", True, [
        ("cdn.heapanalytics.com", 0.95), ("heapanalytics.com", 0.9), ("heap.load", 0.88),
        ("heap.track", 0.85)]),
    "pendo": ("pendo_detected", True, [
        ("cdn.pendo.io", 0.95), ("data.pendo.io", 0.92), ("pendo.initialize", 0.9),
        ("pendo.io", 0.85), ("pendo", 0.4)]),
    "posthog": ("posthog_detected", True, [
        ("us.i.posthog.com", 0.92), ("app.posthog.com", 0.9), ("i.posthog.com", 0.9),
        ("posthog.init", 0.9), ("posthog", 0.45)]),
    "segment": ("segment_detected", True, [
        ("cdn.segment.com", 0.95), ("segment.com/analytics.js", 0.9), ("analytics.segment.io", 0.9),
        ("analytics.load(", 0.65)]),
    "ga4": ("ga4_detected", False, [
        ("googletagmanager.com/gtag/js", 0.9), ("gtag('config', 'g-", 0.92),
        ("google-analytics.com/analytics.js", 0.8)]),
    "google_tag_manager": ("gtm_detected", False, [
        ("googletagmanager.com/gtm.js", 0.85), ("gtm-", 0.55)]),
    "fullstory": ("fullstory_detected", False, [
        ("edge.fullstory.com", 0.95), ("fullstory.com", 0.88), ("window['_fs_", 0.9)]),
    "hotjar": ("hotjar_detected", False, [
        ("static.hotjar.com", 0.95), ("_hjsettings", 0.9), ("hotjar.com", 0.88)]),
    "launchdarkly": ("launchdarkly_detected", False, [
        ("clientstream.launchdarkly", 0.92), ("launchdarkly.com", 0.88), ("ldclient", 0.6)]),
    "optimizely": ("optimizely_detected", False, [
        ("cdn.optimizely.com", 0.95), ("optimizely.com", 0.82)]),
    "vwo": ("vwo_detected", False, [
        ("visualwebsiteoptimizer.com", 0.95), ("_vwo_code", 0.9)]),
    "intercom": ("intercom_detected", False, [
        ("widget.intercom.io", 0.95), ("intercomcdn.com", 0.9), ("intercomsettings", 0.85)]),
    "zendesk": ("zendesk_detected", False, [
        ("static.zdassets.com", 0.95), ("zesettings", 0.85), ("zendesk.com", 0.75)]),
    "gainsight_px": ("gainsight_detected", False, [
        ("aptrinsic", 0.9), ("gainsight", 0.6)]),
    "sprig": ("sprig_detected", False, [("sprig.com", 0.85), ("userleap", 0.85)]),
    "qualtrics": ("qualtrics_detected", False, [("qualtrics.com", 0.85), ("siteintercept", 0.7)]),
    "contentsquare": ("contentsquare_detected", False, [
        ("t.contentsquare.net", 0.95), ("contentsquare.com", 0.88)]),
}


# Only scan own-site chrome. Integrations/changelog/blog/docs/press/careers list
# THIRD-PARTY tools as content and cause false positives, so they are excluded.
# 'product' is excluded too because discovery can resolve it to a changelog post.
OWN_SITE_PAGES = ("homepage", "pricing")


def load_pages(conn, cid):
    out = []
    for r in conn.execute(
        "SELECT url, content_path FROM raw_pages WHERE company_id=? AND http_status=200"
        " AND page_type IN ('homepage','pricing')", (cid,)
    ):
        if r["content_path"]:
            p = os.path.join(E.ROOT, r["content_path"])
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    out.append((r["url"], f.read().lower()))
            except OSError:
                pass
    return out


def detect_company(conn, cid, name):
    pages = load_pages(conn, cid)
    detected = {}  # vendor -> (field, is_pa, best_conf, url, span)
    for url, html in pages:
        for vendor, (field, is_pa, sigs) in SIGNATURES.items():
            for sig, conf in sigs:
                if sig in html:
                    cur = detected.get(vendor)
                    if cur is None or conf > cur[2]:
                        detected[vendor] = (field, is_pa, conf, url, E.snippet(html, sig, 100))
                    break  # take first (highest-priority) matching sig on this page
    pa_tools, all_tools = [], []
    for vendor, (field, is_pa, conf, url, span) in sorted(detected.items()):
        E.store_fact(conn, cid, field, True, "page_source", url, span, conf,
                     inference_flag=0)
        all_tools.append(vendor)
        if is_pa:
            pa_tools.append(vendor)
    # roll-ups (only the high-confidence detections drive the rolled-up list)
    hi = [v for v, d in detected.items() if d[2] >= E.CONFIDENCE_FLOOR]
    hi_pa = [v for v in pa_tools if detected[v][2] >= E.CONFIDENCE_FLOOR]
    if hi:
        any_url = next(iter(detected.values()))[3]
        E.store_fact(conn, cid, "detected_analytics_tools", ",".join(sorted(hi)),
                     "page_source", any_url, ",".join(sorted(hi)), 0.8)
        # average confidence as technographic_confidence
        avg = sum(detected[v][2] for v in hi) / len(hi)
        E.store_fact(conn, cid, "technographic_confidence", round(avg, 2),
                     "page_source", any_url, ",".join(sorted(hi)), round(avg, 2))
    if hi_pa:
        any_url = detected[hi_pa[0]][3]
        E.store_fact(conn, cid, "detected_product_analytics_tools", ",".join(sorted(hi_pa)),
                     "page_source", any_url, ",".join(sorted(hi_pa)), 0.8)
    E.log(conn, "phase3.techno", "ok",
          f"{name}: {len(hi)} tools (hi-conf) [{','.join(sorted(hi))}]", cid)
    return sorted(hi)


def main():
    conn = E.connect()
    rows = conn.execute("SELECT id, company_name FROM companies ORDER BY id").fetchall()
    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only and only.isdigit():
        rows = rows[: int(only)]
    for r in rows:
        tools = detect_company(conn, r["id"], r["company_name"])
        print(f"  [{r['id']:>2}] {r['company_name']:<12} {tools}")
    print("Technographic detection complete.")


if __name__ == "__main__":
    main()
