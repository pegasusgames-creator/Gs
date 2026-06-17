#!/usr/bin/env python3
"""gen_levels.py — PipeConnect level generator (regenerates the LEVELS array
for android/app/src/main/assets/game.html).

Each level is solvable WITH full coverage BY CONSTRUCTION: a Hamiltonian path
on the NxN grid (serpentine + seeded backbite moves) is cut into contiguous
segments, and each segment's two ends become a colour's dot pair. The path
itself is a valid full-board solution, so the level can always be completed
(the win condition only requires the pairs be connected). The generator
records that solution and validates it directly (instant, rigorous) and
rejects any level with grid-adjacent same-colour dots (a trivial one-tap
connection).

This replaces the original hand-authored levels 1-122, which a 2026-06-16
audit found almost entirely UNSOLVABLE. check_pipeconnect_solvable.py is the
permanent gate. Deterministic via fixed seeds.

    python3 PipeConnect/test/gen_levels.py        # prints the LEVELS lines

The size/pair schedule lives in SCHEDULE below.
"""
import json
import sys
from collections import Counter

COLORS = ['red','blue','green','yellow','purple','orange','pink','teal']

def make_rng(a):
    state = a & 0xFFFFFFFF
    def imul(x, y): return ((x & 0xFFFFFFFF) * (y & 0xFFFFFFFF)) & 0xFFFFFFFF
    def rnd():
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = state
        t = imul(t ^ (t >> 15), 1 | t)
        t = (t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF ^ t
        t &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rnd

def serpentine(N):
    p = []
    for r in range(N):
        for c in (range(N) if r % 2 == 0 else range(N-1, -1, -1)):
            p.append(r*N + c)
    return p

def neighbors_idx(i, N):
    r, c = divmod(i, N); out = []
    if r > 0: out.append(i-N)
    if r < N-1: out.append(i+N)
    if c > 0: out.append(i-1)
    if c < N-1: out.append(i+1)
    return out

def backbite(path, N, rnd, steps):
    p = list(path); idx = {v: i for i, v in enumerate(p)}
    for _ in range(steps):
        if rnd() >= 0.5:
            p.reverse(); idx = {v: i for i, v in enumerate(p)}
        head = p[0]
        nbs = [n for n in neighbors_idx(head, N) if idx.get(n, -1) > 1]
        if not nbs: continue
        n = nbs[int(rnd()*len(nbs))]; j = idx[n]
        p = p[:j][::-1] + p[j:]
        idx = {v: i for i, v in enumerate(p)}
    return p

def is_hamiltonian(path, N):
    if len(path) != N*N or len(set(path)) != N*N: return False
    for a, b in zip(path, path[1:]):
        ra, ca = divmod(a, N); rb, cb = divmod(b, N)
        if abs(ra-rb)+abs(ca-cb) != 1: return False
    return True

def gen(seed, N, pairs):
    rnd = make_rng(seed)
    total = N*N
    if pairs*3 > total: return None
    for _ in range(60):
        path = backbite(serpentine(N), N, rnd, N*N*8)
        if not is_hamiltonian(path, N): return None  # sanity
        lens = None
        for _a in range(200):
            cuts = set()
            while len(cuts) < pairs-1: cuts.add(3 + int(rnd()*(total-3)))
            cl = sorted(cuts); ls = []; prev = 0
            for c in cl: ls.append(c-prev); prev = c
            ls.append(total-prev)
            if all(l >= 3 for l in ls): lens = ls; break
        if not lens: continue
        dots = []; segs = []; at = 0
        for si, ln in enumerate(lens):
            seg = path[at:at+ln]; at += ln; segs.append((COLORS[si], seg))
            a, b = seg[0], seg[-1]
            dots.append([a//N, a%N, COLORS[si]]); dots.append([b//N, b%N, COLORS[si]])
        cells = {(d[0], d[1]) for d in dots}
        if len(cells) != len(dots): continue
        # reject trivial puzzles: no same-color pair may be grid-adjacent
        adj = False
        bycol = {}
        for r, c, col in dots: bycol.setdefault(col, []).append((r, c))
        for (a, b) in bycol.values():
            if abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1: adj = True; break
        if adj: continue
        # validate the recorded solution directly
        if not validate(N, dots, segs): continue
        # `solution` keeps the full-coverage witness path per colour as [r,c]
        # cells (used by the screenshot pipeline to render a solved board);
        # the level itself still ships as {size, dots} only.
        solution = {col: [[i // N, i % N] for i in seg] for col, seg in segs}
        return {'size': N, 'dots': dots, 'solution': solution}
    return None

def validate(N, dots, segs):
    cover = [[None]*N for _ in range(N)]
    colors = {}
    for r, c, col in dots: colors.setdefault(col, []).append((r, c))
    for col, seg in segs:
        # contiguous simple path
        prev = None
        for i in seg:
            r, c = divmod(i, N)
            if cover[r][c] is not None: return False  # overlap
            cover[r][c] = col
            if prev is not None:
                pr, pc = prev
                if abs(pr-r)+abs(pc-c) != 1: return False
            prev = (r, c)
        ends = {(seg[0]//N, seg[0]%N), (seg[-1]//N, seg[-1]%N)}
        if ends != set(colors[col]): return False
    # full coverage
    for r in range(N):
        for c in range(N):
            if cover[r][c] is None: return False
    return True

SCHEDULE = [
    (20, 5, (3, 4)),    # 1-20    5x5
    (30, 6, (4, 5)),    # 21-50   6x6
    (30, 7, (4, 6)),    # 51-80   7x7
    (30, 8, (5, 7)),    # 81-110  8x8
    (12, 9, (6, 8)),    # 111-122 9x9
]
out = []; seed = 12345
for count, N, (pmin, pmax) in SCHEDULE:
    made = 0
    while made < count:
        if seed > 3_000_000: raise RuntimeError(f"seed exhausted {N}x{N}")
        pairs = pmin + int(make_rng(seed)()*(pmax-pmin+1))
        L = gen(seed, N, pairs); seed += 1
        if L: out.append(L); made += 1

# --emit-solutions: dump the full-coverage witness solution for every level so
# the screenshot pipeline can render a solved (or mostly-solved) board. Levels
# are 1-indexed to match the in-app "Level N". Does NOT write the levels file.
if "--emit-solutions" in sys.argv:
    sols = [{"level": i + 1, "size": L["size"], "dots": L["dots"],
             "solution": L["solution"]} for i, L in enumerate(out)]
    with open("/tmp/pipeconnect_solutions.json", "w") as fh:
        json.dump(sols, fh)
    # surface the richest candidates: bigger boards with the most colours.
    ranked = sorted(sols, key=lambda s: (s["size"], len(s["solution"])), reverse=True)
    print(f"emitted {len(sols)} solutions → /tmp/pipeconnect_solutions.json")
    print("richest candidates (level / size / colours):")
    for s in ranked[:14]:
        print(f"  L{s['level']:>3}  {s['size']}x{s['size']}  {len(s['solution'])} colours")
    sys.exit(0)

print(f"generated {len(out)} levels; sizes:", dict(Counter(L['size'] for L in out)))
print("pairs per size:", {s: sorted({len(set((d[0],d[1]) for d in L['dots']))//2 for L in out if L['size']==s}) for s in (5,6,7,8,9)})
lines = []; cur = 0; n = 1
for L in out:
    if L['size'] != cur:
        cur = L['size']; lines.append(f"// {n}-{n+ -1}: placeholder")
        lines[-1] = f"// {n}+: {cur}x{cur}"
    dots = json.dumps(L['dots']).replace('"', "'").replace(' ', '')
    lines.append(f"{{size:{L['size']},dots:{dots}}},")
    n += 1
open('/tmp/new_levels_1_122.txt', 'w').write('\n'.join(lines) + '\n')
print("wrote /tmp/new_levels_1_122.txt")
