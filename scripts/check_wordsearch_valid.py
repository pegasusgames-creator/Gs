#!/usr/bin/env python3
"""check_wordsearch_valid.py — every shipped Word Search grid is fair and clean.

Word Search ships its 500 campaign grids as stored letters (no runtime
generation for the campaign). This gate decodes CAMPAIGN, WS_THEMES and
WS_BLOCK_H straight out of WordSearch's game.html and, for EVERY level:

  * band: grid size, word count, word lengths and placement directions match
    the level's band (chapters of 50: 6x6 for levels 1-50 ... 15x15 for
    451-500; words 8-20; directions open up E/S -> +SE -> +NE -> +W/N -> all 8);
  * every listed word is A-Z, comes from the level's curated theme list, and
    is present EXACTLY ONCE along a straight line (all 8 directions are
    scanned; an occurrence is a set of cells, so forward/backward readings of
    the same cells count once), at the stored start/direction;
  * no listed word sits wholly inside another listed word's cells;
  * no blocklisted word appears anywhere in the grid in any of the 8
    directions (blocklist = WordSearch/test/blocklist_rot13.txt, ROT13 so the
    repo holds no plaintext profanity);
  * bonus-word levels (idx % 3 == 1, idx >= 4, not a message level) hide one
    unlisted theme word exactly once; other levels hide none;
  * hidden-message levels (every 10th level on grids up to 12x12) have the
    message spelled, in reading order, by exactly the cells no listed word
    uses; other levels carry no message.

It also screens the on-device word lists (WS_THEMES, used by Daily and
Endless boards) — no blocklisted word inside any word or message in either
reading direction, no palindromes, A-Z only — and asserts WS_BLOCK_H (the
FNV-1a hashes the runtime generator rejects) equals the blocklist, and that
the campaign has >= 500 levels. Any failure BLOCKS.

Extra (developer) mode: `--boards file.json` validates a JSON list of boards
dumped by test/verify_runtime_boards.js (Daily/Endless generator output).

Gate contract: with no arguments, or with WordSearch among the arguments, it
checks WordSearch; with only other app names it prints a skip line, exit 0.

Stdlib only.  Usage: python3 scripts/check_wordsearch_valid.py [App ...]
"""
import codecs
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = 'WordSearch'
GAME = os.path.join(BASE, APP, 'android', 'app', 'src', 'main', 'assets', 'game.html')
BLOCKFILE = os.path.join(BASE, APP, 'test', 'blocklist_rot13.txt')
MIN_LEVELS = 500
CHAPTER = 50

