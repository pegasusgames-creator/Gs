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

Stdlib only. Used by test/gen_levels.py; scripts/check_mahjong_solvable.py
carries its own copy of the rules + solver so the gate is independent.
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


# ─────────────────────────── layout families ───────────────────────────
def rect(x0, y0, cols, rows, z):
    return [(x0 + 2 * i, y0 + 2 * j, z) for i in range(cols) for j in range(rows)]


def rows_shape(widths, z, max_w=None, y0=0, step=2, half=False):
    """Centered rows of the given tile widths (each row one tile tall)."""
    max_w = max_w or max(widths)
    out = []
    for r, w in enumerate(widths):
        if w <= 0:
            continue
        off = (max_w - w)          # half-units: centering shift
        if not half and off % 2:
            off -= 1
        for i in range(w):
            out.append((off + 2 * i, y0 + r * step, z))
    return out


def stack_on(base, z, inset):
    """Tiles of layer z sitting on `base` cells shrunk by `inset` half-units
    from every edge of each row-run (keeps support)."""
    return base


def fam_pyramid(w, h, layers, half):
    t = []
    for k in range(layers):
        if half:
            cw, ch, off = w - k, h - k, k
        else:
            cw, ch, off = w - 2 * k, h - 2 * k, 2 * k
        if cw < 1 or ch < 1:
            break
        t += rect(off, off, cw, ch, k)
    return t


def fam_turtle(w, h, layers):
    # shell: first/last rows narrower, head + tail tiles, side "legs"
    widths = [w - 2] + [w] * (h - 2) + [w - 2]
    base = rows_shape(widths, 0, max_w=w + 2, y0=2)
    # shift so legs fit: legs at row 1 and row h-2 on both sides
    t = [(x + 2, y, z) for (x, y, z) in base]
    cx = (w + 2) // 1  # center in half units of the shifted frame
    # center x (half-units) of the shell = 2 + w (since width w tiles spans 2w)
    mid = 2 + (w + 2 - 2) - 1 + 0
    head_x = 2 + (w + 2) - 2 - 1 + 1
    head_x = (2 * (w + 2) - 2) // 2 + 1 - 1
    head_x = w + 1
    t.append((head_x, 0, 0))                    # head
    t.append((head_x, 2 * h + 2, 0))            # tail
    t.append((0, 4, 0))
    t.append((2 * w + 4, 4, 0))
    t.append((0, 2 * h - 2, 0))
    t.append((2 * w + 4, 2 * h - 2, 0))
    # upper shell layers: centered rects
    for k in range(1, layers):
        cw, ch = w - 2 * k, h - 2 * k
        if cw < 1 or ch < 1:
            break
        t += rect(4 + 2 * (k - 1) + 0, 2 + 2 * k, cw, ch, k)
    return t


def fam_diamond(n, layers):
    t = []
    for k in range(layers):
        m = n - 2 * k
        if m < 1:
            break
        widths = [1 + 2 * min(i, m - 1 - i) for i in range(m)]
        mw = max(widths)
        for r, w in enumerate(widths):
            off = (mw - w)
            for i in range(w):
                t.append((off + 2 * i + 2 * k, 2 * r + 2 * k, k))
    return t


def fam_cross(w, h, bw, bh, layers):
    t = set()
    xs = (w - bw)
    ys = (h - bh)
    for (x, y, z) in rect(xs, 0, bw, h, 0):
        t.add((x, y, z))
    for (x, y, z) in rect(0, ys, w, bh, 0):
        if not any(abs(x - a) < 2 and abs(y - b) < 2 and c == 0 for (a, b, c) in t):
            t.add((x, y, z))
    out = list(t)
    for k in range(1, layers):
        cw, ch = bw - 2 * k + 2, bh - 2 * k + 2
        cw, ch = max(1, bw - k), max(1, bh - k)
        out += rect(xs + k, ys + k, cw, ch, k)
    return out


def fam_fortress(w, h, towers):
    t = rect(0, 0, w, h, 0)
    # walls on top of the outer ring
    ring = [(x, y, 1) for (x, y, z) in t if x in (0, 2 * w - 2) or y in (0, 2 * h - 2)]
    t += ring
    if towers:
        for (x, y) in ((0, 0), (2 * w - 2, 0), (0, 2 * h - 2), (2 * w - 2, 2 * h - 2)):
            t.append((x, y, 2))
    return t


def fam_towers(w, h, spots, height):
    t = rect(0, 0, w, h, 0)
    for (cx, cy) in spots:
        for z in range(1, height + 1):
            t.append((cx, cy, z))
    return t


