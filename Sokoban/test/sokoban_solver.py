#!/usr/bin/env python3
"""sokoban_solver.py — move-optimal Sokoban solver (pure Python 3 stdlib).

Shared by Sokoban/test/solve_levels.py (offline: computes the stored
SOLUTIONS used for stars + hints) and scripts/check_sokoban_solutions.py
(gate: replays them). Not shipped in the APK.

Model
  * Level = ASCII map: '#' wall, ' ' floor, '.' goal, '$' box, '*' box on
    goal, '@' player, '+' player on goal.
  * A solution is a LURD string: lower-case = walk, upper-case = push.
  * solve_moves() runs A* in PUSH space with MOVE cost: a node is the exact
    (player cell, box set) right after a push; an edge = walk to the cell
    behind a box (BFS distance) + 1 push. The heuristic is the sum over boxes
    of the wall-only push distance to the nearest goal — admissible, and
    consistent (one push changes it by at most 1 while costing >= 1) — so the
    first goal popped is MOVE-OPTIMAL. Dead squares (no goal reachable by
    pushing) and 2x2 freeze blocks are pruned; both are sound.
"""
import heapq
from collections import deque

DIRS = {"u": (0, -1), "d": (0, 1), "l": (-1, 0), "r": (1, 0)}
DLIST = list(DIRS.items())


def parse(ascii_map):
    walls, goals, boxes, player = set(), set(), set(), None
    rows = ascii_map.split("\n")
    w = max(len(r) for r in rows)
    for y, line in enumerate(rows):
        for x, ch in enumerate(line):
            c = (x, y)
            if ch == "#":
                walls.add(c)
            elif ch == "$":
                boxes.add(c)
            elif ch == "*":
                boxes.add(c); goals.add(c)
            elif ch == ".":
                goals.add(c)
            elif ch == "@":
                player = c
            elif ch == "+":
                player = c; goals.add(c)
    return {"w": w, "h": len(rows), "walls": walls, "goals": goals,
            "boxes": boxes, "player": player}


def interior(L):
    """Cells reachable by the player ignoring boxes (the playable floor)."""
    seen = {L["player"]}
    q = deque([L["player"]])
    while q:
        c = q.popleft()
        for dx, dy in DIRS.values():
            n = (c[0] + dx, c[1] + dy)
            if n in seen or n in L["walls"]:
                continue
            if not (0 <= n[0] < L["w"] and 0 <= n[1] < L["h"]):
                continue
            seen.add(n); q.append(n)
    return seen


def push_dist(L, floor):
    """Wall-only min pushes from each floor cell to the nearest goal
    (reverse BFS by pulls). Cells absent from the map are dead squares."""
    dist = {}
    q = deque()
    for g in L["goals"]:
        if g in floor:
            dist[g] = 0; q.append(g)
    while q:
        c = q.popleft()
        for dx, dy in DIRS.values():
            # box pulled from c to n=c+d needs the player at c+2d
            n = (c[0] + dx, c[1] + dy)
            p = (c[0] + 2 * dx, c[1] + 2 * dy)
            if n in floor and p in floor and n not in dist:
                dist[n] = dist[c] + 1; q.append(n)
    return dist


def frozen_2x2(boxes, moved, walls, goals):
    """True if `moved` sits in a 2x2 block made only of walls/boxes that
    holds a box off-goal (all boxes in such a block are frozen forever)."""
    x, y = moved
    for ox in (-1, 0):
        for oy in (-1, 0):
            cells = [(x + ox, y + oy), (x + ox + 1, y + oy),
                     (x + ox, y + oy + 1), (x + ox + 1, y + oy + 1)]
            if all(c in walls or c in boxes for c in cells):
                if any(c in boxes and c not in goals for c in cells):
                    return True
    return False


def _reach(start, walls, boxes, floor):
    dist = {start: 0}
    q = deque([start])
    while q:
        c = q.popleft()
        for dx, dy in DIRS.values():
            n = (c[0] + dx, c[1] + dy)
            if n in dist or n in walls or n in boxes or n not in floor:
                continue
            dist[n] = dist[c] + 1; q.append(n)
    return dist