# direction index -> (dr, dc): E SE S SW W NW N NE
DIRS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
DIR_NAMES = ['E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'NE']
B36 = '0123456789abcdefghijklmnopqrstuvwxyz'

WORD_RANGE = {6: (8, 8), 7: (8, 10), 8: (9, 11), 9: (10, 12), 10: (11, 13),
              11: (12, 14), 12: (13, 15), 13: (14, 17), 14: (15, 18), 15: (16, 20)}


# ── band table (shared with WordSearch/test/gen_levels.py) ─────────────────
def band(idx):
    """Band of 0-based campaign level idx."""
    n = 6 + idx // CHAPTER
    if n > 15:
        n = 15
    lo, hi = WORD_RANGE[n]
    j = idx % CHAPTER
    target = lo + (j * (hi - lo + 1)) // CHAPTER
    if idx < 15:
        dirs = {0, 2}
    elif idx < 50:
        dirs = {0, 1, 2}
    elif idx < 100:
        dirs = {0, 1, 2, 7}
    elif idx < 150:
        dirs = {0, 1, 2, 7, 4, 6}
    else:
        dirs = set(range(8))
    min_len = 3 if n <= 8 else 4
    max_len = 5 if idx < 15 else min(n, 13)
    message = (idx + 1) % 10 == 0 and n <= 12
    bonus = (not message) and idx >= 4 and idx % 3 == 1
    return {'n': n, 'words': (lo, hi), 'target': target, 'dirs': dirs,
            'len': (min_len, max_len), 'message': message, 'bonus': bonus}


# ── blocklist ─────────────────────────────────────────────────────────────
def load_blocklist(path=BLOCKFILE):
    out = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            out.append(codecs.decode(line, 'rot13').upper())
    return out


def fnv1a(s):
    h = 0x811c9dc5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xffffffff
    return h


def has_blocked(text, block):
    """True if any blocked word reads inside text forwards or backwards."""
    t = text.upper()
    r = t[::-1]
    return any(b in t or b in r for b in block)


# ── grid scanning ─────────────────────────────────────────────────────────
def lines(n):
    """All maximal straight lines (cell index lists) in the 4 base
    orientations E, S, SE, SW; reversing them gives the other 4."""
    out = []
    for r in range(n):
        out.append([r * n + c for c in range(n)])
    for c in range(n):
        out.append([r * n + c for r in range(n)])
    for k in range(-(n - 1), n):            # SE diagonals: c - r = k
        cells = [r * n + (r + k) for r in range(n) if 0 <= r + k < n]
        if len(cells) >= 2:
            out.append(cells)
    for k in range(0, 2 * n - 1):           # SW diagonals: r + c = k
        cells = [r * n + (k - r) for r in range(n) if 0 <= k - r < n]
        if len(cells) >= 2:
            out.append(cells)
    return out


_LINES = {}


def all_lines(n):
    if n not in _LINES:
        base = lines(n)
        _LINES[n] = base + [list(reversed(l)) for l in base]
    return _LINES[n]


def occurrences(grid, n, word):
    """Distinct cell-sets where word reads along a straight line."""
    found = set()
    for cells in all_lines(n):
        s = ''.join(grid[i] for i in cells)
        start = s.find(word)
        while start != -1:
            found.add(frozenset(cells[start:start + len(word)]))
            start = s.find(word, start + 1)
    return found


def blocked_hits(grid, n, block):
    hits = set()
    for cells in all_lines(n):
        s = ''.join(grid[i] for i in cells)
        for b in block:
            if b in s:
                hits.add(b)
    return hits


def path(n, word_len, r, c, d):
    dr, dc = DIRS[d]
    out = []
    for i in range(word_len):
        rr, cc = r + dr * i, c + dc * i
        if not (0 <= rr < n and 0 <= cc < n):
            return None
        out.append(rr * n + cc)
    return out


def parse_place(tok):
    """'OCEAN0a2' -> ('OCEAN', r, c, d)."""
    if len(tok) < 4:
        raise ValueError('placement too short: %r' % tok)
    w, pos = tok[:-3], tok[-3:]
    if not re.fullmatch(r'[A-Z]+', w):
        raise ValueError('word not A-Z: %r' % tok)
    return w, B36.index(pos[0]), B36.index(pos[1]), int(pos[2])


def check_board(grid, n, words, bonus, message, block, allowed_dirs=None,
                theme_words=None, len_range=None):
    """Validate one board. words: [(w,r,c,d)], bonus: (w,r,c,d)|None,
    message: str|None. Returns list of problems (empty = OK)."""
    p = []
    if len(grid) != n * n:
        return ['grid has %d letters, expected %d' % (len(grid), n * n)]
    if not re.fullmatch(r'[A-Z]+', grid):
        p.append('grid has non A-Z characters')
    seen = set()
    cellsets = []
    for (w, r, c, d) in words:
        if w in seen:
            p.append('duplicate listed word %s' % w)
        seen.add(w)
        if len(w) < 3 or len(w) > n:
            p.append('%s: length %d outside 3..%d' % (w, len(w), n))
        if len_range and not (len_range[0] <= len(w) <= len_range[1]):
            p.append('%s: length %d outside band %d..%d' % (w, len(w), len_range[0], len_range[1]))
        if theme_words is not None and w not in theme_words:
            p.append('%s: not in the level theme list' % w)
        if w == w[::-1]:
            p.append('%s: palindrome' % w)
        if allowed_dirs is not None and d not in allowed_dirs:
            p.append('%s: direction %s not allowed in this band' % (w, DIR_NAMES[d] if 0 <= d < 8 else d))
        cells = path(n, len(w), r, c, d)
        if cells is None or ''.join(grid[i] for i in cells) != w:
            p.append('%s: stored placement (%d,%d,%s) does not spell it' % (w, r, c, d))
            continue
        occ = occurrences(grid, n, w)
        if len(occ) != 1:
            p.append('%s: present %d times (must be exactly once)' % (w, len(occ)))
        cellsets.append((w, frozenset(cells)))
    for i, (a, ca) in enumerate(cellsets):
        for j, (b, cb) in enumerate(cellsets):
            if i != j and ca < cb:
                p.append('%s lies wholly inside %s' % (a, b))
    if bonus:
        w, r, c, d = bonus
        if w in seen:
            p.append('bonus %s is also a listed word' % w)
        if theme_words is not None and w not in theme_words:
            p.append('bonus %s: not in the level theme list' % w)
        if allowed_dirs is not None and d not in allowed_dirs:
            p.append('bonus %s: direction not allowed' % w)
        if w == w[::-1]:
            p.append('bonus %s: palindrome' % w)
        cells = path(n, len(w), r, c, d)
        if cells is None or ''.join(grid[i] for i in cells) != w:
            p.append('bonus %s: stored placement does not spell it' % w)
        else:
            occ = occurrences(grid, n, w)
            if len(occ) != 1:
                p.append('bonus %s: present %d times (must be exactly once)' % (w, len(occ)))
            for (lw, cs) in cellsets:
                if frozenset(cells) <= cs:
                    p.append('bonus %s lies wholly inside %s' % (w, lw))
    if message:
        if not re.fullmatch(r'[A-Z ]+', message):
            p.append('message has characters other than A-Z and space')
        used = set()
        for _, cs in cellsets:
            used |= cs
        left = ''.join(grid[i] for i in range(n * n) if i not in used)
        if left != message.replace(' ', ''):
            p.append('leftover letters %r do not spell the message %r' % (left, message))
        if bonus:
            p.append('message level must not also hide a bonus word')
    hits = blocked_hits(grid, n, block)
    if hits:
        p.append('blocklisted word(s) readable in the grid: %d hit(s)' % len(hits))
    return p


# ── game.html extraction ──────────────────────────────────────────────────
def extract_json(src, name):
    m = re.search(r'const\s+' + name + r'\s*=\s*\[', src)
    if not m:
        raise ValueError('const %s = [...] not found' % name)
    i = m.end() - 1
    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(src)):
        ch = src[j]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return json.loads(src[i:j + 1])
    raise ValueError('unterminated %s' % name)


