#!/usr/bin/env python3
"""gen_levels.py — mine the 500-board Minesweeper campaign.

Every board is NO-GUESS by construction: mines are scattered away from a
chosen start cell (so the first tap opens a "0" area), then the SAME logical
solver the release gate runs (scripts/check_minesweeper_noguess.py) plays it.
When the solver gets stuck, the layout is perturbed Tatham-style — one
unresolved frontier cell swaps state with an untouched interior cell, mine
count unchanged — and the board is re-solved from scratch. A board is kept
only when the solver clears every safe cell.

Ramp (rows x cols, portrait): 6x6/5 mines -> 30x16/104 mines (21.7%, denser
than the classic 99-mine expert board). Inside each size tier the boards are
ordered by how much pair / mine-count reasoning they need, so difficulty
climbs smoothly. Levels 1-10 need only single-number logic (first session:
every early board clears in well under 30 s).

Deterministic: seed = 1000 + 7919 * level. Re-running reproduces the same
campaign byte for byte.

Usage:
    python3 Minesweeper/test/gen_levels.py            # generate + report
    python3 Minesweeper/test/gen_levels.py --write    # also replace the LEVELS region in game.html
"""
from __future__ import annotations

import json
import random
import re
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "scripts"))
import check_minesweeper_noguess as ms  # noqa: E402  (shared solver = the gate)

GAME = BASE / "Minesweeper" / "android" / "app" / "src" / "main" / "assets" / "game.html"
OUT = Path(__file__).resolve().parent / "levels.json"

# (count, rows, cols, first_mines, last_mines, max_pair_rounds)
TIERS = [
    (10, 6, 6, 5, 6, 0),
    (15, 7, 7, 7, 8, 2),
    (25, 8, 8, 8, 10, None),
    (30, 9, 9, 10, 13, None),
    (30, 11, 9, 14, 17, None),
    (40, 12, 10, 17, 21, None),
    (50, 14, 11, 22, 28, None),
    (50, 16, 12, 28, 35, None),
    (60, 18, 14, 38, 47, None),
    (60, 22, 14, 48, 58, None),
    (60, 24, 16, 62, 74, None),
    (70, 30, 16, 80, 104, None),
]
assert sum(t[0] for t in TIERS) == 500
CANDIDATES = 5


def gen_board(rows, cols, n_mines, rng, max_pair=None, max_opening_frac=0.38):
    nb = ms.neighbours(rows, cols)
    n = rows * cols
    # start cell: anywhere at least one cell in from the edge, biased central
    for _restart in range(400):
        r = int(rng.triangular(1, rows - 2, (rows - 1) / 2) + 0.5)
        c = int(rng.triangular(1, cols - 2, (cols - 1) / 2) + 0.5)
        r = min(max(r, 1), rows - 2)
        c = min(max(c, 1), cols - 2)
        start = r * cols + c
        banned = set(nb[start]) | {start}
        pool = [i for i in range(n) if i not in banned]
        mines = set(rng.sample(pool, n_mines))
        for _perturb in range(60 + n // 2):
            res = ms.solve(rows, cols, mines, start)
            if res.solved:
                break
            st = res.state
            frontier = [i for i in range(n) if st[i] == 0 and any(st[j] == 1 for j in nb[i])]
            interior = [i for i in range(n) if st[i] == 0 and i not in banned
                        and not any(st[j] == 1 for j in nb[i])]
            if not frontier or not interior:
                break
            x = rng.choice(frontier)
            cand = [y for y in interior if (y in mines) != (x in mines)]
            if not cand:
                break
            y = rng.choice(cand)
            if x in mines:
                mines.discard(x)
                mines.add(y)
            else:
                mines.discard(y)
                mines.add(x)
        else:
            continue
        if not res.solved:
            continue
        safe_n = n - n_mines
        if res.opening > max_opening_frac * safe_n and n >= 64:
            continue  # the first tap would clear too much of the board
        if res.opening < max(10, int(0.07 * safe_n)):
            continue  # opening too small to feel like an opening
        if max_pair is not None and res.pair_rounds + res.count_rounds > max_pair:
            continue
        return start, mines, res
    raise RuntimeError(f"could not generate {rows}x{cols}/{n_mines}")


def build_levels(verbose=True):
    levels = []
    lvl = 0
    t0 = time.time()
    for count, rows, cols, m0, m1, max_pair in TIERS:
        tier = []
        for k in range(count):
            lvl += 1
            mines_n = round(m0 + (m1 - m0) * (k / max(1, count - 1)))
            rng = random.Random(1000 + 7919 * lvl)
            # several candidates; pick by a difficulty target that climbs
            # through the tier (early = gentlest, late = most reasoning)
            cands = []
            for _c in range(CANDIDATES):
                start, mines, res = gen_board(rows, cols, mines_n, rng, max_pair)
                score = res.pair_rounds * 3 + res.count_rounds * 2 + res.rounds * 0.1
                cands.append((score, start, sorted(mines), res))
            cands.sort(key=lambda t: (t[0], t[1]))
            frac = k / max(1, count - 1)
            score, start, mines, res = cands[round(frac * (len(cands) - 1))]
            tier.append({"code": ms.encode_level(rows, cols, start, mines), "mines": mines_n,
                         "bv": ms.three_bv(rows, cols, set(mines)),
                         "score": round(score, 2), "opening": res.opening,
                         "pair": res.pair_rounds, "count": res.count_rounds})
        # keep the mine-count ramp, then order equal-mine boards by reasoning load
        tier.sort(key=lambda d: (d["mines"], d["score"]))
        levels.extend(tier)
        if verbose:
            print(f"  tier {rows}x{cols} {m0}->{m1}: {count} boards, "
                  f"avg pair rounds {sum(d['pair'] for d in tier) / count:.1f}, "
                  f"t={time.time() - t0:.1f}s", flush=True)
    return levels


def write_game(levels):
    """Replace the LEVELS shell region with the campaign (keeps the markers)."""
    html = GAME.read_text(encoding="utf-8")
    body = ",\n".join('  "%s"' % d["code"] for d in levels)
    region = ("// LEVELS — %d no-guess boards (Minesweeper/test/gen_levels.py).\n"
              "// \"RxC:start:bits\": rows x cols, the safe opening cell, base64url\n"
              "// mine bitmap (6 bits/char, MSB first, row-major). Gate:\n"
              "// scripts/check_minesweeper_noguess.py (all 4 transforms).\n"
              "const CAMPAIGN = [\n%s\n];\n"
              "const LEVELS = CAMPAIGN; // length contract for level-select/addendum\n") % (len(levels), body)
    a = html.index("//@@REGION LEVELS\n") + len("//@@REGION LEVELS\n")
    b = html.index("//@@END LEVELS")
    GAME.write_text(html[:a] + region + html[b:], encoding="utf-8")


def main():
    levels = build_levels()
    OUT.write_text(json.dumps(levels, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(BASE)} ({len(levels)} boards)")
    if "--write" in sys.argv:
        write_game(levels)
        print(f"patched LEVELS in {GAME.relative_to(BASE)}")


if __name__ == "__main__":
    main()
