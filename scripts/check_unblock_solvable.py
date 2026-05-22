#!/usr/bin/env python3
"""
check_unblock_solvable.py — pre-publish puzzle-solvability gate for
sliding-block / Rush-Hour games (UnblockPuzzle and any clone of it).

Wired into scripts/pre_publish_check.py as the "puzzle solvability"
gate. Can also be run standalone:

    python3 scripts/check_unblock_solvable.py <App>
    python3 scripts/check_unblock_solvable.py --all

Why this exists: the 2026-05-15 UnblockPuzzle audit found 35/150 levels
structurally unsolvable and 114/150 with a wrong hand-guessed `optimal`
move count. A non-red horizontal block on the red car's exit row (y=2)
can never leave that row and permanently walls the exit lane — that
single mistake produced every unsolvable level. No hand-authored level
set is trusted without a full solver pass.

This module parses the LEVELS array out of an app's game.html, runs a
BFS solver on every level, and BLOCKS the build if ANY level is:
  - unsolvable, or
  - carrying a stored `optimal` that differs from the solver's true
    minimum-move count, or
  - placing a non-red horizontal block on the exit row y=2.

Apps with no UnblockPuzzle-style LEVELS array are silently skipped, so
`--all` is safe to run across the whole portfolio.

Board model (matches game.html): 6x6 grid; red R = 2x1 horizontal on
row y=2; win when red.x + red.w >= 6; a block slides any number of
empty cells along its axis (horizontal if w>1, else vertical) and each
reposition counts as one move.
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template', '_release', 'docs', 'scripts', 'release_aabs',
        'BLOCKED_APPS', '__pycache__', '.git', '.idea', 'node_modules'}
GRID = 6
MAX_DEPTH = 60

# ───────────────────────── BFS solver ─────────────────────────
# A level is (specs, pos, optimal):
#   specs = tuple of (w, h, isRed) — block shapes, fixed
#   pos   = tuple of (x, y)        — block positions, the search state
def solve(specs, init, max_depth=MAX_DEPTH):
    """Minimum move count to win, or -1 if unsolvable within max_depth."""
    n = len(specs)
    red_i = next((i for i, s in enumerate(specs) if s[2]), None)
    if red_i is None:
        return -1
    rw = specs[red_i][0]
    if init[red_i][0] + rw >= GRID:
        return 0
    seen = {init}
    frontier = [init]
    for depth in range(1, max_depth + 1):
        nxt = []
        for pos in frontier:
            occ = bytearray(GRID * GRID)
            for i in range(n):
                x, y = pos[i]
                w, h, _ = specs[i]
                for dy in range(h):
                    base = (y + dy) * GRID + x
                    for dx in range(w):
                        occ[base + dx] = 1
            for i in range(n):
                x, y = pos[i]
                w, h, is_red = specs[i]
                # vacate this block's own cells before probing its slide
                for dy in range(h):
                    base = (y + dy) * GRID + x
                    for dx in range(w):
                        occ[base + dx] = 0
                if w > 1:                                  # horizontal
                    nx = x - 1
                    while nx >= 0 and not occ[y * GRID + nx]:
                        if is_red and nx + w >= GRID:
                            return depth
                        np = pos[:i] + ((nx, y),) + pos[i + 1:]
                        if np not in seen:
                            seen.add(np)
                            nxt.append(np)
                        nx -= 1
                    nx = x + 1
                    while nx + w <= GRID and not occ[y * GRID + nx + w - 1]:
                        if is_red and nx + w >= GRID:
                            return depth
                        np = pos[:i] + ((nx, y),) + pos[i + 1:]
                        if np not in seen:
                            seen.add(np)
                            nxt.append(np)
                        nx += 1
                else:                                      # vertical
                    ny = y - 1
                    while ny >= 0 and not occ[ny * GRID + x]:
                        np = pos[:i] + ((x, ny),) + pos[i + 1:]
                        if np not in seen:
                            seen.add(np)
                            nxt.append(np)
                        ny -= 1
                    ny = y + 1
                    while ny + h <= GRID and not occ[(ny + h - 1) * GRID + x]:
                        np = pos[:i] + ((x, ny),) + pos[i + 1:]
                        if np not in seen:
                            seen.add(np)
                            nxt.append(np)
                        ny += 1
                # restore this block's cells
                for dy in range(h):
                    base = (y + dy) * GRID + x
                    for dx in range(w):
                        occ[base + dx] = 1
        if not nxt:
            return -1
        frontier = nxt
    return -1


# ───────────────────────── parser ─────────────────────────
_LEVEL_RE = re.compile(r'\{blocks:\[(.*?)\],optimal:(\d+)\}')
_BLOCK_RE = re.compile(r'R\((\d+)\)|H\((\d+),(\d+),(\d+)\)|V\((\d+),(\d+),(\d+)\)')


def parse_levels(html):
    """Return a list of (specs, pos, optimal) for an UnblockPuzzle-style
    LEVELS array, or [] if game.html has no such array."""
    levels = []
    for lm in _LEVEL_RE.finditer(html):
        specs, pos = [], []
        for bm in _BLOCK_RE.finditer(lm.group(1)):
            if bm.group(1) is not None:                    # R(x)
                specs.append((2, 1, True))
                pos.append((int(bm.group(1)), 2))
            elif bm.group(2) is not None:                  # H(x,y,w)
                specs.append((int(bm.group(4)), 1, False))
                pos.append((int(bm.group(2)), int(bm.group(3))))
            else:                                          # V(x,y,h)
                specs.append((1, int(bm.group(7)), False))
                pos.append((int(bm.group(5)), int(bm.group(6))))
        if specs:
            levels.append((specs, tuple(pos), int(lm.group(2))))
    return levels


# ───────────────────────── per-app check ─────────────────────────
def check_app(app):
    """Return a list of (severity, message). Empty list = pass / N/A."""
    html_path = os.path.join(REPO, app, 'android', 'app', 'src', 'main',
                             'assets', 'game.html')
    if not os.path.isfile(html_path):
        return []
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    levels = parse_levels(html)
    if not levels:
        return []                       # not a sliding-block game — skip
    out = []
    for idx, (specs, pos, optimal) in enumerate(levels):
        ln = idx + 1
        for (w, h, is_red), (x, y) in zip(specs, pos):
            if (not is_red) and h == 1 and w > 1 and y == 2:
                out.append(('BLOCKER', f'level {ln}: non-red horizontal '
                            f'block on exit row y=2 — permanently walls '
                            f'the exit lane'))
        d = solve(specs, pos)
        if d < 0:
            out.append(('BLOCKER', f'level {ln}: unsolvable — no BFS '
                        f'solution within {MAX_DEPTH} moves'))
        elif d != optimal:
            out.append(('BLOCKER', f'level {ln}: stored optimal {optimal} '
                        f'!= solver minimum {d}'))
    return out


def list_apps():
    out = []
    for n in sorted(os.listdir(REPO)):
        if n in SKIP or n.startswith('.'):
            continue
        d = os.path.join(REPO, n)
        if not os.path.isdir(d):
            continue
        if os.path.isfile(os.path.join(d, 'android', 'app', 'src', 'main',
                                       'assets', 'game.html')):
            out.append(n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apps', nargs='*')
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    if args.all:
        apps = list_apps()
    elif args.apps:
        apps = args.apps
    else:
        ap.print_help()
        sys.exit(2)

    blockers = []
    checked = 0
    skipped = 0
    for app in apps:
        fs = check_app(app)
        if fs == [] and not _is_unblock_style(app):
            skipped += 1
            continue
        checked += 1
        for sev, msg in fs:
            if sev == 'BLOCKER':
                blockers.append(f'{app}: {msg}')

    print(f'puzzle solvability: {checked} sliding-block app(s) checked, '
          f'{skipped} skipped (not sliding-block), {len(blockers)} blockers')
    if blockers:
        print('\nBLOCKERS:')
        for m in blockers[:40]:
            print(f'  ✗ {m}')
        if len(blockers) > 40:
            print(f'  … and {len(blockers) - 40} more')
    sys.exit(1 if blockers else 0)


def _is_unblock_style(app):
    html_path = os.path.join(REPO, app, 'android', 'app', 'src', 'main',
                             'assets', 'game.html')
    if not os.path.isfile(html_path):
        return False
    with open(html_path, encoding='utf-8') as f:
        return bool(parse_levels(f.read()))


if __name__ == '__main__':
    main()
