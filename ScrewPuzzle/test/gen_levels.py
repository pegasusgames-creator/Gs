#!/usr/bin/env python3
"""gen_levels.py — Screw Puzzle campaign generator (500 solver-verified levels).

The game (ScrewPuzzle/android/app/src/main/assets/game.html) ships its
campaign as `const LEVELS = [ "<level string>", ... ]`. This script builds
that array deterministically from a fixed seed and splices it into game.html
between the `/*LEVELS-BEGIN*/` and `/*LEVELS-END*/` markers.

Rules (identical in game.html, this file and scripts/check_screw_solvable.py):

  * The board is a C x R grid of hole positions. Plates are rectangles of
    cells stacked bottom (z = 0) to top. Every screw sits in one cell of its
    plate; no two screws share a cell.
  * A screw can be tapped only when no plate ABOVE its plate still covers its
    cell. A plate falls (is removed) once its last screw is out.
  * Two colour boxes are open at a time (3 holes each), fed in a fixed queue
    order. A tapped screw goes into the fullest open box of its colour; if
    none has room it goes into the holding tray (K holes). A full box ships
    out, the next queued box slides in and pulls matching screws from the
    tray. A tap with no box room and a full tray is impossible; a board
    with no possible tap is stuck (lost).
  * Because a box only ever takes its own colour, the whole box/tray state
    is a pure function of how many screws of each colour are out — so a game
    state is just the set of removed screws (see `tray_after`).

Level string:  "<C><R><K>|<plate>.<plate>...|<queue>"
  plate  = x y w h (base-36 digits) followed by one "x y colour" triple per
           screw (absolute cell coordinates, colour 0-7)
  queue  = one colour digit per box, in arrival order
No commas or brackets, so the LEVELS literal stays one string per level.

Usage:
    python3 ScrewPuzzle/test/gen_levels.py            # regenerate + splice
    python3 ScrewPuzzle/test/gen_levels.py --dry-run  # stats only
"""
import argparse
import random
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
GAME = BASE / "ScrewPuzzle/android/app/src/main/assets/game.html"
SLOTS = 2          # open colour boxes
TRAY = 5           # holding-tray holes (the +1 Slot booster adds more in-game)
BOX = 3            # screws per box
N_LEVELS = 500
SEED = 20261012
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"


# ───────────────────────── model ─────────────────────────
class Level:
    def __init__(self, cols, rows, k, plates, queue):
        self.cols, self.rows, self.k = cols, rows, k
        self.plates = plates            # [(x, y, w, h, [screw ids])]
        self.queue = queue              # [colour]
        self.screws = []                # [(x, y, colour, plate)]
        self._index()

    def _index(self):
        self.screws = []
        plates = []
        for pi, (x, y, w, h, sc) in enumerate(self.plates):
            ids = []
            for (sx, sy, c) in sc:
                ids.append(len(self.screws))
                self.screws.append((sx, sy, c, pi))
            plates.append((x, y, w, h, ids))
        self.pl = plates
        n = len(self.screws)
        self.n = n
        self.all = (1 << n) - 1
        self.plate_mask = []
        for (_, _, _, _, ids) in plates:
            m = 0
            for i in ids:
                m |= 1 << i
            self.plate_mask.append(m)
        # cover[i] = union of screw masks of every plate above screw i's plate
        # that covers its cell; screw i is free once all of those are removed.
        self.cover = []
        for (sx, sy, c, p) in self.screws:
            m = 0
            for q in range(p + 1, len(plates)):
                x, y, w, h, _ = plates[q]
                if x <= sx < x + w and y <= sy < y + h:
                    m |= self.plate_mask[q]
            self.cover.append(m)
        self.colour = [s[2] for s in self.screws]
        self.ncol = max(self.colour + self.queue) + 1 if self.colour else 0
        self.prefix = prefix_counts(self.queue, self.ncol)

    def encode(self):
        s = B36[self.cols] + B36[self.rows] + B36[self.k] + "|"
        parts = []
        for (x, y, w, h, sc) in self.plates:
            t = B36[x] + B36[y] + B36[w] + B36[h]
            for (sx, sy, c) in sc:
                t += B36[sx] + B36[sy] + str(c)
            parts.append(t)
        return s + ".".join(parts) + "|" + "".join(str(c) for c in self.queue)


