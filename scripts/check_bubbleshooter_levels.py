#!/usr/bin/env python3
"""check_bubbleshooter_levels.py — gate: every shipped Bubble Shooter level
is clearable by a greedy bot within its shot budget.

bubble_levels: BubbleShooter ships 500 fixed goal levels in game.html as
`const CAMPAIGN = ["g|limit|par|target|k|palette|rows", ...]`:

    g        c = clear the board, p = free every trapped Pip (critter pod),
             s = reach `target` points (clearing the board also wins)
    limit    shots the player gets (stars by shots left, see `par`)
    par      shots for 3 stars (the bot's median); 2 stars up to
             par + ceil((limit - par) / 2)
    target   score goal (0 unless g == s)
    k        index of a VERIFIED winning colour queue: the first attempt of
             the level, and the Daily built from it, deal this queue
    palette  the level's colours, e.g. "1245" (1-6 = the six bubble roles)
    rows     hex rows joined by "/": even rows 11 cells, odd rows 10 cells;
             "." empty, "1"-"6" a bubble colour, "P" a trapped Pip

The physics, the rules and the colour queue below are a line-for-line port of
the engine in game.html (bsRaycast / bsResolve / bsDraw / bsBotPick): the
ball is a disc of diameter 1 fired from the launcher, reflecting off the side
walls; it sticks when it comes within HIT of a bubble (or reaches the
ceiling) and snaps to the empty hex cell whose centre is nearest the impact
point (provably the free cell the impact point lies in). 3+ connected of one
colour pop; Pips touching a pop are freed; anything no longer connected to
the ceiling falls. The next bubble is drawn from the colours still on the
board with mulberry32(levelSeed + k * 0x9E3779B1) — the game's attempt k.

The greedy bot ("a player who never plans ahead") aims at every reachable
landing cell — straight, or off the left or right wall — for the current and
the next bubble (swapping is free in the game), and takes the single shot
with the best immediate result. It never uses a booster.

For each level it BLOCKS unless:
  * the level string parses: goal / numbers / palette / row lengths / cells;
  * every bubble colour is in the level's palette (and the palette is used);
  * the board hangs from the ceiling (nothing floating), Pips exist exactly
    on Pip levels and sit in the top three rows, the board fits above the
    danger line;
  * the bot completes the goal within `limit` shots in a MAJORITY of the
    seeded runs (5 queues, k = 0..4), and in >= 95 % of 20 runs for levels
    1-20; the stored queue `k` is one of the bot's wins;
  * par <= limit, 3-star par is not below the bot's best run;
  * the campaign has >= 500 levels, no duplicate boards, levels 1-3 are
    small, quick boards (<= 4 rows, par <= 8 shots) and the colour count
    never jumps by more than one between neighbouring levels.

BubbleShooter/test/gen_levels.py imports this module, so the generator and
the gate can never disagree.

Usage:  python3 scripts/check_bubbleshooter_levels.py [BubbleShooter] [--quiet]
(other app names are skipped: the gate only applies to BubbleShooter).
Exit 1 on any bad level.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = "BubbleShooter"
GAME = BASE / APP / "android" / "app" / "src" / "main" / "assets" / "game.html"
MIN_LEVELS = 500

# ---------------------------------------------------------------- geometry
COLS = 11                     # cells in an even row (odd rows hold 10)
NROWS = 13                    # grid rows 0..12
DEAD = 12                     # a ball that settles in row 12 crossed the line
RH = math.sqrt(3) / 2         # row pitch (bubble diameter = 1)
HIT = 0.86                    # contact distance between centres
HIT2 = HIT * HIT
XMIN, XMAX, YTOP = 0.5, 10.5, 0.5
SX = 5.5
SY = 0.5 + 12 * RH + 1.3      # launcher centre
MINDY = -0.12                 # flattest allowed aim (dy of the unit vector)
MAXSEG = 24
POD = 7                       # cell value of a trapped Pip
NCELL = NROWS * COLS


def row_len(r: int) -> int:
    return COLS if r % 2 == 0 else COLS - 1


def cell_x(i: int) -> float:
    r, c = divmod(i, COLS)
    return (0.5 if r % 2 == 0 else 1.0) + c


def cell_y(i: int) -> float:
    return 0.5 + (i // COLS) * RH


VALID = [(i % COLS) < row_len(i // COLS) for i in range(NCELL)]
CX = [cell_x(i) for i in range(NCELL)]
CY = [cell_y(i) for i in range(NCELL)]


def _neighbours(i: int):
    r, c = divmod(i, COLS)
    out = []
    if r % 2 == 0:
        cand = [(r, c - 1), (r, c + 1), (r - 1, c - 1), (r - 1, c), (r + 1, c - 1), (r + 1, c)]
    else:
        cand = [(r, c - 1), (r, c + 1), (r - 1, c), (r - 1, c + 1), (r + 1, c), (r + 1, c + 1)]
    for rr, cc in cand:
        if 0 <= rr < NROWS and 0 <= cc < row_len(rr):
            out.append(rr * COLS + cc)
    return out


NB = [(_neighbours(i) if VALID[i] else []) for i in range(NCELL)]
ROW0 = [i for i in range(COLS) if VALID[i]]

# ---------------------------------------------------------------- rng


def mulberry32(a: int):
    """Exact port of the shell's mulberry32 (uint32 arithmetic)."""
    st = [a & 0xFFFFFFFF]

    def rnd() -> float:
        st[0] = (st[0] + 0x6D2B79F5) & 0xFFFFFFFF
        a2 = st[0]
        t = ((a2 ^ (a2 >> 15)) * (1 | a2)) & 0xFFFFFFFF
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rnd


