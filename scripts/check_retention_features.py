#!/usr/bin/env python3
"""
check_retention_features.py — enforces the CLAUDE.md "Retention-feature
parity invariant" for any game that sells a season pass.

A game.html that sells `season_pass_monthly` (i.e. ships the retention
stack) must define, at minimum:
  - window.replayPendingGrants (IAP invariant 4)
  - an isSeasonActive() / hasActiveSeasonPass() helper
  - a wrapped window.onPurchaseSuccess (delegates to the original handler)
  - a hint/undo counter mechanic if the matching pack SKU is sold
    (hint_pack ⇒ hintCount/hintPack; undo_pack ⇒ undoPack)

Standalone:  python3 scripts/check_retention_features.py [--all] [App...]
Wired into pre_publish_check.py via check_app(app).
"""
import argparse, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs','BLOCKED_APPS',
        '__pycache__','.git','.idea','node_modules'}


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f: return f.read()
    except (FileNotFoundError, IsADirectoryError): return None


def iaps(app):
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if not raw: return None
    try: return json.loads(raw)
    except json.JSONDecodeError: return None


def sku_ids(app):
    d = iaps(app) or {}
    out = set()
    for k in ('one_time_products', 'subscriptions'):
        for p in d.get(k, []) or []:
            pid = p.get('id') or p.get('product_id') or p.get('sku')
            if pid: out.add(pid)
    return out


def game_html(app):
    return read(os.path.join(REPO, app, 'android', 'app', 'src', 'main', 'assets', 'game.html'))


def applicable(app):
    return 'season_pass_monthly' in sku_ids(app)


def check_app(app):
    out = []
    if not applicable(app): return out
    html = game_html(app)
    if not html:
        out.append(('BLOCKER', 'sells season_pass_monthly but game.html is unreadable'))
        return out
    skus = sku_ids(app)
    if 'replayPendingGrants' not in html:
        out.append(('BLOCKER', 'missing window.replayPendingGrants (IAP invariant 4)'))
    if not re.search(r'\b(isSeasonActive|hasActiveSeasonPass)\b', html):
        out.append(('BLOCKER', 'missing isSeasonActive()/hasActiveSeasonPass() helper'))
    if not re.search(r'window\.onPurchaseSuccess\s*=\s*function', html):
        out.append(('BLOCKER', 'missing wrapped window.onPurchaseSuccess'))
    if 'isPremium' not in html and 'isWeeklyActive' not in html and 'hasActiveWeeklyPass' not in html:
        out.append(('WARNING', 'no isPremium()/isWeeklyActive() helper — weekly_pass benefits may not be honored'))
    if 'hint_pack' in skus and not re.search(r'\bhint(Count|Pack)\b', html):
        out.append(('BLOCKER', 'sells hint_pack but game.html has no hintCount/hintPack counter'))
    if 'undo_pack' in skus and 'undoPack' not in html:
        out.append(('BLOCKER', 'sells undo_pack but game.html has no undoPack counter'))
    if 'starter_pack' in skus and "case 'starter_pack'" not in html and "starter_pack'" not in html:
        out.append(('WARNING', 'sells starter_pack but no obvious starter_pack handler in game.html'))
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
    if not bad: print("retention-feature parity OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
