#!/usr/bin/env python3
"""
check_booster_catalog.py — a game must expose the genre-appropriate
booster set (CLAUDE.md "Booster catalog by genre"):

  sort-puzzle : Color Reveal, Steady Pour, Fresh Start, Extra Tube, Magic Wand
  picross     : Hint, Undo, Reset, Check, Reveal Row, Reveal Cell
  2048-like   : Undo, New Game, Magic Merge, Remove Tile

Genre is inferred from app_themes.py / folder name keywords; if the genre
can't be inferred the check is skipped (warning at most). Detection is a
string-grep of game.html for the booster labels / function names.

Standalone:  python3 scripts/check_booster_catalog.py [--all] [App...]
"""
import argparse, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template','_release','docs','scripts','release_aabs','BLOCKED_APPS',
        '__pycache__','.git','.idea','node_modules'}

GENRE_BOOSTERS = {
    'sort':    ['Color Reveal', 'Steady Pour', 'Fresh Start', 'addExtraTube', 'magicWand'],
    'picross': ['Hint', 'Undo', 'Reset', 'Check', 'revealRow', 'revealCell'],
    '2048':    ['doUndo', 'startNewGame', 'magicMerge', 'removeTile'],
}
# folder/keyword → genre
GENRE_KEYWORDS = [
    (re.compile(r'watersort|ballsort|liquidsort|sortpuzzle', re.I), 'sort'),
    (re.compile(r'nonogram|picross|hanjie', re.I), 'picross'),
    (re.compile(r'2048|puzzle2048|merge2048', re.I), '2048'),
]


def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f: return f.read()
    except (FileNotFoundError, IsADirectoryError): return None


def genre_for(app):
    for rx, g in GENRE_KEYWORDS:
        if rx.search(app): return g
    return None


def check_app(app):
    out = []
    g = genre_for(app)
    if not g: return out
    html = read(os.path.join(REPO, app, 'android', 'app', 'src', 'main', 'assets', 'game.html'))
    if not html:
        out.append(('BLOCKER', f"recognised as a {g} game but game.html unreadable"))
        return out
    missing = [b for b in GENRE_BOOSTERS[g] if b not in html]
    if missing:
        out.append(('BLOCKER', f"{g} game missing booster(s) from the catalog: " + ', '.join(missing)))
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
    if not bad: print("booster catalog OK")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
