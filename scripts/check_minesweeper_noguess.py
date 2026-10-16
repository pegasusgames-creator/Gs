#!/usr/bin/env python3
"""check_minesweeper_noguess.py — gate: every shipped Minesweeper board is
solvable WITHOUT GUESSING from its stored safe first click.

minesweeper_noguess: Minesweeper ships fixed, pre-verified boards. The 500
campaign levels live in game.html as `const CAMPAIGN = ["RxC:start:bits", ...]`
(base64url mine bitmap, 6 bits per char, MSB first, row-major). The daily
board and Endless mode replay these same boards under a mirror / 180-degree
rotation (transformBoard() in the engine), so this gate checks every board
under all four transforms — every board a player can ever be dealt.

For each board it BLOCKS unless:
  * the encoding is well formed (size, bitmap length, zero padding bits);
  * the stored start cell is safe AND touches no mine — the first tap always
    opens an area (a "0" flood), never a lone number;
  * a pure logical solver clears every safe cell from that opening, with no
    guess at any step. The rules (each a sound deduction):
        R1 single number  need == 0 -> hidden neighbours safe;
                          need == hidden -> all mines
        R2 subset / pair  overlapping constraints A, B (a, b mines):
                          b - a == |B\\A|  ->  B\\A all mines, A\\B all safe
                          (covers the subset case A <= B and its mirror)
        R3 mine counter   remaining mines vs. the hidden cells: all-safe /
                          all-mine when the count leaves no choice, also after
                          setting aside ONE constraint or TWO disjoint ones
    All rules are monotone (more revealed truth never disables a deduction)
    and index-free, so the fixpoint is unique: the result does not depend on
    move order, on the transform, or on which safe cells the player opened
    first. The in-game hint runs the same rules (msDeduce in game.html), so a
    hint always exists on a shipped board and is never a guess;
  * no two campaign boards are the same board (incl. under the transforms);
  * the campaign has >= 500 boards, opens at 6x6 / 5 mines, never shrinks,
    ends on 30x16 boards, and levels 1-3 need only single-number logic.

Minesweeper/test/gen_levels.py imports this module's solver, so the
generator and the gate can never disagree.

Usage:  python3 scripts/check_minesweeper_noguess.py [Minesweeper] [--quiet]
(other app names are ignored: the gate only applies to Minesweeper). Exit 1
on any bad board.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = "Minesweeper"
GAME = BASE / APP / "android" / "app" / "src" / "main" / "assets" / "game.html"
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
    """Mirror of the game's msDecode(): returns (rows, cols, start, mines:set).
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
    """Mirror of the game's msTransform(): t 0=identity, 1=mirror columns,
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


def three_bv(rows: int, cols: int, mines) -> int:
    """Bechtel's Board Benchmark Value: the minimum number of clicks that
    clears the board without flags (each 0-region is one click, plus every
    number not on the rim of a 0-region). The game derives its star par
    time from the same count (msBBBV in game.html)."""
    nb = neighbours(rows, cols)
    n = rows * cols
    num = [0] * n
    for m in mines:
        for j in nb[m]:
            num[j] += 1
    seen = bytearray(n)
    bv = 0
    for i in range(n):
        if i in mines or seen[i] or num[i]:
            continue
        bv += 1
        stack = [i]
        seen[i] = 1
        while stack:
            k = stack.pop()
            for j in nb[k]:
                if not seen[j] and j not in mines:
                    seen[j] = 1
                    if num[j] == 0:
                        stack.append(j)
    for i in range(n):
        if i not in mines and not seen[i]:
            bv += 1
    return bv


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


def deduce(n, nb, num, state, total_mines, known_mines, max_rule=3):
    """One round of deduction on `state` (0 hidden, 1 open, 2 known mine).
    Returns (safe:set, mines:set, rule:int) using the lowest rule that finds
    anything (rule 0 = nothing found -> the next move would be a guess)."""
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
    if safe or flag:
        return safe, flag, 1
    if max_rule < 2:
        return safe, flag, 0
    # R2: overlapping pairs (subset reasoning)
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
                if a - b == len(only_a) and (only_a or only_b):
                    flag.update(only_a)
                    safe.update(only_b)
    if safe or flag:
        return safe, flag, 2
    if max_rule < 3:
        return safe, flag, 0
    # R3: mine counter
    unknown = [i for i in range(n) if state[i] == 0]
    un = len(unknown)
    remaining = total_mines - known_mines
    if remaining == 0:
        return set(unknown), flag, 3
    if remaining == un:
        return safe, set(unknown), 3

    def settle(excl, left):
        rest = [i for i in unknown if i not in excl]
        if left == 0:
            safe.update(rest)
        else:
            flag.update(rest)

    for A, a in items:
        rest_n = un - len(A)
        left = remaining - a
        if rest_n > 0 and (left == 0 or left == rest_n):
            settle(A, left)
    if not safe and not flag:
        k = len(items)
        for i in range(k):
            A, a = items[i]
            for j in range(i + 1, k):
                B, b = items[j]
                rest_n = un - len(A) - len(B)
                left = remaining - a - b
                if rest_n > 0 and (left == 0 or left == rest_n) and A.isdisjoint(B):
                    settle(A | B, left)
    if safe or flag:
        return safe, flag, 3
    return safe, flag, 0


def solve(rows: int, cols: int, mines, start: int, max_rule: int = 3) -> SolveResult:
    """Logical solve from the start opening. state: 0 hidden, 1 open, 2 known mine."""
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
    known = 0

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
        safe, flag, rule = deduce(n, nb, num, state, total_mines, known, max_rule)
        if rule == 0:
            break  # stuck: the next move would be a guess
        if rule == 2:
            res.pair_rounds += 1
        elif rule == 3:
            res.count_rounds += 1
        for i in flag:
            if mine[i] != 1:
                raise AssertionError("solver deduced a mine on a safe cell (unsound rule)")
            if state[i] == 0:
                state[i] = 2
                known += 1
        for i in safe:
            if mine[i]:
                raise AssertionError("solver deduced a safe cell on a mine (unsound rule)")
            open_cell(i)
    res.revealed = opened[0]
    res.solved = opened[0] == safe_total
    return res


# -------------------------------------------------------------------- gate


def load_levels(html: str):
    m = re.search(r"const\s+CAMPAIGN\s*=\s*\[(.*?)\];", html, re.S)
    if not m:
        raise ValueError("no `const CAMPAIGN = [...]` in game.html")
    return re.findall(r'"([^"]*)"', m.group(1))


def check(quiet: bool = False) -> int:
    if not GAME.exists():
        print(f"✗ minesweeper_noguess: {GAME} missing")
        return 1
    html = GAME.read_text(encoding="utf-8")
    try:
        codes = load_levels(html)
    except ValueError as e:
        print(f"✗ minesweeper_noguess: {e}")
        return 1
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
        for t in range(4):
            tr = transform(rows, cols, start, mines, t)
            r = solve(rows, cols, tr[3], tr[2])
            if not r.solved:
                bad.append(f"level {li} ({rows}x{cols}, {len(mines)} mines, transform {t}): needs a guess "
                           f"after {r.revealed}/{n - len(mines)} safe cells")
                break
        else:
            if li <= 3 and not solve(rows, cols, mines, start, max_rule=1).solved:
                bad.append(f"level {li}: needs more than single-number logic (first-session boards must be trivial)")
        for t in range(4):
            key = (rows, cols, frozenset(transform(rows, cols, start, mines, t)[3]))
            if key in seen and seen[key] != li:
                bad.append(f"level {li}: same board as level {seen[key]} (transform {t})")
                break
            seen.setdefault(key, li)
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
    for line in bad[:40]:
        print(f"✗ minesweeper_noguess: {line}")
    if len(bad) > 40:
        print(f"✗ minesweeper_noguess: … {len(bad) - 40} more")
    if bad:
        print("  re-run: python3 Minesweeper/test/gen_levels.py --write")
    elif not quiet:
        print(f"minesweeper_noguess: OK — {len(codes)} boards x 4 transforms, every one solvable without "
              f"guessing from its opening tap (6x6/5 -> {shapes[-1][0]}x{shapes[-1][1]}/{shapes[-1][2]})")
    return 1 if bad else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args and APP not in args:
        sys.exit(0)  # gate applies to Minesweeper only
    sys.exit(check("--quiet" in sys.argv))
