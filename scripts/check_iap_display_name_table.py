#!/usr/bin/env python3
"""
check_iap_display_name_table.py — the Step-3 in-app-product table in each
app's RELEASE_HANDOFF.md must have a non-empty Name in every product row.

The handoff table is what the developer copies into Play Console when
creating IAP products. A blank Name column means SKUs get created with
no display name — they show up unlabelled in the purchase sheet.
(Audit 2026-05-15 G6.)

Standalone:  python3 scripts/check_iap_display_name_table.py [--all] [App...]
"""
import argparse
import os
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


def check_app(app):
    out = []
    md = read(os.path.join(REPO, app, 'RELEASE_HANDOFF.md'))
    if md is None:
        return out
    for line in md.splitlines():
        s = line.strip()
        if not s.startswith('|'):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) < 4:
            continue
        # A product row's first cell is a backtick-quoted SKU id; the
        # header row ("Product ID") and separator ("---") are skipped.
        if not (cells[0].startswith('`') and cells[0].endswith('`')):
            continue
        if not cells[2]:
            out.append(('BLOCKER', f"RELEASE_HANDOFF.md IAP table row {cells[0]} "
                        f"has an empty Name column — the SKU would ship with "
                        f"no display name"))
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
        print("IAP display-name table OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
