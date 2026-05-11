#!/usr/bin/env python3
"""
check_iap_invariants.py — pre-publish guard for the four IAP correctness
invariants documented in CLAUDE.md "## IAP correctness invariants".

Wired into scripts/pre_publish_check.py via `check_iap_invariants(apps)`.
Can also be run standalone:

    python3 scripts/check_iap_invariants.py <App>
    python3 scripts/check_iap_invariants.py --all

Invariants enforced:
  1. VALID_PRODUCTS in MainActivity.java == SKU id set in iaps.json.
  2. CONSUMABLE_PRODUCTS set declared and consumeAsync called for it.
     acknowledgePurchase wired for non-consumables. Both behind a 3-day
     Play timeout window — neither path may be missing.
  3. game.html defines window.onPurchaseSuccess (directly or as alias to
     onPurchaseComplete). Java's bridge calls window.onPurchaseSuccess;
     if undefined, every purchase silently drops.
  4. replayPendingGrants() is wired so a SKU bought before its mechanic
     existed (utility apps with template-pasted lives/hints) is replayed
     on the next launch instead of dropped on the floor.

Surfaces the violation reason (not just a yes/no) so Claude Code or the
human reading the report knows what to fix.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs',
        'BLOCKED_APPS','__pycache__','.git','.idea','node_modules'}

# SKUs that must be CONSUMABLE per docs/IAP_CATALOG.md.
CONSUMABLE_SKUS = {
    "coins_small", "coins_large", "five_lives", "unlimited_lives_1h",
    "hint_pack", "undo_pack", "starter_pack",
}


def list_apps():
    out = []
    for n in sorted(os.listdir(REPO)):
        if n in SKIP or n.startswith('.'): continue
        d = os.path.join(REPO, n)
        if not os.path.isdir(d): continue
        if not os.path.isfile(os.path.join(d, 'metadata', 'iaps.json')): continue
        if not os.path.isdir(os.path.join(d, 'android')): continue
        out.append(n)
    return out


def find_main(app):
    root = os.path.join(REPO, app, 'android', 'app', 'src', 'main', 'java')
    if not os.path.isdir(root): return None
    for dp, _, fs in os.walk(root):
        if 'MainActivity.java' in fs:
            return os.path.join(dp, 'MainActivity.java')
    return None


def get_iaps_skus(app):
    p = os.path.join(REPO, app, 'metadata', 'iaps.json')
    if not os.path.isfile(p): return None
    try:
        d = json.load(open(p))
    except (IOError, ValueError):
        return None
    return sorted({x['id'] for x in d.get('one_time_products', []) + d.get('subscriptions', [])
                   if isinstance(x, dict) and 'id' in x})


def check_app(app):
    """Returns list of (severity, message). severity is 'BLOCKER' or 'WARN'."""
    fails = []

    # iaps.json must exist
    skus = get_iaps_skus(app)
    if skus is None:
        return [('BLOCKER', 'iaps.json missing or unreadable')]

    expected_consumables = set(skus) & CONSUMABLE_SKUS

    # MainActivity must exist
    java_path = find_main(app)
    if not java_path:
        return [('BLOCKER', 'MainActivity.java not found')]
    java = open(java_path).read()

    # ── Invariant 1: VALID_PRODUCTS == iaps.json SKUs
    m = re.search(r'VALID_PRODUCTS\s*=\s*new HashSet<>\(Arrays\.asList\(([^)]+)\)', java)
    if not m:
        fails.append(('BLOCKER', 'VALID_PRODUCTS set not declared in MainActivity.java'))
    else:
        valid = set(re.findall(r'"([^"]+)"', m.group(1)))
        if valid != set(skus):
            extra   = sorted(valid - set(skus))
            missing = sorted(set(skus) - valid)
            parts = []
            if missing: parts.append(f'iaps.json has {missing} not in VALID_PRODUCTS')
            if extra:   parts.append(f'VALID_PRODUCTS has {extra} not in iaps.json')
            fails.append(('BLOCKER', 'Invariant 1 — ' + '; '.join(parts)
                          + ' (purchase will be rejected before Play sheet opens)'))

    # ── Invariant 2: CONSUMABLE_PRODUCTS declared, consumeAsync + acknowledgePurchase wired
    m2 = re.search(r'CONSUMABLE_PRODUCTS\s*=\s*new HashSet<>\(Arrays\.asList\(([^)]+)\)', java)
    if not m2:
        fails.append(('BLOCKER', 'Invariant 2 — CONSUMABLE_PRODUCTS set missing '
                      '(consumables can be bought once but never re-bought)'))
    else:
        consumable_set = set(re.findall(r'"([^"]+)"', m2.group(1)))
        miss = expected_consumables - consumable_set
        if miss:
            fails.append(('BLOCKER', f'Invariant 2 — CONSUMABLE_PRODUCTS missing {sorted(miss)}'))
    if 'consumeAsync' not in java:
        fails.append(('BLOCKER', 'Invariant 2 — handlePurchase does not call consumeAsync'))
    if 'ConsumeParams' not in java:
        fails.append(('BLOCKER', 'Invariant 2 — ConsumeParams import missing'))
    if 'acknowledgePurchase' not in java:
        fails.append(('BLOCKER', 'Invariant 2 — handlePurchase does not call acknowledgePurchase '
                      '(non-consumables auto-refund after 3 days)'))
    if 'Log.i("IAP"' not in java and 'Log.w("IAP"' not in java:
        fails.append(('WARN', 'Invariant 2 — no Log.{i,w}("IAP", …) for logcat visibility'))

    # ── Invariants 3 & 4: game.html
    html_path = os.path.join(REPO, app, 'android', 'app', 'src', 'main', 'assets', 'game.html')
    if not os.path.isfile(html_path):
        fails.append(('BLOCKER', 'game.html not found'))
        return fails
    html = open(html_path, encoding='utf-8', errors='replace').read()

    has_assign  = bool(re.search(r'window\.onPurchaseSuccess\s*=', html))
    has_fn_decl = bool(re.search(r'function\s+onPurchaseSuccess\s*\(', html))
    if not (has_assign or has_fn_decl):
        fails.append(('BLOCKER', 'Invariant 3 — game.html has no window.onPurchaseSuccess '
                      'definition (Java bridge call drops every SKU silently)'))

    if 'replayPendingGrants' not in html:
        fails.append(('BLOCKER', 'Invariant 4 — game.html has no replayPendingGrants() — '
                      'SKUs bought without a matching mechanic disappear forever'))
    if 'pendingGrants' not in html:
        fails.append(('BLOCKER', 'Invariant 4 — game.html has no pendingGrants fallback'))

    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apps', nargs='*')
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    if args.all:
        apps = list_apps()
    elif args.apps:
        apps = args.apps
    else:
        ap.print_help()
        sys.exit(2)

    blockers, warnings = [], []
    pass_n = 0
    for app in apps:
        fs = check_app(app)
        b = [m for s, m in fs if s == 'BLOCKER']
        w = [m for s, m in fs if s == 'WARN']
        if b:
            for msg in b: blockers.append(f'{app}: {msg}')
        if w:
            for msg in w: warnings.append(f'{app}: {msg}')
        if not b and not w:
            pass_n += 1

    print(f'IAP invariants: {pass_n}/{len(apps)} pass, '
          f'{len(blockers)} blockers, {len(warnings)} warnings')
    if blockers:
        print('\nBLOCKERS:')
        for m in blockers[:30]: print(f'  ✗ {m}')
        if len(blockers) > 30: print(f'  … and {len(blockers)-30} more')
    if warnings:
        print('\nWARNINGS:')
        for m in warnings[:30]: print(f'  ! {m}')
        if len(warnings) > 30: print(f'  … and {len(warnings)-30} more')
    sys.exit(1 if blockers else 0)


if __name__ == '__main__':
    main()
