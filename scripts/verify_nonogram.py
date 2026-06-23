#!/usr/bin/env python3
"""verify_nonogram.py — offline build gate: assert every Nonogram campaign
level has EXACTLY ONE solution.

buildLevels() in Nonogram/game.html assembles 500 boards:
  1-50    PATTERNS_5  (5x5, curated)      ← used directly, no runtime gate
  51-70   PATTERNS_10 (10x10, curated)    ← used directly, no runtime gate
  71-150  PREGEN_10   (10x10, pregenerated)
  151-300 PREGEN_15   (15x15, pregenerated)
  301-500 PREGEN_20   (20x20, pregenerated)

The curated PATTERNS_* arrays bypass the runtime _generateUnique() gate, so a
hand-drawn but ambiguous board (multiple solutions) ships ambiguous — the
player can "complete" it differently from the stored picture and the win
check (run-length vs clues) still accepts it, but the daily/clue experience is
broken. This gate reconstructs all 500 boards exactly as buildLevels() does,
derives the clues, and counts solutions (capped at 2) with a line-solver +
bounded branch search. Any board with != 1 solution fails the build.

Memorialized 2026-06-23: PATTERNS_5 levels 30/45/46/50 were ambiguous (2
solutions each); replaced with single-cell-edited unique boards.

Usage: python3 scripts/verify_nonogram.py
Exit 0 = all unique; 1 = at least one non-unique (or parse failure).
"""
from __future__ import annotations
import re
import sys
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAME = REPO / "Nonogram/android/app/src/main/assets/game.html"


# ───────────────────────── clue derivation ─────────────────────────
def runs(line):
    out, c = [], 0
    for v in line:
        if v:
            c += 1
        elif c:
            out.append(c); c = 0
    if c:
        out.append(c)
    return out or [0]


def clues(grid, n):
    rows = [runs(grid[r * n:(r + 1) * n]) for r in range(n)]
    cols = [runs([grid[r * n + c] for r in range(n)]) for c in range(n)]
    return rows, cols


# ───────────────────── line feasibility / forcing ─────────────────────
def feasible(clue, known, n):
    """Can the partial line `known` (-1 unknown / 0 empty / 1 fill) be
    completed to satisfy `clue`?"""
    blocks = [b for b in clue if b > 0]
    K = len(blocks)

    @lru_cache(maxsize=None)
    def can(i, j):
        if j == K:
            return all(known[t] != 1 for t in range(i, n))
        if i >= n:
            return False
        res = False
        if known[i] != 1:                       # leave cell i empty
            res = can(i + 1, j)
        if not res:                             # place block j at i
            b = blocks[j]
            if i + b <= n and all(known[i + t] != 0 for t in range(b)):
                after = i + b
                if after == n:
                    res = (j + 1 == K)
                elif known[after] != 1:
                    res = can(after + 1, j + 1)
        return res

    return can(0, 0)


def line_forced(clue, known, n):
    """Return forced cell values (list of -1/0/1) or None if infeasible."""
    if not feasible(clue, known, n):
        return None
    out = [-1] * n
    for c in range(n):
        can0 = known[c] != 1 and feasible(clue, _set(known, c, 0), n)
        can1 = known[c] != 0 and feasible(clue, _set(known, c, 1), n)
        if not can0 and not can1:
            return None
        if can0 and not can1:
            out[c] = 0
        elif can1 and not can0:
            out[c] = 1
    return out


def _set(known, c, v):
    k = list(known)
    k[c] = v
    return tuple(k)


# ───────────────────────── solution counter ─────────────────────────
def propagate(grid, rowclues, colclues, n):
    changed = True
    while changed:
        changed = False
        for r in range(n):
            res = line_forced(rowclues[r], tuple(grid[r * n:(r + 1) * n]), n)
            if res is None:
                return False
            for c in range(n):
                if res[c] != -1 and grid[r * n + c] == -1:
                    grid[r * n + c] = res[c]; changed = True
        for c in range(n):
            col = tuple(grid[r * n + c] for r in range(n))
            res = line_forced(colclues[c], col, n)
            if res is None:
                return False
            for r in range(n):
                if res[r] != -1 and grid[r * n + c] == -1:
                    grid[r * n + c] = res[r]; changed = True
    return True


def count_solutions(rowclues, colclues, n, cap=2):
    def solve(grid):
        g = grid[:]
        if not propagate(g, rowclues, colclues, n):
            return 0
        try:
            idx = g.index(-1)
        except ValueError:
            return 1
        total = 0
        for v in (1, 0):
            g2 = g[:]; g2[idx] = v
            total += solve(g2)
            if total >= cap:
                return total
        return total

    return solve([-1] * (n * n))


# ───────────────────────── board extraction ─────────────────────────
def _array_of_arrays(src, name, cells):
    m = re.search(name + r"\s*=\s*\[(.*?)\n\]\s*;", src, re.S)
    body = m.group(1)
    out = []
    for a in re.findall(r"\[([0-9,\s]+)\]", body):
        nums = [int(x) for x in re.findall(r"\d+", a)]
        if len(nums) == cells:
            out.append(nums)
    return out


def _array_of_strings(src, name):
    m = re.search(name + r"\s*=\s*\[(.*?)\n\]\s*;", src, re.S)
    return [[1 if ch == "1" else 0 for ch in s]
            for s in re.findall(r"""['"]([01]+)['"]""", m.group(1))]


def build_levels(src):
    P5 = _array_of_arrays(src, "PATTERNS_5", 25)
    P10 = _array_of_arrays(src, "PATTERNS_10", 100)
    PRE10 = _array_of_strings(src, "PREGEN_10")
    PRE15 = _array_of_strings(src, "PREGEN_15")
    PRE20 = _array_of_strings(src, "PREGEN_20")
    levels = []
    for i in range(50):
        levels.append((i + 1, 5, P5[i]))
    for i in range(100):
        if i < len(P10):
            levels.append((i + 51, 10, P10[i]))
        else:
            levels.append((i + 51, 10, PRE10[i - len(P10)]))
    for i in range(150):
        levels.append((i + 151, 15, PRE15[i]))
    for i in range(200):
        levels.append((i + 301, 20, PRE20[i]))
    return levels, (len(P5), len(P10), len(PRE10), len(PRE15), len(PRE20))


def main():
    src = GAME.read_text(encoding="utf-8")
    levels, counts = build_levels(src)
    print(f"  reconstructed {len(levels)} levels "
          f"(P5={counts[0]} P10={counts[1]} PRE10={counts[2]} "
          f"PRE15={counts[3]} PRE20={counts[4]})")
    if len(levels) != 500:
        print(f"  ✗ expected 500 levels, got {len(levels)}")
        return 1
    # An empty row/column (clue [0]) is a legal nonogram line and does not
    # affect uniqueness — the only criterion here is "exactly one solution".
    bad = []
    for lvl, n, grid in levels:
        rc, cc = clues(grid, n)
        ns = count_solutions(rc, cc, n, cap=2)
        if ns != 1:
            bad.append((lvl, n, f"{ns}+ solutions"))
    if bad:
        for lvl, n, why in bad:
            print(f"  ✗ level {lvl} ({n}x{n}): {why}")
        print(f"  {len(bad)} non-unique level(s)")
        return 1
    print("  all 500 levels have exactly one solution… ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
