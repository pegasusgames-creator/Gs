#!/usr/bin/env python3
"""
check_menu_completeness.py — a game that ships the retention stack (sells
season_pass_monthly) must surface the cross-cutting menu requirements from
CLAUDE.md "Cross-cutting menu requirements":

  Continue button (when applicable) · Free Coins (rewarded ad, 25/4h) ·
  theme progress strip · Weekly Tournament banner (synthetic bracket) ·
  Missions/Daily indicator · Stats

These are usually injected at runtime by the retention block, so the check
greps game.html for the marker function names rather than parsing the
static menu DOM (the ≤6-static-button limit is enforced separately by
check_menu_button_count, which is why these have to be injected).

Standalone:  python3 scripts/check_menu_completeness.py [--all] [App...]
"""
import argparse, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs','BLOCKED_APPS',
        '__pycache__','.git','.idea','node_modules'}

# label/marker → human name. Each entry is a list of acceptable substrings.
REQUIRED = [
    ('Free Coins button',        ['Free Coins', 'free_coins', 'lastFreeCoinsAt']),
    ('theme progress strip',     ['Next theme', 'ThemeStrip', 'themeProgress', 'updateThemeProgressStrip']),
    ('Weekly Tournament banner', ['weeklyEventBanner', 'TournamentBanner', 'updateTournamentBanner', 'This week']),
    ('Continue/last-progress',   ['lastLevelProgress', 'startOrResumeGame', 'resumeLastLevel', 'Continue ·', 'CONTINUE ·']),
    ('Daily challenge',          ['startDailyChallenge', 'dailyChallenge', 'Daily Challenge', 'DAILY']),
    ('Stats / High scores',      ['statsScreen', 'scoresScreen', 'High Scores', 'hsBestScore', 'Stats']),
]


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
    for name, markers in REQUIRED:
        if not any(m in html for m in markers):
            out.append(('BLOCKER', f"menu is missing the {name} (no marker found: {markers[:2]}…)"))
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
    if not bad: print("menu completeness OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
