#!/usr/bin/env python3
"""check_minesweeper_noguess.py — gate: every shipped Minesweeper board is
solvable WITHOUT GUESSING from its safe first click.

minesweeper_noguess: Minesweeper ships fixed, pre-verified boards (campaign
levels, and the daily / endless modes re-use those same boards under a
mirror/rotation that cannot change their logic). This gate reads the board
data out of Minesweeper/android/app/src/main/assets/game.html EXACTLY as the
game decodes it (`const LEVELS = ["RxC:start:bits", ...]`, base64url mine
bitmap, 6 bits per char, MSB first, row-major) and, for every board:

  * the encoding is well formed (size, bitmap length, zero padding bits);
  * the start cell is safe AND has no adjacent mine — the first tap always
    opens an area (a "0" flood), never a lone number;
  * a sound logical solver clears every safe cell from that opening with no
    guess at any step. Rules (each is a valid deduction, so a full clear
    proves the board is no-guess):
        1. single number  — need == 0 -> neighbours safe; need == unknowns -> mines
        2. number pairs   — for overlapping constraints A, B:
                            b - a == |B\\A| -> B\\A mines, A\\B safe (and mirror)
        3. mine counter   — remaining mines vs. a disjoint cover of
                            constraints: the uncovered rest is all-safe /
                            all-mine when the count leaves no choice
    The fixpoint of monotone sound rules is order independent, so the result
    is the same under any mirror / 180-degree rotation (daily + endless);
    the gate re-checks every transform for a sample of boards anyway;
  * no two campaign boards are identical (incl. under the 4 transforms);
  * the campaign has >= 500 boards, opens at 6x6 / 5 mines and ends on
    30x16 boards (the documented ramp).

The level generator (Minesweeper/test/gen_levels.py) imports this module's
solver, so the gate and the generator can never disagree.

Usage:  python3 scripts/check_minesweeper_noguess.py [--quiet]
Exit 1 on any bad board.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
GAME = BASE / "Minesweeper" / "android" / "app" / "src" / "main" / "assets" / "game.html"
B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
B64_INDEX = {ch: i for i, ch in enumerate(B64)}
MIN_LEVELS = 500

# ---------------------------------------------------------------- encoding


def encode_level(rows: int, cols: int, start: int, mines) -> str:
    """Inverse of decode_level (used by the generator)."""
    n = rows * cols
    bits = [0] * n
    for m in mines:
        bits[m] = 1
    while len(bits) % 6:
        bits.append(0)
    out = []
    for i in range(0, len(bits), 6):
        v = 0
        for b in bits[i:i + 6]:
            v = (v << 1) | b
        out.append(B64[v])
    return f"{rows}x{cols}:{start}:{''.join(out)}"


def decode_level(code: str):
    """Mirror of the game's decodeLevel(): returns (rows, cols, start, mines:set).
    Raises ValueError on any malformed field."""
    m = re.fullmatch(r"(\d+)x(\d+):(\d+):([A-Za-z0-9_-]+)", code)
    if not m:
        raise ValueError(f"malformed level string {code[:40]!r}")
    rows, cols, start, bits = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    n = rows * cols
    if not (5 <= rows <= 40 and 5 <= cols <= 30):
        raise ValueError(f"board size {rows}x{cols} out of range")
    if len(bits) != (n + 5) // 6:
        raise ValueError(f"bitmap has {len(bits)} chars, expected {(n + 5) // 6}")
    mines = set()
    for ci, ch in enumerate(bits):
        v = B64_INDEX[ch]
        for k in range(6):
            idx = ci * 6 + k
            if (v >> (5 - k)) & 1:
                if idx >= n:
                    raise ValueError("non-zero padding bit")
                mines.add(idx)
    if not (0 <= start < n):
        raise ValueError(f"start {start} outside the {rows}x{cols} board")
    return rows, cols, start, mines


def transform(rows: int, cols: int, start: int, mines, t: int):
    """Mirror of the game's transformBoard(): t 0=identity, 1=mirror columns,
    2=mirror rows, 3=rotate 180. Shape is unchanged."""
    def f(i):
        r, c = divmod(i, cols)
        if t & 1:
            c = cols - 1 - c
        if t & 2:
            r = rows - 1 - r
        return r * cols + c
    return rows, cols, f(start), {f(m) for m in mines}


# ------------------------------------------------------------------ solver

_NB_CACHE: dict = {}


def neighbours(rows: int, cols: int):
    key = (rows, cols)
    if key not in _NB_CACHE:
        nb = []
        for i in range(rows * cols):
            r, c = divmod(i, cols)
            lst = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr or dc:
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < rows and 0 <= cc < cols:
                            lst.append(rr * cols + cc)
            nb.append(tuple(lst))
        _NB_CACHE[key] = nb
    return _NB_CACHE[key]


class SolveResult:
    __slots__ = ("solved", "state", "opening", "rounds", "pair_rounds", "count_rounds", "revealed")

    def __init__(self):
        self.solved = False
        self.state = None
        self.opening = 0
        self.rounds = 0
        self.pair_rounds = 0
        self.count_rounds = 0
        self.revealed = 0


def solve(rows: int, cols: int, mines, start: int) -> SolveResult:
    """Logical solve from the start opening. state: 0 unknown, 1 open, 2 known mine."""
    nb = neighbours(rows, cols)
    n = rows * cols
    mine = bytearray(n)
    for m in mines:
        mine[m] = 1
    num = [sum(mine[j] for j in nb[i]) for i in range(n)]
    total_mines = len(mines)
    safe_total = n - total_mines
    state = bytearray(n)
    res = SolveResult()
    res.state = state
    if mine[start] or num[start] != 0:
        return res

    opened = [0]
    known = [0]

    def open_cell(i):
        stack = [i]
        while stack:
            k = stack.pop()
            if state[k]:
                continue
            state[k] = 1
            opened[0] += 1
            if num[k] == 0:
                for j in nb[k]:
                    if not state[j]:
                        stack.append(j)

    open_cell(start)
    res.opening = opened[0]

    while opened[0] < safe_total:
        res.rounds += 1
        safe, flag = set(), set()
        cons = {}
        for i in range(n):
            if state[i] != 1 or num[i] == 0:
                continue
            unk = []
            need = num[i]
            for j in nb[i]:
                s = state[j]
                if s == 0:
                    unk.append(j)
                elif s == 2:
                    need -= 1
            if not unk:
                continue
            if need == 0:
                safe.update(unk)
            elif need == len(unk):
                flag.update(unk)
            else:
                cons[frozenset(unk)] = need
        if not safe and not flag:
            # rule 2: overlapping pairs
            items = list(cons.items())
            by_cell: dict = {}
            for idx, (cells, _) in enumerate(items):
                for c in cells:
                    by_cell.setdefault(c, []).append(idx)
            for ai, (A, a) in enumerate(items):
                seen = set()
                for c in A:
                    for bi in by_cell[c]:
                        if bi <= ai or bi in seen:
                            continue
                        seen.add(bi)
                        B, b = items[bi]
                        only_a = A - B
                        only_b = B - A
                        if b - a == len(only_b) and (only_a or only_b):
                            flag.update(only_b)
                            safe.update(only_a)
                        elif a - b == len(only_a) and (only_a or only_b):
                            flag.update(only_a)
                            safe.update(only_b)
            if safe or flag:
                res.pair_rounds += 1
        if not safe and not flag:
            # rule 3: mine counter vs. a greedy disjoint cover
            unknown = [i for i in range(n) if state[i] == 0]
            remaining = total_mines - known[0]
            covered, cover_mines = set(), 0
            for cells, need in sorted(cons.items(), key=lambda kv: (len(kv[0]), min(kv[0]))):
                if covered.isdisjoint(cells):
                    covered |= cells
                    cover_mines += need
            rest = [i for i in unknown if i not in covered]
            if rest:
                left = remaining - cover_mines
                if left == 0:
                    safe.update(rest)
                elif left == len(rest):
                    flag.update(rest)
            if not safe and not flag:
                if remaining == 0:
                    safe.update(unknown)
                elif remaining == len(unknown):
                    flag.update(unknown)
            if safe or flag:
                res.count_rounds += 1
        if not safe and not flag:
            break  # stuck: the next move would be a guess
        for i in flag:
            if mine[i] != 1:
                raise AssertionError("solver deduced a mine on a safe cell (unsound rule)")
            if state[i] == 0:
                state[i] = 2
                known[0] += 1
        for i in safe:
            if mine[i]:
                raise AssertionError("solver deduced a safe cell on a mine (unsound rule)")
            open_cell(i)
    res.revealed = opened[0]
    res.solved = opened[0] == safe_total
    return res


# -------------------------------------------------------------------- gate


def load_levels(html: str):
    m = re.search(r"const\s+LEVELS\s*=\s*\[(.*?)\];", html, re.S)
    if not m:
        raise SystemExit("minesweeper_noguess: no `const LEVELS = [...]` in game.html")
    return re.findall(r'"([^"]*)"', m.group(1))


def check(quiet: bool = False) -> int:
    if not GAME.exists():
        print(f"✗ minesweeper_noguess: {GAME} missing")
        return 1
    html = GAME.read_text(encoding="utf-8")
    codes = load_levels(html)
    bad = []
    seen = {}
    shapes = []
    for li, code in enumerate(codes, 1):
        try:
            rows, cols, start, mines = decode_level(code)
        except ValueError as e:
            bad.append(f"level {li}: {e}")
            continue
        shapes.append((rows, cols, len(mines)))
        n = rows * cols
        if not (1 <= len(mines) <= n - 10):
            bad.append(f"level {li}: {len(mines)} mines on {n} cells")
            continue
        if start in mines:
            bad.append(f"level {li}: start cell {start} is a mine")
            continue
        nb = neighbours(rows, cols)
        if any(j in mines for j in nb[start]):
            bad.append(f"level {li}: start cell {start} touches a mine — the first tap would not open an area")
            continue
        r = solve(rows, cols, mines, start)
        if not r.solved:
            bad.append(f"level {li} ({rows}x{cols}, {len(mines)} mines): needs a guess after "
                       f"{r.revealed}/{n - len(mines)} safe cells")
            continue
        for t in range(4):
            key = (rows, cols, frozenset(transform(rows, cols, start, mines, t)[3]))
            if key in seen and seen[key] != li:
                bad.append(f"level {li}: same board as level {seen[key]} (transform {t})")
                break
            seen.setdefault(key, li)
        # Daily + endless play these boards mirrored / rotated: re-verify a
        # sample of every transform (logic is symmetric; this proves the
        # decoder's transform keeps the start opening intact).
        if li % 25 == 1:
            for t in (1, 2, 3):
                tr = transform(rows, cols, start, mines, t)
                if not solve(*tr[:2], tr[3], tr[2]).solved:
                    bad.append(f"level {li}: transform {t} is not solvable without guessing")
    if len(codes) < MIN_LEVELS:
        bad.append(f"campaign has {len(codes)} boards, need >= {MIN_LEVELS}")
    if shapes:
        if shapes[0] != (6, 6, 5):
            bad.append(f"level 1 is {shapes[0][0]}x{shapes[0][1]}/{shapes[0][2]}, the ramp must open at 6x6 / 5 mines")
        if shapes[-1][:2] != (30, 16):
            bad.append(f"last level is {shapes[-1][0]}x{shapes[-1][1]}, the ramp must end on 30x16 boards")
        for i in range(1, len(shapes)):
            if shapes[i][0] * shapes[i][1] < shapes[i - 1][0] * shapes[i - 1][1]:
                bad.append(f"level {i + 1}: board shrinks ({shapes[i - 1][:2]} -> {shapes[i][:2]}) — the ramp must not go backwards")
                break
    for line in bad:
        print(f"✗ minesweeper_noguess: {line}")
    if not bad and not quiet:
        print(f"minesweeper_noguess: OK — {len(codes)} boards, every one solvable without guessing "
              f"from its opening tap (6x6/5 -> {shapes[-1][0]}x{shapes[-1][1]}/{shapes[-1][2]})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(check("--quiet" in sys.argv))