def level_seed(idx: int) -> int:
    return ((idx + 1) * 2654435761) % 4294967296


def run_seed(idx: int, k: int) -> int:
    return (level_seed(idx) + k * 0x9E3779B1) % 4294967296

# ---------------------------------------------------------------- codec


def decode(code: str):
    """Mirror of the game's bsDecode(). Returns a dict; raises ValueError."""
    parts = code.split("|")
    if len(parts) != 7:
        raise ValueError(f"expected 7 fields, got {len(parts)}")
    g, s, p, t, k, pal, rows = parts
    if g not in ("c", "p", "s"):
        raise ValueError(f"bad goal {g!r}")
    for name, v in (("limit", s), ("par", p), ("target", t), ("k", k)):
        if not re.fullmatch(r"\d+", v):
            raise ValueError(f"bad {name} {v!r}")
    if not re.fullmatch(r"[1-6]{2,6}", pal) or len(set(pal)) != len(pal) or list(pal) != sorted(pal):
        raise ValueError(f"bad palette {pal!r}")
    rr = rows.split("/")
    if not 1 <= len(rr) <= DEAD:
        raise ValueError(f"{len(rr)} rows")
    board = [0] * NCELL
    for r, line in enumerate(rr):
        if len(line) != row_len(r):
            raise ValueError(f"row {r} has {len(line)} cells, expected {row_len(r)}")
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch == "P":
                board[r * COLS + c] = POD
            elif ch in "123456":
                board[r * COLS + c] = int(ch)
            else:
                raise ValueError(f"bad cell {ch!r} at row {r}")
    return {"g": g, "limit": int(s), "par": int(p), "target": int(t), "k": int(k),
            "pal": [int(x) for x in pal], "board": board, "rows": len(rr)}