def check_themes(themes, block):
    p = []
    for t in themes:
        name = t.get('n', '?')
        words = t.get('w', [])
        if len(set(words)) != len(words):
            p.append('theme %s: duplicate words' % name)
        for w in words:
            if not re.fullmatch(r'[A-Z]{3,15}', w):
                p.append('theme %s: bad word %r' % (name, w))
            elif w == w[::-1]:
                p.append('theme %s: palindrome %s' % (name, w))
            elif has_blocked(w, block):
                p.append('theme %s: word %s contains a blocklisted word' % (name, w))
        usable = [w for w in words if 4 <= len(w) <= 10]
        if len(usable) < 24:
            p.append('theme %s: only %d words of 4-10 letters (Daily/Endless need 24)' % (name, len(usable)))
        if not t.get('e'):
            p.append('theme %s: no emoji' % name)
    return p


def check_app():
    problems = []
    if not os.path.isfile(GAME):
        return ['game.html missing']
    if not os.path.isfile(BLOCKFILE):
        return ['blocklist %s missing' % os.path.relpath(BLOCKFILE, BASE)]
    block = load_blocklist()
    if len(block) < 50:
        problems.append('blocklist has only %d words' % len(block))
    src = open(GAME, encoding='utf-8').read()
    try:
        camp = extract_json(src, 'CAMPAIGN')
        themes = extract_json(src, 'WS_THEMES')
        hashes = extract_json(src, 'WS_BLOCK_H')
    except ValueError as e:
        return [str(e)]
    if sorted(set(hashes)) != sorted({fnv1a(b) for b in block}):
        problems.append('WS_BLOCK_H does not match the blocklist (runtime generator would miss words)')
    m = re.search(r'const\s+WS_BLOCK_MAX\s*=\s*(\d+)', src)
    if not m or max(len(b) for b in block) > int(m.group(1)):
        problems.append('runtime WS_BLOCK_MAX missing or shorter than the longest blocklisted word')
    problems += check_themes(themes, block)
    if len(camp) < MIN_LEVELS:
        problems.append('campaign has %d levels (< %d)' % (len(camp), MIN_LEVELS))
    n_msg = n_bonus = 0
    for idx, e in enumerate(camp):
        tag = 'level %d' % (idx + 1)
        try:
            ti, n, grid, wstr, bstr, msg = e
            words = [parse_place(t) for t in wstr.split()]
            bonus = parse_place(bstr) if bstr else None
        except (ValueError, TypeError) as ex:
            problems.append('%s: unparseable entry (%s)' % (tag, ex))
            continue
        b = band(idx)
        if not (isinstance(ti, int) and 0 <= ti < len(themes)):
            problems.append('%s: bad theme index %r' % (tag, ti))
            continue
        if n != b['n']:
            problems.append('%s: grid %dx%d, band says %dx%d' % (tag, n, n, b['n'], b['n']))
        lo, hi = b['words']
        if not (lo <= len(words) <= hi):
            problems.append('%s: %d words, band says %d-%d' % (tag, len(words), lo, hi))
        if b['message'] != bool(msg):
            problems.append('%s: %s' % (tag, 'hidden-message level has no message' if b['message']
                                        else 'unexpected hidden message'))
        if b['bonus'] != bool(bonus):
            problems.append('%s: %s' % (tag, 'bonus level has no bonus word' if b['bonus']
                                        else 'unexpected bonus word'))
        if msg and has_blocked(msg, block):
            problems.append('%s: message contains a blocklisted word' % tag)
        n_msg += bool(msg)
        n_bonus += bool(bonus)
        for q in check_board(grid, n, words, bonus, msg or None, block, b['dirs'],
                             set(themes[ti]['w']), b['len']):
            problems.append('%s: %s' % (tag, q))
    if camp and n_msg == 0:
        problems.append('no hidden-message levels found')
    if camp and n_bonus == 0:
        problems.append('no bonus-word levels found')
    return problems, len(camp), n_msg, n_bonus


