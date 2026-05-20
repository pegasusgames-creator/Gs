#!/usr/bin/env python3
"""
check_price_string_parity.py — the price STRING shown in game.html's
PRODUCTS array must match metadata/iaps.json's price_usd to the cent.

iaps.json is the catalog source of truth; the PRODUCTS array is the
in-game display source of truth. They drift independently — a shop that
quotes "$3.99" while Play actually charges $4.99 is a Misleading-
Behavior policy risk (the WaterSort unlimited_undos slip that the
2026-05-15 audit caught). (Audit 2026-05-15 G2.)

Standalone:  python3 scripts/check_price_string_parity.py [--all] [App...]
"""
import argparse
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


def iap_prices(app):
    """{sku: price_usd} for every one-time product and subscription."""
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if not raw:
        return {}
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    out = {}
    for grp in ('one_time_products', 'subscriptions'):
        for p in d.get(grp, []) or []:
            pid = p.get('id') or p.get('product_id') or p.get('sku')
            if pid and p.get('price_usd') is not None:
                out[pid] = float(p['price_usd'])
    return out


def products_block(app):
    """Each real-money entry of game.html's PRODUCTS array, as (sku, price_str)."""
    gh = read(os.path.join(REPO, app, 'android', 'app', 'src', 'main',
                           'assets', 'game.html'))
    if not gh:
        return []
    m = re.search(r'const\s+PRODUCTS\s*=\s*\[(.*?)\]\s*;', gh, re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        if "type: 'coin'" in line or 'type: "coin"' in line:
            continue  # in-game-currency product — priced in coins, not dollars
        sku = re.search(r"id:\s*'([^']+)'", line)
        price = re.search(r"price:\s*'([^']+)'", line)
        if sku and price:
            out.append((sku.group(1), price.group(1)))
    return out


def check_app(app):
    out = []
    prices = iap_prices(app)
    prods = products_block(app)
    if not prods:
        return out  # no PRODUCTS array — not an IAP game
    for sku, price_str in prods:
        if sku not in prices:
            continue  # SKU absent from iaps.json — check_iap_invariants covers that
        want = prices[sku]
        m = re.search(r'(\d+(?:\.\d+)?)', price_str.replace(',', ''))
        if not m:
            out.append(('BLOCKER', f"PRODUCTS price for {sku} is {price_str!r} — "
                        f"no numeric price to compare against iaps.json ${want:.2f}"))
            continue
        shown = float(m.group(1))
        if abs(shown - want) > 0.001:
            out.append(('BLOCKER', f"PRODUCTS price for {sku} shows {price_str!r} "
                        f"(${shown:.2f}) but iaps.json price_usd is ${want:.2f} — "
                        f"the shop is quoting a different price than Play charges"))
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
        print("price string parity OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
