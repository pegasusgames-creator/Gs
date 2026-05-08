#!/usr/bin/env python3
"""IAP catalog audit + auto-fix for the Pegasus Games portfolio.

Implements Parts A-F of the user's spec. Part G is rendered by the
caller from the artifacts this script produces.
"""

import datetime
import json
import os
import re
import sys
from collections import defaultdict

BASE = "/home/pgs/Documents/Gs"
SKIP = {"_template", "_release", "__pycache__", "docs", "scripts",
        "BLOCKED_APPS", ".git", ".idea", "node_modules"}

# What each canonical IAP grants. Used for anomaly detection.
REWARD_MAP = {
    "remove_ads":              {"qty": "",       "unit": "ads_off",      "duration": "forever",  "type": "non_consumable"},
    "coins_small":             {"qty": "100",    "unit": "coins",        "duration": "",         "type": "consumable"},
    "coins_large":             {"qty": "500",    "unit": "coins",        "duration": "",         "type": "consumable"},
    "five_lives":              {"qty": "5",      "unit": "lives",        "duration": "",         "type": "consumable"},
    "unlimited_lives_1h":      {"qty": "inf",    "unit": "lives",        "duration": "1h",       "type": "consumable"},
    "unlimited_lives_forever": {"qty": "inf",    "unit": "lives",        "duration": "forever",  "type": "non_consumable"},
    "unlimited_undos":         {"qty": "inf",    "unit": "undos",        "duration": "forever",  "type": "non_consumable"},
    "undo_pack":               {"qty": "10",     "unit": "undos",        "duration": "",         "type": "consumable"},
    "hint_pack":               {"qty": "10",     "unit": "hints",        "duration": "",         "type": "consumable"},
    "starter_pack":            {"qty": "bundle", "unit": "coins+lives+hints", "duration": "",    "type": "consumable"},
    "season_pass_monthly":     {"qty": "",       "unit": "subscription", "duration": "P1M",      "type": "subscription"},
}

# Standard tiers per the audit spec the user provided.
STANDARD_TIERS_USD = {0.99, 1.99, 2.99, 4.99, 7.99, 9.99, 14.99,
                      19.99, 29.99, 49.99, 99.99}

# HIGH-confidence canonical price targets (from audit spec).
TARGET_PRICES = {
    "remove_ads":              2.99,
    "coins_small":              0.99,
    "coins_large":              2.99,   # current portfolio value; spec optional ladder differs but ladder isn't enforced
    "five_lives":               0.99,
    "unlimited_lives_1h":       1.99,   # FIX: spec says $1.99, not $0.99
    "unlimited_lives_forever":  4.99,
    "unlimited_undos":          4.99,   # FIX: $3.99 is off the spec's tier list; $4.99 matches unlimited_lives_forever
    "undo_pack":                0.99,
    "hint_pack":                1.99,
    "starter_pack":             0.99,
    "season_pass_monthly":      1.99,
}

# Which products to grant a HIGH-confidence reprice to.
# (Only products where the user's spec gives a clear right answer.)
HIGH_CONFIDENCE_REPRICE = {
    "unlimited_lives_1h",
    "unlimited_undos",
}


# ---------- helpers --------------------------------------------------------

def list_apps():
    apps = []
    for name in sorted(os.listdir(BASE)):
        if name in SKIP or name.startswith("."):
            continue
        d = os.path.join(BASE, name)
        if not os.path.isdir(d):
            continue
        if not os.path.isdir(os.path.join(d, "metadata")):
            continue
        if os.path.isfile(os.path.join(d, "metadata", "iaps.json")):
            apps.append(name)
    return apps


def load_iaps(app):
    p = os.path.join(BASE, app, "metadata", "iaps.json")
    with open(p) as f:
        return p, json.load(f)


def is_published(app):
    p = os.path.join(BASE, app, "metadata", "app_info.json")
    if not os.path.isfile(p):
        return False
    try:
        return bool(json.load(open(p)).get("first_upload_at"))
    except (IOError, ValueError):
        return False


def find_main_activity(app):
    root = os.path.join(BASE, app, "android", "app", "src", "main", "java")
    if not os.path.isdir(root):
        return None
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f == "MainActivity.java":
                return os.path.join(dp, f)
    return None


def java_iap_ids(app):
    """Extract IAP-looking ids from MainActivity.java VALID_PRODUCTS-style arrays."""
    p = find_main_activity(app)
    if not p:
        return None
    text = open(p).read()
    ids = set()
    # Conservative: any string literal that matches a known canonical IAP id
    for cand in REWARD_MAP.keys():
        if re.search(rf'"{cand}"', text):
            ids.add(cand)
    return ids


