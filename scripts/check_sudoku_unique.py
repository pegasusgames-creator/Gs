#!/usr/bin/env python3
"""check_sudoku_unique.py — pre-publish content gate for Sudoku.

Parses the shipped puzzles straight out of Sudoku's game.html (the LEVELS
region: `const CAMPAIGN = [...]` and the daily/endless `const SD_POOL`) and
BLOCKS unless every puzzle:

  1. is well-formed: band letter (E/M/H/X) + 81 cells of '.'/1-9;
  2. has EXACTLY one solution — counted by this file's own brute-force
     search (independent of the grader, capped at 2);
  3. is solved completely by the technique grader in
     Sudoku/test/sudoku_core.py (singles → pairs/pointing/claiming →
     triples/quads/X-Wing → XY-Wing/Swordfish/XYZ-Wing/Jellyfish) and grades
     into its declared band;
and the campaign as a whole:
  4. has exactly 500 entries, banded Easy 1-125 / Medium 126-250 /
     Hard 251-375 / Expert 376-500, levels 1-3 with >= 45 givens,
     no duplicate puzzles (campaign + pool);
  5. the daily/endless pool holds >= 20 puzzles per band, and the
     relabel/shuffle the game applies to them keeps the grade (sampled).

    python3 scripts/check_sudoku_unique.py          # prints OK / ✗
Returns ([blocking], [warnings]) from check_app(app) for pre_publish_check.
"""

import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
APP = "Sudoku"
GAME = REPO / APP / "android" / "app" / "src" / "main" / "assets" / "game.html"
BANDS = "EMHX"
BAND_NAMES = {"E": "Easy", "M": "Medium", "H": "Hard", "X": "Expert"}
ENTRY = re.compile(r"^[EMHX][.1-9]{81}$")


def _array(html, name):
    m = re.search(r"const\s+" + name + r"\s*=\s*\[(.*?)\];", html, re.S)
    if not m:
        return None
    return re.findall(r'"([^"]*)"', m.group(1))


