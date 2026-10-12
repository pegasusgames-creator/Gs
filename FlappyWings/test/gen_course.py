#!/usr/bin/env python3
"""
gen_course.py — Flappy Wings course generator + flight simulator (pure
Python 3 stdlib), a bit-exact port of the JS generator in game.html.

The game never ships a fixed level list: every flight is a seeded course
generated on the fly (endless runs use a random 32-bit seed, the Daily
flight uses a seed derived from the local date). The numbers that shape a
course live in ONE place — the FW_TUNING JSON block in game.html, between
the /*FW_TUNING_BEGIN*/ and /*FW_TUNING_END*/ markers — and this module
reads them from there, so the fairness gate always checks what ships.

What lives here:
  * mulberry32()      — the game's PRNG (Math.imul / >>> semantics)
  * ramp(T, k)        — difficulty at gate index k (gap, spacing, max
                        vertical change, speed, bobbing-gate chance)
  * gen_course()      — gate k = {x, c (gap centre), gap, amp, phase,
                        feather}; identical draws/rounding to the JS
  * daily_seed()      — the Daily flight seed for a day index
  * fly()             — the game's fixed-timestep physics (60 Hz) driven
                        by a deterministic autopilot with a HUMAN tap-rate
                        limit and an inflated hitbox. A completed flight is
                        a constructive witness that the course is passable.

Used by scripts/check_flappywings_fair.py. Standalone:
    python3 FlappyWings/test/gen_course.py [seed] [gates]
prints the first gates of a course and flies it.
"""
import json
import math
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
GAME = BASE / "FlappyWings" / "android" / "app" / "src" / "main" / "assets" / "game.html"

U32 = 0xFFFFFFFF


# ── tuning ──────────────────────────────────────────────────────────────
def load_tuning(path=GAME):
    """Parse the FW_TUNING JSON object out of game.html (exactly the object
    the game reads at runtime)."""
    src = Path(path).read_text(encoding="utf-8")
    m = re.search(r"/\*FW_TUNING_BEGIN\*/(.*?)/\*FW_TUNING_END\*/", src, re.S)
    if not m:
        raise ValueError("FW_TUNING markers not found in game.html")
    return json.loads(m.group(1))


def generator_source(path=GAME):
    """The JS generator text between /*FW_GEN_BEGIN*/ and /*FW_GEN_END*/."""
    src = Path(path).read_text(encoding="utf-8")
    m = re.search(r"/\*FW_GEN_BEGIN\*/(.*?)/\*FW_GEN_END\*/", src, re.S)
    if not m:
        raise ValueError("FW_GEN markers not found in game.html")
    return m.group(1)


# ── JS number semantics ─────────────────────────────────────────────────
def imul(a, b):
    return ((a & U32) * (b & U32)) & U32


def round_js(v):
    """Math.round: halves round toward +Infinity (Python's round() is
    banker's rounding — never use it for a port)."""
    return math.floor(v + 0.5)


def mulberry32(seed):
    state = seed & U32

    def rnd():
        nonlocal state
        state = (state + 0x6D2B79F5) & U32
        t = state
        t = imul(t ^ (t >> 15), 1 | t)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & U32) ^ t
        t &= U32
        return ((t ^ (t >> 14)) & U32) / 4294967296
    return rnd


# ── difficulty ramp ─────────────────────────────────────────────────────
def ramp(T, k):
    R, B = T["ramp"], T["bob"]
    gap = max(R["gapMin"], R["gapStart"] - math.floor(k * R["gapStep"]))
    spacing = max(R["spacingMin"], R["spacingStart"] - math.floor(k * R["spacingStep"]))
    delta = min(R["deltaMax"], R["deltaStart"] + math.floor(k * R["deltaStep"]))
    speed = min(R["speedMax"], R["speedStart"] + k * R["speedStep"])
    bob = 0 if k < B["from"] else min(B["chanceMax"], B["chanceStart"] + (k - B["from"]) * B["chanceStep"])
    return {"gap": gap, "spacing": spacing, "delta": delta, "speed": speed, "bob": bob}


# ── course generator (mirror of genGate/genCourse in game.html) ─────────
def gen_course(T, seed, n):
    W, G, B, F = T["world"], T["gates"], T["bob"], T["feathers"]
    rng = mulberry32(seed)
    out = []
    prev_c, prev_a, x = W["startY"], 0, G["firstX"]
    for k in range(n):
        rp = ramp(T, k)
        gap, spacing, delta = rp["gap"], rp["spacing"], rp["delta"]
        if k > 0:
            x += spacing
        r1, r2, r3, r4, r5 = rng(), rng(), rng(), rng(), rng()
        amp = B["amp"] if (k >= B["from"] and r2 < rp["bob"]) else 0
        lo = W["marginTop"] + gap / 2 + amp
        hi = W["floorY"] - W["marginBottom"] - gap / 2 - amp
        reach = delta - amp - prev_a
        min_c = max(lo, prev_c - reach)
        max_c = min(hi, prev_c + reach)
        if min_c > max_c:
            c = round_js(min(max(prev_c, lo), hi))
        else:
            c = round_js(min_c + r1 * (max_c - min_c))
        c = min(max(c, math.ceil(lo)), math.floor(hi))
        phase = math.floor(r3 * B["wavelength"])
        lead = (G["firstX"] if k == 0 else spacing) / 2
        feather = None
        if r4 < F["chance"]:
            feather = (x - lead, round_js((prev_c + c) / 2) + round_js((r5 * 2 - 1) * F["spread"]))
        out.append({"k": k, "x": x, "c": c, "gap": gap, "amp": amp,
                    "phase": phase, "feather": feather})
        prev_c, prev_a = c, amp
    return out


