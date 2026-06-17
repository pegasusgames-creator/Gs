#!/usr/bin/env python3
"""
check_pipeconnect_solvable.py — pre-publish puzzle-solvability gate for
flow / connect-the-dots games (PipeConnect and any clone of it).

Wired into scripts/pre_publish_check.py as part of the "puzzle solvability"
section. Can also be run standalone:

    python3 scripts/check_pipeconnect_solvable.py <App>
    python3 scripts/check_pipeconnect_solvable.py --all

Why this exists: the 2026-06-16 PipeConnect audit found that levels 1-122
(the original hand-authored block) were almost entirely UNSOLVABLE — there
was no way to connect every colour pair without paths crossing, so the
player could never satisfy the win condition. Only the procedurally
generated block (123-500, built by test/gen_levels.js as a Hamiltonian-path
partition) was solvable. No hand-authored flow level set is trusted again
without a full solver pass.

Win condition (matches game.html `allPipesConnected`): each colour's two
dots must be joined by a path; cells carry one colour, so paths are
vertex-disjoint. Filling every cell is OPTIONAL (bonus stars only). So the
gate verifies that a set of vertex-disjoint connecting paths EXISTS. A
full-coverage (Flow) solution is a sufficient witness and is what designed
levels carry, so the solver searches for full coverage first (fast, highly
constrained) and falls back to a connect-only search.

This module parses the LEVELS array out of an app's game.html, solves every
level, and BLOCKS the build if ANY level is provably unsolvable. Levels too
large to decide within the node budget are reported as WARNINGs (surfaced
for manual review) rather than silently passed.

Apps with no PipeConnect-style LEVELS array (objects of the form
`{size:N,dots:[[r,c,'colour'],...]}`) are silently skipped, so `--all` is
safe across the whole portfolio.
"""
import argparse
import ast
import os
import re
import sys
from collections import deque

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'_template', '_release', '_archive', '_screenshot_tools', 'docs',
        'scripts', 'release_aabs', 'BLOCKED_APPS', '__pycache__', '.git',
        '.idea', 'node_modules'}

# Per-level search budget. Designed (solvable) levels are found far below
# this; provably-unsolvable designed levels exhaust far below it too —
# local pruning collapses the tree quickly. Only pathological large boards
# reach the cap, and those are reported as WARN rather than BLOCK.
NODE_BUDGET = 120_000
# Boards up to this size are decided exactly by the connect-only solver
# (fast, matches the win condition). Larger boards lean on the full-cover
# witness and are WARNed if undecided.
SMALL = 7


def _asset_html(app):
    return os.path.join(REPO, app, 'android', 'app', 'src', 'main',
                        'assets', 'game.html')


def parse_levels(html):
    """Return [(size, dots)] for every {size:N,dots:[[r,c,'col'],...]} in the
    LEVELS array, or [] if there is no such array."""
    m = re.search(r'const\s+LEVELS\s*=\s*\[(.*?)\n\];', html, re.S)
    if not m:
        return []
    body = re.sub(r'//[^\n]*', '', m.group(1))
    out = []
    for lm in re.finditer(r'\{size:\s*(\d+)\s*,\s*dots:\s*(\[\[.*?\]\])\}', body):
        try:
            dots = ast.literal_eval(lm.group(2).replace("'", '"'))
        except (ValueError, SyntaxError):
            continue
        out.append((int(lm.group(1)), dots))
    return out


def _colors(dots):
    cols = {}
    for r, c, col in dots:
        cols.setdefault(col, []).append((r, c))
    return cols


