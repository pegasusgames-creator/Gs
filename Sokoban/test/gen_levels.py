#!/usr/bin/env python3
"""gen_levels.py — Sokoban level generator (regenerates the LEVELS array in
android/app/src/main/assets/game.html to the 500-level release floor).

Solvable BY CONSTRUCTION via REVERSE generation: start from a SOLVED state
(every box on a target) and apply random player walks + box *pulls*. A pull
is the exact inverse of a push, so the reversed pull-sequence is a valid push
solution — every generated level is guaranteed solvable. A bounded forward
A* solver double-checks the smaller levels and yields the push-count used to
band difficulty. The existing hand-authored levels are kept as the gentle
prefix; generated levels are appended with a rising box-count / size ramp.

    python3 Sokoban/test/gen_levels.py            # rewrites the LEVELS array

Deterministic (fixed seed). check_sokoban_solvable.py is the permanent gate.
"""
import re
import sys
import heapq
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
GAME = REPO / "Sokoban/android/app/src/main/assets/game.html"
DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]


# ───────────────────────── deterministic RNG ─────────────────────────
class RNG:
    def __init__(self, seed): self.s = seed & 0xFFFFFFFF
    def next(self):
        self.s = (self.s * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.s / 0x100000000
    def randint(self, a, b): return a + int(self.next() * (b - a + 1))
    def choice(self, xs): return xs[self.randint(0, len(xs) - 1)]


# ───────────────────────── grid helpers ─────────────────────────
def make_room(rng, w, h, n_interior):
    """Border walls, floor interior, a few non-trapping interior walls."""
    walls = set()
    for x in range(w):
        walls.add((x, 0)); walls.add((x, h - 1))
    for y in range(h):
        walls.add((0, y)); walls.add((w - 1, y))
    floor = [(x, y) for y in range(1, h - 1) for x in range(1, w - 1)]
    placed = 0
    tries = 0
    while placed < n_interior and tries < 40:
        tries += 1
        c = rng.choice(floor)
        # keep interior walls off the outer ring of floor (avoid sealing)
        if 2 <= c[0] <= w - 3 and 2 <= c[1] <= h - 3 and c not in walls:
            walls.add(c); placed += 1
    return walls, [c for c in floor if c not in walls]


def neighbors(c): return [(c[0] + d[0], c[1] + d[1]) for d in DIRS]


def gen_level(rng, w, h, n_boxes, n_interior, pulls):
    walls, floor = make_room(rng, w, h, n_interior)
    floor_set = set(floor)
    if len(floor) < n_boxes + 4:
        return None
    # solved state: boxes on targets
    targets = []
    pool = floor[:]
    for _ in range(n_boxes):
        if not pool:
            return None
        t = rng.choice(pool)
        pool = [c for c in pool if c != t]
        targets.append(t)
    boxes = set(targets)
    # player on a free floor cell
    free = [c for c in floor if c not in boxes]
    if not free:
        return None
    player = rng.choice(free)

    def is_free(c):
        return c in floor_set and c not in boxes
    # reverse scramble: walk + pull
    for _ in range(pulls):
        # candidate pulls: box adjacent to player, with the opposite cell free
        opts = []
        for d in DIRS:
            bx = (player[0] + d[0], player[1] + d[1])     # box in front
            back = (player[0] - d[0], player[1] - d[1])   # player steps back
            if bx in boxes and is_free(back):
                opts.append((d, bx, back))
        # bias toward pulling; otherwise random walk
        if opts and rng.next() < 0.7:
            d, bx, back = rng.choice(opts)
            boxes.discard(bx); boxes.add(player)   # box slides into player cell
            player = back
        else:
            walk = [n for n in neighbors(player) if is_free(n)]
            if walk:
                player = rng.choice(walk)
    if boxes == set(targets):
        return None                                  # nothing moved → trivial
    return {"walls": walls, "w": w, "h": h, "targets": set(targets),
            "boxes": boxes, "player": player}


def to_ascii(L):
    rows = []
    for y in range(L["h"]):
        row = []
        for x in range(L["w"]):
            c = (x, y)
            if c in L["walls"]:
                row.append("#")
            elif c in L["boxes"] and c in L["targets"]:
                row.append("*")
            elif c in L["boxes"]:
                row.append("$")
            elif c == L["player"] and c in L["targets"]:
                row.append("+")
            elif c == L["player"]:
                row.append("@")
            elif c in L["targets"]:
                row.append(".")
            else:
                row.append(" ")
        rows.append("".join(row).rstrip())
    return "\n".join(rows)


# ───────────────────────── forward A* solver (bounded) ─────────────────────────
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


def solve(walls, targets, boxes, player, budget=200000):
    """A* min pushes; returns push-count, -1 unsolvable, None if budget blown."""
    targets = frozenset(targets)
    def heur(bs):
        return sum(min(abs(b[0]-t[0])+abs(b[1]-t[1]) for t in targets) for b in bs)
    if player is None:
        return -1
    start = (player, frozenset(boxes))
    h0 = heur(start[1])
    pq = [(h0, 0, start)]
    best = {start: 0}
    seen = 0
    while pq:
        f, g, (pl, bs) = heapq.heappop(pq)
        if bs == targets:
            return g
        if best.get((pl, bs), 1e9) < g:
            continue
        seen += 1
        if seen > budget:
            return None
        # player reachability (no push) — BFS over free cells
        free_seen = {pl}; stack = [pl]
        reach = {pl}
        while stack:
            c = stack.pop()
            for n in neighbors(c):
                if n in walls or n in bs or n in free_seen:
                    continue
                free_seen.add(n); reach.add(n); stack.append(n)
        for b in bs:
            for d in DIRS:
                src = (b[0] - d[0], b[1] - d[1])     # player must stand here
                dst = (b[0] + d[0], b[1] + d[1])     # box pushed here
                if src not in reach:
                    continue
                if dst in walls or dst in bs:
                    continue
                nb = set(bs); nb.discard(b); nb.add(dst); nb = frozenset(nb)
                ng = g + 1
                st = (b, nb)
                if ng < best.get(st, 1e9):
                    best[st] = ng
                    heapq.heappush(pq, (ng + heur(nb), ng, st))
    return -1


# ───────────────────────── build the 500 campaign ─────────────────────────
def existing_levels(html):
    m = re.search(r"const LEVELS=\[(.*?)\];", html, re.S)
    if not m:
        return []
    return re.findall(r"`([^`]*)`", m.group(1))


def main():
    html = GAME.read_text()
    # The existing 50 hand-authored levels have NO player char (@) — the
    # parser defaults the player to (0,0), a wall, so they are unplayable.
    # Regenerate the whole set with valid, player-placed, solvable levels.
    keep = []
    print(f"existing levels discarded (no player char): "
          f"{len(existing_levels(html))}")
    # difficulty ramp (count, w, h, boxes, interior walls, scramble pulls)
    SCHEDULE = [
        (100, 6, 6, 1, 0, 18),
        (100, 7, 7, 2, 1, 26),
        (100, 8, 7, 2, 2, 34),
        (100, 8, 8, 3, 2, 42),
        (90,  9, 8, 3, 3, 52),
        (10,  9, 9, 4, 3, 64),
    ]
    rng = RNG(20260618)
    need = 500 - len(keep)
    out = []
    si = 0
    counts = [c[0] for c in SCHEDULE]
    made_per = [0] * len(SCHEDULE)
    while len(out) < need:
        # pick the current schedule band
        band = 0
        acc = 0
        for i, c in enumerate(counts):
            if len(out) < acc + c:
                band = i; break
            acc += c
        else:
            band = len(SCHEDULE) - 1
        _, w, h, nb, iw, pl = SCHEDULE[band]
        L = gen_level(rng, w, h, nb, iw, pl)
        if not L:
            continue
        ascii_map = to_ascii(L)
        walls, targets, boxes, player = parse_ascii(ascii_map)
        if len(boxes) != len(targets) or player is None:
            continue
        # verify (bounded). None = too big to decide -> trust construction.
        d = solve(walls, targets, boxes, player)
        if d == -1:
            continue                       # solver proved unsolvable -> skip
        if d is not None and d < 2:
            continue                       # too trivial
        out.append(ascii_map)
        if len(out) % 50 == 0:
            print(f"  generated {len(out)}/{need}")
    campaign = keep + out
    print(f"TOTAL {len(campaign)} levels")
    body = ",\n".join("`" + m + "`" for m in campaign)
    block = "const LEVELS=[\n" + body + "\n];"
    new, n = re.subn(r"const LEVELS=\[.*?\];", block, html, count=1, flags=re.S)
    assert n == 1
    GAME.write_text(new)
    print("wrote LEVELS array")


if __name__ == "__main__":
    main()
