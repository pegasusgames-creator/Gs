#!/usr/bin/env python3
"""
check_coin_tier_ladder.py — a game that sells any coin pack must sell the
full four-tier ladder (CLAUDE.md "Coin tier ladder"), and the ladder must
be strictly monotonic — each tier costs more, gives more coins, and a
better coins-per-dollar rate than the one below it:

  coins_small  $0.99 /  100   (~101 coins/$)
  coins_medium $2.99 /  400   (~134 coins/$)
  coins_large  $4.99 /  800   (~160 coins/$)
  coins_mega   $9.99 / 2000   (~200 coins/$ — best value, the anchor)

A partial ladder ("just a $0.99 and a $2.99 pack") leaves money on the
table and confuses returning buyers. The pre-2026-05 ordering where
coins_large was a cheap $2.99 "anchor" priced *below* coins_medium is
also forbidden. If a game sells none of the coin SKUs (pure utility
app), it's not subject to this check.

Standalone:  python3 scripts/check_coin_tier_ladder.py [--all] [App...]
"""
import argparse, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs','BLOCKED_APPS',
        '__pycache__','.git','.idea','node_modules'}

# Canonical ladder, lowest tier first: (sku, price_usd, coin_amount)
LADDER = [
    ('coins_small',  0.99,  100),
    ('coins_medium', 2.99,  400),
    ('coins_large',  4.99,  800),
    ('coins_mega',   9.99, 2000),
]
LADDER_PRICE = {sku: price for sku, price, _ in LADDER}
LADDER_COINS = {sku: coins for sku, _, coins in LADDER}
LADDER_SKUS  = {sku for sku, _, _ in LADDER}


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f: return f.read()
    except (FileNotFoundError, IsADirectoryError): return None


def products(app):
    """Returns {sku: {'price': float|None, 'desc': str}} from one_time_products."""
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if not raw: return {}
    try: d = json.loads(raw)
    except json.JSONDecodeError: return {}
    out = {}
    for p in d.get('one_time_products', []) or []:
        pid = p.get('id') or p.get('product_id') or p.get('sku')
        if pid: out[pid] = {'price': p.get('price_usd'), 'desc': p.get('description') or ''}
    return out


def check_app(app):
    out = []
    prods = products(app)
    sells_any = bool(set(prods) & LADDER_SKUS)
    if not sells_any: return out
    for sku, want_price, want_coins in LADDER:
        if sku not in prods:
            out.append(('BLOCKER', f"sells coin packs but is missing {sku} (${want_price:.2f} / {want_coins} coins) — the ladder must be complete"))
            continue
        have_price = prods[sku]['price']
        if have_price is not None and abs(float(have_price) - want_price) > 0.001:
            out.append(('WARNING', f"{sku} priced ${have_price} — canonical ladder price is ${want_price:.2f}"))
        desc = prods[sku]['desc']
        nums = {int(n) for n in re.findall(r'\d+', desc.replace(',', ''))}
        if nums and want_coins not in nums:
            out.append(('WARNING', f"{sku} description mentions {sorted(nums)} — canonical coin amount is {want_coins}"))
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