def daily_seed(day_index):
    """Day 0 = 2026-01-01 (local calendar date). Mirror of dailySeed()."""
    return (imul(day_index + 1, 2654435761) ^ 0x5F1D2A77) & U32


def day_index(y, m, d):
    """Whole days from the epoch in FW_TUNING.daily.epoch to (y, m, d)."""
    import datetime
    return (datetime.date(y, m, d) - datetime.date(2026, 1, 1)).days


# ── physics ─────────────────────────────────────────────────────────────
def gate_centre(T, g, cam_x):
    if not g["amp"]:
        return g["c"]
    lam = T["bob"]["wavelength"]
    return g["c"] + g["amp"] * math.sin(2 * math.pi * (cam_x + g["phase"]) / lam)


def _circle_rect(cx, cy, r, x0, y0, x1, y1):
    dx = max(x0 - cx, 0.0, cx - x1)
    dy = max(y0 - cy, 0.0, cy - y1)
    return dx * dx + dy * dy < r * r


def hits_gate(T, g, cam_x, y, r):
    G = T["gates"]
    pw, cw, ch = G["pillarW"], G["capW"], G["capH"]
    if abs(g["x"] - cam_x) > cw / 2 + r:
        return False
    cy = gate_centre(T, g, cam_x)
    top, bot = cy - g["gap"] / 2, cy + g["gap"] / 2
    x = g["x"]
    return (_circle_rect(cam_x, y, r, x - pw / 2, -1e9, x + pw / 2, top - ch) or
            _circle_rect(cam_x, y, r, x - cw / 2, top - ch, x + cw / 2, top) or
            _circle_rect(cam_x, y, r, x - cw / 2, bot, x + cw / 2, bot + ch) or
            _circle_rect(cam_x, y, r, x - pw / 2, bot + ch, x + pw / 2, 1e9))


def _gap_edges(T, g, cam_x):
    cy = gate_centre(T, g, cam_x)
    return cy - g["gap"] / 2, cy + g["gap"] / 2


def climb_table(T, interval, n=400):
    """D[n] = height change (world units, negative = up) n ticks after a
    tap at tick 0 followed by a tap every `interval` ticks — the climb a
    player gets from tapping at that steady rhythm."""
    P = T["phys"]
    dt = 1.0 / T["tickHz"]
    y = vy = 0.0
    out = [0.0]
    for t in range(n):
        if t % interval == 0:
            vy = P["flapV"]
        vy = min(vy + P["gravity"] * dt, P["maxFall"])
        y += vy * dt
        out.append(y)
    return out


class _Pilot:
    """The reference autopilot (see fly())."""

    def __init__(self, T, course, min_tap_ticks, plan_interval, margin):
        self.T, self.course = T, course
        W, G = T["world"], T["gates"]
        self.dt = 1.0 / T["tickHz"]
        self.r = W["birdR"]
        self.rr = self.r + margin
        self.cw = G["capW"]
        self.floor = W["floorY"]
        self.min_tap = min_tap_ticks
        self.climb = climb_table(T, plan_interval)

    def must_tap(self, st):
        """Latest-safe-tap rule: tap only if waiting this tick drops the bird
        onto a lower cap / the cloud sea next tick, or leaves it too low to
        climb into the next gap at a relaxed tapping rhythm."""
        T, P, course = self.T, self.T["phys"], self.course
        y, vy, cam, score = st[0], st[1], st[2], st[3]
        speed = ramp(T, score)["speed"]
        x1 = cam + speed * self.dt
        y1 = y + min(vy + P["gravity"] * self.dt, P["maxFall"]) * self.dt
        rr = self.rr
        if y1 + rr >= self.floor - 1:
            return True
        for j in range(max(0, score - 1), min(len(course), score + 3)):
            g = course[j]
            left, right = g["x"] - self.cw / 2 - rr, g["x"] + self.cw / 2 + rr
            if right < x1:
                continue
            if left <= x1:
                _, bot = _gap_edges(T, g, x1)
                if y1 + rr >= bot - 1:
                    return True
                continue
            ticks_to = int(math.ceil((left - x1) / (speed * self.dt)))
            _, bot = _gap_edges(T, g, left)
            best = y1 + self.climb[min(ticks_to, len(self.climb) - 1)]
            return best + rr >= bot - 2
        return False

    def step(self, st, tap):
        """Advance one 60 Hz tick (identical order of operations to the
        game's step()). st = (y, vy, cam, score, since, tick). Returns
        (new_state, crashed_reason_or_None)."""
        T, P, course = self.T, self.T["phys"], self.course
        y, vy, cam, score, since, tick = st
        speed = ramp(T, score)["speed"]
        if tap:
            vy, since = P["flapV"], 0
        else:
            since += 1
        vy = min(vy + P["gravity"] * self.dt, P["maxFall"])
        y = y + vy * self.dt
        cam += speed * self.dt
        if y < self.r:
            y = self.r
            if vy < 0:
                vy = 0.0
        while score < len(course) and course[score]["x"] <= cam:
            score += 1
        tick += 1
        why = None
        if y + self.rr >= self.floor:
            why = "cloud sea"
        else:
            for j in range(max(0, score - 2), min(len(course), score + 2)):
                if hits_gate(T, course[j], cam, y, self.rr):
                    why = "gate %d" % (j + 1)
                    break
        return (y, vy, cam, score, since, tick), why

    def policy(self, st, forced):
        if st[4] < self.min_tap:
            return False
        return st[5] in forced or self.must_tap(st)


