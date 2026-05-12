#!/usr/bin/env python3
"""
check_seasonal_events.py — a game that ships the retention stack (sells
season_pass_monthly) must define a SEASONAL_EVENTS table covering at
least October (Halloween), December (Winter) and February (Spring), per
CLAUDE.md "Seasonal events".

Detection: grep game.html for a SEASONAL_EVENTS / SEASONAL constant and
the three month markers.

Standalone:  python3 scripts/check_seasonal_events.py [--all] [App...]
"""
import argparse, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs','BLOCKED_APPS',
        '__pycache__','.git','.idea','node_modules'}


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f: return f.read()
    except (FileNotFoundError, IsADirectoryError): return None


def iaps_skus(app):
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if not raw: return set()
    try: d = json.loads(raw)
    except json.JSONDecodeError: return set()
    out = set()
    for k in ('one_time_products', 'subscriptions'):
        for p in d.get(k, []) or []:
            pid = p.get('id') or p.get('product_id') or p.get('sku')
            if pid: out.add(pid)
    return out


def check_app(app):
    out = []
    if 'season_pass_monthly' not in iaps_skus(app): return out
    html = read(os.path.join(REPO, app, 'android', 'app', 'src', 'main', 'assets', 'game.html'))
    if not html:
        out.append(('BLOCKER', 'ships the retention stack but game.html unreadable'))
        return out
    if not re.search(r'\bSEASONAL_EVENTS\b|\bSEASONAL\s*=', html):
        out.append(('BLOCKER', 'no SEASONAL_EVENTS constant defined'))
        return out
    flat = html.replace(' ', '')
    have_oct = 'month:10' in flat or 'Halloween' in html
    have_dec = 'month:12' in flat or 'Winter' in html
    have_feb = 'month:2' in flat or 'Spring' in html
    miss = [n for n, ok in [('October/Halloween', have_oct), ('December/Winter', have_dec), ('February/Spring', have_feb)] if not ok]
    if miss:
        out.append(('BLOCKER', 'SEASONAL_EVENTS missing month(s): ' + ', '.join(miss)))
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
    if not bad: print("seasonal events OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
