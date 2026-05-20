#!/usr/bin/env python3
"""
check_iap_grant_parity.py — every promise an IAP makes in its store
description must be honored by the literal grant value in game.html.

The bug class this catches: a "Coin Pack S" listed in iaps.json as
"Adds 100 coins" whose onPurchaseSuccess handler actually does
`State.coins += 50`. Released users pay and get half. Google still
charges them. (WaterSort, Nonogram and Puzzle2048 all shipped this.)

Wired into scripts/pre_publish_check.py via check_app(app). Standalone:

    python3 scripts/check_iap_grant_parity.py <App>
    python3 scripts/check_iap_grant_parity.py --all

Scope: only apps whose metadata/iaps.json actually sells one of the
known economy SKUs. Utility apps that never wired a coin/hint mechanic
are not subject to this check.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template', '_release', 'docs', 'scripts', 'release_aabs',
        'BLOCKED_APPS', '__pycache__', '.git', '.idea', 'node_modules'}

# SKU id -> list of (label, regex of an acceptable literal grant in game.html
#                    near that SKU's purchase-handler case).
# The numbers here are the canonical grants from CLAUDE.md "Coin tier
# ladder" and "## IAP correctness invariants".
EXPECTED_GRANTS = {
    'coins_small':  [('100 coins', r'\b100\b')],
    'coins_medium': [('400 coins', r'\b400\b')],
    'coins_large':  [('800 coins', r'\b800\b')],
    'coins_mega':   [('2000 coins', r'\b2000\b')],
    'hint_pack':    [('10 hints', r'\b10\b')],
    'undo_pack':    [('10 undos', r'\b10\b')],
    'starter_pack': [('100 coins', r'\b100\b'),
                     ('5 hints or 5 undos', r'\b5\b'),
                     ('5 lives', r'\b5\b')],
}
ECONOMY_SKUS = set(EXPECTED_GRANTS)


def read(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError):
        return None


def iaps_skus(app):
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if not raw:
        return set()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return set()
    ids = set()
    for key in ('one_time_products', 'subscriptions'):
        for p in data.get(key, []) or []:
            pid = p.get('product_id') or p.get('id') or p.get('sku')
            if pid:
                ids.add(pid)
    return ids


def game_html(app):
    return read(os.path.join(REPO, app, 'android', 'app', 'src', 'main',
                             'assets', 'game.html'))


def applicable(app):
    return bool(iaps_skus(app) & ECONOMY_SKUS)


def _case_window(html, sku):
    """Return the chunk of game.html following `case 'sku':` up to the
    next `case '...'` / `break;` cluster, where the grant should live.
    Concatenates every occurrence (original handler + any hooked one)."""
    out = []
    for m in re.finditer(r"case\s+['\"]" + re.escape(sku) + r"['\"]\s*:", html):
        start = m.end()
        tail = html[start:start + 600]
        # cut at the next `case '` so we don't bleed into the next SKU
        nxt = re.search(r"case\s+['\"]", tail)
        if nxt:
            tail = tail[:nxt.start()]
        out.append(tail)
    # also catch `if (id === 'sku') { ... }` style hooks
    for m in re.finditer(r"['\"]" + re.escape(sku) + r"['\"]\s*\)\s*\{", html):
        out.append(html[m.end():m.end() + 400])
    return "\n".join(out)


def check_app(app):
    out = []
    if not applicable(app):
        return out
    skus = iaps_skus(app)
    html = game_html(app)
    if not html:
        out.append(('BLOCKER', 'game.html unreadable — cannot verify grant parity'))
        return out
    for sku in sorted(skus & ECONOMY_SKUS):
        window = _case_window(html, sku)
        if not window:
            out.append(('BLOCKER', f"{sku} is sold in iaps.json but has no "
                                   f"onPurchaseSuccess handler in game.html"))
            continue
        for label, pat in EXPECTED_GRANTS[sku]:
            if not re.search(pat, window):
                out.append(('BLOCKER', f"{sku} handler does not appear to grant "
                                       f"the promised {label} (expected /{pat}/ "
                                       f"near `case '{sku}':`)"))
    return out


def list_apps():
    out = []
    for n in sorted(os.listdir(REPO)):
        if n in SKIP or n.startswith('.'):
            continue
        d = os.path.join(REPO, n)
        if not os.path.isdir(d) or not os.path.isdir(os.path.join(d, 'android')):
            continue
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
        print("grant parity OK" + ("" if a.apps else " (all applicable apps)"))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