def decode(s):
    head, ps, q = s.split("|")
    cols, rows, k = (int(ch, 36) for ch in head)
    plates = []
    for p in ps.split("."):
        x, y, w, h = (int(ch, 36) for ch in p[:4])
        sc = []
        for j in range(4, len(p), 3):
            sc.append((int(p[j], 36), int(p[j + 1], 36), int(p[j + 2])))
        plates.append((x, y, w, h, sc))
    return Level(cols, rows, k, plates, [int(ch) for ch in q])


def tray_after(counts, queue, prefix=None):
    """(tray size, boxes entered) for per-colour removed counts.

    Boxes enter in queue order; SLOTS are open at once and each full box is
    replaced by the next. A colour's screws sit in its entered boxes up to
    their capacity, the overflow sits in the tray — so the state depends
    only on the counts, never on the order (checked against an explicit
    step-by-step simulation in test/sim_check)."""
    Q = len(queue)
    if prefix is None:
        prefix = prefix_counts(queue, len(counts))
    e = min(Q, SLOTS)
    while True:
        ent = prefix[e]
        closed = 0
        for c in range(len(counts)):
            v = counts[c]
            cap = BOX * ent[c]
            closed += (v if v < cap else cap) // BOX
        ne = min(Q, SLOTS + closed)
        if ne == e:
            break
        e = ne
    ent = prefix[e]
    tray = 0
    for c in range(len(counts)):
        d = counts[c] - BOX * ent[c]
        if d > 0:
            tray += d
    return tray, e


def prefix_counts(queue, ncol):
    """prefix[e][c] = boxes of colour c among the first e queued boxes."""
    out = [[0] * ncol]
    for c in queue:
        row = out[-1][:]
        row[c] += 1
        out.append(row)
    return out


def counts_of(L, removed):
    cnt = [0] * L.ncol
    i = 0
    m = removed
    while m:
        if m & 1:
            cnt[L.colour[i]] += 1
        m >>= 1
        i += 1
    return cnt


def legal_moves(L, removed, counts, k):
    """[(screw, goes_to_box)] for every tappable screw."""
    tray0, _ = tray_after(counts, L.queue, L.prefix)
    out = []
    for i in range(L.n):
        b = 1 << i
        if removed & b:
            continue
        cv = L.cover[i]
        if removed & cv != cv:
            continue
        c = L.colour[i]
        counts[c] += 1
        t, _ = tray_after(counts, L.queue, L.prefix)
        counts[c] -= 1
        if t <= k:
            out.append((i, t <= tray0))
    return out


def solve(L, k=None, budget=400000):
    """Depth-first search over removed-sets. Returns a list of screw ids
    (a full clearing order) or None. Raises TimeoutError past `budget`."""
    k = L.k if k is None else k
    dead = set()
    nodes = [0]
    path = []
    counts = [0] * L.ncol

    def dfs(removed):
        if removed == L.all:
            return True
        if removed in dead:
            return False
        nodes[0] += 1
        if nodes[0] > budget:
            raise TimeoutError
        mv = legal_moves(L, removed, counts, k)
        # box moves first; then screws that drop a plate; then the colour
        # whose box arrives soonest
        def key(m):
            i, box = m
            p = L.screws[i][3]
            drops = (L.plate_mask[p] & ~removed) == (1 << i)
            return (0 if box else 1, 0 if drops else 1, i)
        mv.sort(key=key)
        for i, _ in mv:
            c = L.colour[i]
            counts[c] += 1
            path.append(i)
            if dfs(removed | (1 << i)):
                return True
            path.pop()
            counts[c] -= 1
        dead.add(removed)
        return False

    return list(path) if dfs(0) else None


def playout(L, rnd, k=None, greedy=True):
    """One simulated casual play: random taps, preferring box moves."""
    k = L.k if k is None else k
    removed = 0
    counts = [0] * L.ncol
    while removed != L.all:
        mv = legal_moves(L, removed, counts, k)
        if not mv:
            return False
        if greedy:
            box = [m for m in mv if m[1]]
            if box:
                mv = box
        i, _ = rnd.choice(mv)
        counts[L.colour[i]] += 1
        removed |= 1 << i
    return True


# ───────────────────────── layout generation ─────────────────────────
SHAPES_BAR = [(2, 1), (3, 1), (1, 2), (1, 3), (4, 1), (1, 4)]
SHAPES_PANEL = [(2, 2), (2, 3), (3, 2), (3, 3)]


def screw_spots(x, y, w, h):
    """Candidate screw cells on a plate: ends of bars, corners of panels."""
    if w == 1 or h == 1:
        cells = [(x + i, y + j) for i in range(w) for j in range(h)]
        ends = [cells[0], cells[-1]]
        mid = cells[1:-1]
        return ends, mid
    corners = [(x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)]
    inner = [(x + i, y + j) for i in range(w) for j in range(h) if (x + i, y + j) not in corners]
    return corners, inner


