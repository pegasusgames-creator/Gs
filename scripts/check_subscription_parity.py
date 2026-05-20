#!/usr/bin/env python3
"""
check_subscription_parity.py — every benefit promised in a subscription's
store description must have a corresponding code path in game.html.

`season_pass_monthly` listed as "ad-free play, +100 coins every day, all
themes unlocked, unlimited hints" requires four honored flags. `weekly_pass`
at "+50 coins every day" requires the +50 grant path. We can't prove the
semantics, but we can require the obvious markers exist. (The monthly plan
intentionally grants MORE daily coins than the weekly — the monthly is the
unambiguous best deal, the weekly is the low-commitment entry tier.)

Standalone:  python3 scripts/check_subscription_parity.py [--all] [App...]
"""
import argparse, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs','BLOCKED_APPS',
        '__pycache__','.git','.idea','node_modules'}

# Canonical subscription prices (USD), keep in sync with docs/IAP_CATALOG.md.
# season_pass_monthly is the higher-priced default offer; weekly_pass is the
# cheap low-commitment entry plan — a weekly sub costing MORE than the monthly
# one (the pre-2026-05 bug) is a blocker.
CANONICAL_SUB_PRICE = {'season_pass_monthly': 4.99, 'weekly_pass': 1.99}


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f: return f.read()
    except (FileNotFoundError, IsADirectoryError): return None


def iaps(app):
    raw = read(os.path.join(REPO, app, 'metadata', 'iaps.json'))
    if not raw: return None
    try: return json.loads(raw)
    except json.JSONDecodeError: return None


def game_html(app):
    return read(os.path.join(REPO, app, 'android', 'app', 'src', 'main', 'assets', 'game.html'))


def check_app(app):
    out = []
    d = iaps(app)
    if not d: return out
    subs = d.get('subscriptions', []) or []
    if not subs: return out
    html = game_html(app) or ''
    if not html:
        out.append(('BLOCKER', 'has subscriptions but game.html is unreadable'))
        return out
    # Price sanity: canonical values + weekly must be cheaper than monthly.
    prices = {}
    for s in subs:
        sid, p = s.get('id') or '', s.get('price_usd')
        if sid and p is not None:
            try: prices[sid] = float(p)
            except (TypeError, ValueError): pass
        want = CANONICAL_SUB_PRICE.get(sid)
        if want is not None and sid in prices and abs(prices[sid] - want) > 0.001:
            out.append(('WARNING', f"{sid} priced ${prices[sid]} — canonical price is ${want:.2f}"))
    if 'weekly_pass' in prices and 'season_pass_monthly' in prices \
            and prices['weekly_pass'] >= prices['season_pass_monthly']:
        out.append(('BLOCKER', f"weekly_pass (${prices['weekly_pass']}) is priced >= season_pass_monthly "
                               f"(${prices['season_pass_monthly']}) — the weekly plan must be the cheaper one"))
    for s in subs:
        sid = s.get('id') or ''
        desc = (s.get('description') or '').lower()
        if sid and ("case '" + sid + "'" not in html) and (sid + "'" not in html) and (sid not in html):
            out.append(('BLOCKER', f"subscription {sid} has no handler in game.html"))
            continue
        # promised "daily coins" → there must be a daily-grant path
        m = re.search(r'\+?\s*(\d+)\s*coins?\s*(?:every\s*day|daily|a\s*day|per\s*day)', desc)
        if m and not re.search(r'lastSeasonGrantDate|lastWeeklyGrantDate|grantPassDailyBonus|passDaily', html):
            out.append(('WARNING', f"{sid} promises {m.group(1)} daily coins but no daily-grant code path (lastSeasonGrantDate / passDaily)"))
        if 'ad-free' in desc or 'ad free' in desc or 'no ads' in desc:
            if not re.search(r'adsRemoved|isPremium|isSeasonActive', html):
                out.append(('BLOCKER', f"{sid} promises ad-free but no adsRemoved()/isPremium() gate"))
        if 'all themes' in desc or 'exclusive theme' in desc or 'themes unlocked' in desc:
            if not re.search(r'isPremium|isSeasonActive', html):
                out.append(('WARNING', f"{sid} promises themes but no isPremium()/isSeasonActive() unlock-all path"))
        if 'unlimited hint' in desc and not re.search(r'isPremium|isSeasonActive', html):
            out.append(('WARNING', f"{sid} promises unlimited hints but hint decrement isn't gated by premium"))
        if 'unlimited undo' in desc and not re.search(r'isPremium|isSeasonActive', html):
            out.append(('WARNING', f"{sid} promises unlimited undos but undo decrement isn't gated by premium"))
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
    if not bad: print("subscription promise parity OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
