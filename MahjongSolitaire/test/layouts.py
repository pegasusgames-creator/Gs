#!/usr/bin/env python3
"""layouts.py — the curated layout families of Mahjong Solitaire.

Every layout is built in HALF-tile units (see mahjong_core.py): a tile at
(x, y, z) covers half-cells x..x+1, y..y+1 on layer z. Bases are written as
CENTRED ROWS (a row of w tiles centred on one axis lands on half-steps by
itself, which is what gives lanterns and lotuses their soft edges); upper
layers are derived from the layer below by stacking operations that keep
every tile fully supported:

  erode     keep a tile only if its left, right, upper and lower neighbours exist
  erode_h   keep a tile only if its left and right neighbours exist
  half_up   a tile straddling every 2x2 block (the classic half-step apex)
  same      the layer below, unchanged (a straight tower)

Portrait limits: at most 8 tiles across and 10 tiles down, so a tile stays
~40 CSS px wide on a 360 px phone. Each family yields several sizes; the
level schedule (gen_levels.py) picks sizes that grow with the campaign.

The names are generic shape words (Turtle is the traditional name of the
classic stack); nothing here copies another product's layout set.
"""
import math

from mahjong_core import normalize, validate_layout, encode_layout, Geo

MAX_COLS = 8
MAX_ROWS = 10
MAX_TILES = 144
CX = 40  # working centre (half units); layouts are normalised afterwards


# ─────────────────────────── row DSL ───────────────────────────
def row(y, spec, z=0, cx=CX):
    """Centred row at half-unit y. spec = n tiles, or [n, gap, n, gap, n...]
    alternating tile counts and gaps in half units."""
    if isinstance(spec, int):
        spec = [spec]
    span = 0
    for i, v in enumerate(spec):
        span += 2 * v if i % 2 == 0 else v
    x = cx - span // 2
    out = []
    for i, v in enumerate(spec):
        if i % 2 == 0:
            for _ in range(v):
                out.append((x, y, z))
                x += 2
        else:
            x += v
    return out


def rows(y0, specs, z=0, step=2, cx=CX):
    out = []
    for r, s in enumerate(specs):
        if s:
            out += row(y0 + r * step, s, z, cx)
    return out


# ─────────────────────────── stacking ops ───────────────────────────
def _xy(layer):
    return {(x, y) for (x, y, _) in layer}


def lift(layer, z):
    return [(x, y, z) for (x, y, _) in layer]


def erode(layer, z):
    s = _xy(layer)
    return [(x, y, z) for (x, y) in sorted(s)
            if (x - 2, y) in s and (x + 2, y) in s and (x, y - 2) in s and (x, y + 2) in s]


def erode_h(layer, z):
    s = _xy(layer)
    return [(x, y, z) for (x, y) in sorted(s) if (x - 2, y) in s and (x + 2, y) in s]


def erode_v(layer, z):
    s = _xy(layer)
    return [(x, y, z) for (x, y) in sorted(s) if (x, y - 2) in s and (x, y + 2) in s]


def half_up(layer, z):
    """Tiles straddling 2x2 blocks (offset half a tile right and down)."""
    s = _xy(layer)
    cand = sorted((x + 1, y + 1) for (x, y) in s
                  if (x + 2, y) in s and (x, y + 2) in s and (x + 2, y + 2) in s)
    out, occ = [], set()
    for (x, y) in cand:
        cells = {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}
        if cells & occ:
            continue
        occ |= cells
        out.append((x, y, z))
    return out


def half_x(layer, z):
    """Bricks laid across two neighbours of the same row."""
    s = _xy(layer)
    cand = sorted((x + 1, y) for (x, y) in s if (x + 2, y) in s)
    out, occ = [], set()
    for (x, y) in cand:
        cells = {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}
        if cells & occ:
            continue
        occ |= cells
        out.append((x, y, z))
    return out


def keep(layer, pred, z=None):
    return [(x, y, z if z is not None else c) for (x, y, c) in layer if pred(x, y)]


def stack(base, ops):
    """base layer + a list of op names / callables applied layer by layer."""
    layers = [base]
    for k, op in enumerate(ops, start=1):
        below = layers[-1]
        if not below:
            break
        if callable(op):
            nxt = op(below, k)
        else:
            nxt = {'erode': erode, 'erode_h': erode_h, 'erode_v': erode_v,
                   'half_up': half_up, 'half_x': half_x, 'same': lift}[op](below, k)
        if not nxt:
            break
        layers.append(nxt)
    return [t for L in layers for t in L]


