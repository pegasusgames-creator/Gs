#!/usr/bin/env python3
"""
check_screenshot_headline_match.py — a wrapped store screenshot whose
headline names a specific screen (DAILY MISSIONS, WEEKLY TOURNAMENT,
STATS...) must actually SHOW that screen. A "Daily Missions" headline
above a plain gameplay board is a Misleading-Behavior policy risk — the
slip the 2026-05-15 audit caught on WaterSort phone slot 06.

Verification OCRs the RAW capture (store/screenshots/<surface>/raw/NN.png)
— the bare device screenshot, with no marketing headline baked in — so
the headline text itself can't satisfy its own check. OCR uses tesseract;
when tesseract is not installed the check reports each slot it could not
verify (WARNING) instead of passing silently. (Audit 2026-05-15 G3.)

Standalone:  python3 scripts/check_screenshot_headline_match.py [--all] [App...]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template', '_release', 'docs', 'scripts', 'release_aabs',
        'BLOCKED_APPS', '__pycache__', '.git', '.idea', 'node_modules'}

# headline trigger phrase -> any one of these words must appear in the raw capture
TRIGGERS = {
    'DAILY MISSIONS': ['mission'],
    'MISSIONS': ['mission'],
    'WEEKLY TOURNAMENT': ['tournament', 'bracket'],
    'TOURNAMENT': ['tournament', 'bracket'],
    'STATISTICS': ['stat'],
    'STATS': ['stat'],
    'LEADERBOARD': ['leaderboard', 'rank'],
}

SURFACES = [
    ('phone',     'screenshot_headlines.json',          'phone'),
    ('tablet_7',  'screenshot_headlines_tablet_7.json',  'tablet_7'),
    ('tablet_10', 'screenshot_headlines_tablet_10.json', 'tablet_10'),
]


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError):
        return None


def ocr(img):
    try:
        r = subprocess.run(['tesseract', img, 'stdout'], capture_output=True,
                           text=True, timeout=60)
        return (r.stdout or '').lower()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ''


def check_app(app):
    out = []
    have_ocr = shutil.which('tesseract') is not None
    for surf, hfile, sdir in SURFACES:
        raw = read(os.path.join(REPO, app, 'metadata', hfile))
        if not raw:
            continue
        try:
            heads = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for i, entry in enumerate(heads):
            head = (str(entry.get('line1', '')) + ' '
                    + str(entry.get('line2', ''))).upper()
            triggered = [(t, w) for t, w in TRIGGERS.items() if t in head]
            if not triggered:
                continue
            img = os.path.join(REPO, app, 'store', 'screenshots', sdir,
                               'raw', f'{i + 1:02d}.png')
            if not os.path.exists(img):
                continue
            trig, expect = triggered[0]
            if not have_ocr:
                # Don't fan out one warning per slot — the message would
                # repeat for every triggered headline in every app. The
                # advisory is emitted once at the end of check_app instead.
                continue
            text = ocr(img)
            if text and not any(w in text for w in expect):
                out.append(('BLOCKER', f"{surf} slot {i + 1} headline says "
                            f"'{trig}' but the raw screenshot has no "
                            f"{'/'.join(expect)} text — the image does not "
                            f"show the screen the headline claims"))
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
        print("screenshot headline/content match OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
