#!/usr/bin/env python3
"""
check_coin_tier_ladder.py — a game that sells any coin pack must sell the
full four-tier ladder (CLAUDE.md "Coin tier ladder"):

  coins_small  $0.99 / 100   coins_medium $4.99 / 600
  coins_large  $2.99 / 500    coins_mega   $9.99 / 1400

A partial ladder ("just a $0.99 and a $2.99 pack") leaves money on the
table and confuses returning buyers. If a game sells none of the coin
SKUs (pure utility app), it's not subject to this check.

Standalone:  python3 scripts/check_coin_tier_ladder.py [--all] [App...]
"""
import argparse, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs','BLOCKED_APPS',
        '__pycache__','.git','.idea','node_modules'}
LADDER = {'coins_small': 0.99, 'coins_medium': 4.99, 'coins_large': 2.99, 'coins_mega': 9.99}


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f: return f.read()
    except (FileNotFoundError, IsADirectoryError): return None


def products(app):
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if not raw: return {}
    try: d = json.loads(raw)
    except json.JSONDecodeError: return {}
    out = {}
    for p in d.get('one_time_products', []) or []:
        pid = p.get('id') or p.get('product_id') or p.get('sku')
        if pid: out[pid] = p.get('price_usd')
    return out


def check_app(app):
    out = []
    prods = products(app)
    sells_any = bool(set(prods) & set(LADDER))
    if not sells_any: return out
    for sku, want_price in LADDER.items():
        if sku not in prods:
            out.append(('BLOCKER', f"sells coin packs but is missing {sku} (${want_price}) — the ladder must be complete"))
        elif prods[sku] is not None and abs(float(prods[sku]) - want_price) > 0.001:
            out.append(('WARNING', f"{sku} priced ${prods[sku]} — canonical ladder price is ${want_price}"))
    return out


def list_apps():
    out = []
    for n in sorted(os.listdir(REPO)):
        if n in SKIP or n.startswith('.'): continue
        d = os.path.join(REPO, n)
        if os.path.isdir(d) and os.path.isdir(os.path.join(d, 'android')): out.append(n)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('apps', nargs='*'); ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    apps = list_apps() if a.all or not a.apps else a.apps
    bad = 0
    for app in apps:
        for sev, msg in check_app(app):
            bad += 1; print(f"[{sev}] {app}: {msg}")
    if not bad: print("coin tier ladder OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
