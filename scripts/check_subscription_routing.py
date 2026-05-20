#!/usr/bin/env python3
"""
check_subscription_routing.py — every subscription SKU an app sells must
be routed to the Play SUBS billing flow.

MainActivity.java's launchPurchase() decides, per product ID, whether to
open a one-time (INAPP) or a subscription (SUBS) billing flow. A
subscription SKU sent down the INAPP path makes Play return no
ProductDetails, so launchBillingFlow() never fires and the purchase
sheet never opens — a sold SKU that simply cannot be bought, with no
visible error.

This catches the May 2026 UnblockPuzzle / PipeConnect bug: launchPurchase
hardcoded `"season_pass_monthly".equals(productId)` and never routed the
second subscription, `weekly_pass`. The fix is a SUBSCRIPTION_PRODUCTS
set covering every subscription SKU — the pattern the shipped apps
(WaterSortPuzzle / Nonogram / Puzzle2048) already use.

A subscription SKU counts as routed if, inside the `if (...)` guard that
controls a launchSubscription() call, its product ID appears either as a
`"<sku>".equals(productId)` literal or inside a Set the guard tests with
`.contains(productId)`. (Audit 2026-05-20.)

Standalone:  python3 scripts/check_subscription_routing.py [--all] [App...]
"""
import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template', '_release', 'docs', 'scripts', 'release_aabs',
        'BLOCKED_APPS', '__pycache__', '.git', '.idea', 'node_modules'}


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError):
        return None


def subscription_skus(app):
    """Subscription SKU IDs declared in metadata/iaps.json."""
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if raw is None:
        return []
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    subs = []

    def _add(item):
        sid = item.get('id') or item.get('product_id')
        if sid and sid not in subs:
            subs.append(sid)

    if isinstance(data, dict):
        for item in data.get('subscriptions', []) or []:
            _add(item)
        # also a flat catalog whose items carry a type marker
        for key in ('products', 'iaps', 'one_time_products'):
            for item in data.get(key, []) or []:
                if str(item.get('type', '')).lower() in ('subs', 'subscription'):
                    _add(item)
    elif isinstance(data, list):
        for item in data:
            if str(item.get('type', '')).lower() in ('subs', 'subscription'):
                _add(item)
    return subs


def main_activity_path(app):
    hits = glob.glob(os.path.join(
        REPO, app, 'android', 'app', 'src', 'main', 'java',
        '**', 'MainActivity.java'), recursive=True)
    return hits[0] if hits else None


def routed_skus(src):
    """SKU IDs that launchPurchase() routes to the SUBS billing flow."""
    lines = src.splitlines()
    routed, set_vars = set(), set()
    for i, line in enumerate(lines):
        if 'launchSubscription' not in line:
            continue
        if re.search(r'void\s+launchSubscription', line):
            continue  # the method definition itself, not a call site
        # guard = the nearest enclosing `if (` up to the call line
        start = i
        for j in range(i, max(-1, i - 6), -1):
            if re.search(r'\bif\s*\(', lines[j]):
                start = j
                break
        guard = '\n'.join(lines[start:i + 1])
        routed.update(re.findall(r'"([A-Za-z0-9_]+)"\s*\.equals', guard))
        routed.update(re.findall(r'\.equals\(\s*"([A-Za-z0-9_]+)"', guard))
        for m in re.finditer(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\.contains\s*\(', guard):
            # VALID_PRODUCTS guards the whole method, not the SUBS branch
            if m.group(1) != 'VALID_PRODUCTS':
                set_vars.add(m.group(1))
    # expand each routing Set's Arrays.asList(...) literals
    for var in set_vars:
        m = re.search(re.escape(var) + r'\s*=\s*new\s+\w+<>?\(\s*Arrays\.asList\((.*?)\)\s*\)',
                      src, re.DOTALL)
        if m:
            routed.update(re.findall(r'"([A-Za-z0-9_]+)"', m.group(1)))
    return routed


def check_app(app):
    out = []
    subs = subscription_skus(app)
    if not subs:
        return out
    ma = main_activity_path(app)
    src = read(ma) if ma else None
    if src is None:
        return out
    if 'launchSubscription' not in src:
        out.append(('BLOCKER',
                    "sells subscription SKUs (%s) but MainActivity.java has no "
                    "launchSubscription() / SUBS billing path" % ', '.join(sorted(subs))))
        return out
    routed = routed_skus(src)
    for s in sorted(subs):
        if s not in routed:
            out.append(('BLOCKER',
                        "subscription SKU '%s' is not routed to the SUBS billing "
                        "flow in launchPurchase() — Play would query it as a "
                        "one-time INAPP product and the purchase sheet would "
                        "never open. Add it to the SUBSCRIPTION_PRODUCTS set." % s))
    return out


def list_apps():
    out = []
    for n in sorted(os.listdir(REPO)):
        if n in SKIP or n.startswith('.'):
            continue
        d = os.path.join(REPO, n)
        if os.path.isdir(d) and os.path.isdir(os.path.join(d, 'android')):
            out.append(n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apps', nargs='*')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    apps = list_apps() if a.all or not a.apps else a.apps
    bad = 0
    for app in apps:
        for sev, msg in check_app(app):
            bad += 1
            print(f"[{sev}] {app}: {msg}")
    if not bad:
        print("subscription billing routing OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