def build_layout(rnd, cols, rows, target, panel_bias, overlap_bias):
    """Stack plates until exactly `target` screws exist. Returns list of
    (x, y, w, h, [(sx, sy)]) bottom→top, or None."""
    plates = []
    taken = set()            # cells holding a screw
    depth = {}               # cell -> number of plates covering it
    total = 0
    tries = 0
    while total < target and tries < 400:
        tries += 1
        shapes = SHAPES_PANEL if rnd.random() < panel_bias else SHAPES_BAR
        w, h = rnd.choice(shapes)
        if w > cols or h > rows:
            continue
        cands = []
        for x in range(cols - w + 1):
            for y in range(rows - h + 1):
                cells = [(x + i, y + j) for i in range(w) for j in range(h)]
                if max(depth.get(c, 0) for c in cells) >= 4:
                    continue
                prim, sec = screw_spots(x, y, w, h)
                free = [c for c in prim if c not in taken]
                if not free:
                    continue
                covered = sum(1 for c in cells if c in taken)
                score = 1.0 + overlap_bias * covered
                if not plates:
                    score = 1.0
                cands.append((score, x, y, prim, sec))
        if not cands:
            continue
        tot = sum(c[0] for c in cands)
        r = rnd.random() * tot
        for sc, x, y, prim, sec in cands:
            r -= sc
            if r <= 0:
                break
        free = [c for c in prim if c not in taken]
        rnd.shuffle(free)
        if w == 1 or h == 1:
            n = 2 if (len(free) >= 2 and rnd.random() < 0.8) else 1
        else:
            n = min(len(free), rnd.choice([2, 2, 3, 4]))
        spots = free[:n]
        if (w >= 3 or h >= 3) and rnd.random() < 0.2:
            extra = [c for c in sec if c not in taken]
            if extra and (w == 1 or h == 1):
                spots.append(rnd.choice(extra))
        if total + len(spots) > target:
            spots = spots[: target - total]
        if not spots:
            continue
        for c in spots:
            taken.add(c)
        for i in range(w):
            for j in range(h):
                depth[(x + i, y + j)] = depth.get((x + i, y + j), 0) + 1
        plates.append((x, y, w, h, spots))
        total += len(spots)
    if total != target:
        return None
    return plates


def make_level(rnd, spec):
    cols, rows, k = spec["cols"], spec["rows"], TRAY
    nscrew = spec["screws"]
    ncol = spec["colours"]
    lay = build_layout(rnd, cols, rows, nscrew, spec["panel"], spec["overlap"])
    if not lay:
        return None
    nbox = nscrew // BOX
    if ncol > nbox:
        ncol = nbox
    boxes = list(range(ncol))
    while len(boxes) < nbox:
        boxes.append(rnd.randrange(ncol))
    # colour palette subset: random distinct colour ids out of 8
    pal = rnd.sample(range(8), ncol)
    colours = []
    for b in boxes:
        colours += [pal[b]] * BOX
    rnd.shuffle(colours)
    queue = [pal[b] for b in boxes]
    rnd.shuffle(queue)
    if len(queue) > 1 and queue[0] == queue[1] and len(set(queue)) > 1:
        j = next(i for i in range(2, len(queue)) if queue[i] != queue[0])
        queue[1], queue[j] = queue[j], queue[1]
    it = iter(colours)
    plates = [(x, y, w, h, [(sx, sy, next(it)) for (sx, sy) in sp]) for (x, y, w, h, sp) in lay]
    # compact the colour ids to 0..n-1 in order of first queue appearance? No:
    # keep palette ids (0-7) so themes colour them consistently.
    return Level(cols, rows, k, plates, queue)


