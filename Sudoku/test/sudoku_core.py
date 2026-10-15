#!/usr/bin/env python3
"""
sudoku_core.py — Sudoku brute-force solver, technique-based grader and
generator (stdlib only). Shared by Sudoku/test/gen_levels.py (mining) and
scripts/check_sudoku_unique.py (the content gate), so the grader that mines
the campaign is the same one that verifies it.

Grid = list of 81 ints (0 = empty). Puzzle strings are 81 chars, '.' = empty.

Technique tiers (the band a puzzle grades into = the hardest tier it NEEDS
when the solver always applies the simplest available technique first):

  0 Easy   naked single, hidden single
  1 Medium pointing, claiming (locked candidates), naked pair, hidden pair
  2 Hard   naked triple, hidden triple, X-Wing, naked quad, hidden quad
  3 Expert XY-Wing, Swordfish, XYZ-Wing, Jellyfish

Every technique is a sound deduction (none assumes uniqueness), so a puzzle
the grader solves completely has exactly one solution. The gate still
double-checks uniqueness with an independent brute-force counter.
"""
import random
from itertools import combinations

ROWS = [[r * 9 + c for c in range(9)] for r in range(9)]
COLS = [[r * 9 + c for r in range(9)] for c in range(9)]
BOXES = [[(3 * (b // 3) + k // 3) * 9 + 3 * (b % 3) + k % 3 for k in range(9)] for b in range(9)]
UNITS = ROWS + COLS + BOXES
ROW_OF = [i // 9 for i in range(81)]
COL_OF = [i % 9 for i in range(81)]
BOX_OF = [(i // 27) * 3 + (i % 9) // 3 for i in range(81)]
PEERS = [sorted(set(ROWS[ROW_OF[i]] + COLS[COL_OF[i]] + BOXES[BOX_OF[i]]) - {i}) for i in range(81)]
PEERSET = [frozenset(p) for p in PEERS]
POP = [bin(m).count("1") for m in range(512)]
BITS = [[1 << d for d in range(9) if m >> d & 1] for m in range(512)]
FULL = 511
BIT2D = {1 << d: d + 1 for d in range(9)}

BAND_NAMES = ["Easy", "Medium", "Hard", "Expert"]
BAND_LETTER = "EMHX"
TECH_TIER = {
    "naked_single": 0, "hidden_single": 0,
    "pointing": 1, "claiming": 1, "naked_pair": 1, "hidden_pair": 1,
    "naked_triple": 2, "hidden_triple": 2, "x_wing": 2, "naked_quad": 2, "hidden_quad": 2,
    "xy_wing": 3, "swordfish": 3, "xyz_wing": 3, "jellyfish": 3,
}
TECH_WEIGHT = {
    "naked_single": 1, "hidden_single": 2,
    "pointing": 8, "claiming": 9, "naked_pair": 10, "hidden_pair": 14,
    "naked_triple": 18, "hidden_triple": 24, "x_wing": 26, "naked_quad": 30, "hidden_quad": 34,
    "xy_wing": 40, "swordfish": 44, "xyz_wing": 48, "jellyfish": 56,
}


def parse(s):
    s = s.strip()
    assert len(s) == 81, "puzzle string must be 81 chars, got %d" % len(s)
    return [0 if ch in ".0" else int(ch) for ch in s]


def fmt(grid):
    return "".join(str(v) if v else "." for v in grid)


# ── brute force ─────────────────────────────────────────────────────────────
def _search(grid, limit, rng=None, want=False):
    rows = [0] * 9
    cols = [0] * 9
    boxs = [0] * 9
    g = list(grid)
    empt = []
    for i, v in enumerate(g):
        if v:
            b = 1 << (v - 1)
            r, c, x = ROW_OF[i], COL_OF[i], BOX_OF[i]
            if (rows[r] | cols[c] | boxs[x]) & b:
                return 0, None
            rows[r] |= b
            cols[c] |= b
            boxs[x] |= b
        else:
            empt.append(i)
    n = len(empt)
    found = [0, None]

    def rec(k):
        if k == n:
            found[0] += 1
            if want and found[1] is None:
                found[1] = list(g)
            return found[0] >= limit
        best = k
        bm = 0
        bc = 10
        for j in range(k, n):
            i = empt[j]
            m = FULL & ~(rows[ROW_OF[i]] | cols[COL_OF[i]] | boxs[BOX_OF[i]])
            pc = POP[m]
            if pc < bc:
                bc, best, bm = pc, j, m
                if pc <= 1:
                    break
        if bc == 0:
            return False
        empt[k], empt[best] = empt[best], empt[k]
        i = empt[k]
        r, c, x = ROW_OF[i], COL_OF[i], BOX_OF[i]
        bits = BITS[bm]
        if rng is not None:
            bits = bits[:]
            rng.shuffle(bits)
        for b in bits:
            rows[r] |= b
            cols[c] |= b
            boxs[x] |= b
            g[i] = BIT2D[b]
            stop = rec(k + 1)
            rows[r] ^= b
            cols[c] ^= b
            boxs[x] ^= b
            g[i] = 0
            if stop:
                return True
        empt[k], empt[best] = empt[best], empt[k]
        return False

    rec(0)
    return found[0], found[1]


def count_solutions(grid, limit=2):
    return _search(grid, limit)[0]


def solve(grid):
    """First solution (or None)."""
    n, sol = _search(grid, 1, want=True)
    return sol if n else None


def random_full_grid(rng):
    n, sol = _search([0] * 81, 1, rng=rng, want=True)
    return sol


# ── technique grader ────────────────────────────────────────────────────────
class Stuck(Exception):
    pass


def _init(grid):
    g = list(grid)
    c = [0] * 81
    for i in range(81):
        if g[i]:
            continue
        m = FULL
        for p in PEERS[i]:
            v = g[p]
            if v:
                m &= ~(1 << (v - 1))
        c[i] = m
    # givens must not clash
    for u in UNITS:
        seen = 0
        for i in u:
            v = g[i]
            if v:
                b = 1 << (v - 1)
                if seen & b:
                    return None, None
                seen |= b
    return g, c


def _place(g, c, i, b):
    g[i] = BIT2D[b]
    c[i] = 0
    nb = ~b
    for p in PEERS[i]:
        c[p] &= nb


def _naked_single(g, c):
    n = 0
    for i in range(81):
        if not g[i]:
            m = c[i]
            if m == 0:
                raise Stuck("contradiction")
            if POP[m] == 1:
                _place(g, c, i, m)
                n += 1
    return n


def _hidden_single(g, c):
    n = 0
    for u in UNITS:
        once = twice = placed = 0
        for i in u:
            if g[i]:
                placed |= 1 << (g[i] - 1)
            else:
                m = c[i]
                twice |= once & m
                once |= m
        if (once | placed) != FULL:
            raise Stuck("digit has no home")
        single = once & ~twice & ~placed
        while single:
            b = single & -single
            single ^= b
            for i in u:
                if not g[i] and c[i] & b:
                    _place(g, c, i, b)
                    n += 1
                    break
    return n


def _elim(c, cells, mask):
    ch = False
    nm = ~mask
    for i in cells:
        if c[i] & mask:
            c[i] &= nm
            ch = True
    return ch


def _pointing(g, c):
    ch = False
    for b in range(9):
        box = BOXES[b]
        # three row segments / three col segments of the box
        for seg_of, lines in ((lambda k: k // 3, ROWS), (lambda k: k % 3, COLS)):
            seg = [0, 0, 0]
            for k in range(9):
                seg[seg_of(k)] |= c[box[k]]
            for s in range(3):
                only = seg[s] & ~(seg[(s + 1) % 3] | seg[(s + 2) % 3])
                if only:
                    cell0 = box[s * 3] if lines is ROWS else box[s]
                    line = ROWS[ROW_OF[cell0]] if lines is ROWS else COLS[COL_OF[cell0]]
                    others = [i for i in line if BOX_OF[i] != b]
                    if _elim(c, others, only):
                        ch = True
    return ch


def _claiming(g, c):
    ch = False
    for lines in (ROWS, COLS):
        for line in lines:
            seg = [0, 0, 0]
            for k in range(9):
                seg[k // 3] |= c[line[k]]
            for s in range(3):
                only = seg[s] & ~(seg[(s + 1) % 3] | seg[(s + 2) % 3])
                if only:
                    lset = set(line)
                    box = BOXES[BOX_OF[line[s * 3]]]
                    others = [i for i in box if i not in lset]
                    if _elim(c, others, only):
                        ch = True
    return ch


def _naked_subset(g, c, k):
    ch = False
    for u in UNITS:
        cells = [i for i in u if not g[i] and 2 <= POP[c[i]] <= k]
        if len(cells) < k:
            continue
        empties = [i for i in u if not g[i]]
        if len(empties) <= k:
            continue
        for combo in combinations(cells, k):
            m = 0
            for i in combo:
                m |= c[i]
            if POP[m] == k:
                rest = [i for i in empties if i not in combo]
                if _elim(c, rest, m):
                    ch = True
    return ch


def _hidden_subset(g, c, k):
    ch = False
    for u in UNITS:
        empties = [i for i in u if not g[i]]
        if len(empties) <= k:
            continue
        pos = {}
        for b in (1 << d for d in range(9)):
            pm = [i for i in empties if c[i] & b]
            if 2 <= len(pm) <= k:
                pos[b] = pm
        if len(pos) < k:
            continue
        for combo in combinations(list(pos), k):
            cells = set()
            for b in combo:
                cells.update(pos[b])
            if len(cells) == k:
                keep = 0
                for b in combo:
                    keep |= b
                for i in cells:
                    if c[i] & ~keep:
                        c[i] &= keep
                        ch = True
    return ch


def _fish(g, c, n):
    ch = False
    for d in range(9):
        b = 1 << d
        for base, cover, base_of, cover_of in ((ROWS, COLS, ROW_OF, COL_OF), (COLS, ROWS, COL_OF, ROW_OF)):
            lines = []
            for li, line in enumerate(base):
                pm = 0
                for i in line:
                    if c[i] & b:
                        pm |= 1 << cover_of[i]
                if 2 <= POP[pm] <= n:
                    lines.append((li, pm))
            if len(lines) < n:
                continue
            for combo in combinations(lines, n):
                um = 0
                for _, pm in combo:
                    um |= pm
                if POP[um] != n:
                    continue
                base_idx = {li for li, _ in combo}
                for ci in range(9):
                    if um >> ci & 1:
                        others = [i for i in cover[ci] if base_of[i] not in base_idx]
                        if _elim(c, others, b):
                            ch = True
    return ch


def _xy_wing(g, c):
    ch = False
    biv = [i for i in range(81) if not g[i] and POP[c[i]] == 2]
    bivset = set(biv)
    for p in biv:
        pm = c[p]
        wings = [a for a in PEERS[p] if a in bivset and POP[c[a] & pm] == 1]
        for a in wings:
            z = c[a] & ~pm
            if not z:
                continue
            want = (pm & ~c[a]) | z
            for b2 in wings:
                if b2 != a and c[b2] == want:
                    targets = [i for i in PEERSET[a] & PEERSET[b2] if i != p and not g[i]]
                    if _elim(c, targets, z):
                        ch = True
    return ch


def _xyz_wing(g, c):
    ch = False
    for p in range(81):
        if g[p] or POP[c[p]] != 3:
            continue
        pm = c[p]
        wings = [a for a in PEERS[p] if not g[a] and POP[c[a]] == 2 and (c[a] & ~pm) == 0]
        for a, b2 in combinations(wings, 2):
            if c[a] == c[b2] or (c[a] | c[b2]) != pm:
                continue
            z = c[a] & c[b2]
            targets = [i for i in PEERSET[p] & PEERSET[a] & PEERSET[b2] if not g[i]]
            if _elim(c, targets, z):
                ch = True
    return ch


TECHNIQUES = [
    ("naked_single", _naked_single),
    ("hidden_single", _hidden_single),
    ("pointing", _pointing),
    ("claiming", _claiming),
    ("naked_pair", lambda g, c: _naked_subset(g, c, 2)),
    ("hidden_pair", lambda g, c: _hidden_subset(g, c, 2)),
    ("naked_triple", lambda g, c: _naked_subset(g, c, 3)),
    ("hidden_triple", lambda g, c: _hidden_subset(g, c, 3)),
    ("x_wing", lambda g, c: _fish(g, c, 2)),
    ("naked_quad", lambda g, c: _naked_subset(g, c, 4)),
    ("hidden_quad", lambda g, c: _hidden_subset(g, c, 4)),
    ("xy_wing", _xy_wing),
    ("swordfish", lambda g, c: _fish(g, c, 3)),
    ("xyz_wing", _xyz_wing),
    ("jellyfish", lambda g, c: _fish(g, c, 4)),
]


class Grade:
    __slots__ = ("solved", "tier", "hardest", "counts", "score", "grid", "givens")

    def __repr__(self):
        return "Grade(solved=%s tier=%s hardest=%s score=%s givens=%s)" % (
            self.solved, self.tier, self.hardest, self.score, self.givens)


def grade(grid, max_tier=3):
    """Solve with techniques, simplest first. solved=False if the puzzle is
    invalid or needs a technique above max_tier (or beyond the catalogue)."""
    r = Grade()
    r.solved = False
    r.tier = -1
    r.hardest = None
    r.counts = {}
    r.score = 0
    r.givens = sum(1 for v in grid if v)
    g, c = _init(grid)
    r.grid = g
    if g is None:
        return r
    techs = [t for t in TECHNIQUES if TECH_TIER[t[0]] <= max_tier]
    try:
        while True:
            if all(g):
                break
            progressed = False
            for name, fn in techs:
                res = fn(g, c)
                if res:
                    r.counts[name] = r.counts.get(name, 0) + int(res)
                    key = (TECH_TIER[name], TECH_WEIGHT[name])
                    if r.hardest is None or key > (TECH_TIER[r.hardest], TECH_WEIGHT[r.hardest]):
                        r.hardest = name
                    r.tier = max(r.tier, TECH_TIER[name])
                    progressed = True
                    break
            if not progressed:
                return r
    except Stuck:
        return r
    # verify the filled grid is a valid solution
    for u in UNITS:
        if sorted(g[i] for i in u) != list(range(1, 10)):
            return r
    r.solved = True
    r.tier = max(r.tier, 0)
    r.score = sum(TECH_WEIGHT[k] * v for k, v in r.counts.items()) + (81 - r.givens)
    return r


# ── generator ───────────────────────────────────────────────────────────────
def make_puzzle(rng, band, floor_givens, symmetric=True):
    """Dig a random full grid: remove clue pairs (180° symmetric) while the
    puzzle stays technique-solvable at <= band, down to floor_givens.
    Returns (puzzle, solution, grade) — caller checks grade.tier == band."""
    sol = random_full_grid(rng)
    puz = list(sol)
    if symmetric:
        groups = [(i, 80 - i) if i != 40 else (40,) for i in range(41)]
    else:
        groups = [(i,) for i in range(81)]
    rng.shuffle(groups)
    givens = 81
    for grp in groups:
        if givens - len(grp) < floor_givens:
            continue
        for i in grp:
            puz[i] = 0
        r = grade(puz, max_tier=band)
        if r.solved:
            givens -= len(grp)
        else:
            for i in grp:
                puz[i] = sol[i]
    return puz, sol, grade(puz)


# ── isomorphic transforms (daily / endless variety) ─────────────────────────
def transform(grid, perm_digits, row_order, col_order, transpose):
    """Validity-, uniqueness- and technique-grade-preserving relabel/shuffle."""
    out = [0] * 81
    for r in range(9):
        for cc in range(9):
            sr, sc = row_order[r], col_order[cc]
            if transpose:
                sr, sc = sc, sr
            v = grid[sr * 9 + sc]
            out[r * 9 + cc] = perm_digits[v - 1] if v else 0
    return out
