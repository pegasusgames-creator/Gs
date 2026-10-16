#!/usr/bin/env python3
"""check_sokoban_solvable.py — puzzle-solvability gate for Sokoban games.

Wired into pre_publish_check.py. Parses the `const LEVELS=[ `...` , ... ]`
ASCII maps out of a Sokoban game.html and, for each level, BLOCKS if:
  - there is no player (@ or +) — the parser would default to (0,0), a wall,
    making the level unplayable (the entire 2026 hand-authored set had this);
  - the box count != target count;
  - a bounded forward A* solver proves it unsolvable.
Levels too large to decide within the node budget WARN (trusted by the
pull-construction witness, same policy as check_pipeconnect_solvable).

Witness fast path (2026-10-16): when the game ships `const SOLUTIONS=[...]`
(run-length LURD per level — lower case walks, upper case pushes), each
stored line is REPLAYED; a legal replay that docks every crate proves the
level solvable in microseconds, so the A* search only runs for levels with
no stored line. A stored line that does not solve its level BLOCKS (the game
uses it for hints and par).

Apps with no Sokoban-style LEVELS array are silently skipped.

    python3 scripts/check_sokoban_solvable.py <App> | --all
"""
import argparse
import heapq
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
BUDGET = 200000


def parse_ascii(s):
    walls = set(); targets = set(); boxes = set(); player = None
    for y, line in enumerate(s.split("\n")):
        for x, ch in enumerate(line):
            c = (x, y)
            if ch == "#": walls.add(c)
            elif ch == "$": boxes.add(c)
            elif ch == "*": boxes.add(c); targets.add(c)
            elif ch == ".": targets.add(c)
            elif ch == "@": player = c
            elif ch == "+": player = c; targets.add(c)
    return walls, targets, boxes, player


def _neighbors(c):
    return [(c[0] + d[0], c[1] + d[1]) for d in DIRS]


def solve(walls, targets, boxes, player, budget=BUDGET):
    """A* min pushes; -1 unsolvable, None if budget blown, 0 already solved."""
    if player is None:
        return -1
    targets = frozenset(targets)
    def heur(bs):
        return sum(min(abs(b[0]-t[0]) + abs(b[1]-t[1]) for t in targets)
                   for b in bs)
    start = (player, frozenset(boxes))
    pq = [(heur(start[1]), 0, start)]
    best = {start: 0}
    seen = 0
    while pq:
        f, g, (pl, bs) = heapq.heappop(pq)
        if bs == targets:
            return g
        if best.get((pl, bs), 1 << 30) < g:
            continue
        seen += 1
        if seen > budget:
            return None
        reach = {pl}; stack = [pl]
        while stack:
            c = stack.pop()
            for n in _neighbors(c):
                if n in walls or n in bs or n in reach:
                    continue
                reach.add(n); stack.append(n)
        for b in bs:
            for d in DIRS:
                src = (b[0] - d[0], b[1] - d[1])
                dst = (b[0] + d[0], b[1] + d[1])
                if src not in reach or dst in walls or dst in bs:
                    continue
                nb = set(bs); nb.discard(b); nb.add(dst); nb = frozenset(nb)
                ng = g + 1
                st = (b, nb)
                if ng < best.get(st, 1 << 30):
                    best[st] = ng
                    heapq.heappush(pq, (ng + heur(nb), ng, st))
    return -1


LURD = {"u": (0, -1), "d": (0, 1), "l": (-1, 0), "r": (1, 0)}


def parse_solutions(html):
    m = re.search(r"const SOLUTIONS\s*=\s*\[(.*?)\];", html, re.S)
    return re.findall(r"'([0-9udlrUDLR]*)'", m.group(1)) if m else None


def replay(walls, targets, boxes, player, sol):
    """True iff the RLE LURD line is legal and ends with every box docked."""
    seq = re.sub(r"(\d+)([udlrUDLR])", lambda x: x.group(2) * int(x.group(1)), sol)
    boxes = set(boxes); p = player
    for ch in seq:
        if ch.lower() not in LURD:
            return False  # malformed line (e.g. a dangling run count)
        dx, dy = LURD[ch.lower()]
        n = (p[0] + dx, p[1] + dy)
        if n in walls:
            return False
        if ch.isupper():
            b = (n[0] + dx, n[1] + dy)
            if n not in boxes or b in walls or b in boxes:
                return False
            boxes.discard(n); boxes.add(b)
        elif n in boxes:
            return False
        p = n
    return boxes == targets


def parse_levels(html):
    m = re.search(r"const LEVELS\s*=\s*\[(.*?)\];", html, re.S)
    if not m:
        return None
    maps = re.findall(r"`([^`]*)`", m.group(1))
    # only treat as Sokoban if the maps look like Sokoban ASCII
    if not maps or not all("#" in mp for mp in maps[:3]):
        return None
    if not any(("$" in mp or "*" in mp) for mp in maps[:3]):
        return None
    return maps


def check_app(app):
    path = os.path.join(REPO, app, "android/app/src/main/assets/game.html")
    if not os.path.isfile(path):
        return [], []
    html = open(path, encoding="utf-8").read()
    maps = parse_levels(html)
    if not maps:
        return [], []
    sols = parse_solutions(html) or []
    blockers, warnings = [], []
    for i, mp in enumerate(maps):
        ln = i + 1
        walls, targets, boxes, player = parse_ascii(mp)
        if player is None:
            blockers.append(f"{app}: level {ln} has no player (@/+) — "
                            f"defaults to (0,0)/wall, unplayable")
            continue
        if len(boxes) != len(targets):
            blockers.append(f"{app}: level {ln} box count {len(boxes)} != "
                            f"target count {len(targets)}")
            continue
        if not boxes:
            blockers.append(f"{app}: level {ln} has no boxes")
            continue
        if i < len(sols) and sols[i]:
            if replay(walls, targets, boxes, player, sols[i]):
                continue
            blockers.append(f"{app}: level {ln} stored solution does not solve it "
                            f"(hint/par would be wrong)")
            continue
        d = solve(walls, targets, boxes, player)
        if d == -1:
            blockers.append(f"{app}: level {ln} unsolvable (A* exhausted)")
        elif d is None:
            warnings.append(f"{app}: level {ln} too large to decide within "
                            f"the {BUDGET} budget — trusting construction")
    return blockers, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    apps = a.apps
    if a.all or not apps:
        apps = sorted(p for p in os.listdir(REPO)
                      if os.path.isdir(os.path.join(REPO, p, "android"))
                      and not p.startswith(("_", ".")))
    fail = 0
    checked = 0
    for app in apps:
        b, w = check_app(app)
        if b or w:
            checked += 1
        for line in b:
            print(f"✗ {line}"); fail = 1
        for line in w:
            print(f"!  {line}")
    if not fail:
        print(f"[sokoban solvable] ok")
    return fail


if __name__ == "__main__":
    sys.exit(main())