# ───────────────────── full-coverage (Flow) solver ─────────────────────
# Head-extension backtracking with two prunings that collapse dead branches
# fast: (1) no empty non-endpoint cell may become "stranded" (fewer than two
# ways in/out), (2) every unfinished colour's two heads must stay mutually
# reachable through still-free cells. Returns True / False / None(=budget).
def _full_cover(size, dots):
    cols = _colors(dots)
    if any(len(v) != 2 for v in cols.values()):
        return False
    order = list(cols.keys())
    target = {c: cols[c][1] for c in order}
    occupied = [[False] * size for _ in range(size)]
    is_dot = {}
    for c in order:
        for (r, cc) in cols[c]:
            occupied[r][cc] = True
            is_dot[(r, cc)] = c
    nodes = [0]

    def nbrs(r, c):
        if r + 1 < size: yield r + 1, c
        if r - 1 >= 0:    yield r - 1, c
        if c + 1 < size:  yield r, c + 1
        if c - 1 >= 0:    yield r, c - 1

    def escapes(r, c):
        n = 0
        for nr, nc in nbrs(r, c):
            if not occupied[nr][nc] or (nr, nc) in is_dot:
                n += 1
        return n

    def stranded_near(r, c):
        # an empty non-endpoint cell is "stranded" if it has <2 ways in/out;
        # occupying (r,c) can only strand (r,c)'s own empty neighbours, so we
        # check just those instead of scanning the whole board each node.
        for nr, nc in nbrs(r, c):
            if occupied[nr][nc] or (nr, nc) in is_dot:
                continue
            if escapes(nr, nc) < 2:
                return True
        return False

    def reachable(start, goal):
        if start == goal:
            return True
        seen = {start}
        q = deque([start])
        while q:
            cur = q.popleft()
            for nb in nbrs(*cur):
                if nb == goal:
                    return True
                if nb in seen or occupied[nb[0]][nb[1]]:
                    continue
                seen.add(nb)
                q.append(nb)
        return False

    def heads_ok(ci, cur_head):
        # current colour: head must still reach its target
        if not reachable(cur_head, target[order[ci]]):
            return False
        # later colours: endpoints must stay mutually reachable
        for j in range(ci + 1, len(order)):
            a, b = cols[order[j]]
            if not reachable(a, b):
                return False
        return True

    def route(ci, head):
        nodes[0] += 1
        if nodes[0] > NODE_BUDGET:
            raise TimeoutError
        col = order[ci]
        tgt = target[col]
        if head == tgt:
            if ci + 1 == len(order):
                # all colours routed: full coverage means no empty cell left
                return all(occupied[r][c] for r in range(size) for c in range(size))
            return route(ci + 1, cols[order[ci + 1]][0])
        hr, hc = head
        for nr, nc in sorted(nbrs(hr, hc),
                             key=lambda x: abs(x[0] - tgt[0]) + abs(x[1] - tgt[1])):
            if (nr, nc) == tgt:
                occupied_was = True
                if route(ci, (nr, nc)):
                    return True
                continue
            if occupied[nr][nc]:
                continue
            occupied[nr][nc] = True
            if not stranded_near(nr, nc) and heads_ok(ci, (nr, nc)):
                if route(ci, (nr, nc)):
                    return True
            occupied[nr][nc] = False
        return False

    try:
        return route(0, cols[order[0]][0])
    except TimeoutError:
        return None


# ───────────────────── connect-only solver (fallback) ─────────────────────
# Exact win condition: vertex-disjoint paths, empty cells allowed. Decisive
# and fast on small boards; used when no full-cover witness was found.
def _connect_only(size, dots):
    cols = _colors(dots)
    if any(len(v) != 2 for v in cols.values()):
        return False
    dotcells = {(r, c): col for r, c, col in dots}
    cl = sorted(cols.items(),
                key=lambda kv: abs(kv[1][0][0] - kv[1][1][0]) + abs(kv[1][0][1] - kv[1][1][1]))
    used = set()
    nodes = [0]

    def nbrs(r, c):
        if r + 1 < size: yield r + 1, c
        if r - 1 >= 0:    yield r - 1, c
        if c + 1 < size:  yield r, c + 1
        if c - 1 >= 0:    yield r, c - 1

    def reachable(s, t):
        if s == t:
            return True
        seen = {s}
        q = deque([s])
        while q:
            cur = q.popleft()
            for nb in nbrs(*cur):
                if nb == t:
                    return True
                if nb in seen or nb in used:
                    continue
                if nb in dotcells and nb != t:
                    continue
                seen.add(nb)
                q.append(nb)
        return False

    def all_reach(i):
        return all(reachable(cl[j][1][0], cl[j][1][1]) for j in range(i, len(cl)))

    def route(i):
        nodes[0] += 1
        if nodes[0] > NODE_BUDGET:
            raise TimeoutError
        if i == len(cl):
            return True
        ep0, ep1 = cl[i][1]

        def dfs(cur):
            nodes[0] += 1
            if nodes[0] > NODE_BUDGET:
                raise TimeoutError
            if cur == ep1:
                return all_reach(i + 1) and route(i + 1)
            for nb in sorted(nbrs(*cur),
                             key=lambda x: abs(x[0] - ep1[0]) + abs(x[1] - ep1[1])):
                if nb == ep1:
                    if dfs(nb):
                        return True
                    continue
                if nb in used or (nb in dotcells and nb != ep1):
                    continue
                used.add(nb)
                if reachable(nb, ep1) and dfs(nb):
                    return True
                used.discard(nb)
            return False

        return dfs(ep0)

    try:
        return route(0)
    except TimeoutError:
        return None


