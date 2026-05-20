#!/usr/bin/env python3
"""
check_restore_purchases_ui.py — every game must expose Restore Purchases
in its UI: a control whose handler calls Android.restorePurchases().

Without it, a user who reinstalls or switches devices cannot recover
non-consumable purchases (Remove Ads, passes, unlimited unlocks) and
refund rates spike. The control may be a static Settings row or one
added by the runtime settings addendum — either way game.html
references restorePurchases. (Audit 2026-05-15 G4.)

Standalone:  python3 scripts/check_restore_purchases_ui.py [--all] [App...]
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
    gh = read(os.path.join(REPO, app, 'android', 'app', 'src', 'main',
                           'assets', 'game.html'))
    if gh is None:
        return out
    if 'restorePurchases' not in gh:
        out.append(('BLOCKER', "no Restore Purchases control in game.html — "
                    "Settings needs a row whose handler calls "
                    "Android.restorePurchases()"))
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
        print("restore purchases UI OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
