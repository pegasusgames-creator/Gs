#!/usr/bin/env python3
"""check_mahjong_solvable.py — every shipped Mahjong Solitaire deal clears.

Mahjong Solitaire's campaign deals are generated in reverse (pairs of free
tiles are lifted off the full layout and given matching faces), and each deal
ships with that removal order. This gate re-derives nothing from the
generator: it decodes MJ_LAYOUTS + CAMPAIGN straight out of game.html and,
for every deal,

  * checks the layout: no two tiles overlap on a layer, every upper tile is
    fully supported by the layer below, coordinates in range, even count;
  * checks the faces: one per tile, valid symbols, at most four of any
    regular face and at most one of each flower / season;
  * checks the stored order is a permutation of all tiles, two per step;
  * REPLAYS it: at each step both tiles must still be on the board, both
    must be free (nothing on top, and an open left or right side), and they
    must match (identical face; any flower with any flower; any season with
    any season). After the last step the board must be empty.

It also asserts the campaign has at least 500 deals. Any failure BLOCKS.

Gate contract: with no arguments, or with MahjongSolitaire among the
arguments, it checks MahjongSolitaire; with only other app names it prints a
skip line and exits 0.

Stdlib only.  Usage: python3 scripts/check_mahjong_solvable.py [App ...]
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = 'MahjongSolitaire'
GAME = os.path.join(BASE, APP, 'android', 'app', 'src', 'main', 'assets', 'game.html')
ALPHA36 = '0123456789abcdefghijklmnopqrstuvwxyz'
FACES = '0123456789abcdefghijklmnopqrstuvwxyzABCDEF'   # 42 faces
MIN_LEVELS = 500


def match_key(f):
    if f >= 38:
        return 38            # seasons match each other
    if f >= 34:
        return 34            # flowers match each other
    return f


def extract_array(src, name):
    m = re.search(r'const\s+' + name + r'\s*=\s*\[', src)
    if not m:
        raise ValueError('const %s = [...] not found' % name)
    i = m.end() - 1
    depth = 0
    in_str = False
    for j in range(i, len(src)):
        c = src[j]
        if in_str:
            if c == '\\':
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return json.loads(src[i:j + 1])
    raise ValueError('unterminated %s' % name)


def decode_layout(t):
    tiles = []
    for z, part in enumerate(t.split('|')):
        if len(part) % 2:
            raise ValueError('odd-length layer %d' % z)
        for k in range(0, len(part), 2):
            tiles.append((ALPHA36.index(part[k]), ALPHA36.index(part[k + 1]), z))
    return tiles


def layout_error(tiles):
    occ = set()
    for (x, y, z) in tiles:
        if x > 30 or y > 30:
            return 'tile %r out of range' % ((x, y, z),)
        for dx in (0, 1):
            for dy in (0, 1):
                c = (x + dx, y + dy, z)
                if c in occ:
                    return 'tiles overlap at %r' % (c,)
                occ.add(c)
    for (x, y, z) in tiles:
        if z and any((x + dx, y + dy, z - 1) not in occ for dx in (0, 1) for dy in (0, 1)):
            return 'tile %r is not fully supported' % ((x, y, z),)
    if len(tiles) % 2 or not tiles:
        return 'tile count %d is not a positive even number' % len(tiles)
    return None


def relations(tiles):
    n = len(tiles)
    cover = [[] for _ in range(n)]
    left = [[] for _ in range(n)]
    right = [[] for _ in range(n)]
    for i, (x, y, z) in enumerate(tiles):
        for j, (a, b, c) in enumerate(tiles):
            if i == j:
                continue
            if c == z + 1 and abs(a - x) < 2 and abs(b - y) < 2:
                cover[i].append(j)          # j lies on top of i
            elif c == z and abs(b - y) < 2:
                if a == x - 2:
                    left[i].append(j)
                elif a == x + 2:
                    right[i].append(j)
    return cover, left, right


def is_free(i, present, cover, left, right):
    if any(present[j] for j in cover[i]):
        return False
    return not any(present[j] for j in left[i]) or not any(present[j] for j in right[i])


def check_deal(num, entry, layouts):
    li = entry.get('l')
    if not isinstance(li, int) or not (0 <= li < len(layouts)):
        return 'layout index %r invalid' % (li,)
    try:
        tiles = decode_layout(layouts[li]['t'])
    except (ValueError, KeyError) as e:
        return 'layout %d undecodable: %s' % (li, e)
    err = layout_error(tiles)
    if err:
        return 'layout %d (%s): %s' % (li, layouts[li].get('n'), err)
    n = len(tiles)
    fs = entry.get('f', '')
    if len(fs) != n:
        return 'faces string has %d symbols for %d tiles' % (len(fs), n)
    if any(c not in FACES for c in fs):
        return 'unknown face symbol'
    faces = [FACES.index(c) for c in fs]
    for f in set(faces):
        cnt = faces.count(f)
        if (f < 34 and cnt > 4) or (f >= 34 and cnt > 1):
            return 'face %d appears %d times' % (f, cnt)
    o = entry.get('o', '')
    if len(o) != 2 * n or any(c not in ALPHA36 for c in o):
        return 'removal order has wrong length or symbols'
    idx = [ALPHA36.index(o[k]) * 36 + ALPHA36.index(o[k + 1]) for k in range(0, len(o), 2)]
    if sorted(idx) != list(range(n)):
        return 'removal order is not a permutation of the %d tiles' % n
    cover, left, right = relations(tiles)
    present = [True] * n
    for step in range(0, n, 2):
        a, b = idx[step], idx[step + 1]
        if not (present[a] and present[b]) or a == b:
            return 'step %d: tile already removed' % (step // 2 + 1)
        if not is_free(a, present, cover, left, right) or not is_free(b, present, cover, left, right):
            return 'step %d: tile %d or %d is not free' % (step // 2 + 1, a, b)
        if match_key(faces[a]) != match_key(faces[b]):
            return 'step %d: faces %d and %d do not match' % (step // 2 + 1, faces[a], faces[b])
        present[a] = present[b] = False
    if any(present):
        return 'board not cleared'
    return None


def main(argv):
    apps = [a.rstrip('/') for a in argv if not a.startswith('-')]
    if apps and APP not in apps:
        print('check_mahjong_solvable: skip (%s not in run)' % APP)
        return 0
    try:
        src = open(GAME, encoding='utf-8').read()
        layouts = extract_array(src, 'MJ_LAYOUTS')
        campaign = extract_array(src, 'CAMPAIGN')
    except (OSError, ValueError) as e:
        print('✗ check_mahjong_solvable: %s' % e)
        return 1
    bad = []
    for i, entry in enumerate(campaign):
        err = check_deal(i + 1, entry, layouts)
        if err:
            bad.append('level %d: %s' % (i + 1, err))
    if len(campaign) < MIN_LEVELS:
        bad.append('only %d deals (release floor %d)' % (len(campaign), MIN_LEVELS))
    if bad:
        print('✗ check_mahjong_solvable: %d problem(s)' % len(bad))
        for b in bad[:20]:
            print('   ' + b)
        return 1
    tiles = sum(len(decode_layout(layouts[e['l']]['t'])) for e in campaign)
    print('✓ check_mahjong_solvable: %d deals on %d layouts replay to an empty board '
          '(%d tiles, every step two free matching tiles)' % (len(campaign), len(layouts), tiles))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