def repeat_erode(base, top='half_up', limit=5):
    """Pyramid-style: erode until nothing is left, then a half-step cap."""
    layers = [base]
    while len(layers) < limit:
        nxt = erode(layers[-1], len(layers))
        if not nxt:
            break
        layers.append(nxt)
    if top and len(layers) < limit:
        cap = half_up(layers[-1], len(layers)) if top == 'half_up' else []
        if cap and len(cap) <= 4:
            layers.append(cap)
    return [t for L in layers for t in L]


# ─────────────────────────── families ───────────────────────────
def f_pyramid(w, h):
    return repeat_erode(rows(0, [w] * h))


def f_ziggurat(w, h):
    layers = [rows(0, [w] * h)]
    while len(layers) < 5:
        nxt = half_up(layers[-1], len(layers))
        if not nxt:
            break
        layers.append(nxt)
    return [t for L in layers for t in L]


def f_turtle(w, h):
    y0 = 2
    body = rows(y0, [w - 2] + [w] * (h - 2) + [w - 2])
    t = list(body)
    t += row(0, 1)                         # head
    t += row(y0 + 2 * h, 1)                # tail
    t += row(y0 + 1, [1, 2 * w, 1])        # front flippers (half a row down)
    t += row(y0 + 2 * h - 3, [1, 2 * w, 1])  # back flippers
    inner = [p for p in body if p[1] > y0 and p[1] < y0 + 2 * (h - 1)]
    layers = [inner]
    up = []
    cur = rows(y0 + 2, [w - 2] * (h - 2), z=1)
    k = 1
    while cur and k < 5:
        up += cur
        k += 1
        nxt = erode(cur, k)
        if not nxt:
            cap = half_up(cur, k)
            if cap and len(cap) <= 2:
                up += cap
            break
        cur = nxt
    return t + up


def f_fortress(w, h, towers=2, keep_core=True):
    base = rows(0, [w] * h)
    ring = [(x, y, 1) for (x, y, _) in base
            if y in (0, 2 * (h - 1)) or (x, y) in {(p[0], p[1]) for p in row(0, [1, 2 * (w - 2), 1])} or False]
    ring = []
    left = min(x for x, _, _ in base)
    right = max(x for x, _, _ in base)
    for (x, y, _) in base:
        if y in (0, 2 * (h - 1)) or x in (left, right):
            ring.append((x, y, 1))
    t = base + ring
    corners = [(x, y) for (x, y, _) in ring if x in (left, right) and y in (0, 2 * (h - 1))]
    for z in range(2, 2 + towers):
        t += [(x, y, z) for (x, y) in corners]
    if keep_core and w >= 5 and h >= 5:
        core = erode(erode(base, 1), 1)
        core = [(x, y, 1) for (x, y, _) in core]
        t += core
        cap = half_up(core, 2)
        if cap and len(cap) <= 4:
            t += cap
    return t


def lantern_widths(w, h):
    out = []
    for r in range(h):
        f = math.sin(math.pi * (r + 0.5) / h)
        out.append(max(2, int(round(w * (0.35 + 0.65 * f)))))
    return out


def f_lantern(w, h):
    base = rows(0, lantern_widths(w, h))
    return stack(base, ['erode_h', 'erode', 'half_up'])


def f_lotus(R):
    widths = [R - abs(r - (R - 1)) for r in range(2 * R - 1)]
    base = rows(0, widths)
    return stack(base, ['erode_h', 'erode_h', 'erode'])


def f_diamond(R):
    widths = [1 + 2 * (R - 1 - abs(r - (R - 1))) for r in range(2 * R - 1)]
    base = rows(0, widths)
    return repeat_erode(base)


def f_hourglass(w, h, neck):
    widths = []
    for r in range(h):
        d = abs(r - (h - 1) / 2.0) / ((h - 1) / 2.0)
        widths.append(max(neck, int(round(neck + (w - neck) * d))))
    base = rows(0, widths)
    return stack(base, ['erode_h', 'erode_h', 'same'])


def f_butterfly(a, h):
    specs = []
    for r in range(h):
        d = abs(r - (h - 1) / 2.0) / ((h - 1) / 2.0)
        wing = max(1, int(round(1 + (a - 1) * d)))
        specs.append([wing, 1, 1, 1, wing])
    base = rows(0, specs)
    body_x = CX - 1
    body = [(x, y, 1) for (x, y, _) in base if x == body_x]
    body2 = [(x, y, 2) for (x, y, _) in body if 0 < y < 2 * (h - 1)]
    wings = erode_h(base, 1)
    wings = [p for p in wings if p[0] != body_x]
    return base + body + body2 + wings