def fam_hourglass(widths, layers):
    t = rows_shape(widths, 0, half=True)
    mw = max(widths)
    for k in range(1, layers):
        ws = [w - 2 * k for w in widths[k:len(widths) - k]]
        if not ws or max(ws) < 1:
            break
        for r, w in enumerate(ws):
            if w < 1:
                continue
            off = (mw - w)
            for i in range(w):
                t.append((off + 2 * i, 2 * (r + k), k))
    return t


def fam_steps(w, h, layers, down):
    t = []
    for k in range(layers):
        rows = h - k * (h // layers)
        if rows < 1:
            break
        y0 = 0 if not down else 2 * (h - rows)
        t += rect(0, y0, w, rows, k)
    return t


def fam_flower(petal_w, petal_h, center_layers, diag):
    t = []
    cw = 2
    # center block 2x2 at (pw*2, ph*2)
    px, py = 2 * petal_w, 2 * petal_h
    t += rect(px, py, cw, cw, 0)
    t += rect(0, py, petal_w, cw, 0)                 # west petal
    t += rect(px + 2 * cw, py, petal_w, cw, 0)       # east petal
    t += rect(px, 0, cw, petal_h, 0)                 # north
    t += rect(px, py + 2 * cw, cw, petal_h, 0)       # south
    if diag:
        t += rect(px - 2, py - 2, 1, 1, 0) if petal_w and petal_h else []
        t += rect(px + 4, py - 2, 1, 1, 0)
        t += rect(px - 2, py + 4, 1, 1, 0)
        t += rect(px + 4, py + 4, 1, 1, 0)
    for k in range(1, center_layers + 1):
        if k == center_layers:
            t.append((px + 1, py + 1, k))
        else:
            t += rect(px, py, cw, cw, k)
    return t


def fam_bricks(w, h, layers):
    t = []
    for r in range(h):
        off = 1 if r % 2 else 0
        cols = w if r % 2 == 0 else w - 1
        for i in range(cols):
            t.append((off + 2 * i, 2 * r, 0))
    for k in range(1, layers):
        for r in range(k, h - k):
            off = 1 if (r + k) % 2 else 0
            cols = (w - k) if (r + k) % 2 == 0 else (w - k - 1)
            for i in range(cols):
                x = off + 2 * i + k + (0 if (r + k) % 2 == 0 else 0)
                t.append((x, 2 * r, k))
    return t


def spiral_path(w, h):
    """Cells (col,row) of a square spiral inward with a 1-cell gap between
    turns: walls of a maze-like spiral."""
    grid = [[0] * w for _ in range(h)]
    x, y = 0, 0
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    d = 0
    path = []

    def ok(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or grid[ny][nx]:
            return False
        # keep a one-cell gap from earlier (non-adjacent in path) cells
        for (ax, ay) in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)):
            if 0 <= ax < w and 0 <= ay < h and grid[ay][ax] and (ax, ay) != (x, y):
                return False
        return True

    grid[y][x] = 1
    path.append((x, y))
    turns_failed = 0
    while turns_failed < 2:
        nx, ny = x + dirs[d][0], y + dirs[d][1]
        if ok(nx, ny):
            x, y = nx, ny
            grid[y][x] = 1
            path.append((x, y))
            turns_failed = 0
        else:
            d = (d + 1) % 4
            turns_failed += 1
    return path


