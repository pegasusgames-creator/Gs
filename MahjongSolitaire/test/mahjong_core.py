#!/usr/bin/env python3
"""mahjong_core.py — geometry, layout families, reverse-removal dealer and a
solver for Mahjong Solitaire's shipped campaign.

Coordinates are HALF-tile units: a tile at (x, y, z) covers the half-cells
x..x+1 by y..y+1 on layer z. Two tiles on one layer touch sideways when
dx == ±2 and |dy| < 2; a tile is covered when any tile on layer z+1 has
|dx| < 2 and |dy| < 2. A tile is FREE when it is not covered and at least
one of its left / right sides is open — the classic rule.

Faces (42): 0-8 pebbles 1-9, 9-17 bamboo 1-9, 18-26 numerals 1-9,
27-30 winds E S W N, 31-33 dragons (red, green, white), 34-37 flowers,
38-41 seasons. Faces 0-33 match only themselves; any flower matches any
flower and any season matches any season (match keys 34 / 38).

Dealing is solvable BY CONSTRUCTION: positions are removed from the full
layout two free tiles at a time (a legal forward play), and each removed
pair is then given one matching pair of faces. The forward solution is that
removal order. The solver below re-proves every shipped deal independently.

Layout families live in layouts.py. Stdlib only. Used by test/gen_levels.py;
scripts/check_mahjong_solvable.py carries its own copy of the rules so the
gate is independent of this file.
"""
import random

ALPHA36 = "0123456789abcdefghijklmnopqrstuvwxyz"
FACE_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEF"   # 42 faces
N_REGULAR = 34
FLOWERS = (34, 35, 36, 37)
SEASONS = (38, 39, 40, 41)
MAX_X = 16          # 9 tiles wide (portrait phone)
MAX_Y = 22          # 12 tiles tall


def match_key(face):
    if face >= 38:
        return 38
    if face >= 34:
        return 34
    return face


# ─────────────────────────── geometry ───────────────────────────
class Geo:
    """Precomputed blocking relations for one layout (list of (x,y,z))."""

    def __init__(self, tiles):
        self.tiles = list(tiles)
        n = len(self.tiles)
        self.n = n
        self.cover = [[] for _ in range(n)]   # tiles above that overlap
        self.left = [[] for _ in range(n)]
        self.right = [[] for _ in range(n)]
        for i, (x, y, z) in enumerate(self.tiles):
            for j, (a, b, c) in enumerate(self.tiles):
                if i == j:
                    continue
                if c == z + 1 and abs(a - x) < 2 and abs(b - y) < 2:
                    self.cover[i].append(j)
                elif c == z and abs(b - y) < 2:
                    if a - x == -2:
                        self.left[i].append(j)
                    elif a - x == 2:
                        self.right[i].append(j)
        self.cover_m = [sum(1 << j for j in l) for l in self.cover]
        self.left_m = [sum(1 << j for j in l) for l in self.left]
        self.right_m = [sum(1 << j for j in l) for l in self.right]

    def is_free(self, i, mask):
        if self.cover_m[i] & mask:
            return False
        return not (self.left_m[i] & mask) or not (self.right_m[i] & mask)

    def free_list(self, mask):
        out = []
        m = mask
        while m:
            low = m & -m
            i = low.bit_length() - 1
            if self.is_free(i, mask):
                out.append(i)
            m ^= low
        return out


def validate_layout(tiles):
    """Return an error string or None. No overlap on a layer, every upper
    tile fully supported, bounds, even count."""
    occ = {}
    for (x, y, z) in tiles:
        if x < 0 or y < 0 or z < 0 or x > MAX_X or y > MAX_Y:
            return "out of bounds %r" % ((x, y, z),)
        for dx in (0, 1):
            for dy in (0, 1):
                k = (x + dx, y + dy, z)
                if k in occ:
                    return "overlap at %r" % (k,)
                occ[k] = 1
    for (x, y, z) in tiles:
        if z == 0:
            continue
        for dx in (0, 1):
            for dy in (0, 1):
                if (x + dx, y + dy, z - 1) not in occ:
                    return "unsupported tile %r" % ((x, y, z),)
    if len(tiles) % 2:
        return "odd tile count %d" % len(tiles)
    if len(set(tiles)) != len(tiles):
        return "duplicate tile"
    return None


def normalize(tiles):
    tiles = set(tiles)
    mx = min(t[0] for t in tiles)
    my = min(t[1] for t in tiles)
    return sorted(((x - mx, y - my, z) for (x, y, z) in tiles), key=lambda t: (t[2], t[1], t[0]))


def encode_layout(tiles):
    return "".join(ALPHA36[x] + ALPHA36[y] + ALPHA36[z] for (x, y, z) in tiles)


def decode_layout(s):
    return [(ALPHA36.index(s[i]), ALPHA36.index(s[i + 1]), ALPHA36.index(s[i + 2]))
            for i in range(0, len(s), 3)]


