#!/usr/bin/env python3
"""gen_levels.py — mine Word Search's 500 campaign grids.

For each level the band (scripts/check_wordsearch_valid.py::band — the gate
and this miner share it) fixes the grid size, word count, word lengths and
directions. A seeded RNG picks words from the level's curated theme
(test/ws_content.py, screened against test/blocklist_rot13.txt in both
reading directions), places them longest-first (crossings allowed, never two
words overlapping along the same line, no word inside another), then:

  * bonus levels: hides one extra, unlisted theme word;
  * hidden-message levels: chooses a message whose letter count equals the
    number of unused cells and writes it into them in reading order;
  * otherwise fills the free cells with letters.

Every candidate grid goes through the gate's own check_board() (each listed
word exactly once, no blocklisted word in any direction ...) and is redrawn
until it passes, so every shipped grid passes the gate by construction.

Writes test/levels.json and test/levels_region.js (the LEVELS region:
WS_THEMES for the on-device Daily/Endless generator, WS_BLOCK_H, CAMPAIGN).
Install with: python3 scripts/shell_region.py WordSearch LEVELS --set WordSearch/test/levels_region.js

Deterministic. Stdlib only.  Usage: python3 WordSearch/test/gen_levels.py
"""
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(BASE, 'scripts'))
sys.path.insert(0, HERE)

import check_wordsearch_valid as gate  # noqa: E402
from ws_content import THEMES, GENERIC_MESSAGES, FACT_PREFIXES  # noqa: E402

N_LEVELS = 500
FREQ = ('E' * 127 + 'T' * 91 + 'A' * 82 + 'O' * 75 + 'I' * 70 + 'N' * 67 + 'S' * 63 + 'H' * 61 +
        'R' * 60 + 'D' * 43 + 'L' * 40 + 'C' * 28 + 'U' * 28 + 'M' * 24 + 'W' * 24 + 'F' * 22 +
        'G' * 20 + 'Y' * 20 + 'P' * 19 + 'B' * 15 + 'V' * 10 + 'K' * 8 + 'J' * 2 + 'X' * 2 +
        'Q' * 1 + 'Z' * 1)


def screen(block):
    """Screened themes: [{'n','e','w':[...], 'msgs':[...]}]. Prints drops."""
    out = []
    dropped = []
    for (name, emoji, words, facts, sayings) in THEMES:
        ws = []
        for w in words.split():
            if not re.fullmatch(r'[A-Z]{3,15}', w):
                dropped.append((name, w, 'format'))
            elif w == w[::-1]:
                dropped.append((name, w, 'palindrome'))
            elif gate.has_blocked(w, block):
                dropped.append((name, w, 'blocklist'))
            elif w in ws:
                dropped.append((name, w, 'duplicate'))
            else:
                ws.append(w)
        msgs = []
        for f in facts:
            for pre in FACT_PREFIXES:
                msgs.append(((pre + ' ' + f).strip(), 0 if not pre else 1))
        for s in sayings:
            msgs.append((s, 0))
        keep = []
        for m, pri in msgs:
            if gate.has_blocked(m.replace(' ', ''), block):
                dropped.append((name, m, 'message blocklist'))
            else:
                keep.append((m, pri))
        out.append({'n': name, 'e': emoji, 'w': ws, 'msgs': keep})
    gen = []
    for m in GENERIC_MESSAGES:
        if gate.has_blocked(m.replace(' ', ''), block):
            dropped.append(('generic', m, 'message blocklist'))
        else:
            gen.append(m)
    return out, gen, dropped


