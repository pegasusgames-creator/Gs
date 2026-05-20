#!/usr/bin/env python3
"""
check_interstitial_cadence.py — a game that shows interstitials must gate
at least one by a play-volume counter (levels/games played), not only by
a screen transition.

Transition-only gating ("show an interstitial whenever we return to the
menu") means a long uninterrupted session can see zero interstitials,
while a player who dips in and out gets one every time. A counter — a
"levelsSinceInterstitial >= N" tally, or a "currentLevel % N === 0"
modulo gate — makes the cadence predictable. Games with no interstitials
at all (pure utility apps) are not subject to this. (Audit 2026-05-15 G5.)

Standalone:  python3 scripts/check_interstitial_cadence.py [--all] [App...]
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template', '_release', 'docs', 'scripts', 'release_aabs',
        'BLOCKED_APPS', '__pycache__', '.git', '.idea', 'node_modules'}

# An interstitial CALL site (the function definition is excluded separately).
INT_CALL = re.compile(r'(?:safe)?[Ss]how[Ii]nterstitial\s*\(')
# A play-volume gate near a call: a modulo cadence, a since-counter, or a
# ">= N" tally tracked against an interstitial counter.
COUNTER_NEAR = re.compile(r'%\s*\d|[Ss]ince[Ii]nterstitial'
                          r'|[Ii]nterstitial\w*[Cc]ount|[Cc]ount\w*[Ii]nterstitial'
                          r'|>=\s*\d')


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
    lines = gh.splitlines()
    call_lines = [i for i, l in enumerate(lines)
                  if INT_CALL.search(l) and 'function' not in l]
    if not call_lines:
        return out  # no interstitials — not subject to this check
    for i in call_lines:
        window = '\n'.join(lines[max(0, i - 3):i + 2])
        if COUNTER_NEAR.search(window):
            return out  # at least one counter-gated interstitial — OK
    out.append(('BLOCKER', "shows interstitials but none are gated by a "
                "level/game counter — gate one with a levelsSinceInterstitial "
                "tally or a 'currentLevel % N' cadence so long sessions still "
                "see ads instead of relying only on screen transitions"))
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
        print("interstitial cadence OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
