#!/usr/bin/env python3
"""
migrate_coin_ladder_2026_05.py — one-time migration: rewrite every app's
metadata/iaps.json to the 2026-05 canonical coin ladder + swapped pass
prices (CLAUDE.md "Coin tier ladder" / "Subscription/bundle promise parity",
docs/IAP_CATALOG.md).

  coins_medium  $4.99 / 600  →  $2.99 / 400
  coins_large   $2.99 / 500  →  $4.99 / 800   ("Best value" → "Great value")
  coins_mega    $9.99 / 1400 →  $9.99 / 2000  ("our largest" + "best value")
  season_pass_monthly  $1.99/mo → $4.99/mo
  weekly_pass          $4.99/wk → $1.99/wk
  (coins_small $0.99/100 is unchanged.)

Descriptions/titles for those SKUs are normalised to the canonical
verbatim text (check_iaps_descriptions enforces it anyway). Other SKUs
are left untouched. Preserves key order and 2-space JSON formatting.

Usage:  python3 scripts/migrate_coin_ladder_2026_05.py [--dry-run] [App...]
"""
import argparse, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template', '_release', 'docs', 'scripts', 'release_aabs',
        'BLOCKED_APPS', '__pycache__', '.git', '.idea', 'node_modules'}

ONE_TIME = {
    'coins_medium': {'price_usd': 2.99, 'title': '400 Coins',
        'description': 'Adds 400 coins to your wallet. Spend coins on hints, boosters, and unlocking new themes.'},
    'coins_large':  {'price_usd': 4.99, 'title': '800 Coins',
        'description': 'Adds 800 coins to your wallet. Great value coin pack — spend on hints, extra moves, and unlocking new themes.'},
    'coins_mega':   {'price_usd': 9.99, 'title': '2000 Coins',
        'description': 'Adds 2000 coins to your wallet. Our largest coin pack and best value — spend on hints, boosters, and unlocking new themes.'},
}
SUBS = {
    'season_pass_monthly': {'price_usd': 4.99,
        'description': 'Monthly pass: ad-free play, +100 coins every day, all themes unlocked, and unlimited boosters. Cancel anytime in Google Play.'},
    'weekly_pass': {'price_usd': 1.99,
        'description': 'Weekly pass: ad-free play, +50 coins every day, all themes unlocked, and unlimited boosters. Cancel anytime in Google Play.'},
}


def apply_entry(entry, canon):
    """Mutate one product dict in place; return list of (key, old, new) changes."""
    changes = []
    for key, new in canon.items():
        # 'title' canon maps onto whichever of title/name the entry uses
        if key == 'title' and 'title' not in entry and 'name' in entry:
            key = 'name'
        old = entry.get(key)
        if old != new and not (isinstance(old, float) and isinstance(new, float) and abs(old - new) < 1e-9):
            if key in entry or key in ('price_usd', 'description'):
                entry[key] = new
                changes.append((key, old, new))
    return changes


def list_apps():
    out = []
    for n in sorted(os.listdir(REPO)):
        if n in SKIP or n.startswith('.'):
            continue
        d = os.path.join(REPO, n)
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'metadata', 'iaps.json')):
            out.append(n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apps', nargs='*')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    apps = a.apps or list_apps()

    total_files = 0
    for app in apps:
        path = os.path.join(REPO, app, 'metadata', 'iaps.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"  ! {app}: cannot read iaps.json ({e})")
            continue
        if not isinstance(data, dict):
            continue
        app_changes = []
        for entry in data.get('one_time_products', []) or []:
            pid = entry.get('id') or entry.get('product_id') or entry.get('sku')
            if pid in ONE_TIME:
                for k, o, n in apply_entry(entry, ONE_TIME[pid]):
                    app_changes.append(f"{pid}.{k}: {o!r} → {n!r}")
        for entry in data.get('subscriptions', []) or []:
            pid = entry.get('id') or entry.get('product_id') or entry.get('sku')
            if pid in SUBS:
                for k, o, n in apply_entry(entry, SUBS[pid]):
                    app_changes.append(f"{pid}.{k}: {o!r} → {n!r}")
        if not app_changes:
            continue
        total_files += 1
        print(f"{app}:")
        for c in app_changes:
            print(f"    {c}")
        if not a.dry_run:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')

    print(f"\n{'(dry-run) ' if a.dry_run else ''}{total_files} iaps.json file(s) "
          f"{'would be' if a.dry_run else ''} updated.")


if __name__ == '__main__':
    main()