def has_mechanic(app, kind):
    """Best-effort grep of game.html to see whether the app implements the
    mechanic referenced by an IAP (lives / undos / hints). Returns True if
    we have positive evidence, False if we have positive negative evidence,
    None if we can't tell."""
    p = os.path.join(BASE, app, "android", "app", "src", "main", "assets", "game.html")
    if not os.path.isfile(p):
        return None
    try:
        text = open(p, errors="ignore").read().lower()
    except Exception:
        return None
    if kind == "lives":
        # Look for lives/hearts handling in the JS — not just the IAP id string
        markers = ["lives:", "hearts:", "addlife", "addlives", "deductlife",
                   "lives--", "lives -=", "consume lives", "current_lives",
                   "lives_count", '"lives"', "'lives'", "loseheart"]
    elif kind == "hints":
        markers = ["hints:", "hint count", "addhint", "usehint", "hints--",
                   "hints -=", "current_hints", "hints_count", '"hints"',
                   "'hints'", "show hint", "showhint"]
    elif kind == "undos":
        markers = ["undos:", "undo count", "addundo", "useundo", "undos--",
                   "undos -=", "current_undos", "undos_count", '"undos"',
                   "'undos'", "undo move", "performundo"]
    else:
        return None
    for m in markers:
        if m in text:
            return True
    return False


def gradle_path(app):
    return os.path.join(BASE, app, "android", "app", "build.gradle")


def bump_version_code(app):
    p = gradle_path(app)
    if not os.path.isfile(p):
        return None
    text = open(p).read()
    m = re.search(r"versionCode\s+(\d+)", text)
    if not m:
        return None
    old = int(m.group(1))
    new = old + 1
    new_text = text[:m.start()] + f"versionCode {new}" + text[m.end():]
    with open(p, "w") as f:
        f.write(new_text)
    return (old, new)


# ---------- Part A: inventory ---------------------------------------------

def part_a_inventory(apps):
    rows = [["app", "product_id", "type", "price_usd", "reward_qty",
             "reward_unit", "duration", "notes"]]
    rich = []  # for downstream reuse: dicts not just rows
    for app in apps:
        path, data = load_iaps(app)
        for section, default_type in (("one_time_products", "consumable"),
                                       ("subscriptions", "subscription")):
            for p in data.get(section, []):
                pid = p.get("id", "")
                price = p.get("price_usd", "")
                reward = REWARD_MAP.get(pid, {})
                ptype = p.get("type") or reward.get("type") or default_type
                qty = reward.get("qty", "")
                unit = reward.get("unit", "")
                duration = reward.get("duration", "") or p.get("billing_period", "")
                notes = ""
                if pid not in REWARD_MAP:
                    notes = "unknown_id"
                rows.append([app, pid, ptype, str(price), qty, unit, duration, notes])
                rich.append({"app": app, "id": pid, "type": ptype,
                             "price": float(price) if isinstance(price, (int, float)) else None,
                             "qty": qty, "unit": unit, "duration": duration,
                             "section": section})
    with open("/tmp/iap_audit.tsv", "w") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
    return rich


# ---------- Part B: anomalies ---------------------------------------------