def fly(T, course, min_tap_ticks=9, plan_interval=14, margin=3.0,
        max_gates=None, repair_window=150):
    """Fly a course with the reference autopilot; return
    {ok, gates, ticks, taps, max_rate, repairs, why}.

    Policy = "latest safe tap": tap only when NOT tapping this tick would
    (a) drop the bird onto a lower cap / the cloud sea next tick, or
    (b) leave it too low to climb into the next gap in time at a relaxed
    rhythm (plan_interval = 14 ticks = 4.3 taps/s). When that myopic rule
    runs into a wall, the pilot backtracks and taps EARLIER (bounded
    repair search over the last `repair_window` ticks). Taps are never
    closer than `min_tap_ticks` (9 ticks = 6.7 taps/s) and every collision
    uses an inflated radius (birdR + margin), so a completed flight is a
    constructive witness that each gap is passable at the shipped
    speed/gravity with room to spare — not a pixel-perfect line."""
    pilot = _Pilot(T, course, min_tap_ticks, plan_interval, margin)
    W = T["world"]
    max_gates = min(max_gates or len(course), len(course) - 2)
    st = (float(W["startY"]), 0.0, 0.0, 0, 999, 0)
    hist, taps_at, forced = [], [], set()
    repairs = 0
    while st[3] < max_gates:
        tap = pilot.policy(st, forced)
        hist.append(st)
        taps_at.append(tap)
        nst, why = pilot.step(st, tap)
        if why is None:
            st = nst
            if st[5] > 400000:
                break
            continue
        # crashed at this tick: backtrack and try ONE earlier extra tap
        fail_tick = st[5]
        fixed = False
        lo_t = max(0, fail_tick - repair_window)
        for t in range(fail_tick, lo_t - 1, -1):
            cand = hist[t]
            if taps_at[t] or cand[4] < pilot.min_tap:
                continue
            trial = set(forced)
            trial.add(t)
            ok, _ = _rollout(pilot, cand, trial, fail_tick + 90)
            if ok:
                forced = trial
                del hist[t:]
                del taps_at[t:]
                st = cand
                fixed = True
                repairs += 1
                break
        if not fixed:
            taps = [h[5] for h, tp in zip(hist, taps_at) if tp]
            return _res(False, st[3], st[5], len(taps), taps, T, why, repairs)
    taps = [h[5] for h, tp in zip(hist, taps_at) if tp]
    return _res(st[3] >= max_gates, st[3], st[5], len(taps), taps, T, None, repairs)


def _rollout(pilot, st, forced, until_tick):
    while st[5] < until_tick:
        tap = pilot.policy(st, forced)
        st, why = pilot.step(st, tap)
        if why is not None:
            return False, why
        if st[3] >= len(pilot.course) - 2:
            break
    return True, None


def _res(ok, score, tick, taps, tap_ticks, T, why, repairs=0):
    hz = T["tickHz"]
    best, j = 0, 0
    for i in range(len(tap_ticks)):
        while tap_ticks[i] - tap_ticks[j] >= hz:
            j += 1
        best = max(best, i - j + 1)
    return {"ok": ok, "gates": score, "ticks": tick, "taps": taps,
            "max_rate": best, "repairs": repairs, "why": why}


def main(argv):
    T = load_tuning()
    seed = int(argv[1]) if len(argv) > 1 else 12345
    n = int(argv[2]) if len(argv) > 2 else 200
    course = gen_course(T, seed, n)
    for g in course[:12]:
        print(g)
    print(fly(T, course))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
