#!/usr/bin/env python3
"""check_solitaire_winnable.py — every shipped Solitaire deal is WINNABLE.

Solitaire (Klondike, draw-1) ships 500 numbered deals (`const CAMPAIGN`) and a
364-day Daily Deal pool (`const KS_DAILY`), each stored as "<seed>:<moves>".
The game deals a seed with its KLONDIKE CORE (ksRng = mulberry32 → Fisher-Yates
with `r() % (i+1)` → 7 columns dealt row by row, column c holding c face-down
cards under one face-up, the remaining 24 cards the stock in draw order).

This gate ports that shuffle and the rules bit-exactly (stdlib only), re-deals
every deal from its seed and replays its stored winning line move by move:

  BLOCK  any illegal move (draw from an empty stock, recycle with stock left,
         a card onto a wrong rank/colour, a non-King into an empty column, a
         wrong-suit/rank foundation play, a column→column move with no fitting
         card), an undecodable token, a line that ends with any foundation
         short of 13 cards, a duplicate seed, fewer than 500 numbered deals,
         a daily pool of the wrong size.
  BLOCK  (when `node` is on PATH) the game's own JS core deals differently from
         this port for a sample of seeds — the port must stay bit-exact.

Codec: 'a'..'x' = 1..24 draws · 'z' = recycle waste → stock · otherwise two
chars <src><dst>: src 0-6 column | W waste | S H D C foundation of that suit;
dst 0-6 column | F foundation. A column→column move carries the single card of
the source's face-up run that fits the destination (a King for an empty column)
plus everything above it.

Usage: python3 scripts/check_solitaire_winnable.py [AppDir]   (default Solitaire)
Exit 0 = OK, 1 = blocked.
"""
import json
import os
import re
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = sys.argv[1] if len(sys.argv) > 1 else "Solitaire"
GAME = os.path.join(BASE, APP, "android", "app", "src", "main", "assets", "game.html")
MIN_DEALS = 500
DAILY_SIZE = 364
M32 = 0xFFFFFFFF
RED = (0, 1, 1, 0)          # ♠ ♥ ♦ ♣
FS = "SHDC"


def imul(a, b):
    return (a * b) & M32


def rng(seed):
    """mulberry32, integer output — mirrors ksRng() in game.html."""
    st = [seed & M32]

    def nxt():
        a = (st[0] + 0x6D2B79F5) & M32
        st[0] = a
        t = imul(a ^ (a >> 15), 1 | a)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
        return (t ^ (t >> 14)) & M32
    return nxt


def deal(seed):
    r = rng(seed)
    d = list(range(52))
    for i in range(51, 0, -1):
        j = r() % (i + 1)
        d[i], d[j] = d[j], d[i]
    t = [[] for _ in range(7)]
    k = 0
    for row in range(7):
        for c in range(row, 7):
            t[c].append(d[k])
            k += 1
    return {"t": t, "h": [0, 1, 2, 3, 4, 5, 6], "T": d[28:], "p": 0, "f": [0, 0, 0, 0]}


def suit(c):
    return c // 13


def rank(c):
    return c % 13


def stacks(x, onto):
    return rank(x) == rank(onto) - 1 and RED[suit(x)] != RED[suit(onto)]


def flip(S, c):
    n = len(S["t"][c])
    if S["h"][c] >= n:
        S["h"][c] = n - 1 if n else 0


def decode(s):
    out, i = [], 0
    while i < len(s):
        ch = s[i]
        if ch == "z":
            out.append(("r",))
            i += 1
            continue
        if "a" <= ch <= "x":
            out.extend([("d",)] * (ord(ch) - 96))
            i += 1
            continue
        if i + 1 >= len(s):
            raise ValueError("dangling token at %d" % i)
        a, b = s[i], s[i + 1]
        if a in "0123456":
            src = int(a)
        elif a == "W":
            src = 7
        elif a in FS:
            src = 8 + FS.index(a)
        else:
            raise ValueError("bad source %r at %d" % (a, i))
        if b in "0123456":
            dst = int(b)
        elif b == "F":
            dst = 8
        else:
            raise ValueError("bad destination %r at %d" % (b, i + 1))
        out.append(("m", src, dst))
        i += 2
    return out


def run_start(S, c, d):
    src, dst = S["t"][c], S["t"][d]
    if not src:
        return -1
    if not dst:
        for i in range(S["h"][c], len(src)):
            if rank(src[i]) == 12:
                return i
        return -1
    top = dst[-1]
    for i in range(S["h"][c], len(src)):
        if stacks(src[i], top):
            return i
    return -1