def encode(g, limit, par, target, k, pal, board) -> str:
    last = max((i // COLS for i in range(NCELL) if board[i]), default=0)
    rows = []
    for r in range(last + 1):
        line = ""
        for c in range(row_len(r)):
            v = board[r * COLS + c]
            line += "." if v == 0 else ("P" if v == POD else str(v))
        rows.append(line)
    return f"{g}|{limit}|{par}|{target}|{k}|{''.join(str(x) for x in sorted(pal))}|{'/'.join(rows)}"

# ---------------------------------------------------------------- physics


def exposed_list(board):
    """Bubbles the ball can touch first: those with a free neighbour (or on
    the bottom row). A fully enclosed bubble can never be hit first."""
    out = []
    for i in range(NCELL):
        if board[i]:
            if i // COLS == NROWS - 1 or any(board[n] == 0 for n in NB[i]):
                out.append((i, CX[i], CY[i]))
    return out


def raycast(board, exposed, dx, dy):
    """Trace a shot along unit vector (dx, dy). Returns (cell, path) where
    cell is the landing index or -1 for a ball that crosses the danger line.
    Port of bsRaycast()."""
    px, py = SX, SY
    path = [(px, py)]
    for _ in range(MAXSEG):
        if dx > 1e-12:
            tw = (XMAX - px) / dx
        elif dx < -1e-12:
            tw = (XMIN - px) / dx
        else:
            tw = math.inf
        tc = (YTOP - py) / dy
        tb = math.inf
        hb = -1
        for (i, x, y) in exposed:
            ox = px - x
            oy = py - y
            b = dx * ox + dy * oy
            if b >= 0:
                continue
            c = ox * ox + oy * oy - HIT2
            disc = b * b - c
            if disc < 0:
                continue
            t = -b - math.sqrt(disc)
            if t < tb:
                tb = t
                hb = i
        if tb <= tw and tb <= tc:
            qx = px + dx * tb
            qy = py + dy * tb
            path.append((qx, qy))
            best = -1
            bd = math.inf
            for n in NB[hb]:
                if board[n] == 0:
                    ex = CX[n] - qx
                    ey = CY[n] - qy
                    d2 = ex * ex + ey * ey
                    if d2 < bd:
                        bd = d2
                        best = n
            if best < 0 or best // COLS >= DEAD:
                return -1, path
            return best, path
        if tc <= tw:
            qx = px + dx * tc
            path.append((qx, YTOP))
            best = -1
            bd = math.inf
            for n in ROW0:
                if board[n] == 0:
                    ex = CX[n] - qx
                    d2 = ex * ex
                    if d2 < bd:
                        bd = d2
                        best = n
            return best, path
        px = XMAX if dx > 0 else XMIN
        py = py + dy * tw
        dx = -dx
        path.append((px, py))
    return -1, path


def aims(board):
    """The bot's (and the hint's) candidate shots: aim at the centre of every
    free cell the ball could stick to, straight and off each wall. Port of
    bsAims(). Returns unit vectors."""
    out = []
    for i in range(DEAD * COLS):
        if not VALID[i] or board[i]:
            continue
        if i >= COLS and not any(board[n] for n in NB[i]):
            continue
        tx, ty = CX[i], CY[i]
        for ax in (tx, 2 * XMIN - tx, 2 * XMAX - tx):
            vx = ax - SX
            vy = ty - SY
            ln = math.sqrt(vx * vx + vy * vy)
            ux = vx / ln
            uy = vy / ln
            if uy <= MINDY:
                out.append((ux, uy))
    return out


def landings(board):
    """Distinct landing cells reachable this shot: {cell: (dx, dy)} (first
    aim found per cell, in aim order)."""
    ex = exposed_list(board)
    res = {}
    for (ux, uy) in aims(board):
        cell, _ = raycast(board, ex, ux, uy)
        if cell >= 0 and cell not in res:
            res[cell] = (ux, uy)
    return res

# ---------------------------------------------------------------- rules


def cluster(board, i, colour):
    """Cells of `colour` connected to i, with i treated as `colour`."""
    seen = {i}
    stack = [i]
    while stack:
        j = stack.pop()
        for n in NB[j]:
            if n not in seen and board[n] == colour:
                seen.add(n)
                stack.append(n)
    return seen


def drop_floaters(board):
    """Remove everything not connected to the ceiling. Returns
    (dropped bubbles, dropped pips, dropped cells)."""
    seen = set()
    stack = [i for i in ROW0 if board[i]]
    seen.update(stack)
    while stack:
        j = stack.pop()
        for n in NB[j]:
            if board[n] and n not in seen:
                seen.add(n)
                stack.append(n)
    nb = npod = 0
    cells = []
    for i in range(NCELL):
        if board[i] and i not in seen:
            if board[i] == POD:
                npod += 1
            else:
                nb += 1
            cells.append(i)
            board[i] = 0
    return nb, npod, cells


def remove_and_free(board, removed):
    """Clear `removed`; Pips inside it or touching it are freed. Returns
    (bubbles removed, pips freed)."""
    freed = 0
    nb = 0
    for j in removed:
        if board[j] == POD:
            freed += 1
        elif board[j]:
            nb += 1
        board[j] = 0
    for j in removed:
        for n in NB[j]:
            if board[n] == POD:
                board[n] = 0
                freed += 1
    return nb, freed


def resolve(board, i, colour):
    """Place `colour` at i and apply the rules in place. Port of bsResolve().
    Returns (popped, dropped, pips freed)."""
    board[i] = colour
    cl = cluster(board, i, colour)
    if len(cl) < 3:
        return 0, 0, 0
    popped, freed = remove_and_free(board, cl)
    dropped, dpods, _ = drop_floaters(board)
    return popped, dropped, freed + dpods


def points(popped, dropped, pips, combo):
    base = 10 * popped + 20 * dropped + 100 * pips
    return (base * (min(combo, 5) + 1)) // 2


def colours_on(board):
    return sorted({v for v in board if 0 < v < POD})


def draw(rnd, board):
    pres = colours_on(board)
    if not pres:
        return 1
    return pres[int(rnd() * len(pres))]


def pods_on(board):
    return sum(1 for v in board if v == POD)


def goal_met(g, board, score, target):
    if not any(board):
        return True
    if g == "p":
        return pods_on(board) == 0
    if g == "s":
        return score >= target
    return False

# ---------------------------------------------------------------- bot


def evaluate(board, cell, colour, g):
    """Greedy value of putting `colour` at `cell` (higher is better)."""
    cl = cluster(board, cell, colour)
    row = cell // COLS
    if len(cl) < 3:
        v = -1.0 - 0.06 * row
        if len(cl) == 2:
            v += 0.45
        return v
    b = board[:]
    popped, dropped, pips = resolve(b, cell, colour)
    v = popped + 1.6 * dropped + (9.0 if g == "p" else 1.0) * pips
    if not any(b):
        v += 50
    if g == "p" and pips == 0:
        # dig toward the pips: value pops that leave a pip exposed
        v += 0.6 * sum(1 for j in range(NCELL) if b[j] == POD and any(b[n] == 0 for n in NB[j]))
    return v


def bot_pick(board, cur, nxt, g):
    """(cell, use_next, value) of the best single shot, or (-1, False, None)."""
    lands = landings(board)
    best = (-1, False, None)
    opts = [(cur, False)] + ([(nxt, True)] if nxt != cur else [])
    for cell in lands:
        for colour, swap in opts:
            v = evaluate(board, cell, colour, g)
            if best[2] is None or v > best[2]:
                best = (cell, swap, v)
    return best


def play(lv, seed, cap):
    """One greedy run. Returns (shots used to meet the goal or None, score)."""
    board = lv["board"][:]
    g, target = lv["g"], lv["target"]
    rnd = mulberry32(seed)
    cur = draw(rnd, board)
    nxt = draw(rnd, board)
    score = 0
    combo = 0
    for shot in range(1, cap + 1):
        cell, swap, _ = bot_pick(board, cur, nxt, g)
        if swap:
            cur, nxt = nxt, cur
        if cell < 0:
            combo = 0                  # wasted shot (crossed the line)
        else:
            popped, dropped, pips = resolve(board, cell, cur)
            if popped:
                combo += 1
                score += points(popped, dropped, pips, combo)
            else:
                combo = 0
        if goal_met(g, board, score, target):
            return shot, score
        cur = nxt
        nxt = draw(rnd, board)
        pres = colours_on(board)
        if cur not in pres:
            cur = draw(rnd, board)
    return None, score


def score_run(lv, seed, shots):
    """Score the bot reaches in exactly `shots` shots (board clear = done)."""
    lv2 = dict(lv)
    lv2["g"] = "s"
    lv2["target"] = 10 ** 9
    board = lv["board"][:]
    rnd = mulberry32(seed)
    cur = draw(rnd, board)
    nxt = draw(rnd, board)
    score = combo = 0
    for shot in range(1, shots + 1):
        cell, swap, _ = bot_pick(board, cur, nxt, "s")
        if swap:
            cur, nxt = nxt, cur
        if cell >= 0:
            popped, dropped, pips = resolve(board, cell, cur)
            if popped:
                combo += 1
                score += points(popped, dropped, pips, combo)
            else:
                combo = 0
        else:
            combo = 0
        if not any(board):
            return score, shot
        cur = nxt
        nxt = draw(rnd, board)
        if cur not in colours_on(board):
            cur = draw(rnd, board)
    return score, None

# ---------------------------------------------------------------- checks


def structural(lv):
    """List of structural problems with a decoded level."""
    errs = []
    board = lv["board"]
    used = colours_on(board)
    pal = lv["pal"]
    bad = [c for c in used if c not in pal]
    if bad:
        errs.append(f"colours {bad} outside palette {pal}")
    unused = [c for c in pal if c not in used]
    if unused:
        errs.append(f"palette colours {unused} not on the board")
    if not any(board[i] for i in ROW0):
        errs.append("nothing hangs from the ceiling")
    b = board[:]
    nb, npod, _ = drop_floaters(b)
    if nb or npod:
        errs.append(f"{nb + npod} cells float (not connected to the ceiling)")
    pods = [i for i in range(NCELL) if board[i] == POD]
    if lv["g"] == "p":
        if not pods:
            errs.append("Pip level with no Pips")
        if any(i // COLS > 2 for i in pods):
            errs.append("a Pip below row 3")
    elif pods:
        errs.append("Pips on a non-Pip level")
    if lv["g"] == "s" and lv["target"] <= 0:
        errs.append("score level without a target")
    if lv["g"] != "s" and lv["target"]:
        errs.append("target on a non-score level")
    if lv["limit"] < 1 or lv["par"] < 1 or lv["par"] > lv["limit"]:
        errs.append(f"bad budget limit={lv['limit']} par={lv['par']}")
    if lv["rows"] > 10:
        errs.append(f"{lv['rows']} rows (max 10, the line is row {DEAD})")
    if len(used) < 2:
        errs.append("fewer than 2 colours")
    return errs


def runs_for(idx):
    return 20 if idx < 20 else 5


def verify_level(idx, lv):
    """(errors, stats) for one level: structure + bot runs."""
    errs = structural(lv)
    if errs:
        return errs, None
    n = runs_for(idx)
    used = []
    wins = []
    for k in range(n):
        s, _ = play(lv, run_seed(idx, k), lv["limit"])
        used.append(s)
        if s is not None:
            wins.append(k)
    need = 19 if idx < 20 else (n // 2 + 1)
    if len(wins) < need:
        errs.append(f"bot met the goal in {len(wins)}/{n} runs within {lv['limit']} shots (need {need})")
    if lv["k"] not in wins:
        errs.append(f"stored first-attempt queue k={lv['k']} is not a bot win")
    best = min((s for s in used if s is not None), default=None)
    if best is not None and lv["par"] < best:
        errs.append(f"3-star par {lv['par']} below the bot's best run ({best})")
    return errs, {"wins": len(wins), "runs": n, "used": used}


def load_campaign(src: str):
    m = re.search(r"const\s+CAMPAIGN\s*=\s*\[(.*?)\];", src, re.S)
    if not m:
        raise ValueError("no `const CAMPAIGN = [...]` in game.html")
    return re.findall(r'"([^"]*)"', m.group(1))


def check(quiet=False) -> int:
    src = GAME.read_text(encoding="utf-8")
    try:
        codes = load_campaign(src)
    except ValueError as e:
        print(f"✗ {APP}: {e}")
        return 1
    bad = 0
    if len(codes) < MIN_LEVELS:
        print(f"✗ {APP}: {len(codes)} levels (< {MIN_LEVELS})")
        bad += 1
    seen = {}
    prev_cols = None
    totals = {"c": 0, "p": 0, "s": 0}
    win_runs = all_runs = 0
    for idx, code in enumerate(codes):
        try:
            lv = decode(code)
        except ValueError as e:
            print(f"✗ level {idx + 1}: does not parse — {e}")
            bad += 1
            continue
        board_key = code.split("|")[6]
        if board_key in seen:
            print(f"✗ level {idx + 1}: same board as level {seen[board_key] + 1}")
            bad += 1
        seen.setdefault(board_key, idx)
        ncol = len(lv["pal"])
        if prev_cols is not None and abs(ncol - prev_cols) > 1:
            print(f"✗ level {idx + 1}: colour count jumps {prev_cols} → {ncol}")
            bad += 1
        prev_cols = ncol
        if idx < 3 and (lv["rows"] > 4 or lv["par"] > 8):
            print(f"✗ level {idx + 1}: opening level too big ({lv['rows']} rows, par {lv['par']})")
            bad += 1
        errs, st = verify_level(idx, lv)
        for e in errs:
            print(f"✗ level {idx + 1}: {e}")
        bad += bool(errs)
        totals[lv["g"]] += 1
        if st:
            win_runs += st["wins"]
            all_runs += st["runs"]
        if not quiet and (idx + 1) % 50 == 0:
            print(f"  … {idx + 1} levels checked", flush=True)
    if bad:
        print(f"✗ {APP}: {bad} problem(s) in bubble levels")
        return 1
    rate = 100.0 * win_runs / max(1, all_runs)
    print(f"✓ {APP}: {len(codes)} levels clearable by the greedy bot "
          f"({totals['c']} clear / {totals['p']} free-the-Pips / {totals['s']} score; "
          f"{win_runs}/{all_runs} seeded runs won, {rate:.1f}%)")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args and APP not in args:
        print(f"· check_bubbleshooter_levels: skipped ({', '.join(args)} — gate applies to {APP} only)")
        return 0
    if not GAME.exists():
        print(f"✗ {APP}: game.html missing")
        return 1
    return check("--quiet" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