def part_b_anomalies(apps, rich):
    """Returns list of dicts: severity, app, ids, anomaly, evidence, confidence."""
    anomalies = []

    by_app = defaultdict(list)
    for r in rich:
        by_app[r["app"]].append(r)

    # Anomaly 1 — same price, different value (within app)
    # Compare every pair within each app
    def relative_value(r):
        """Crude value tag for comparison. Returns a tuple
        (unit, comparable_value) where higher = more value, or None
        if not comparable."""
        if r["unit"] == "lives":
            if r["duration"] == "forever":
                return ("lives", 10**9)
            if r["duration"] == "1h":
                return ("lives", 60)        # 1h of unlimited lives ≫ 5 lives
            if r["qty"].isdigit():
                return ("lives", int(r["qty"]))
        elif r["unit"] == "undos":
            if r["duration"] == "forever":
                return ("undos", 10**9)
            if r["qty"].isdigit():
                return ("undos", int(r["qty"]))
        elif r["unit"] == "hints":
            if r["qty"].isdigit():
                return ("hints", int(r["qty"]))
        elif r["unit"] == "coins":
            if r["qty"].isdigit():
                return ("coins", int(r["qty"]))
        return None

    for app, items in by_app.items():
        # Anomaly 1 — same price, different value (same unit)
        seen = []
        for r in items:
            v = relative_value(r)
            if not v or r["price"] is None:
                continue
            for prev in seen:
                pv = relative_value(prev)
                if not pv:
                    continue
                if pv[0] != v[0]:
                    continue
                if r["price"] == prev["price"] and v[1] != pv[1]:
                    higher_id = r["id"] if v[1] > pv[1] else prev["id"]
                    lower_id  = prev["id"] if v[1] > pv[1] else r["id"]
                    anomalies.append({
                        "severity": "BLOCKER",
                        "app": app,
                        "ids": f"{lower_id} + {higher_id}",
                        "anomaly": "same_price_different_value",
                        "evidence": f"both at ${r['price']:.2f}; '{higher_id}' grants strictly more {v[0]} than '{lower_id}'",
                        "confidence": "HIGH",
                    })
            seen.append(r)

        # Anomaly 2 — higher price, lower reward (dominated)
        for i, a in enumerate(items):
            va = relative_value(a)
            if not va or a["price"] is None: continue
            for b in items[i+1:]:
                vb = relative_value(b)
                if not vb or b["price"] is None: continue
                if va[0] != vb[0]: continue
                if a["price"] > b["price"] and va[1] < vb[1]:
                    anomalies.append({
                        "severity": "BLOCKER", "app": app,
                        "ids": f"{a['id']} dominated by {b['id']}",
                        "anomaly": "dominated_product",
                        "evidence": f"'{a['id']}' costs ${a['price']:.2f} for {va[1]} {va[0]}; "
                                    f"'{b['id']}' costs ${b['price']:.2f} for {vb[1]} {vb[0]}",
                        "confidence": "HIGH",
                    })
                if b["price"] > a["price"] and vb[1] < va[1]:
                    anomalies.append({
                        "severity": "BLOCKER", "app": app,
                        "ids": f"{b['id']} dominated by {a['id']}",
                        "anomaly": "dominated_product",
                        "evidence": f"'{b['id']}' costs ${b['price']:.2f} for {vb[1]} {vb[0]}; "
                                    f"'{a['id']}' costs ${a['price']:.2f} for {va[1]} {va[0]}",
                        "confidence": "HIGH",
                    })

        # Anomaly 3 — quantity-discount inversion (per-unit value goes the wrong way)
        unit_groups = defaultdict(list)
        for r in items:
            if r["unit"] in ("coins", "hints", "undos") and r["qty"].isdigit() and r["price"]:
                unit_groups[r["unit"]].append((int(r["qty"]), r["price"], r["id"]))
        for unit, lst in unit_groups.items():
            lst.sort()
            for i in range(len(lst) - 1):
                qa, pa, ia = lst[i]
                qb, pb, ib = lst[i+1]
                ppua = pa / qa
                ppub = pb / qb
                if ppub > ppua:  # bigger pack has WORSE per-unit value
                    anomalies.append({
                        "severity": "MAJOR", "app": app,
                        "ids": f"{ia} vs {ib}",
                        "anomaly": "quantity_discount_inversion",
                        "evidence": f"{ia}: {qa} {unit} @ ${pa:.2f} = ${ppua:.4f}/unit; "
                                    f"{ib}: {qb} {unit} @ ${pb:.2f} = ${ppub:.4f}/unit "
                                    f"(larger pack should have BETTER per-unit value)",
                        "confidence": "HIGH",
                    })

        # Anomaly 4 — off-tier price
        for r in items:
            if r["price"] is None: continue
            if round(r["price"], 2) not in STANDARD_TIERS_USD:
                anomalies.append({
                    "severity": "MINOR", "app": app, "ids": r["id"],
                    "anomaly": "off_tier_price",
                    "evidence": f"${r['price']:.2f} is not in spec tier list "
                                f"({sorted(STANDARD_TIERS_USD)})",
                    "confidence": "HIGH",
                })

        # Anomaly 8 — reward/mechanic mismatch (best-effort grep)
        for r in items:
            if r["unit"] == "lives" and r["id"] != "starter_pack":
                ev = has_mechanic(app, "lives")
                if ev is False:
                    anomalies.append({
                        "severity": "BLOCKER", "app": app, "ids": r["id"],
                        "anomaly": "mechanic_mismatch_lives",
                        "evidence": "no 'lives' / 'hearts' references found in game.html — "
                                    "user could buy a SKU the app can't grant",
                        "confidence": "LOW",
                    })
            if r["unit"] == "hints":
                ev = has_mechanic(app, "hints")
                if ev is False:
                    anomalies.append({
                        "severity": "BLOCKER", "app": app, "ids": r["id"],
                        "anomaly": "mechanic_mismatch_hints",
                        "evidence": "no 'hints' references found in game.html",
                        "confidence": "LOW",
                    })
            if r["unit"] == "undos":
                ev = has_mechanic(app, "undos")
                if ev is False:
                    anomalies.append({
                        "severity": "BLOCKER", "app": app, "ids": r["id"],
                        "anomaly": "mechanic_mismatch_undos",
                        "evidence": "no 'undos' references found in game.html",
                        "confidence": "LOW",
                    })

    # Anomaly 5 — subscription/consumable confusion
    for r in rich:
        if r["section"] == "subscriptions" and "season" not in r["id"].lower() and "pass" not in r["id"].lower() and "monthly" not in r["id"].lower():
            anomalies.append({
                "severity": "MAJOR", "app": r["app"], "ids": r["id"],
                "anomaly": "subscription_naming_atypical",
                "evidence": f"subscription id '{r['id']}' doesn't follow season/pass/monthly naming",
                "confidence": "LOW",
            })
        if r["section"] == "one_time_products" and (r["id"].endswith("_monthly") or "season_pass" in r["id"]):
            anomalies.append({
                "severity": "MAJOR", "app": r["app"], "ids": r["id"],
                "anomaly": "consumable_named_like_subscription",
                "evidence": f"one-time product '{r['id']}' is named like a subscription",
                "confidence": "LOW",
            })

    # Anomaly 6 — cross-app price inconsistency for same product_id
    by_id_price = defaultdict(set)
    by_id_apps = defaultdict(lambda: defaultdict(list))
    for r in rich:
        if r["price"] is None: continue
        by_id_price[r["id"]].add(round(r["price"], 2))
        by_id_apps[r["id"]][round(r["price"], 2)].append(r["app"])
    for pid, prices in by_id_price.items():
        if len(prices) > 1:
            ev_parts = []
            for pr, apps_at in by_id_apps[pid].items():
                ev_parts.append(f"${pr:.2f} ({len(apps_at)} apps)")
            anomalies.append({
                "severity": "MAJOR", "app": "<portfolio-wide>", "ids": pid,
                "anomaly": "cross_app_price_inconsistency",
                "evidence": f"'{pid}' priced at multiple values: " + ", ".join(ev_parts),
                "confidence": "LOW",
            })

    # Anomaly 7 — missing standard SKUs
    standard_buckets = {
        "remove_ads":   ["remove_ads"],
        "coin_packs":   ["coins_small", "coins_large"],
        "starter_pack": ["starter_pack"],
        "season_pass":  ["season_pass_monthly"],
    }
    for app in apps:
        ids_in_app = {r["id"] for r in by_app[app]}
        missing = []
        for bucket, members in standard_buckets.items():
            if not any(m in ids_in_app for m in members):
                missing.append(bucket)
        if len(missing) >= 3:
            anomalies.append({
                "severity": "MINOR", "app": app, "ids": ",".join(missing),
                "anomaly": "missing_standard_skus",
                "evidence": f"app missing {len(missing)} standard buckets: {missing}",
                "confidence": "LOW",
            })

    # write tsv
    with open("/tmp/iap_anomalies.tsv", "w") as f:
        f.write("severity\tapp\tproduct_ids\tanomaly_type\tevidence\tconfidence\n")
        for a in anomalies:
            f.write(f"{a['severity']}\t{a['app']}\t{a['ids']}\t{a['anomaly']}\t{a['evidence']}\t{a['confidence']}\n")
    return anomalies