class Board:
    def __init__(self, n):
        self.n = n
        self.g = [None] * (n * n)
        self.axes = [set() for _ in range(n * n)]   # line axes (d % 4) through each cell
        self.placed = []                            # (w, r, c, d)

    def candidates(self, w, dirs):
        n = self.n
        out = []
        L = len(w)
        for d in dirs:
            dr, dc = gate.DIRS[d]
            ax = d % 4
            for r in range(n):
                er = r + dr * (L - 1)
                if not 0 <= er < n:
                    continue
                for c in range(n):
                    ec = c + dc * (L - 1)
                    if not 0 <= ec < n:
                        continue
                    ov = 0
                    ok = True
                    for i in range(L):
                        k = (r + dr * i) * n + (c + dc * i)
                        ch = self.g[k]
                        if ch is None:
                            continue
                        if ch != w[i] or ax in self.axes[k]:
                            ok = False
                            break
                        ov += 1
                    if ok and ov < L:
                        out.append((ov, r, c, d))
        return out

    def put(self, w, r, c, d):
        dr, dc = gate.DIRS[d]
        for i in range(len(w)):
            k = (r + dr * i) * self.n + (c + dc * i)
            self.g[k] = w[i]
            self.axes[k].add(d % 4)
        self.placed.append((w, r, c, d))


def related(a, b):
    return a in b or b in a or a[::-1] in b or b in a[::-1]


def try_place(rng, bd, w, dirs, overlap_bias):
    cands = bd.candidates(w, dirs)
    if not cands:
        return False
    if overlap_bias > 0 and rng.random() < overlap_bias:
        best = max(c[0] for c in cands)
        cands = [c for c in cands if c[0] == best]
    ov, r, c, d = cands[rng.randrange(len(cands))]
    bd.put(w, r, c, d)
    return True


def layout(rng, n, pool, count, dirs, overlap_bias, long_bias):
    """Place `count` words from pool. Returns Board or None."""
    order = pool[:]
    rng.shuffle(order)
    if long_bias:
        order.sort(key=lambda w: -len(w) + rng.random() * long_bias)
    else:
        # pick the subset first (random), then place longest first
        pass
    bd = Board(n)
    chosen = []
    for w in order:
        if len(chosen) >= count:
            break
        if any(related(w, p) for p in chosen):
            continue
        chosen.append(w)
    if len(chosen) < count:
        return None
    # place longest first; on failure, swap in another pool word
    spare = [w for w in order if w not in chosen]
    chosen.sort(key=lambda w: -len(w))
    final = []
    for w in chosen:
        ok = try_place(rng, bd, w, dirs, overlap_bias)
        while not ok and spare:
            alt = spare.pop(0)
            if any(related(alt, p) for p in final) or any(related(alt, p) for p in chosen if p != w):
                continue
            w = alt
            ok = try_place(rng, bd, w, dirs, overlap_bias)
        if not ok:
            return None
        final.append(w)
    return bd


def fill_letters(rng, bd, words):
    pool = ''.join(words)
    out = bd.g[:]
    for k in range(len(out)):
        if out[k] is None:
            out[k] = pool[rng.randrange(len(pool))] if rng.random() < 0.5 else FREQ[rng.randrange(len(FREQ))]
    return ''.join(out)


def enc(w, r, c, d):
    return w + gate.B36[r] + gate.B36[c] + str(d)


def gen_level(idx, ti, theme, generic, block):
    b = gate.band(idx)
    n = b['n']
    lo, hi = b['words']
    mn, mx = b['len']
    pool = [w for w in theme['w'] if mn <= len(w) <= mx]
    tw = set(theme['w'])
    dirs = sorted(b['dirs'])
    rng = random.Random(1000003 * (idx + 1) + 7 * ti)
    for attempt in range(4000):
        if b['message']:
            count = rng.randint(max(lo, b['target']), hi)
            bd = layout(rng, n, pool, count, dirs, 0.85, 3.0 if n >= 9 else 0)
        else:
            count = b['target']
            bd = layout(rng, n, pool, count, dirs, 0.35, 0)
        if bd is None:
            continue
        words = [p[0] for p in bd.placed]
        bonus = None
        if b['bonus']:
            bpool = [w for w in theme['w'] if 4 <= len(w) <= min(n, 9) and w not in words
                     and not any(related(w, p) for p in words)]
            rng.shuffle(bpool)
            for w in bpool[:12]:
                if try_place(rng, bd, w, dirs, 0.2):
                    bonus = bd.placed.pop()  # keep it out of the listed words
                    break
            if bonus is None:
                continue
        if b['message']:
            free = [k for k in range(n * n) if bd.g[k] is None]
            F = len(free)
            opts = [m for m, pri in theme['msgs'] if len(m.replace(' ', '')) == F]
            rng.shuffle(opts)
            gopts = [m for m in generic if len(m.replace(' ', '')) == F]
            rng.shuffle(gopts)
            for m in (opts + gopts)[:8]:
                letters = m.replace(' ', '')
                g = bd.g[:]
                for k, ch in zip(free, letters):
                    g[k] = ch
                grid = ''.join(g)
                probs = gate.check_board(grid, n, bd.placed, None, m, block, b['dirs'], tw, b['len'])
                if not probs:
                    return [ti, n, grid, ' '.join(enc(*p) for p in sorted(bd.placed)), '', m]
            continue
        for _ in range(30):
            grid = fill_letters(rng, bd, words)
            probs = gate.check_board(grid, n, bd.placed, bonus, None, block, b['dirs'], tw, b['len'])
            if not probs:
                return [ti, n, grid, ' '.join(enc(*p) for p in sorted(bd.placed)),
                        enc(*bonus) if bonus else '', '']
    return None