def fam_spiral(w, h, rise):
    path = spiral_path(w, h)
    t = [(2 * c, 2 * r, 0) for (c, r) in path]
    n = len(path)
    if rise >= 1:
        for (c, r) in path[n // 3:]:
            t.append((2 * c, 2 * r, 1))
    if rise >= 2:
        for (c, r) in path[2 * n // 3:]:
            t.append((2 * c, 2 * r, 2))
    return t


def fam_rings(w, h, layers):
    t = []
    for k in range(layers):
        cw, ch = w - 2 * k, h - 2 * k
        if cw < 1 or ch < 1:
            break
        for (x, y, z) in rect(2 * k, 2 * k, cw, ch, 0):
            pass
    # concentric frames on layer 0 separated by gaps of half a tile
    out = []
    x0, y0, cw, ch = 0, 0, w, h
    ring = 0
    while cw >= 1 and ch >= 1:
        for i in range(cw):
            for j in range(ch):
                if i in (0, cw - 1) or j in (0, ch - 1):
                    out.append((x0 + 2 * i, y0 + 2 * j, 0))
        ring += 1
        x0 += 3
        y0 += 3
        cw -= 3
        ch -= 3
        if cw <= 0 or ch <= 0:
            break
        # integer tile steps of 1.5 tiles: snap to half units
    if layers > 1:
        out += [(x, y, 1) for (x, y, z) in out if z == 0 and (x == 0 or y == 0 or x == 2 * w - 2 or y == 2 * h - 2)]
    return out


def fam_columns(cols, h, gap, height_fn):
    t = []
    for c in range(cols):
        x = c * (2 + gap)
        for r in range(h):
            t.append((x, 2 * r, 0))
            for z in range(1, height_fn(c, r) + 1):
                t.append((x, 2 * r, z))
    return t


def fam_chevron(w, h, layers):
    # V rows: each row a pair of arms that move toward the center
    t = []
    for r in range(h):
        arm = max(1, w // 2 - abs(r - h // 2))
        left = [(2 * i, 2 * r, 0) for i in range(arm)]
        right = [(2 * (w - 1 - i), 2 * r, 0) for i in range(arm)]
        for p in left + right:
            if p not in t:
                t.append(p)
    for k in range(1, layers):
        up = [(x, y, k) for (x, y, z) in t if z == k - 1]
        keep = []
        for (x, y, z) in up:
            # inset: drop the outermost tile of each arm
            if (x - 2, y, k - 1) in t and (x + 2, y, k - 1) in t:
                keep.append((x, y, z))
        t += keep
    return t


def fam_pagoda(w, tiers, tier_rows):
    t = []
    y = 0
    widths = [max(1, w - 2 * (tiers - 1 - i)) for i in range(tiers)]
    for i, tw in enumerate(widths):
        off = (w - tw)
        for r in range(tier_rows):
            for c in range(tw):
                t.append((off + 2 * c, y + 2 * r, 0))
        y += 2 * tier_rows
    # central spine rising
    spine_x = w - 1 if w % 2 == 0 else w - 1
    rows_total = tiers * tier_rows
    for r in range(rows_total):
        z = 1
        x = (w - 1)  # half-unit center for odd w
        cell = (x - (0 if w % 2 else 1), 2 * r)
    return t


def fam_lantern(w, h, layers):
    widths = []
    for r in range(h):
        f = 1 - ((2 * r - (h - 1)) / float(h)) ** 2
        widths.append(max(2, int(round(w * (0.45 + 0.55 * f)))))
    t = rows_shape(widths, 0, max_w=w, half=True)
    for k in range(1, layers):
        inner = [max(0, ww - 2 * k) for ww in widths[k:h - k]]
        for r, ww in enumerate(inner):
            off = (w - ww)
            for i in range(ww):
                t.append((off + 2 * i, 2 * (r + k), k))
    return t


def fam_twin(w, h, layers, vertical):
    a = fam_pyramid(w, h, layers, True)
    if vertical:
        b = [(x, y + 2 * h + 1, z) for (x, y, z) in a]
    else:
        b = [(x + 2 * w + 1, y, z) for (x, y, z) in a]
    return a + b


def support_filter(tiles):
    """Drop upper tiles that are not fully supported (repeat to fixpoint)."""
    tiles = set(tiles)
    changed = True
    while changed:
        changed = False
        occ = set()
        for (x, y, z) in tiles:
            for dx in (0, 1):
                for dy in (0, 1):
                    occ.add((x + dx, y + dy, z))
        for t in list(tiles):
            x, y, z = t
            if z == 0:
                continue
            if not all((x + dx, y + dy, z - 1) in occ for dx in (0, 1) for dy in (0, 1)):
                tiles.discard(t)
                changed = True
    return tiles


def overlap_filter(tiles):
    """Keep tiles in a deterministic order, dropping any that overlap one
    already kept on the same layer."""
    occ = set()
    out = []
    for t in sorted(set(tiles), key=lambda t: (t[2], t[1], t[0])):
        x, y, z = t
        cells = [(x + dx, y + dy, z) for dx in (0, 1) for dy in (0, 1)]
        if any(c in occ for c in cells):
            continue
        occ.update(cells)
        out.append(t)
    return out


def make_even(tiles):
    """Fix an odd count by removing the topmost, most central tile."""
    tiles = list(tiles)
    if len(tiles) % 2 == 0:
        return tiles
    xs = [t[0] for t in tiles]
    cx = (min(xs) + max(xs)) / 2.0
    ys = [t[1] for t in tiles]
    cy = (min(ys) + max(ys)) / 2.0
    # removable = not supporting anything
    top = []
    occ_above = set()
    for (x, y, z) in tiles:
        if z > 0:
            for dx in (0, 1):
                for dy in (0, 1):
                    occ_above.add((x + dx, y + dy, z - 1))
    for t in tiles:
        x, y, z = t
        if not any((x + dx, y + dy, z) in occ_above for dx in (0, 1) for dy in (0, 1)):
            top.append(t)
    top.sort(key=lambda t: (-t[2], abs(t[0] - cx) + abs(t[1] - cy), t[1], t[0]))
    tiles.remove(top[0])
    return tiles


def candidates():
    """Yield (family, params, tiles) for a broad parameter sweep."""
    for w in range(3, 10):
        for h in range(3, 13):
            for layers in range(1, 5):
                for half in (False, True):
                    yield ("pyramid", (w, h, layers, half), fam_pyramid(w, h, layers, half))
    for w in range(3, 8):
        for h in range(4, 11):
            for layers in range(1, 5):
                yield ("turtle", (w, h, layers), fam_turtle(w, h, layers))
    for n in range(3, 10, 2):
        for layers in range(1, 5):
            yield ("diamond", (n, layers), fam_diamond(n, layers))
    for w in range(5, 10, 2):
        for h in range(5, 13, 2):
            for bw in range(1, 4, 2):
                for bh in range(1, 4, 2):
                    for layers in range(1, 4):
                        yield ("cross", (w, h, bw, bh, layers), fam_cross(w, h, bw, bh, layers))
    for w in range(4, 10):
        for h in range(4, 13):
            for towers in (False, True):
                yield ("fortress", (w, h, towers), fam_fortress(w, h, towers))
    for w in range(4, 10):
        for h in range(4, 13):
            for height in (1, 2, 3):
                for pat in range(3):
                    if pat == 0:
                        spots = [(2, 2), (2 * w - 4, 2), (2, 2 * h - 4), (2 * w - 4, 2 * h - 4)]
                    elif pat == 1:
                        spots = [(w - 1 if w % 2 else w - 2, 2), (w - 1 if w % 2 else w - 2, 2 * h - 4),
                                 (2, h - 1 if h % 2 else h - 2), (2 * w - 4, h - 1 if h % 2 else h - 2)]
                    else:
                        spots = [((w - 1) if w % 2 else (w - 2), (h - 1) if h % 2 else (h - 2))]
                    yield ("towers", (w, h, height, pat), fam_towers(w, h, spots, height))
    for top in range(5, 10):
        for neck in range(1, 4):
            for h in range(6, 13):
                half_h = h // 2
                ws = []
                for r in range(h):
                    d = abs(r - (h - 1) / 2.0) / ((h - 1) / 2.0)
                    ws.append(max(neck, int(round(neck + (top - neck) * d))))
                for layers in (1, 2, 3):
                    yield ("hourglass", (top, neck, h, layers), fam_hourglass(ws, layers))
    for w in range(4, 10):
        for h in range(4, 13):
            for layers in (2, 3, 4):
                for down in (False, True):
                    yield ("steps", (w, h, layers, down), fam_steps(w, h, layers, down))
    for pw in range(1, 4):
        for ph in range(1, 5):
            for cl in range(1, 4):
                for diag in (False, True):
                    yield ("flower", (pw, ph, cl, diag), fam_flower(pw, ph, cl, diag))
    for w in range(4, 10):
        for h in range(4, 13):
            for layers in (1, 2, 3):
                yield ("bricks", (w, h, layers), fam_bricks(w, h, layers))
    for w in range(5, 10):
        for h in range(5, 13):
            for rise in (0, 1, 2):
                yield ("spiral", (w, h, rise), fam_spiral(w, h, rise))
    for w in range(5, 10):
        for h in range(6, 13):
            for layers in (1, 2):
                yield ("rings", (w, h, layers), fam_rings(w, h, layers))
    for cols in range(3, 7):
        for h in range(3, 13):
            for mode in range(4):
                def hf(c, r, mode=mode, cols=cols, h=h):
                    if mode == 0:
                        return 0
                    if mode == 1:
                        return 1 if (c + r) % 2 == 0 else 0
                    if mode == 2:
                        return min(c, cols - 1 - c)
                    return 1 if (r % 3 == 1) else 0
                gap = 1 if cols >= 5 else 2
                yield ("columns", (cols, h, mode), fam_columns(cols, h, gap, hf))
    for w in range(5, 10):
        for h in range(5, 13):
            for layers in (1, 2, 3):
                yield ("chevron", (w, h, layers), fam_chevron(w, h, layers))
    for w in range(5, 10):
        for h in range(5, 13):
            for layers in (1, 2, 3, 4):
                yield ("lantern", (w, h, layers), fam_lantern(w, h, layers))
    for w in range(2, 5):
        for h in range(2, 6):
            for layers in (1, 2, 3):
                for vertical in (False, True):
                    yield ("twin", (w, h, layers, vertical), fam_twin(w, h, layers, vertical))


def clean(tiles):
    t = overlap_filter(tiles)
    t = support_filter(t)
    t = make_even(list(t))
    t = support_filter(t)
    if len(t) % 2:
        t = make_even(list(t))
    if len(t) < 6:
        return None
    t = normalize(t)
    if validate_layout(t):
        return None
    return t


def layout_pool():
    """All valid, de-duplicated candidate layouts: list of (family, params, tiles)."""
    seen = set()
    pool = []
    for fam, params, raw in candidates():
        t = clean(raw)
        if not t:
            continue
        key = encode_layout(t)
        if key in seen:
            continue
        seen.add(key)
        pool.append((fam, params, t))
    return pool


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
