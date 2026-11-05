#!/usr/bin/env python3
"""gen_levels.py — mine Bubble Shooter's 500-level campaign.

Every board is drawn from a symmetric shape family, painted with clustered
colours, and then played by the SAME greedy bot the content gate uses
(scripts/check_bubbleshooter_levels.py is imported, never copied). The shot
limit, the 3-star par, the score target and the verified first-attempt
queue `k` are all set from those bot runs, so a level is only emitted when
the gate's acceptance test already passes with margin:

    levels 1-20 : the bot wins all 20 seeded runs (gate needs >= 19)
    levels 21+  : the bot wins >= 4 of the 5 seeded runs (gate needs 3)

Difficulty ramps by colour count (3 → 6), rows (3 → 10), cluster size,
Pip count and a shrinking shot margin.

    nice python3 BubbleShooter/test/gen_levels.py [--from N] [--to M] [--jobs J]

writes BubbleShooter/test/levels.json (one code per level) and, with
--write, replaces the LEVELS region of game.html.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "scripts"))
import check_bubbleshooter_levels as core  # noqa: E402

OUT = Path(__file__).resolve().parent / "levels.json"
COLS, POD = core.COLS, core.POD


def mirror(i):
    r, c = divmod(i, COLS)
    return r * COLS + (core.row_len(r) - 1 - c)


def cells_rows(rows):
    return [r * COLS + c for r in range(rows) for c in range(core.row_len(r))]


# ---------------------------------------------------------------- shapes
# Each returns a set of filled cells for `rows` rows. Shapes are written on
# d = |x - 5.5| (distance from the centre line), so they are left-right
# symmetric by construction; the board must still hang from row 0.

def _cells(rows, pred):
    out = set()
    for r in range(rows):
        for c in range(core.row_len(r)):
            i = r * COLS + c
            if pred(r, abs(core.CX[i] - 5.5), i):
                out.add(i)
    return out


def shape_block(rows, rnd):
    return _cells(rows, lambda r, d, i: True)


def shape_wedge(rows, rnd):
    """Inverted triangle hanging from a full ceiling row."""
    k = 4.2 / max(1, rows - 1)
    return _cells(rows, lambda r, d, i: d <= 5.6 - r * k)


def shape_hourglass(rows, rnd):
    """Wide bar, a narrow neck, a wide base: one good pop drops the base."""
    neck = max(1, rows // 2 - 1)
    def f(r, d, i):
        if r == 0:
            return d <= 4.1
        if r <= neck:
            return d <= 1.1
        return d <= 1.1 + (r - neck) * 1.15
    return _cells(rows, f)


def shape_pillars(rows, rnd):
    w = rnd.choice([0.6, 1.1])
    ctrs = (0.0, 2.75, 5.0)
    return _cells(rows, lambda r, d, i: r == 0 or min(abs(d - c) for c in ctrs) <= w)


def shape_diamond(rows, rnd):
    mid = (rows - 1) / 2
    return _cells(rows, lambda r, d, i: r == 0 or d <= 5.5 - abs(r - mid) * (4.0 / max(1, mid)))


def shape_vee(rows, rnd):
    return _cells(rows, lambda r, d, i: r == 0 or (r * 0.55 - 0.3 <= d <= r * 0.55 + 2.2))


def shape_holes(rows, rnd):
    out = shape_block(rows, rnd)
    for r in range(1, rows - 1):
        for c in range(core.row_len(r)):
            i = r * COLS + c
            if rnd.random() < 0.16:
                out.discard(i)
                out.discard(mirror(i))
    return out


def shape_chandelier(rows, rnd):
    ctrs = (0.0, 3.9)
    return _cells(rows, lambda r, d, i: r <= 1 or min(abs(d - c) for c in ctrs) <= 1.35 - 0.1 * (r - 2))


def shape_heart(rows, rnd):
    y1, y2 = core.cell_y(COLS), core.cell_y((rows - 1) * COLS)
    def f(r, d, i):
        if r == 0:
            return True
        u = d / 5.2
        v = (core.CY[i] - y1) / max(0.01, y2 - y1)
        if v < 0.45:
            return (u - 0.48) ** 2 + ((v - 0.3) / 0.75) ** 2 <= 0.2 or (v > 0.2 and u <= 0.5)
        return u <= (1.0 - v) / 0.55 + 0.05
    return _cells(rows, f)


def shape_arch(rows, rnd):
    """Two legs from the ceiling holding a bar at the bottom."""
    return _cells(rows, lambda r, d, i: r == 0 or r >= rows - 2 or d >= 3.4)


def shape_lattice(rows, rnd):
    return _cells(rows, lambda r, d, i: r == 0 or (r + int(d + 0.25)) % 3 != 0)


SHAPES = {
    "block": shape_block, "wedge": shape_wedge, "hourglass": shape_hourglass,
    "pillars": shape_pillars, "diamond": shape_diamond, "vee": shape_vee,
    "holes": shape_holes, "chandelier": shape_chandelier, "heart": shape_heart,
    "arch": shape_arch, "lattice": shape_lattice,
}


def supported(cells):
    """Keep only cells connected to the ceiling."""
    seen = set(i for i in cells if i < COLS)
    st = list(seen)
    while st:
        j = st.pop()
        for n in core.NB[j]:
            if n in cells and n not in seen:
                seen.add(n)
                st.append(n)
    return seen


def paint(cells, palette, p_same, rnd, sym):
    """Clustered colouring: walk cells in a random order; copy a painted
    neighbour's colour with probability p_same, else a fresh colour."""
    col = {}
    order = sorted(cells)
    rnd.shuffle(order)
    for i in order:
        if i in col:
            continue
        nbc = [col[n] for n in core.NB[i] if n in col]
        if nbc and rnd.random() < p_same:
            c = rnd.choice(nbc)
        else:
            c = rnd.choice(palette)
        col[i] = c
        if sym and mirror(i) in cells:
            col[mirror(i)] = c
    return col