# ───────────────────────── campaign schedule ─────────────────────────
def spec_for(i):
    """Difficulty spec for 0-based level i: intro (1-3), then six tiers by
    level range with a sawtooth — every 10th level is a breather (one tier
    down) and every level ending in 9 is a tough one (one tier up)."""
    if i == 0:
        return dict(cols=3, rows=4, screws=6, colours=2, panel=0.0, overlap=0.5,
                    band="intro", pmax=1.01, mintray=(0, 1))
    if i == 1:
        return dict(cols=4, rows=4, screws=9, colours=3, panel=0.3, overlap=1.0,
                    band="intro", pmax=1.01, mintray=(0, 2))
    if i == 2:
        return dict(cols=4, rows=5, screws=9, colours=3, panel=0.3, overlap=1.5,
                    band="intro", pmax=1.01, mintray=(1, 2))
    edges = [40, 110, 200, 300, 400, 500]          # last level (1-based) of each tier
    tier = next(t for t, e in enumerate(edges) if i < e)
    phase = (i + 1) % 10
    tier = min(5, max(0, tier + (-1 if phase == 1 else (1 if phase == 0 else 0))))
    tiers = [
        # cols rows screws    colours panel overlap pmax  mintray  band
        (4, 5, (9, 12),  (3, 4), 0.35, 1.5, 1.01, (1, 3), "easy"),
        (4, 6, (12, 15), (4, 5), 0.35, 2.0, 0.95, (2, 3), "easy"),
        (5, 6, (15, 21), (4, 6), 0.40, 2.5, 0.85, (2, 4), "medium"),
        (5, 7, (18, 24), (5, 6), 0.40, 3.0, 0.70, (3, 4), "medium"),
        (6, 7, (24, 27), (6, 7), 0.45, 3.0, 0.55, (3, 5), "hard"),
        (6, 8, (27, 33), (6, 8), 0.45, 3.5, 0.40, (4, 5), "expert"),
    ]
    cols, rows, scr, cl, panel, ov, pmax, mt, band = tiers[tier]
    return dict(cols=cols, rows=rows, screws=scr, colours=cl, panel=panel, overlap=ov,
                band=band, pmax=pmax, mintray=mt)


def gen_one(rnd, i, budget=80000, playouts=120):
    """First candidate for level i that (a) clears with a tray of mintray[1]
    holes, (b) provably does NOT clear with mintray[0]-1 holes (so the tray
    really matters), and (c) a casual 'box-first, otherwise random' player
    wins at most pmax of the time (but not almost never)."""
    sp = spec_for(i)
    lo, hi = sp["mintray"]
    for attempt in range(6000):
        s = dict(sp)
        lo_s, hi_s = s["screws"]
        s["screws"] = rnd.choice([v for v in range(lo_s, hi_s + 1) if v % BOX == 0])
        s["colours"] = rnd.randint(*s["colours"])
        L = make_level(rnd, s)
        if L is None:
            continue
        try:
            if solve(L, hi, budget) is None:
                continue
            if lo > 0 and solve(L, lo - 1, budget) is not None:
                continue
        except TimeoutError:
            continue
        prnd = random.Random(i * 7919 + attempt)
        wins = sum(playout(L, prnd) for _ in range(playouts))
        p = wins / playouts
        if p > sp["pmax"]:
            continue
        if i >= 3 and p < 0.05:
            continue                       # near-impossible for humans
        return L, dict(band=sp["band"], mintray=f"{lo}-{hi}", p=round(p, 2), screws=L.n, attempt=attempt)
    raise RuntimeError(f"level {i + 1}: no candidate met spec {sp}")


def splice(levels, stats):
    html = GAME.read_text(encoding="utf-8")
    body = ",\n".join('"%s"' % s for s in levels)
    block = ("/*LEVELS-BEGIN*/\n// 500 levels generated by ScrewPuzzle/test/gen_levels.py (seed %d) and\n"
             "// re-verified by scripts/check_screw_solvable.py. Do not hand-edit.\n"
             "const LEVELS = [\n%s\n];\n/*LEVELS-END*/" % (SEED, body))
    new, n = re.subn(r"/\*LEVELS-BEGIN\*/.*?/\*LEVELS-END\*/", lambda m: block, html, flags=re.S)
    if n != 1:
        raise SystemExit("game.html: LEVELS markers not found")
    GAME.write_text(new, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--count", type=int, default=N_LEVELS)
    a = ap.parse_args()
    rnd = random.Random(SEED)
    levels, stats = [], []
    for i in range(a.count):
        L, st = gen_one(rnd, i)
        levels.append(L.encode())
        stats.append(st)
        if i % 25 == 0 or i == a.count - 1:
            print(f"  L{i + 1:>3} {st}", flush=True)
    bands = {}
    for st in stats:
        bands.setdefault(st["band"], []).append(st)
    for b, v in bands.items():
        print(f"  {b:7s} n={len(v):3d} avg p={sum(x['p'] for x in v) / len(v):.2f} "
              f"avg screws={sum(x['screws'] for x in v) / len(v):.1f}")
    if len(set(levels)) != len(levels):
        raise SystemExit("duplicate levels generated")
    if not a.dry_run:
        splice(levels, stats)
        print(f"wrote {len(levels)} levels into {GAME.relative_to(BASE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