# ── independent brute-force solution counter (no shared code) ───────────────
def _count(cells, cap=2):
    rows = [0] * 9
    cols = [0] * 9
    boxs = [0] * 9
    empty = []
    for i, v in enumerate(cells):
        r, c = divmod(i, 9)
        b = (r // 3) * 3 + c // 3
        if v:
            bit = 1 << v
            if rows[r] & bit or cols[c] & bit or boxs[b] & bit:
                return 0
            rows[r] |= bit
            cols[c] |= bit
            boxs[b] |= bit
        else:
            empty.append((r, c, b))
    total = [0]

    def rec(rest):
        if not rest:
            total[0] += 1
            return total[0] >= cap
        best, bopts = None, None
        for k, (r, c, b) in enumerate(rest):
            used = rows[r] | cols[c] | boxs[b]
            opts = [d for d in range(1, 10) if not used >> d & 1]
            if bopts is None or len(opts) < len(bopts):
                best, bopts = k, opts
                if len(opts) <= 1:
                    break
        if not bopts:
            return False
        r, c, b = rest[best]
        nxt = rest[:best] + rest[best + 1:]
        for d in bopts:
            bit = 1 << d
            rows[r] |= bit
            cols[c] |= bit
            boxs[b] |= bit
            stop = rec(nxt)
            rows[r] ^= bit
            cols[c] ^= bit
            boxs[b] ^= bit
            if stop:
                return True
        return False

    rec(empty)
    return total[0]


def _cells(entry):
    return [0 if ch == "." else int(ch) for ch in entry[1:]]


def check_app(app=APP):
    blocking, warnings = [], []
    if app != APP:
        return blocking, warnings
    if not GAME.exists():
        return [f"{app}: game.html not found"], warnings
    sys.path.insert(0, str(REPO / APP / "test"))
    try:
        import sudoku_core as sc
    except Exception as e:  # pragma: no cover
        return [f"{app}: cannot import Sudoku/test/sudoku_core.py ({e})"], warnings
    html = GAME.read_text(encoding="utf-8")
    camp = _array(html, "CAMPAIGN")
    pool = _array(html, "SD_POOL")
    if camp is None:
        return [f"{app}: no `const CAMPAIGN = [...]` in game.html"], warnings
    if pool is None:
        blocking.append(f"{app}: no `const SD_POOL = [...]` (daily/endless pool) in game.html")
        pool = []
    if len(camp) != 500:
        blocking.append(f"{app}: CAMPAIGN has {len(camp)} puzzles, expected 500")
    seen = {}
    bad = []

    def verify(where, idx, entry, want_band=None):
        tag = f"{where} {idx}"
        if not ENTRY.match(entry):
            bad.append(f"{tag}: malformed entry")
            return
        band = entry[0]
        if want_band and band != want_band:
            bad.append(f"{tag}: band {band}, expected {want_band}")
        body = entry[1:]
        if body in seen:
            bad.append(f"{tag}: duplicate of {seen[body]}")
        seen[body] = tag
        cells = _cells(entry)
        n = _count(cells)
        if n != 1:
            bad.append(f"{tag}: {'no' if n == 0 else 'multiple'} solution(s)")
            return
        g = sc.grade(cells)
        if not g.solved:
            bad.append(f"{tag}: not solvable by the technique catalogue")
            return
        if sc.BAND_LETTER[g.tier] != band:
            bad.append(f"{tag}: grades {sc.BAND_NAMES[g.tier]} ({g.hardest}), declared {BAND_NAMES[band]}")
        return g

    for i, e in enumerate(camp):
        want = BANDS[min(3, i // 125)]
        g = verify("level", i + 1, e, want)
        if i < 3 and g is not None and g.givens < 45:
            bad.append(f"level {i + 1}: only {g.givens} givens (levels 1-3 need >= 45)")
    per_band = {b: [] for b in BANDS}
    for i, e in enumerate(pool):
        verify("pool", i, e)
        if ENTRY.match(e):
            per_band[e[0]].append(e)
    for b in BANDS:
        if len(per_band[b]) < 20:
            bad.append(f"pool: only {len(per_band[b])} {BAND_NAMES[b]} puzzles (need >= 20)")
    # the game's daily/endless transform must keep uniqueness + grade
    rng = random.Random(20261015)
    for b in BANDS:
        for e in per_band[b][:6]:
            cells = _cells(e)
            for _ in range(2):
                perm = list(range(1, 10))
                rng.shuffle(perm)
                bands3 = [0, 1, 2]
                rng.shuffle(bands3)
                rows = [bb * 3 + k for bb in bands3 for k in rng.sample(range(3), 3)]
                stacks = [0, 1, 2]
                rng.shuffle(stacks)
                cols = [ss * 3 + k for ss in stacks for k in rng.sample(range(3), 3)]
                t = sc.transform(cells, perm, rows, cols, rng.random() < 0.5)
                if _count(t) != 1:
                    bad.append(f"pool {b}: transform broke uniqueness")
                    continue
                gt = sc.grade(t)
                if not gt.solved or sc.BAND_LETTER[gt.tier] != b:
                    bad.append(f"pool {b}: transformed copy grades {gt.tier}, expected {b}")
    if bad:
        blocking.append(f"{app}: {len(bad)} bad Sudoku puzzle(s): " + "; ".join(bad[:10])
                        + ("…" if len(bad) > 10 else "") + " — re-run Sudoku/test/gen_levels.py --inject")
    return blocking, warnings


def main():
    b, w = check_app(APP)
    for m in b:
        print(f"  ✗ {m}")
    for m in w:
        print(f"  ! {m}")
    if b:
        print("✗ Sudoku content gate FAILED")
        sys.exit(1)
    print("OK — Sudoku: 500 campaign + pool puzzles, each exactly one solution, graded into its band")


if __name__ == "__main__":
    main()
