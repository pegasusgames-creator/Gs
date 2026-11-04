#!/usr/bin/env python3
"""gen_levels.py — builds Mahjong Solitaire's 500-level campaign.

Pipeline (stdlib only, deterministic):
  1. layouts.all_variants() — every curated family at every size that fits
     a portrait phone (<= 8 tiles across, <= 10 down, <= 144 tiles).
  2. A schedule grows the tile count from 14 (level 1) to ~136 (level 500)
     and rotates families so neighbouring levels never share a shape.
  3. Each level is DEALT IN REVERSE: two free tiles are lifted off the full
     layout at a time (a legal forward play), and each lifted pair receives
     one matching pair of faces. That removal order is stored with the deal,
     so every level ships with a witnessed solution; the gate
     scripts/check_mahjong_solvable.py replays all 500 independently.
  4. Difficulty: levels 1-30 use every tile kind at most once per pair (no
     dead ends are possible: any match is part of some full clear); later
     levels add four-of-a-kind sets. Among four candidate deals the one whose
     random-play stuck rate is closest to the level's target is kept.

Writes test/levels.json (readable) and test/levels_region.js (the game.html
LEVELS region; install with `python3 scripts/shell_region.py MahjongSolitaire
LEVELS --set MahjongSolitaire/test/levels_region.js`).
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from mahjong_core import (Geo, removal_order, pair_tokens, encode_layout,  # noqa: E402
                          encode_faces, match_key, FLOWERS, SEASONS)
import layouts as LY  # noqa: E402

N_LEVELS = 500
ALPHA36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def target_n(i):
    t = 14 + 114 * (i / float(N_LEVELS - 1)) ** 0.62
    return int(round(t / 2.0)) * 2


def dup_frac(i):
    if i < 30:
        return 0.0
    return min(1.0, 0.15 + 0.85 * (i - 30) / 370.0)


def stuck_target(i):
    if i < 30:
        return 0.0
    return min(0.40, 0.05 + 0.35 * (i - 30) / 400.0)


def enc_layout(tiles):
    """Per-layer encoding: base-36 x,y pairs, layers separated by '|'.
    Tile index = order of appearance (z, then y, then x)."""
    top = max(z for _, _, z in tiles)
    return '|'.join(''.join(ALPHA36[x] + ALPHA36[y] for (x, y, z) in tiles if z == k)
                    for k in range(top + 1))


def enc_index(k):
    return ALPHA36[k // 36] + ALPHA36[k % 36]


def make_faces(geo, order, rng, i):
    tokens = pair_tokens(len(order), dup_frac(i), rng, allow_bonus=(i >= 15))
    faces = [None] * geo.n
    fl, se = list(FLOWERS), list(SEASONS)
    rng.shuffle(fl)
    rng.shuffle(se)
    for (a, b), k in zip(order, tokens):
        if k == 34:
            fa, fb = fl.pop(), fl.pop()
        elif k == 38:
            fa, fb = se.pop(), se.pop()
        else:
            fa = fb = k
        faces[a], faces[b] = fa, fb
    return faces


def stuck_rate(geo, faces, rng, k=14):
    keys = [match_key(f) for f in faces]
    full = (1 << geo.n) - 1
    stuck = 0
    for _ in range(k):
        mask = full
        while mask:
            free = geo.free_list(mask)
            by = {}
            for t in free:
                by.setdefault(keys[t], []).append(t)
            pairs = [(g[a], g[b]) for g in by.values() if len(g) > 1
                     for a in range(len(g)) for b in range(a + 1, len(g))]
            if not pairs:
                stuck += 1
                break
            a, b = rng.choice(pairs)
            mask &= ~((1 << a) | (1 << b))
    return stuck / float(k)


def replay_ok(geo, faces, order):
    mask = (1 << geo.n) - 1
    for (a, b) in order:
        if not ((mask >> a) & 1 and (mask >> b) & 1) or a == b:
            return False
        if not (geo.is_free(a, mask) and geo.is_free(b, mask)):
            return False
        if match_key(faces[a]) != match_key(faces[b]):
            return False
        mask &= ~((1 << a) | (1 << b))
    return mask == 0


def pick_layouts(variants, rng):
    info = []
    for key, name, params, tiles in variants:
        st = LY.stats(tiles)
        info.append(dict(key=key, name=name, tiles=tiles, code=encode_layout(tiles), **st))
    used = {}
    last = {}
    fam_use = {}
    hist = []
    out = []
    for i in range(N_LEVELS):
        T = target_n(i)
        chosen = None
        for widen in range(0, 8):
            tol = max(2, int(0.08 * T)) + 2 * widen
            cands = []
            for v in info:
                if abs(v['n'] - T) > tol:
                    continue
                cap = 3
                if used.get(v['code'], 0) >= cap or i - last.get(v['code'], -999) < 45:
                    continue
                if v['key'] in hist[-(4 if widen < 4 else 2):]:
                    continue
                if i < 12 and (v['layers'] > 2 or v['free0'] < 0.45 * v['n']):
                    continue
                if i < 40 and v['layers'] > 3:
                    continue
                cands.append(v)
            if cands:
                cands.sort(key=lambda v: (fam_use.get(v['key'], 0) * 4 + abs(v['n'] - T)
                                          + 3 * rng.random()
                                          - (5 if used.get(v['code']) else 0)))
                chosen = cands[0]
                break
        if chosen is None:
            raise SystemExit('no layout for level %d (target %d)' % (i + 1, T))
        used[chosen['code']] = used.get(chosen['code'], 0) + 1
        last[chosen['code']] = i
        fam_use[chosen['key']] = fam_use.get(chosen['key'], 0) + 1
        hist.append(chosen['key'])
        out.append(chosen)
    return out


def main():
    rng = random.Random(20261104)
    variants = LY.all_variants()
    plan = pick_layouts(variants, rng)
    lay_index = {}
    layouts = []
    campaign = []
    report = []
    for i, v in enumerate(plan):
        if v['code'] not in lay_index:
            lay_index[v['code']] = len(layouts)
            layouts.append({'n': v['name'], 't': enc_layout(v['tiles'])})
        assert v['tiles'] == sorted(v['tiles'], key=lambda p: (p[2], p[1], p[0]))
        geo = Geo(v['tiles'])
        lrng = random.Random(7919 * (i + 1) + 13)
        cands = []
        tries = 1 if i < 30 else (4 if i < 200 else 6)
        for _ in range(40):
            order = removal_order(geo, lrng)
            if not order:
                continue
            faces = make_faces(geo, order, lrng, i)
            if not replay_ok(geo, faces, order):
                raise SystemExit('dealer produced a bad deal at level %d' % (i + 1))
            rate = stuck_rate(geo, faces, lrng) if i >= 30 else 0.0
            cands.append((abs(rate - stuck_target(i)), rate, faces, order))
            if len(cands) >= tries:
                break
        if not cands:
            raise SystemExit('could not deal level %d (%s)' % (i + 1, v['name']))
        cands.sort(key=lambda c: c[0])
        _, rate, faces, order = cands[0]
        campaign.append({
            'l': lay_index[v['code']],
            'f': encode_faces(faces),
            'o': ''.join(enc_index(a) + enc_index(b) for (a, b) in order),
        })
        report.append((i + 1, v['name'], v['n'], v['layers'], round(rate, 2)))
    with open(os.path.join(HERE, 'levels.json'), 'w') as fh:
        json.dump({'layouts': layouts, 'campaign': campaign}, fh, indent=0)
        fh.write('\n')
    lines = [
        '// LEVELS — 500 deals from test/gen_levels.py. Each deal was dealt in',
        '// reverse (free pairs lifted off the full layout), so its stored removal',
        '// order `o` (2-char base-36 tile indices, two per step) clears the board.',
        '// scripts/check_mahjong_solvable.py replays every one. `t` = layout: base-36',
        '// x,y pairs in half-tile units, layers split by |; `f` = one face per tile.',
        'const MJ_LAYOUTS = [',
        ',\n'.join(json.dumps(l, separators=(',', ':')) for l in layouts),
        '];',
        'const CAMPAIGN = [',
        ',\n'.join(json.dumps(c, separators=(',', ':')) for c in campaign),
        '];',
        'const LEVELS = CAMPAIGN; // length contract for level-select/addendum',
    ]
    with open(os.path.join(HERE, 'levels_region.js'), 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    for r in report[:12] + report[25:35:3] + report[99::50] + report[-1:]:
        print('L%-3d %-12s n=%-3d layers=%d stuck=%.2f' % r)
    print('layouts:', len(layouts), ' levels:', len(campaign),
          ' region bytes:', os.path.getsize(os.path.join(HERE, 'levels_region.js')))


if __name__ == '__main__':
    main()
