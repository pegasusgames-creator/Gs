#!/usr/bin/env python3
"""
gen_levels.py — mine Sudoku's 500-puzzle campaign + the daily/endless pool.

  nice python3 Sudoku/test/gen_levels.py            # mine + write levels.json
  nice python3 Sudoku/test/gen_levels.py --inject   # also rewrite the LEVELS region

Bands (graded by sudoku_core.grade — the same grader the gate runs):
  Easy   1-125   singles only, 48 → 36 givens (levels 1-3 ≥ 45), symmetric
  Medium 126-250 needs pairs / pointing / claiming, symmetric
  Hard   251-375 needs triples / quads / X-Wing
  Expert 376-500 needs XY-Wing / Swordfish / XYZ-Wing / Jellyfish
Every puzzle is dug from a random full grid while it stays solvable by the
technique catalogue, so each one has exactly one solution. Deterministic:
job seeds are consumed in order, results are collected in seed order.
"""
import json
import os
import random
import subprocess
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sudoku_core as sc  # noqa: E402

BASE = os.path.abspath(os.path.join(HERE, "..", ".."))
APP = "Sudoku"
PER_BAND = 125
POOL_PER_BAND = 30
WORKERS = 3


def easy_target(i):
    """Givens for easy level i (0-based within band): 48 → 36."""
    return int(round(48 - 12 * i / (PER_BAND - 1)))


def job(args):
    band, seed, floor, sym = args
    rng = random.Random(seed * 7919 + band * 104729 + 17)
    puz, sol, r = sc.make_puzzle(rng, band, floor, symmetric=sym)
    if not r.solved or r.tier != band:
        return None
    return {"p": sc.fmt(puz), "band": band, "givens": r.givens, "score": r.score,
            "hardest": r.hardest, "seed": seed}


def mine(pool, band, need, floor, sym, seed0):
    out = []
    seed = seed0
    batch = 240
    while len(out) < need:
        args = [(band, s, floor, sym) for s in range(seed, seed + batch)]
        for res in pool.imap(job, args, chunksize=8):
            if res and len(out) < need:
                out.append(res)
        seed += batch
        print("  band %s: %d/%d (seeds to %d)" % (sc.BAND_NAMES[band], len(out), need, seed), flush=True)
    return out


def mine_easy(pool, seed0):
    args = [(0, seed0 + i, easy_target(i), True) for i in range(PER_BAND + POOL_PER_BAND)]
    res = list(pool.imap(job, args, chunksize=8))
    assert all(res), "easy dig failed"
    return res


def main():
    seen = set()
    data = {}
    with Pool(WORKERS) as pool:
        print("mining Easy…", flush=True)
        easy = mine_easy(pool, 1000)
        print("mining Medium…", flush=True)
        med = mine(pool, 1, PER_BAND + POOL_PER_BAND, 17, True, 200000)
        print("mining Hard…", flush=True)
        hard = mine(pool, 2, PER_BAND + POOL_PER_BAND, 17, False, 400000)
        print("mining Expert…", flush=True)
        expert = mine(pool, 3, PER_BAND + POOL_PER_BAND, 17, False, 600000)
    for name, lst in (("easy", easy), ("med", med), ("hard", hard), ("expert", expert)):
        for e in lst:
            assert e["p"] not in seen, "duplicate puzzle"
            seen.add(e["p"])
        data[name] = lst
    campaign = []
    pool_out = []
    # Easy: campaign = first 125 (givens schedule), sorted by givens desc then score
    e_camp = sorted(easy[:PER_BAND], key=lambda e: (-e["givens"], e["score"]))
    campaign += e_camp
    pool_out += easy[PER_BAND:]
    for lst in (med, hard, expert):
        camp = sorted(lst[:PER_BAND], key=lambda e: (e["score"], -e["givens"]))
        campaign += camp
        pool_out += lst[PER_BAND:]
    assert len(campaign) == 500
    out = {"campaign": [sc.BAND_LETTER[e["band"]] + e["p"] for e in campaign],
           "pool": [sc.BAND_LETTER[e["band"]] + e["p"] for e in pool_out],
           "meta": [{k: e[k] for k in ("givens", "score", "hardest", "seed")} for e in campaign]}
    with open(os.path.join(HERE, "levels.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote test/levels.json — campaign %d, pool %d" % (len(out["campaign"]), len(out["pool"])))
    if "--inject" in sys.argv:
        inject(out)


def region_text(out):
    def arr(name, items):
        lines = ["const %s = [" % name]
        for k in range(0, len(items), 4):
            lines.append("  " + ",".join('"%s"' % s for s in items[k:k + 4]) + ",")
        lines[-1] = lines[-1].rstrip(",")
        lines.append("];")
        return "\n".join(lines)
    return "\n".join([
        "// ============================================================",
        "// SUDOKU CAMPAIGN — 500 puzzles mined by test/gen_levels.py and",
        "// verified by scripts/check_sudoku_unique.py (exactly one solution,",
        "// technique grade == declared band). Entry = band letter + 81 cells",
        "// ('.' = empty). E Easy 1-125 · M Medium 126-250 · H Hard 251-375 ·",
        "// X Expert 376-500. Solutions are solved at load (unique by the gate).",
        "// ============================================================",
        arr("CAMPAIGN", out["campaign"]),
        "const LEVELS = CAMPAIGN; // length contract for level-select/addendum",
        "// Daily / endless pool (30 per band), shown through a date-seeded",
        "// relabel + row/column shuffle that keeps uniqueness and grade.",
        arr("SD_POOL", out["pool"]),
    ])


def inject(out):
    tmp = os.path.join(HERE, ".levels_region.tmp")
    with open(tmp, "w") as f:
        f.write(region_text(out) + "\n")
    subprocess.check_call([sys.executable, os.path.join(BASE, "scripts", "shell_region.py"), APP, "LEVELS", "--set", tmp])
    os.remove(tmp)
    print("injected LEVELS region")


if __name__ == "__main__":
    if "--inject-only" in sys.argv:
        with open(os.path.join(HERE, "levels.json")) as f:
            inject(json.load(f))
    else:
        main()