# ---------- Part C: cross-reference Java ----------------------------------

def part_c_java_xref(apps, rich):
    by_app = defaultdict(set)
    for r in rich:
        by_app[r["app"]].add(r["id"])
    findings = []
    for app in apps:
        java_ids = java_iap_ids(app)
        if java_ids is None:
            continue
        json_ids = by_app[app]
        in_json_not_java = json_ids - java_ids
        in_java_not_json = java_ids - json_ids
        if in_json_not_java:
            findings.append({
                "severity": "BLOCKER", "app": app,
                "ids": ",".join(sorted(in_json_not_java)),
                "anomaly": "iap_in_json_missing_from_java",
                "evidence": f"iaps.json declares {sorted(in_json_not_java)} but MainActivity.java VALID_PRODUCTS does not — purchase will fail",
                "confidence": "LOW",
            })
        if in_java_not_json:
            findings.append({
                "severity": "MAJOR", "app": app,
                "ids": ",".join(sorted(in_java_not_json)),
                "anomaly": "iap_in_java_missing_from_json",
                "evidence": f"MainActivity.java declares {sorted(in_java_not_json)} but iaps.json does not — Play Console will have no SKU to sell",
                "confidence": "LOW",
            })
    return findings


# ---------- Part D: fix proposals -----------------------------------------