# ─────────────────────────── dealing ───────────────────────────
def removal_order(geo, rng, tries=400):
    """Remove two free tiles at a time until the layout is empty. Returns a
    list of (i, j) pairs (a forward solution) or None."""
    n = geo.n
    full = (1 << n) - 1
    tiles = geo.tiles
    for _ in range(tries):
        mask = full
        order = []
        ok = True
        while mask:
            free = geo.free_list(mask)
            if len(free) < 2:
                ok = False
                break
            # weight: higher tiles and tiles that block others go first
            def weight(i):
                x, y, z = tiles[i]
                blocks = 0
                for j in range(n):
                    if (mask >> j) & 1 and (geo.cover_m[j] >> i) & 1:
                        blocks += 1
                return 1.0 + 2.5 * z + 1.5 * blocks + rng.random()
            free.sort(key=weight, reverse=True)
            top = free[:max(2, min(len(free), 6))]
            a = rng.choice(top)
            rest = [f for f in free if f != a]
            # second tile: prefer one far away from the first (harder look)
            ax, ay, _ = tiles[a]
            rest.sort(key=lambda j: -(abs(tiles[j][0] - ax) + abs(tiles[j][1] - ay)) - 6 * rng.random())
            b = rest[0] if rng.random() < 0.6 else rng.choice(rest)
            order.append((a, b))
            mask &= ~((1 << a) | (1 << b))
        if ok:
            return order
    return None


def pair_tokens(npairs, dup_frac, rng, allow_bonus):
    """Return a list of npairs match-group tokens (kinds). A kind used twice
    contributes two pairs (all four copies)."""
    kinds = list(range(N_REGULAR)) + ([34, 38] if allow_bonus else [])
    max_kinds = len(kinds)
    d = int(round(npairs * dup_frac / 2.0))
    d = max(d, npairs - max_kinds)
    d = min(d, npairs // 2)
    u = npairs - 2 * d
    if u + d > max_kinds:
        raise ValueError("too many pairs for the tile set")
    chosen = rng.sample(kinds, u + d)
    tokens = []
    for k in chosen[:d]:
        tokens += [k, k]
    for k in chosen[d:]:
        tokens.append(k)
    rng.shuffle(tokens)
    return tokens


def deal(geo, rng, dup_frac, allow_bonus):
    order = removal_order(geo, rng)
    if not order:
        return None
    tokens = pair_tokens(len(order), dup_frac, rng, allow_bonus)
    faces = [None] * geo.n
    flower_pool = list(FLOWERS)
    season_pool = list(SEASONS)
    rng.shuffle(flower_pool)
    rng.shuffle(season_pool)
    for (a, b), k in zip(order, tokens):
        if k == 34:
            fa, fb = flower_pool.pop(), flower_pool.pop()
        elif k == 38:
            fa, fb = season_pool.pop(), season_pool.pop()
        else:
            fa = fb = k
        faces[a], faces[b] = fa, fb
    return faces, order


def encode_faces(faces):
    return "".join(FACE_CHARS[f] for f in faces)


def decode_faces(s):
    return [FACE_CHARS.index(c) for c in s]


# ─────────────────────────── solver ───────────────────────────
def solve(geo, faces, node_limit=300000):
    """DFS with memo over the set of remaining tiles. Returns (solution
    list of pairs, nodes) or (None, nodes). solution None + nodes>=limit
    means "undecided"."""
    n = geo.n
    keys = [match_key(f) for f in faces]
    full = (1 << n) - 1
    seen = set()
    nodes = [0]
    sol = []

    def moves(mask):
        free = geo.free_list(mask)
        by = {}
        for i in free:
            by.setdefault(keys[i], []).append(i)
        groups = [g for g in by.values() if len(g) >= 2]
        return groups

    def remaining_of_kind(mask, k):
        c = 0
        m = mask
        while m:
            low = m & -m
            i = low.bit_length() - 1
            if keys[i] == k:
                c += 1
            m ^= low
        return c

    def rec(mask):
        if mask == 0:
            return True
        if mask in seen:
            return False
        nodes[0] += 1
        if nodes[0] > node_limit:
            return False
        groups = moves(mask)
        if not groups:
            seen.add(mask)
            return False
        # safe moves: every remaining tile of a kind is free (2 or 4) → take all
        for g in groups:
            k = keys[g[0]]
            if len(g) in (2, 4) and remaining_of_kind(mask, k) == len(g):
                pairs = [(g[0], g[1])] + ([(g[2], g[3])] if len(g) == 4 else [])
                m2 = mask
                for (a, b) in pairs:
                    m2 &= ~((1 << a) | (1 << b))
                sol.extend(pairs)
                if rec(m2):
                    return True
                for _ in pairs:
                    sol.pop()
                seen.add(mask)
                return False
        cand = []
        for g in groups:
            for x in range(len(g)):
                for y in range(x + 1, len(g)):
                    a, b = g[x], g[y]
                    m2 = mask & ~((1 << a) | (1 << b))
                    # heuristic: prefer moves that free more tiles, higher z
                    gain = len(geo.free_list(m2)) - 0
                    cand.append((-(gain + geo.tiles[a][2] + geo.tiles[b][2]), a, b, m2))
        cand.sort()
        for _, a, b, m2 in cand:
            sol.append((a, b))
            if rec(m2):
                return True
            sol.pop()
            if nodes[0] > node_limit:
                return False
        seen.add(mask)
        return False

    import sys
    sys.setrecursionlimit(10000)
    ok = rec(full)
    return (list(sol) if ok else None), nodes[0]