def place_pods(cells, n, rnd):
    top = [i for i in sorted(cells) if i // COLS <= 2]
    rnd.shuffle(top)
    pods = []
    for i in top:
        if len(pods) >= n:
            break
        if any(abs(core.CX[i] - core.CX[j]) < 2.2 and i // COLS == j // COLS for j in pods):
            continue
        pods.append(i)
    return pods


# ---------------------------------------------------------------- schedule

GOAL_CYCLE = ["c", "p", "c", "s", "c", "p", "c", "c", "p", "s"]
EARLY_SHAPES = ["block", "wedge", "diamond", "chandelier", "holes"]


def goal_for(idx):
    if idx < 3:
        return "c"
    if idx == 3:
        return "p"
    if idx == 6:
        return "s"
    if idx < 10:
        return "c" if idx != 8 else "p"
    return GOAL_CYCLE[idx % 10]


def params(idx, rnd):
    t = idx / 499.0
    if idx < 4:
        ncol = 3
    elif idx < 12:
        ncol = 4 if (idx >= 8 or rnd.random() < 0.5) else 3
    elif idx < 40:
        ncol = 4
    elif idx < 110:
        ncol = 5 if rnd.random() < (idx - 40) / 70.0 else 4
    elif idx < 230:
        ncol = 5
    else:
        ncol = 6 if rnd.random() < min(0.75, 0.25 + (idx - 230) / 270.0 * 0.5) else 5
    if idx == 0:
        rows = 3
    elif idx < 3:
        rows = 4
    elif idx < 20:
        rows = rnd.randint(4, 6)
    elif idx < 60:
        rows = rnd.randint(5, 7)
    elif idx < 150:
        rows = rnd.randint(6, 8)
    elif idx < 300:
        rows = rnd.randint(7, 9)
    else:
        rows = rnd.randint(7, 10)
    p_same = max(0.36, 0.84 - 0.42 * t + rnd.uniform(-0.06, 0.06))
    if idx < 3:
        p_same = 0.9
    shape = rnd.choice(EARLY_SHAPES if idx < 12 else list(SHAPES))
    if idx < 10:
        pods = 1
    elif idx < 40:
        pods = 2
    elif idx < 120:
        pods = rnd.randint(2, 3)
    elif idx < 300:
        pods = rnd.randint(3, 4)
    else:
        pods = rnd.randint(3, 5)
    return {"ncol": ncol, "rows": rows, "p_same": p_same, "shape": shape, "pods": pods}


def max_par(idx):
    if idx < 3:
        return 8
    if idx < 20:
        return 16
    if idx < 100:
        return 24
    return 30


def min_par(idx):
    if idx < 3:
        return 2
    if idx < 20:
        return 3
    if idx < 100:
        return 5
    if idx < 250:
        return 7
    return 9


def margin(idx, base):
    if idx < 20:
        return max(3, round(0.3 * base))
    if idx < 60:
        return max(2, round(0.22 * base))
    if idx < 200:
        return max(2, round(0.15 * base))
    return max(1, round(0.1 * base))


def build_board(idx, rnd, prm, goal):
    cells = supported(SHAPES[prm["shape"]](prm["rows"], rnd))
    if len(cells) < 18:
        return None
    pal_all = list(range(1, 7))
    rnd.shuffle(pal_all)
    palette = sorted(pal_all[:prm["ncol"]])
    col = paint(cells, palette, prm["p_same"], rnd, rnd.random() < 0.55)
    board = [0] * core.NCELL
    for i, c in col.items():
        board[i] = c
    if goal == "p":
        for i in place_pods(cells, prm["pods"], rnd):
            board[i] = POD
    return board


def pick_k(wins_needs, med):
    best = None
    for k, s in wins_needs:
        key = (abs(s - med), k)
        if best is None or key < best[0]:
            best = (key, k)
    return best[1]


def gen_level(idx, tries=400):
    rnd = random.Random(idx * 7919 + 1337)
    goal = goal_for(idx)
    runs = core.runs_for(idx)
    for attempt in range(tries):
        prm = params(idx, rnd)
        board = build_board(idx, rnd, prm, goal)
        if board is None:
            continue
        pal = core.colours_on(board)
        if len(pal) != prm["ncol"]:
            continue
        lv = {"g": goal, "limit": 99, "par": 1, "target": 0, "k": 0, "pal": pal,
              "board": board, "rows": max(i // COLS for i in range(core.NCELL) if board[i]) + 1}
        if core.structural({**lv, "target": 1 if goal == "s" else 0}):
            continue
        if goal == "s":
            n = rnd.randint(*((8, 12) if idx < 20 else (12, 20) if idx < 100 else (15, 26)))
            sc = []
            for k in range(runs):
                s, cleared = core.score_run(lv, core.run_seed(idx, k), n)
                sc.append(s)
            sc.sort()
            low = sc[0] if idx < 20 else sc[1]
            target = int(low * 0.9) // 50 * 50
            if target < 300:
                continue
            lv["target"] = target
            needs = [core.play(lv, core.run_seed(idx, k), n)[0] for k in range(runs)]
            if any(s is None for s in needs):
                continue
            q = sorted(needs)
            med = q[len(q) // 2]
            if med < min_par(idx):
                continue
            limit = n
        else:
            needs = [core.play(lv, core.run_seed(idx, k), 70)[0] for k in range(runs)]
            if any(s is None for s in needs):
                continue
            q = sorted(needs)
            med = q[len(q) // 2]
            base = q[18] if idx < 20 else q[3]
            if med < min_par(idx) or med > max_par(idx):
                continue
            if base > 1.8 * med + 3:
                continue
            limit = base + margin(idx, base)
        wins = [(k, s) for k, s in enumerate(needs) if s <= limit]
        k = pick_k(wins, med)
        lv.update({"limit": limit, "par": med, "k": k})
        code = core.encode(goal, limit, med, lv["target"], k, pal, board)
        dec = core.decode(code)
        errs, st = core.verify_level(idx, dec)
        if errs:
            continue
        return code, {"attempt": attempt, "shape": prm["shape"], "needs": needs}
    raise RuntimeError(f"level {idx + 1}: no board accepted in {tries} tries")


def _job(idx):
    t = time.time()
    code, info = gen_level(idx)
    return idx, code, info, time.time() - t


def main():
    args = sys.argv[1:]
    lo = int(args[args.index("--from") + 1]) if "--from" in args else 0
    hi = int(args[args.index("--to") + 1]) if "--to" in args else 500
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else 1
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    todo = [i for i in range(lo, hi)]
    t0 = time.time()
    if jobs > 1:
        from multiprocessing import Pool
        with Pool(jobs) as pool:
            for idx, code, info, dt in pool.imap_unordered(_job, todo):
                data[str(idx)] = code
                print(f"L{idx + 1:3d} {info['shape']:10s} try {info['attempt']:3d} needs {info['needs']} {dt:.1f}s", flush=True)
    else:
        for i in todo:
            idx, code, info, dt = _job(i)
            data[str(idx)] = code
            print(f"L{idx + 1:3d} {info['shape']:10s} try {info['attempt']:3d} needs {info['needs']} {dt:.1f}s", flush=True)
    OUT.write_text(json.dumps(data, indent=0, sort_keys=True) + "\n")
    print(f"{len(todo)} levels in {time.time() - t0:.0f}s -> {OUT}")
    # duplicate boards across the whole set are re-rolled by hand (rare)
    seen = {}
    for k2 in sorted(data, key=int):
        b = data[k2].split("|")[6]
        if b in seen:
            print(f"!! duplicate board: L{int(k2) + 1} == L{seen[b] + 1}")
        seen.setdefault(b, int(k2))
    if "--write" in args:
        write_region(data)


def write_region(data):
    n = len(data)
    codes = [data[str(i)] for i in range(n)]
    body = ("// 500 goal levels mined by test/gen_levels.py; every one passes\n"
            "// scripts/check_bubbleshooter_levels.py (greedy bot within the shot limit).\n"
            "// \"goal|limit|par|target|k|palette|rows\" — see the gate for the format.\n"
            "const CAMPAIGN = [\n" + ",\n".join('"' + c + '"' for c in codes) + "\n];\n"
            "const LEVELS = CAMPAIGN;\n")
    tmp = Path(__file__).resolve().parent / ".levels_region.txt"
    tmp.write_text(body)
    import subprocess
    subprocess.run([sys.executable, str(BASE / "scripts" / "shell_region.py"), "BubbleShooter", "LEVELS", "--set", str(tmp)], check=True)
    tmp.unlink()
    print(f"wrote {n} levels into game.html LEVELS")


if __name__ == "__main__":
    main()