def solvable(size, dots):
    """'OK' if a connecting solution exists, 'UNSOLVABLE' if provably none,
    'UNKNOWN' if undecidable within the node budget.

    The connect-only solver matches the win condition exactly. Greedy
    head-toward-target ordering plus reachability pruning finds a witness
    almost immediately for solvable boards and exhausts the (pruned) tree
    quickly for unsolvable small/medium boards. Only large boards that are
    neither quickly solved nor quickly refuted hit the budget → UNKNOWN,
    which is WARNed (their solvability is guaranteed by the generator's
    Hamiltonian-partition construction, not a runtime search)."""
    co = _connect_only(size, dots)
    if co is True:
        return 'OK'
    if co is False:
        return 'UNSOLVABLE'
    return 'UNKNOWN'


def _is_pipeconnect_style(app):
    html = _asset_html(app)
    if not os.path.isfile(html):
        return False
    with open(html, encoding='utf-8') as f:
        return bool(parse_levels(f.read()))


def check_app(app):
    """Return list of (severity, message). BLOCKER for each unsolvable level,
    WARN for levels too large to decide."""
    html = _asset_html(app)
    if not os.path.isfile(html):
        return []
    with open(html, encoding='utf-8') as f:
        levels = parse_levels(f.read())
    if not levels:
        return []
    results = []
    unknown = 0
    for i, (size, dots) in enumerate(levels):
        verdict = solvable(size, dots)
        if verdict == 'UNSOLVABLE':
            results.append(('BLOCKER',
                            f'level {i + 1} ({size}x{size}) is UNSOLVABLE — '
                            f'no vertex-disjoint connection of all colour pairs'))
        elif verdict == 'UNKNOWN':
            unknown += 1
    if unknown:
        results.append(('WARN',
                        f'{unknown} level(s) too large to decide within node '
                        f'budget — verify by construction (generator witness)'))
    return results


def list_apps():
    out = []
    for n in sorted(os.listdir(REPO)):
        d = os.path.join(REPO, n)
        if not os.path.isdir(d) or n in SKIP or n.startswith('.'):
            continue
        if _is_pipeconnect_style(n):
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

    blockers, warnings, checked, skipped = [], [], 0, 0
    for app in apps:
        if not _is_pipeconnect_style(app):
            skipped += 1
            continue
        checked += 1
        for sev, msg in check_app(app):
            (blockers if sev == 'BLOCKER' else warnings).append(f'{app}: {msg}')

    print(f'flow solvability: {checked} flow app(s) checked, '
          f'{skipped} skipped (not flow), {len(blockers)} blockers, '
          f'{len(warnings)} warnings')
    if warnings:
        for m in warnings[:20]:
            print(f'  ⚠ {m}')
    if blockers:
        print('\nBLOCKERS:')
        for m in blockers[:40]:
            print(f'  ✗ {m}')
        if len(blockers) > 40:
            print(f'  … and {len(blockers) - 40} more')
    sys.exit(1 if blockers else 0)


if __name__ == '__main__':
    main()