def check_boards_file(path):
    block = load_blocklist()
    boards = json.load(open(path, encoding='utf-8'))
    bad = 0
    for k, bd in enumerate(boards):
        words = [parse_place(t) for t in bd['words']]
        bonus = parse_place(bd['bonus']) if bd.get('bonus') else None
        probs = check_board(bd['grid'], bd['n'], words, bonus, None, block,
                            set(bd['dirs']) if 'dirs' in bd else None,
                            set(bd['theme']) if 'theme' in bd else None)
        if probs:
            bad += 1
            if bad <= 10:
                print('  ✗ board %d (%s): %s' % (k, bd.get('label', ''), '; '.join(probs[:3])))
    print(('✓' if not bad else '✗') + ' %d runtime boards checked, %d bad' % (len(boards), bad))
    return 1 if bad else 0


def main(argv):
    if '--boards' in argv:
        return check_boards_file(argv[argv.index('--boards') + 1])
    apps = [a for a in argv if not a.startswith('-')]
    if apps and APP not in apps:
        print('check_wordsearch_valid: skip (%s not in run)' % APP)
        return 0
    res = check_app()
    if isinstance(res, list):
        problems, total, n_msg, n_bonus = res, 0, 0, 0
    else:
        problems, total, n_msg, n_bonus = res
    if problems:
        print('✗ %s: %d word-search problem(s)' % (APP, len(problems)))
        for q in problems[:40]:
            print('   - ' + q)
        if len(problems) > 40:
            print('   … %d more' % (len(problems) - 40))
        return 1
    print('✓ %s: %d grids — every listed word exactly once on a straight line, '
          'bands match, no blocklisted word in any direction (%d hidden-message, '
          '%d bonus-word levels)' % (APP, total, n_msg, n_bonus))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