def apply(S, mv):
    """Apply one move; return None if legal, else a reason string."""
    if mv[0] == "d":
        if S["p"] >= len(S["T"]):
            return "draw from an empty stock"
        S["p"] += 1
        return None
    if mv[0] == "r":
        if S["p"] != len(S["T"]) or S["p"] == 0:
            return "recycle while the stock still has cards (or nothing to recycle)"
        S["p"] = 0
        return None
    _, s, d = mv
    if s == d:
        return "move onto itself"
    if s >= 8 and d == 8:
        return "foundation to foundation"
    # the card that lands
    if s < 7:
        col = S["t"][s]
        if not col:
            return "move from empty column %d" % s
        if d < 7:
            i = run_start(S, s, d)
            if i < 0:
                return "no card in column %d fits column %d" % (s, d)
        else:
            i = len(col) - 1
        x = col[i]
    elif s == 7:
        if S["p"] == 0:
            return "play from an empty waste"
        x = S["T"][S["p"] - 1]
    else:
        su = s - 8
        if S["f"][su] == 0:
            return "take from an empty foundation"
        x = su * 13 + S["f"][su] - 1
    if d == 8:
        if S["f"][suit(x)] != rank(x):
            return "card %d is not next on its foundation" % x
    else:
        dst = S["t"][d]
        if not dst:
            if rank(x) != 12:
                return "non-King into empty column %d" % d
        elif not stacks(x, dst[-1]):
            return "card %d does not stack on column %d" % (x, d)
    # commit
    if s < 7:
        cards = S["t"][s][i:]
        del S["t"][s][i:]
        flip(S, s)
    elif s == 7:
        cards = [S["T"].pop(S["p"] - 1)]
        S["p"] -= 1
    else:
        cards = [x]
        S["f"][s - 8] -= 1
    if d == 8:
        S["f"][suit(cards[0])] += 1
    else:
        S["t"][d].extend(cards)
    return None


def replay(seed, sol):
    S = deal(seed)
    try:
        moves = decode(sol)
    except ValueError as e:
        return "undecodable line: %s" % e
    for n, mv in enumerate(moves, 1):
        why = apply(S, mv)
        if why:
            return "illegal move %d (%s): %s" % (n, mv, why)
    if S["f"] != [13, 13, 13, 13]:
        return "line ends with foundations %s (not four complete)" % S["f"]
    return None


def array_strings(html, name):
    m = re.search(r"(?:const|var|let)\s+" + name + r"\s*=\s*\[(.*?)\];", html, re.S)
    if not m:
        return None
    return re.findall(r"'([^']*)'|\"([^\"]*)\"", m.group(1))


def entries(html, name):
    raw = array_strings(html, name)
    if raw is None:
        return None
    out = []
    for a, b in raw:
        s = a or b
        mm = re.fullmatch(r"(\d+):([0-6WSHDCFa-xz]+)", s)
        out.append((int(mm.group(1)), mm.group(2)) if mm else (None, s))
    return out


def node_crosscheck(html, seeds):
    node = shutil.which("node")
    if not node:
        return None
    a, b = html.find("/*KSCORE{*/"), html.find("/*}KSCORE*/")
    if a < 0 or b < 0:
        return "KSCORE block missing from game.html"
    js = (html[a:b] + "\nconst out={};for(const s of %s){const S=ksDeal(s,1);out[s]={t:S.t,T:S.T};}"
          "process.stdout.write(JSON.stringify(out));" % json.dumps(seeds))
    try:
        res = subprocess.run([node, "-e", js], capture_output=True, text=True, timeout=60)
    except Exception as e:  # pragma: no cover
        return None
    if res.returncode != 0:
        return "game KSCORE failed under node: " + res.stderr.strip()[:200]
    got = json.loads(res.stdout)
    for s in seeds:
        d = deal(s)
        g = got[str(s)]
        if g["t"] != d["t"] or g["T"] != d["T"]:
            return "seed %d: game deal != Python port (shuffle drifted)" % s
    return ""


def main():
    if not os.path.isfile(GAME):
        print("✗ %s: game.html not found" % APP)
        return 1
    html = open(GAME, encoding="utf-8").read()
    errors = []
    camp = entries(html, "CAMPAIGN")
    daily = entries(html, "KS_DAILY")
    if camp is None:
        errors.append("no `const CAMPAIGN = [...]` array")
        camp = []
    if daily is None:
        errors.append("no `const KS_DAILY = [...]` daily pool")
        daily = []
    if len(camp) < MIN_DEALS:
        errors.append("only %d numbered deals (< %d)" % (len(camp), MIN_DEALS))
    if daily and len(daily) != DAILY_SIZE:
        errors.append("daily pool has %d deals (need %d — index = day %% %d)" % (len(daily), DAILY_SIZE, DAILY_SIZE))
    seen = {}
    pars = []
    for label, lst in (("deal", camp), ("daily", daily)):
        for i, (seed, sol) in enumerate(lst, 1):
            tag = "%s %d" % (label, i)
            if seed is None:
                errors.append("%s: malformed entry %r" % (tag, sol[:40]))
                continue
            if seed in seen:
                errors.append("%s: seed %d duplicates %s" % (tag, seed, seen[seed]))
            seen[seed] = tag
            why = replay(seed, sol)
            if why:
                errors.append("%s (seed %d): %s" % (tag, seed, why))
            elif label == "deal":
                pars.append(len(decode(sol)))
    sample = [s for s, _ in (camp[:12] + daily[:6]) if s is not None]
    cc = node_crosscheck(html, sample) if sample else None
    if cc:
        errors.append(cc)
    if errors:
        for e in errors[:40]:
            print("✗ " + e)
        if len(errors) > 40:
            print("✗ … %d more" % (len(errors) - 40))
        print("✗ %s: %d winnability problem(s)" % (APP, len(errors)))
        return 1
    print("OK %s: %d numbered deals + %d daily deals re-dealt from seed and replayed to four "
          "complete foundations (par %d–%d)%s" % (
              APP, len(camp), len(daily), min(pars), max(pars),
              "; JS core deal == Python port" if cc == "" else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