def main():
    block = gate.load_blocklist()
    themes, generic, dropped = screen(block)
    if '--show-drops' in sys.argv:
        for d in dropped:
            print('  drop %-12s %-28s %s' % d)
    print('screened %d themes; dropped %d entries' % (len(themes), len(dropped)))
    T = len(themes)
    camp = []
    last = []
    for idx in range(N_LEVELS):
        b = gate.band(idx)
        mn, mx = b['len']
        k = 0
        while True:
            ti = (idx * 23 + k * 7) % T
            pool = [w for w in themes[ti]['w'] if mn <= len(w) <= mx]
            if len(pool) >= b['words'][1] + 6 and ti not in last[-6:]:
                break
            k += 1
        lv = None
        for kk in range(T):
            lv = gen_level(idx, ti, themes[ti], generic, block)
            if lv:
                break
            ti = (ti + 11) % T
        if not lv:
            print('FAILED level %d' % (idx + 1))
            return 1
        camp.append(lv)
        last.append(lv[0])
        if (idx + 1) % 50 == 0:
            print('  %3d levels mined (%dx%d)' % (idx + 1, b['n'], b['n']))
            sys.stdout.flush()
    json.dump(camp, open(os.path.join(HERE, 'levels.json'), 'w'), indent=0)
    write_region(themes, block, camp)
    print('wrote %d levels' % len(camp))
    return 0


def write_region(themes, block, camp):
    hashes = sorted({gate.fnv1a(b) for b in block})
    lines = []
    lines.append('// LEVELS — Word Search campaign (500 grids), mined by WordSearch/test/gen_levels.py')
    lines.append('// and verified by scripts/check_wordsearch_valid.py. Entry:')
    lines.append('// [themeIdx, size, "GRID row-major", "WORD+r+c+dir ...", "BONUS+r+c+dir" or "", "HIDDEN MESSAGE" or ""]')
    lines.append('// r,c base-36; dir 0..7 = E SE S SW W NW N NE.')
    lines.append('// WS_THEMES: curated, family-friendly, blocklist-screened lists (Daily/Endless use them too).')
    lines.append('const WS_THEMES = ' + json.dumps([{'n': t['n'], 'e': t['e'], 'w': t['w']} for t in themes],
                                                  ensure_ascii=False, separators=(',', ':')) + ';')
    lines.append('// FNV-1a hashes of the blocklist: on-device boards are rejected if any reads in any direction.')
    lines.append('const WS_BLOCK_H = ' + json.dumps(hashes, separators=(',', ':')) + ';')
    lines.append('const CAMPAIGN = [')
    for i, e in enumerate(camp):
        lines.append(json.dumps(e, ensure_ascii=False, separators=(',', ':')) + (',' if i < len(camp) - 1 else ''))
    lines.append('];')
    lines.append('const LEVELS = CAMPAIGN; // length contract for level-select/addendum')
    open(os.path.join(HERE, 'levels_region.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    sys.exit(main())