def part_d_proposals(apps, rich, anomalies, java_findings):
    """Build /tmp/iap_fixes.md with HIGH (auto) and LOW (review) sections."""
    high_fixes = []   # actually applied in Part E
    low_review = []

    # Identify HIGH-confidence price fixes from the spec.
    # Targets: unlimited_lives_1h ($0.99 → $1.99), unlimited_undos ($3.99 → $4.99)
    for r in rich:
        if r["price"] is None: continue
        if r["id"] not in HIGH_CONFIDENCE_REPRICE: continue
        target = TARGET_PRICES.get(r["id"])
        if target is None: continue
        if round(r["price"], 2) != round(target, 2):
            # Reason text per id
            if r["id"] == "unlimited_lives_1h":
                reason = ("same price as five_lives ($0.99) at less value — "
                          "Anomaly 1 (same-price-different-value); spec ladder "
                          "puts unlimited 1h at $1.99")
            elif r["id"] == "unlimited_undos":
                reason = ("$3.99 is off the spec's standard tier list; nearest "
                          "on-tier price matching unlimited_lives_forever is $4.99")
            else:
                reason = "matches spec target"
            high_fixes.append({
                "app": r["app"], "id": r["id"], "section": r["section"],
                "old": r["price"], "new": target, "reason": reason,
            })

    # Everything LOW-confidence goes into review section
    for a in anomalies:
        if a["confidence"] == "LOW":
            low_review.append(a)
    for a in java_findings:
        low_review.append(a)

    # Render the doc
    lines = []
    lines.append("# IAP audit fix proposals")
    lines.append("")
    lines.append(f"Generated: {datetime.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Apps audited: {len(apps)}")
    lines.append(f"Total IAP entries: {len(rich)}")
    lines.append(f"Anomalies surfaced: {len(anomalies)}")
    lines.append(f"Java cross-reference findings: {len(java_findings)}")
    lines.append("")

    lines.append("## Section 1: HIGH-confidence auto-applicable fixes")
    lines.append("")
    lines.append("These will be applied automatically in Part E.")
    lines.append("")
    if not high_fixes:
        lines.append("_(none)_")
    else:
        # Group by id for compact display, but keep per-app rows
        by_id = defaultdict(list)
        for f in high_fixes:
            by_id[f["id"]].append(f)
        for pid, fxs in sorted(by_id.items()):
            lines.append(f"### {pid} — {len(fxs)} app(s)")
            sample = fxs[0]
            lines.append(f"- {sample['app']}/{pid}: ${sample['old']:.2f} → ${sample['new']:.2f}")
            if len(fxs) > 1:
                lines.append(f"- _… and {len(fxs)-1} more apps with the same change_")
            lines.append(f"- Reason: {sample['reason']}")
            lines.append(f"- Confidence: HIGH")
            lines.append("")

    lines.append("## Section 2: LOW-confidence fixes for human review")
    lines.append("")
    lines.append("These are surfaced but NOT applied automatically.")
    lines.append("")
    if not low_review:
        lines.append("_(none)_")
    else:
        by_anom = defaultdict(list)
        for a in low_review:
            by_anom[a["anomaly"]].append(a)
        for anom, items in sorted(by_anom.items()):
            lines.append(f"### {anom} — {len(items)} case(s)")
            for it in items[:30]:
                lines.append(f"- [{it['severity']}] {it['app']} / {it['ids']}: {it['evidence']}")
            if len(items) > 30:
                lines.append(f"- _… and {len(items)-30} more_")
            lines.append("")

    with open("/tmp/iap_fixes.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    return high_fixes, low_review


# ---------- Part E: apply auto-fixes --------------------------------------

def part_e_apply(high_fixes):
    """Apply all HIGH-confidence reprice fixes; bump versionCode per app."""
    by_app = defaultdict(list)
    for f in high_fixes:
        by_app[f["app"]].append(f)

    log_path = "/tmp/iap_changes.log"
    log = open(log_path, "w")
    apps_modified = 0
    iaps_repriced = 0
    version_bumps = []

    for app, fixes in sorted(by_app.items()):
        path, data = load_iaps(app)
        changed = False
        for fx in fixes:
            section = fx["section"]
            for p in data.get(section, []):
                if p.get("id") == fx["id"]:
                    if p.get("price_usd") != fx["new"]:
                        p["price_usd"] = fx["new"]
                        changed = True
                        iaps_repriced += 1
                        log.write(
                            f"{datetime.datetime.now().isoformat(timespec='seconds')}\t"
                            f"{app}\t{fx['id']}\t${fx['old']:.2f} → ${fx['new']:.2f}\n"
                        )
        if changed:
            with open(path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            apps_modified += 1
            bump = bump_version_code(app)
            if bump:
                version_bumps.append((app, bump[0], bump[1]))
    log.close()
    return apps_modified, iaps_repriced, version_bumps


# ---------- Part F: Play Console checklist --------------------------------

def part_f_play_console(apps, high_fixes):
    """Generate /tmp/play_console_iap_updates.md with sections only for
    PUBLISHED apps that had repricings."""
    by_app = defaultdict(list)
    for f in high_fixes:
        by_app[f["app"]].append(f)
    published = [a for a in by_app if is_published(a)]
    lines = ["# Play Console manual IAP price updates", ""]
    lines.append("Repo `iaps.json` is now the source of truth. For each "
                 "PUBLISHED app below, also update the prices in Play Console "
                 "(Monetize → Products → In-app products) so live customers "
                 "see the new prices.")
    lines.append("")
    if not published:
        lines.append("_No published apps were repriced. No Play Console action required._")
    else:
        for app in sorted(published):
            lines.append(f"## {app}")
            lines.append(f"Open: Play Console → {app} → Monetize → Products → In-app products")
            lines.append("")
            lines.append("Update these IAPs:")
            for fx in by_app[app]:
                lines.append(f"- `{fx['id']}`: ${fx['old']:.2f} → ${fx['new']:.2f}")
            lines.append("")
    with open("/tmp/play_console_iap_updates.md", "w") as f:
        f.write("\n".join(lines) + "\n")
    return published


# ---------- main -----------------------------------------------------------

def main():
    apps = list_apps()
    print(f"[A] Inventory: {len(apps)} apps with iaps.json")
    rich = part_a_inventory(apps)
    print(f"[A] Total IAP entries: {len(rich)}")

    print("[B] Detecting anomalies …")
    anomalies = part_b_anomalies(apps, rich)
    print(f"[B] {len(anomalies)} anomalies found")

    print("[C] Cross-referencing MainActivity.java …")
    java_findings = part_c_java_xref(apps, rich)
    print(f"[C] {len(java_findings)} Java/JSON mismatches")

    print("[D] Generating fix proposals …")
    high_fixes, low_review = part_d_proposals(apps, rich, anomalies, java_findings)
    print(f"[D] {len(high_fixes)} HIGH-confidence fixes; {len(low_review)} LOW-confidence items")

    print("[E] Applying HIGH-confidence fixes …")
    apps_mod, iaps_rep, bumps = part_e_apply(high_fixes)
    print(f"[E] Apps modified: {apps_mod}; IAPs repriced: {iaps_rep}; versionCode bumps: {len(bumps)}")

    print("[F] Generating Play Console checklist …")
    published = part_f_play_console(apps, high_fixes)
    print(f"[F] Published apps needing Play Console updates: {len(published)}")

    # Print a brief breakdown for Part G
    by_anom = defaultdict(int)
    for a in anomalies:
        by_anom[a["anomaly"]] += 1
    print()
    print("Anomaly counts:")
    for k, v in sorted(by_anom.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}")

    return {
        "n_apps": len(apps),
        "n_iaps": len(rich),
        "n_anomalies": len(anomalies),
        "n_java": len(java_findings),
        "n_high_fixes": len(high_fixes),
        "n_low_review": len(low_review),
        "apps_modified": apps_mod,
        "iaps_repriced": iaps_rep,
        "n_published_repriced": len(published),
        "by_anom": dict(by_anom),
    }


if __name__ == "__main__":
    summary = main()
    json.dump(summary, open("/tmp/iap_audit_summary.json", "w"), indent=2)
    print("\nSummary written to /tmp/iap_audit_summary.json")
