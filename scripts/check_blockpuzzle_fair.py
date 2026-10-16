#!/usr/bin/env python3
"""check_blockpuzzle_fair.py — Block Puzzle's dealer is fair and its daily is
deterministic.

Block Puzzle (BlockPuzzle/) is a score game: every tray of three pieces is
dealt live by the BPCORE block in game.html (between //@@BPCORE-BEGIN and
//@@BPCORE-END). This gate ports that block 1:1 (stdlib only, bitboards) and:

  BLOCK  the BPCORE block changed since BlockPuzzle/test/golden.json was made
         (re-run `node BlockPuzzle/test/golden.js`, then this gate)
  BLOCK  the Python port disagrees with the JS golden traces (trays dealt,
         forced fallbacks, final score/board) — the port would be proving
         nothing about the shipped dealer
  BLOCK  any tray / Refresh / Revive is dealt with ZERO placeable pieces
         while some catalogue piece fits the board (simulated with a greedy
         bot AND a random-legal bot over hundreds of classic runs + a year of
         dailies — the random bot crowds the board so the fallback fires)
  BLOCK  a daily seed is not deterministic: the same day replayed gives a
         different run, two days share a seed, or the main piece sequence
         changes with how the player plays (it must be the same for everyone)
  BLOCK  a piece family is not closed under the Rotate booster's
         (o+1) % n orientation step, or the 1x1 piece is missing (the
         fairness guarantee rests on it)
  WARN   the greedy bot reaches the daily target on < 50% of days

The tutorial's first tray is a fixed preset (domino + small L + 2x2 on a board
with one gap that the domino fills), not a dealer output.

Standalone: python3 scripts/check_blockpuzzle_fair.py   (prints OK / ✗)
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = BASE / "BlockPuzzle"
HTML = APP / "android/app/src/main/assets/game.html"
GOLDEN = APP / "test/golden.json"

M32 = 0xFFFFFFFF
N = 8
FULL = (1 << 64) - 1
ROWS = [0xFF << (8 * i) for i in range(8)]
COLS = [sum(1 << (8 * r + j) for r in range(8)) for j in range(8)]
COL0, COL7, ROW0, ROW7 = COLS[0], COLS[7], ROWS[0], ROWS[7]


def imul(a, b):
    return (a * b) & M32


class Rng:
    __slots__ = ("s",)

    def __init__(self, seed):
        self.s = seed & M32


def u32(r):
    r.s = (r.s + 0x6D2B79F5) & M32
    t = r.s
    t = imul(t ^ (t >> 15), 1 | t)
    t = ((t + imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
    return (t ^ (t >> 14)) & M32


def pick(r, n):
    return (u32(r) * n) >> 32


def norm(cells):
    mr = min(c[0] for c in cells)
    mc = min(c[1] for c in cells)
    return sorted((a - mr, b - mc) for a, b in cells)


def build_orients(cells):
    out = []
    cur = norm(cells)
    for _ in range(4):
        if cur not in out:
            out.append(cur)
        cur = norm([(c, -r) for r, c in cur])
    return out


def sub_seed(seed, ti, salt):
    return (seed ^ imul(ti + 1, 0x9E3779B1) ^ imul(salt + 1, 0x85EBCA77)) & M32


def daily_seed(day):
    return (imul(day + 1, 2654435761) ^ 0x2B7E1516) & M32


def popcount(x):
    return bin(x).count("1")


class Core:
    def __init__(self, cfg):
        self.cfg = cfg
        self.fams = cfg["families"]
        self.orients = [build_orients([tuple(c) for c in f["cells"]]) for f in self.fams]
        self.masks = []
        for ors in self.orients:
            fl = []
            for cells in ors:
                h = max(a for a, _ in cells) + 1
                w = max(b for _, b in cells) + 1
                pl = []
                for r in range(N - h + 1):
                    for c in range(N - w + 1):
                        m = 0
                        for a, b in cells:
                            m |= 1 << ((r + a) * N + c + b)
                        pl.append((r, c, m))
                fl.append(pl)
            self.masks.append(fl)
        self.violations = []

    def weights(self, filled, score, daily):
        if daily:
            return [f["w"] * 100 for f in self.fams]
        st, rp = self.cfg["stress"], self.cfg["ramp"]
        stress = min(100, max(0, filled - st["from"]) * 100 // st["span"])
        ramp = min(100, score * 100 // rp["span"])
        out = []
        for f in self.fams:
            size = len(f["cells"])
            adj = 0
            if size <= 3:
                adj = stress
            elif size >= 5:
                adj = ramp * rp["big"] // 100 - stress // 2
            out.append(f["w"] * (100 + adj))
        return out

    def pick_w(self, rng, W):
        x = pick(rng, sum(W))
        acc = 0
        for i, w in enumerate(W):
            acc += w
            if x < acc:
                return i
        return len(W) - 1

    def draw(self, rng, W):
        f = self.pick_w(rng, W)
        return (f, pick(rng, len(self.orients[f])))

    def can_place(self, board, p):
        for _, _, m in self.masks[p[0]][p[1]]:
            if not board & m:
                return True
        return False

    def any_placeable(self, board):
        return any(self.can_place(board, (f, o)) for f in range(len(self.fams)) for o in range(len(self.orients[f])))

    def count_placeable(self, board, tray):
        return sum(1 for p in tray if p is not None and self.can_place(board, p))

    def draw_placeable(self, rng, W, board):
        cands, ws = [], []
        for f in range(len(self.fams)):
            for o in range(len(self.orients[f])):
                if self.can_place(board, (f, o)):
                    cands.append((f, o))
                    ws.append(W[f])
        if not cands:
            return None
        return cands[self.pick_w(rng, ws)]

    def best_of(self, rng, W, board, tries):
        best, best_n = None, -1
        for _ in range(tries):
            tray = [self.draw(rng, W) for _ in range(3)]
            n = self.count_placeable(board, tray)
            if n > best_n:
                best, best_n = tray, n
            if n == 3:
                break
        forced = False
        if best_n == 0 and self.any_placeable(board):
            k = pick(rng, 3)
            best[k] = self.draw_placeable(rng, W, board)
            forced = True
        return best, forced

    def generosity(self, score):
        for lim, t in self.cfg["generosity"]:
            if score < lim:
                return t
        return 1


class State:
    def __init__(self, core, mode, seed, tag=""):
        self.core, self.mode, self.tag = core, mode, tag
        self.seed = seed & M32
        self.rng = Rng(seed)
        self.board = 0
        self.tray = [None, None, None]
        self.score = self.combo = self.since = self.ti = self.sub = 0
        self.moves = self.lines = 0
        self.log = []
        self.forced = 0

    def deal(self, kind):
        core, cfg = self.core, self.core.cfg
        raw = None
        if self.mode == "daily":
            W = core.weights(0, 0, True)
            if kind == "tray":
                raw = [core.draw(self.rng, W) for _ in range(3)]
                tray = list(raw)
                forced = False
                if core.count_placeable(self.board, tray) == 0 and core.any_placeable(self.board):
                    sub = Rng(sub_seed(self.seed, self.ti, 0))
                    k = pick(sub, 3)
                    tray[k] = core.draw_placeable(sub, W, self.board)
                    forced = True
                self.ti += 1
            else:
                self.sub += 1
                sub = Rng(sub_seed(self.seed, self.ti, self.sub))
                tries = cfg["refreshTries"] if kind == "refresh" else cfg["reviveTries"]
                tray, forced = core.best_of(sub, W, self.board, tries)
        else:
            W = core.weights(popcount(self.board), self.score, False)
            if kind == "tray":
                tries = core.generosity(self.score)
                self.ti += 1
            else:
                tries = cfg["refreshTries"] if kind == "refresh" else cfg["reviveTries"]
            tray, forced = core.best_of(self.rng, W, self.board, tries)
        # ── the fairness property ──
        if core.count_placeable(self.board, tray) == 0 and core.any_placeable(self.board):
            core.violations.append(f"{self.tag}: {kind} #{len(self.log)} dealt with no placeable piece "
                                   f"(board {self.board:016x})")
        if forced:
            self.forced += 1
        self.tray = tray
        enc = lambda p: p[0] * 4 + p[1] if p is not None else -1
        self.log.append([kind, [enc(p) for p in tray], 1 if forced else 0, [enc(p) for p in raw] if raw else None])

    def apply(self, slot, r, c):
        core, cfg = self.core, self.core.cfg
        f, o = self.tray[slot]
        cells = core.orients[f][o]
        m = 0
        for a, b in cells:
            m |= 1 << ((r + a) * N + c + b)
        if self.board & m:
            raise AssertionError("illegal placement")
        nb = self.board | m
        cleared, lines = 0, 0
        for rm in ROWS:
            if nb & rm == rm:
                cleared |= rm
                lines += 1
        for cm in COLS:
            if nb & cm == cm:
                cleared |= cm
                lines += 1
        nb &= ~cleared & FULL
        self.board = nb
        self.tray[slot] = None
        pts = len(cells)
        if lines:
            self.combo += 1
            self.since = 0
            mult = min(self.combo, cfg["comboCap"])
            pts += cfg["lines"][lines] * mult
            if nb == 0:
                pts += cfg["spotless"] * mult
        else:
            self.since += 1
            if self.since >= cfg["comboGrace"]:
                self.combo = 0
        self.score += pts
        self.moves += 1
        self.lines += lines
        if all(p is None for p in self.tray):
            self.deal("tray")

    def revive_clear(self):
        K = self.core.cfg["revive"]
        best, br, bc = -1, 0, 0
        for r in range(N - K + 1):
            for c in range(N - K + 1):
                w = 0
                for a in range(K):
                    for b in range(K):
                        w |= 1 << ((r + a) * N + c + b)
                n = popcount(self.board & w)
                if n > best:
                    best, br, bc = n, r, c
        w = 0
        for a in range(K):
            for b in range(K):
                w |= 1 << ((br + a) * N + bc + b)
        self.board &= ~w & FULL

    def bomb_clear(self, r, c):
        B = self.core.cfg["bomb"]
        r0 = min(max(r - 1, 0), N - B)
        c0 = min(max(c - 1, 0), N - B)
        w = 0
        for a in range(B):
            for b in range(B):
                w |= 1 << ((r0 + a) * N + c0 + b)
        self.board &= ~w & FULL

    def legal_moves(self):
        out = []
        for s in range(3):
            p = self.tray[s]
            if p is None:
                continue
            for r, c, m in self.core.masks[p[0]][p[1]]:
                if not self.board & m:
                    out.append((s, r, c, m))
        return out


def _L(b):
    return ((b << 1) & ~COL0 & FULL) | COL0


def _R(b):
    return ((b >> 1) & ~COL7 & FULL) | COL7


def _U(b):
    return ((b << 8) & FULL) | ROW0


def _D(b):
    return (b >> 8) | ROW7


def evaluate(board, m):
    nb = board | m
    cleared, lines = 0, 0
    for rm in ROWS:
        if nb & rm == rm:
            cleared |= rm
            lines += 1
    for cm in COLS:
        if nb & cm == cm:
            cleared |= cm
            lines += 1
    after = nb & ~cleared & FULL
    holes = popcount(~after & FULL & _L(after) & _R(after) & _U(after) & _D(after))
    adj = popcount(m & _L(board)) + popcount(m & _R(board)) + popcount(m & _U(board)) + popcount(m & _D(board))
    return lines * 120 - holes * 30 - popcount(after) * 2 + adj * 3


def greedy(st, _rng=None):
    best, best_h = None, None
    for s, r, c, m in st.legal_moves():
        h = evaluate(st.board, m)
        if best_h is None or h > best_h:
            best_h, best = h, (s, r, c)
    return best


def randomly(st, rng):
    mv = st.legal_moves()
    if not mv:
        return None
    s, r, c, _ = mv[pick(rng, len(mv))]
    return (s, r, c)


def drive(core, mode, seed, max_moves=300, refresh_at=7, bomb_at=13, bot=greedy, bot_seed=1, tag=""):
    st = State(core, mode, seed, tag)
    st.deal("tray")
    revived = ref = bomb = False
    brng = Rng(bot_seed)
    while st.moves < max_moves:
        if not ref and st.moves == refresh_at:
            ref = True
            st.deal("refresh")
        if not bomb and st.moves == bomb_at:
            bomb = True
            st.bomb_clear(3, 3)
        mv = bot(st, brng)
        if mv is None:
            if not revived:
                revived = True
                st.revive_clear()
                st.deal("revive")
                continue
            break
        st.apply(*mv)
    return st


def board_str(b):
    return "".join("1" if b >> i & 1 else "0" for i in range(64))


def load():
    html = HTML.read_text(encoding="utf-8")
    a, b = html.find("//@@BPCORE-BEGIN"), html.find("//@@BPCORE-END")
    if a < 0 or b < 0:
        return None, None, "BPCORE markers missing from game.html"
    block = html[a + len("//@@BPCORE-BEGIN"):b]
    m = re.search(r"const BP_CFG=(\{.*?\});\n", block, re.S)
    if not m:
        return None, None, "BP_CFG not found in the BPCORE block"
    return block, json.loads(m.group(1)), None


def check():
    blockers, warnings, info = [], [], []
    if not HTML.exists():
        return [f"{HTML} missing"], [], []
    block, cfg, err = load()
    if err:
        return [err], [], []
    core = Core(cfg)

    # catalogue sanity: 1x1 present; Rotate's (o+1)%n is a true 90° turn
    if not any(len(f["cells"]) == 1 for f in core.fams):
        blockers.append("no 1x1 piece in the catalogue — the fairness guarantee needs it")
    for f, ors in enumerate(core.orients):
        n = len(ors)
        for o, cells in enumerate(ors):
            if norm([(c, -r) for r, c in cells]) != ors[(o + 1) % n]:
                blockers.append(f"family {core.fams[f]['id']}: orientation {o}→{(o + 1) % n} is not a 90° rotation")

    # 1. JS ↔ Python parity against the node golden traces
    if not GOLDEN.exists():
        blockers.append("BlockPuzzle/test/golden.json missing — run `node BlockPuzzle/test/golden.js`")
    else:
        g = json.loads(GOLDEN.read_text(encoding="utf-8"))
        sha = hashlib.sha256(block.encode("utf-8")).hexdigest()
        if g.get("core_sha256") != sha:
            blockers.append("BPCORE block changed since golden.json — run `node BlockPuzzle/test/golden.js` "
                            "and re-run this gate (the Python port must be re-verified)")
        bad = 0
        for c in g.get("cases", []):
            o = c["opt"]
            st = drive(core, c["mode"], c["seed"], o["max"], o["refreshAt"], o["bombAt"], tag="golden")
            out = c["out"]
            if (st.log != out["log"] or st.score != out["score"] or st.moves != out["moves"]
                    or board_str(st.board) != out["board"]):
                bad += 1
                if bad <= 3:
                    blockers.append(f"port drift: {c['mode']} seed {c['seed']} — Python {st.score}/{st.moves} "
                                    f"vs JS {out['score']}/{out['moves']}")
        if bad > 3:
            blockers.append(f"port drift in {bad} of {len(g['cases'])} golden cases")
        info.append(f"golden parity: {len(g.get('cases', [])) - bad}/{len(g.get('cases', []))} JS traces reproduced")

    # 2. fairness: classic (greedy + random-legal), refresh/bomb/revive paths
    deals = forced = 0
    scores = []
    for i in range(250):
        st = drive(core, "classic", 1000003 * (i + 1), 400, refresh_at=5 + i % 11, bomb_at=9 + i % 17, tag=f"classic g{i}")
        deals += len(st.log)
        forced += st.forced
        scores.append(st.score)
    for i in range(250):
        st = drive(core, "classic", 7777 + 31 * i, 400, refresh_at=3 + i % 7, bomb_at=6 + i % 9, bot=randomly,
                   bot_seed=i + 1, tag=f"classic r{i}")
        deals += len(st.log)
        forced += st.forced
    scores.sort()
    info.append(f"classic: 500 runs, {deals} deals, {forced} forced fallbacks; greedy-bot score "
                f"p25/p50/p75 = {scores[62]}/{scores[125]}/{scores[187]}")

    # 3. daily: deterministic, distinct seeds, same main sequence for everyone
    seeds = [daily_seed(d) for d in range(3653)]
    if len(set(seeds)) != len(seeds):
        blockers.append("daily seeds collide within 10 years")
    reached = 0
    dtargets = cfg["dailyTargets"]
    if len(dtargets) != 7:
        blockers.append("dailyTargets must list 7 weekday targets (Sun..Sat)")
    nondet = mixed = 0
    for d in range(366):
        s1 = drive(core, "daily", daily_seed(d), 300, refresh_at=-1, bomb_at=-1, tag=f"daily {d}")
        s2 = drive(core, "daily", daily_seed(d), 300, refresh_at=-1, bomb_at=-1, tag=f"daily {d}")
        if s1.log != s2.log or s1.score != s2.score or s1.board != s2.board:
            nondet += 1
        s3 = drive(core, "daily", daily_seed(d), 300, refresh_at=4, bomb_at=8, bot=randomly, bot_seed=d + 5,
                   tag=f"daily {d} random")
        raw1 = [e[3] for e in s1.log if e[0] == "tray"]
        raw3 = [e[3] for e in s3.log if e[0] == "tray"]
        k = min(len(raw1), len(raw3))
        if raw1[:k] != raw3[:k]:
            mixed += 1
        if len(dtargets) == 7 and s1.score >= dtargets[(d + 4) % 7]:
            reached += 1
    if nondet:
        blockers.append(f"daily not deterministic on {nondet} day(s): same seed, different run")
    if mixed:
        blockers.append(f"daily main piece sequence depends on how the player plays on {mixed} day(s)")
    pct = reached * 100 // 366
    info.append(f"daily: 366 days × 3 runs deterministic; greedy bot reaches the target on {pct}% of days")
    if pct < 50:
        warnings.append(f"greedy bot reaches the daily target on only {pct}% of days — targets may be too high")

    if core.violations:
        blockers.append(f"{len(core.violations)} unfair deal(s); first: {core.violations[0]}")
    return blockers, warnings, info


def main() -> int:
    blockers, warnings, info = check()
    for line in info:
        print("  ·", line)
    for w in warnings:
        print("  !", w)
    for b in blockers:
        print("  ✗", b)
    if blockers:
        print(f"blockpuzzle fair: {len(blockers)} blocker(s)")
        return 1
    print("blockpuzzle fair: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