def _walk_path(a, b, walls, boxes, floor):
    """Shortest walk a->b avoiding boxes, as a lower-case LURD string."""
    if a == b:
        return ""
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for k, (dx, dy) in DLIST:
            n = (c[0] + dx, c[1] + dy)
            if n in prev or n in walls or n in boxes or n not in floor:
                continue
            prev[n] = (c, k); q.append(n)
    if b not in prev:
        return None
    out = []
    c = b
    while prev[c] is not None:
        c, k = prev[c]
        out.append(k)
    return "".join(reversed(out))


def solve_moves(L, budget=3_000_000):
    """Move-optimal LURD solution, '' if already solved, None if the budget
    is exhausted, False if proven unsolvable."""
    floor = interior(L)
    walls = L["walls"]
    goals = frozenset(L["goals"])
    pd = push_dist(L, floor)
    start_boxes = frozenset(L["boxes"])
    if start_boxes == goals:
        return ""
    if any(b not in pd for b in start_boxes):
        return False

    def h(bs):
        return sum(pd[b] for b in bs)

    start = (L["player"], start_boxes)
    g0 = {start: 0}
    parent = {start: None}
    pq = [(h(start_boxes), 0, 0, start)]
    tick = 0
    expanded = 0
    while pq:
        f, g, _, node = heapq.heappop(pq)
        if g0.get(node, 1 << 30) < g:
            continue
        pl, bs = node
        if bs == goals:
            # rebuild
            chain = []
            n = node
            while parent[n] is not None:
                prevn, src, k = parent[n]
                chain.append((prevn, src, k))
                n = prevn
            chain.reverse()
            out = []
            for (prevn, src, k) in chain:
                ppl, pbs = prevn
                out.append(_walk_path(ppl, src, walls, pbs, floor))
                out.append(k.upper())
            return "".join(out)
        expanded += 1
        if expanded > budget:
            return None
        reach = _reach(pl, walls, bs, floor)
        for b in bs:
            for k, (dx, dy) in DLIST:
                src = (b[0] - dx, b[1] - dy)
                dst = (b[0] + dx, b[1] + dy)
                if src not in reach or dst in bs or dst not in pd:
                    continue
                nbs = set(bs); nbs.discard(b); nbs.add(dst)
                if frozen_2x2(nbs, dst, walls, goals):
                    continue
                nbs = frozenset(nbs)
                ng = g + reach[src] + 1
                nn = (b, nbs)
                if ng < g0.get(nn, 1 << 30):
                    g0[nn] = ng
                    parent[nn] = (node, src, k)
                    tick += 1
                    heapq.heappush(pq, (ng + h(nbs), ng, tick, nn))
    return False


def replay(L, lurd):
    """Replay a LURD string; returns (ok, message, moves, pushes). ok=True
    only if every step is legal, push/walk case matches what happens, and
    every box ends on a goal."""
    walls = L["walls"]
    boxes = set(L["boxes"])
    pl = L["player"]
    pushes = 0
    for i, ch in enumerate(lurd):
        k = ch.lower()
        if k not in DIRS:
            return False, f"bad char {ch!r} at {i}", i, pushes
        dx, dy = DIRS[k]
        n = (pl[0] + dx, pl[1] + dy)
        if n in walls:
            return False, f"walks into a wall at step {i}", i, pushes
        if n in boxes:
            dst = (n[0] + dx, n[1] + dy)
            if dst in walls or dst in boxes:
                return False, f"blocked push at step {i}", i, pushes
            if ch != k.upper():
                return False, f"push not marked upper-case at step {i}", i, pushes
            boxes.discard(n); boxes.add(dst); pushes += 1
        elif ch != k:
            return False, f"walk marked as push at step {i}", i, pushes
        pl = n
    if boxes != set(L["goals"]):
        return False, "boxes not all on goals at the end", len(lurd), pushes
    return True, "ok", len(lurd), pushes


def rle(lurd):
    """Run-length encode: 'rrrUUl' -> '3r2Ul'."""
    out = []
    i = 0
    while i < len(lurd):
        j = i
        while j < len(lurd) and lurd[j] == lurd[i]:
            j += 1
        n = j - i
        out.append((str(n) if n > 1 else "") + lurd[i])
        i = j
    return "".join(out)


def unrle(s):
    out = []
    num = ""
    for ch in s:
        if ch.isdigit():
            num += ch
        else:
            out.append(ch * (int(num) if num else 1))
            num = ""
    return "".join(out)