def spiral_cells(w, h):
    grid = [[0] * w for _ in range(h)]
    x = y = 0
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    d = 0
    path = [(0, 0)]
    grid[0][0] = 1

    def ok(nx, ny, px, py):
        if not (0 <= nx < w and 0 <= ny < h) or grid[ny][nx]:
            return False
        for (ax, ay) in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)):
            if 0 <= ax < w and 0 <= ay < h and grid[ay][ax] and (ax, ay) != (px, py):
                return False
        return True

    fails = 0
    while fails < 2:
        nx, ny = x + dirs[d][0], y + dirs[d][1]
        if ok(nx, ny, x, y):
            x, y = nx, ny
            grid[y][x] = 1
            path.append((x, y))
            fails = 0
        else:
            d = (d + 1) % 4
            fails += 1
    return path


def f_spiral(w, h, rise):
    path = spiral_cells(w, h)
    t = [(2 * c, 2 * r, 0) for (c, r) in path]
    n = len(path)
    for k in range(1, rise + 1):
        t += [(2 * c, 2 * r, k) for (c, r) in path[(k * n) // (rise + 2):]]
    return t


def f_compass(arm, thick, tower):
    n = 2 * arm + thick
    specs = []
    for r in range(n):
        if arm <= r < arm + thick:
            specs.append(n)
        else:
            specs.append(thick)
    base = rows(0, specs)
    xs = sorted({x for x, _, _ in base})
    mid = [(x, y, 0) for (x, y, _) in base
           if row(0, thick)[0][0] <= x <= row(0, thick)[-1][0] and arm * 2 <= y <= (arm + thick - 1) * 2]
    t = list(base)
    cur = mid
    for z in range(1, tower + 1):
        cur = [(x, y, z) for (x, y, _) in cur]
        t += cur
        if z >= 2:
            cur = erode(cur, z) or cur
    cap = half_up(cur, tower + 1)
    if cap and len(cap) <= 4:
        t += cap
    # arm tips get a second tile
    return t


def f_twin(w, h, gap):
    a = repeat_erode(rows(0, [w] * h))
    b = [(x, y + 2 * h + gap, z) for (x, y, z) in a]
    return a + b


def f_moongate(w, h, inner):
    specs = []
    for r in range(h):
        if r == 0 or r == h - 1:
            specs.append(max(2, w - 2))
        elif r == 1 or r == h - 2:
            specs.append([2, 2 * (w - 4), 2])
        else:
            specs.append([1, 2 * (w - 2), 1])
    base = rows(0, specs)
    t = list(base)
    t += [(x, y, 1) for (x, y, _) in base if y in (0, 2 * (h - 1))]
    if inner:
        core = rows(2 * (h // 2) - 2, [2, 2], z=0)
        if w >= 6:
            core = rows(h - 2, [2, 2], z=0)
        t += core
        t += half_up(core, 1)
    return t


def f_pagoda(tiers, base_w):
    specs = []
    w = base_w - 2 * (tiers - 1)
    if w < 2:
        raise ValueError('spire too thin')
    for i in range(tiers):
        specs += [max(1, w - 1), w]
        w += 2
    specs = specs[:MAX_ROWS]
    base = rows(0, specs)
    spine = [(x, y, 1) for (x, y, _) in base if abs(x - (CX - 1)) <= 2]
    spine = [p for p in spine if (p[0] - 2, p[1]) in {(q[0], q[1]) for q in base} or (p[0] + 2, p[1]) in {(q[0], q[1]) for q in base}]
    roofs = erode_h(base, 1)
    up = {(x, y) for (x, y, _) in roofs} | {(x, y) for (x, y, _) in spine}
    l1 = [(x, y, 1) for (x, y) in sorted(up)]
    l2 = [(x, y, 2) for (x, y, _) in l1 if abs(x - (CX - 1)) <= 1]
    return base + l1 + l2


def f_wall(w, h, layers):
    specs = [w if r % 2 == 0 else w - 1 for r in range(h)]
    base = rows(0, specs)
    t = list(base)
    cur = base
    for k in range(1, layers):
        cur = erode_h(cur, k)
        cur = [p for p in cur if 0 < p[1] < 2 * (h - 1)]
        if not cur:
            break
        t += cur
    return t


def f_heart(size):
    if size == 0:
        specs = [[2, 2, 2], 5, 5, 4, 3, 2, 1]
    elif size == 1:
        specs = [[2, 2, 2], [3, 0, 3], 6, 6, 5, 4, 3, 2, 1]
    else:
        specs = [[2, 4, 2], [3, 2, 3], 8, 8, 7, 6, 5, 4, 3, 2]
    base = rows(0, specs)
    return stack(base, ['erode_h', 'erode', 'half_up'])


def f_islands(cols, rws, h):
    t = []
    for i in range(cols):
        for j in range(rws):
            x0, y0 = i * 5, j * 5
            blk = [(x0, y0, 0), (x0 + 2, y0, 0), (x0, y0 + 2, 0), (x0 + 2, y0 + 2, 0)]
            t += blk
            if h >= 1:
                t.append((x0 + 1, y0 + 1, 1))
    return t


def f_crown(w, h):
    specs = [[1, 2, 1, 2, 1] if w >= 5 else [1, 2, 1]] + [w] * (h - 1)
    specs[0] = []
    pts = []
    base = rows(2, [w] * (h - 1))
    xs = sorted({x for x, _, _ in base})
    for x in xs[::2]:
        pts.append((x, 0, 0))
    t = base + pts
    l1 = erode_h(base, 1)
    l1 = [p for p in l1 if p[1] < 2 + 2 * (h - 2)]
    t += l1
    t += [(x, y, 2) for (x, y, _) in l1 if y == 2]
    return t


def f_towers(w, h, height):
    base = rows(0, [w] * h)
    t = list(base)
    pts = [(x, y) for (x, y, _) in base]
    xs = sorted({x for x, _ in pts})
    ys = sorted({y for _, y in pts})
    spots = [(x, y) for (x, y) in pts if xs.index(x) % 2 == 1 and ys.index(y) % 2 == 1]
    for z in range(1, height + 1):
        t += [(x, y, z) for (x, y) in spots]
    return t


def f_waves(w, bands):
    t = []
    y = 0
    for b in range(bands):
        off = 1 if b % 2 else 0
        t += row(y, w - off, cx=CX + off)
        t += row(y + 2, w, cx=CX - off)
        y += 5
    l1 = erode_h(t, 1)
    return t + l1


def f_chevron(w, h):
    specs = []
    for r in range(h):
        arm = max(1, min(r + 1, h - r))
        gap = max(0, 2 * (w - 2 * arm))
        specs.append([arm, gap, arm] if gap > 0 else 2 * arm)
    base = rows(0, specs)
    return stack(base, ['erode_h', 'same'])


FAMILIES = {
    'pyramid':   ('Pyramid',     f_pyramid,   [(w, h) for w in range(3, 9) for h in range(3, 11)]),
    'ziggurat':  ('Ziggurat',    f_ziggurat,  [(w, h) for w in range(3, 9) for h in range(3, 11)]),
    'turtle':    ('Turtle',      f_turtle,    [(w, h) for w in range(4, 7) for h in range(4, 9)]),
    'fortress':  ('Fortress',    f_fortress,  [(w, h, tw, kc) for w in range(4, 9) for h in range(4, 11)
                                               for tw in (0, 1, 2) for kc in (False, True)]),
    'lantern':   ('Lantern',     f_lantern,   [(w, h) for w in range(4, 9) for h in range(4, 11)]),
    'lotus':     ('Lotus',       f_lotus,     [(R,) for R in range(3, 6)]),
    'diamond':   ('Diamond',     f_diamond,   [(R,) for R in range(2, 5)]),
    'hourglass': ('Hourglass',   f_hourglass, [(w, h, n) for w in range(4, 9) for h in range(5, 11) for n in (1, 2, 3)]),
    'butterfly': ('Butterfly',   f_butterfly, [(a, h) for a in (2, 3) for h in range(5, 11)]),
    'spiral':    ('Spiral',      f_spiral,    [(w, h, r) for w in range(5, 9) for h in range(5, 11) for r in (0, 1, 2)]),
    'compass':   ('Compass',     f_compass,   [(a, th, tw) for a in (1, 2, 3) for th in (1, 2) for tw in (1, 2, 3)]),
    'twin':      ('Twin Peaks',  f_twin,      [(w, h, g) for w in range(3, 9) for h in range(2, 5) for g in (1, 2)]),
    'moongate':  ('Moon Gate',   f_moongate,  [(w, h, i) for w in range(5, 9) for h in range(5, 11) for i in (False, True)]),
    'pagoda':    ('Pagoda',      f_pagoda,    [(tr, bw) for tr in (2, 3, 4, 5) for bw in range(4, 9)]),
    'wall':      ('Garden Wall', f_wall,      [(w, h, l) for w in range(4, 9) for h in range(3, 11) for l in (1, 2, 3)]),
    'heart':     ('Heart',       f_heart,     [(s,) for s in (0, 1, 2)]),
    'islands':   ('Islands',     f_islands,   [(c, r, 1) for c in (1, 2, 3) for r in (1, 2, 3, 4)]),
    'crown':     ('Crown',       f_crown,     [(w, h) for w in range(5, 9) for h in range(3, 9)]),
    'towers':    ('Towers',      f_towers,    [(w, h, t) for w in range(4, 9) for h in range(4, 11) for t in (1, 2, 3)]),
    'waves':     ('Waves',       f_waves,     [(w, b) for w in range(4, 9) for b in (2, 3, 4)]),
    'gateway':   ('Gateway',     f_chevron,   [(w, h) for w in range(4, 9) for h in range(4, 11)]),
}


def _even(tiles):
    """Fix an odd count by dropping one topmost tile that supports nothing,
    nearest the middle (keeps symmetric shapes symmetric when the apex is
    unique)."""
    if len(tiles) % 2 == 0:
        return tiles
    occ_above = set()
    for (x, y, z) in tiles:
        if z > 0:
            for dx in (0, 1):
                for dy in (0, 1):
                    occ_above.add((x + dx, y + dy, z - 1))
    xs = [t[0] for t in tiles]
    ys = [t[1] for t in tiles]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    tops = [t for t in tiles
            if not any((t[0] + dx, t[1] + dy, t[2]) in occ_above for dx in (0, 1) for dy in (0, 1))]
    tops.sort(key=lambda t: (-t[2], abs(t[0] - cx) + abs(t[1] - cy), t[1], t[0]))
    if tops[0][2] == 0:
        return None          # would punch a hole in a flat shape: skip it
    out = list(tiles)
    out.remove(tops[0])
    return out


def finish(raw):
    """dedupe, normalise, even, validate. Returns tiles or None."""
    t = sorted(set(raw), key=lambda p: (p[2], p[1], p[0]))
    if len(t) < 8:
        return None
    t = _even(normalize(t))
    if not t:
        return None
    t = normalize(t)
    if len(t) > MAX_TILES or validate_layout(t):
        return None
    cols = (max(x for x, _, _ in t) + 2) / 2.0
    rws = (max(y for _, y, _ in t) + 2) / 2.0
    if cols > MAX_COLS or rws > MAX_ROWS:
        return None
    return t


def mirror(tiles):
    mx = max(x for x, _, _ in tiles)
    return normalize([(mx - x, y, z) for (x, y, z) in tiles])


def deepen(tiles):
    """Taller versions of a shape: one more layer on its top layer (half-step,
    eroded, or bricks across neighbours). Returns a list of raw tile lists."""
    top = max(z for _, _, z in tiles)
    layer = [t for t in tiles if t[2] == top]
    out = []
    for op in (half_up, erode, erode_h, half_x):
        nxt = op(layer, top + 1)
        if 2 <= len(nxt) <= max(2, len(layer) - 2):
            out.append(list(tiles) + nxt)
    return out


def all_variants():
    """[(family_key, display_name, params, tiles)] — de-duplicated."""
    seen = set()
    out = []
    for key, (name, fn, plist) in FAMILIES.items():
        for p in plist:
            try:
                t = finish(fn(*p))
            except (ValueError, IndexError, ZeroDivisionError):
                t = None
            if not t:
                continue
            forms = [t]
            if len(t) >= 40:
                for d1 in deepen(t):
                    f1 = finish(d1)
                    if f1:
                        forms.append(f1)
                        for d2 in deepen(f1)[:1]:
                            f2 = finish(d2)
                            if f2:
                                forms.append(f2)
            for v in [m for f in forms for m in (f, mirror(f))]:
                code = encode_layout(v)
                if code in seen:
                    continue
                seen.add(code)
                out.append((key, name, p, v))
    return out


def stats(tiles):
    g = Geo(tiles)
    full = (1 << g.n) - 1
    return {
        'n': len(tiles),
        'cols': (max(x for x, _, _ in tiles) + 2) / 2.0,
        'rows': (max(y for _, y, _ in tiles) + 2) / 2.0,
        'layers': max(z for _, _, z in tiles) + 1,
        'free0': len(g.free_list(full)),
    }


if __name__ == '__main__':
    import collections
    vs = all_variants()
    c = collections.Counter(k for k, *_ in vs)
    print(len(vs), dict(c))
