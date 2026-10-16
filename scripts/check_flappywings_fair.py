#!/usr/bin/env python3
"""check_flappywings_fair.py — Flappy Wings course fairness gate (stdlib).

Flappy Wings never ships a fixed level list: every flight is a seeded course
built at runtime by the generator in game.html (FW_TUNING + FW_GEN blocks).
This gate re-simulates that generator (FlappyWings/test/gen_course.py, a
bit-exact Python port) and BLOCKS when any course could be unfair:

  1. RAMP      difficulty is monotonic and bounded: gap never widens, gate
               spacing never grows, max vertical change / speed / moving-gate
               chance never drop, and every parameter saturates at a sane
               floor/ceiling (the smallest gap still fits the bird 5x over).
  2. GEOMETRY  every generated gate keeps its gap (incl. drift) inside the
               sky band, consecutive gaps never differ by more than the ramp
               allows, feathers float in open air (never inside a gate).
  3. FLIGHT    every course is FLOWN at the shipped physics (60 Hz fixed
               tick, gravity / flap / terminal speed from FW_TUNING) by a
               deterministic autopilot that taps no faster than a human
               (>= 9 ticks apart = 6.7 taps/s) with an inflated hitbox
               (+3 units). A completed flight is a constructive witness that
               every gap is passable with room to spare:
                 * endless: many random seeds, through the whole ramp and
                   180+ gates at maximum difficulty;
                 * daily: every Daily course for 2026-01-01 .. 2027-12-31,
                   to its target + 15 gates;
                 * first flights: the opening 10 gates also pass for a relaxed
                   pilot (<= 4.3 taps/s, +10 hitbox) — new players reach the
                   first goal (5 gates) in about 10 s of flight.
  4. DAILY     the Daily seed is deterministic (same day -> same seed ->
               same course, computed twice), distinct for every day in the
               window, and each weekday has a target that ramps Mon -> Sun.
  5. PARITY    the Python port matches the SHIPPED JS generator gate-for-gate
               (node FlappyWings/test/parity.js) when node is available;
               otherwise the FW_GEN/FW_TUNING source must match the
               fingerprint pinned in FlappyWings/test/gen_fingerprint.json
               (re-pin with --pin after a node parity pass).

Standalone:  python3 scripts/check_flappywings_fair.py [FlappyWings] [--quick] [--pin]
Exit 0 = OK, 1 = blocked.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = "FlappyWings"
TEST = BASE / APP / "test"
sys.path.insert(0, str(TEST))
import gen_course as gc  # noqa: E402

FINGERPRINT = TEST / "gen_fingerprint.json"


def fingerprint(path=gc.GAME):
    src = Path(path).read_text(encoding="utf-8")
    import re
    t = re.search(r"/\*FW_TUNING_BEGIN\*/(.*?)/\*FW_TUNING_END\*/", src, re.S).group(1)
    g = re.search(r"/\*FW_GEN_BEGIN\*/(.*?)/\*FW_GEN_END\*/", src, re.S).group(1)
    m = re.search(r"function mulberry32\(a\)\{[^\n]*\}", src).group(0)
    return hashlib.sha256((m + "\n" + t + "\n" + g).encode("utf-8")).hexdigest()


def check_ramp(T, errs):
    R, W = T["ramp"], T["world"]
    prev = None
    for k in range(0, 600):
        r = gc.ramp(T, k)
        if prev:
            if r["gap"] > prev["gap"]:
                errs.append("ramp: gap widens at gate %d" % k)
            if r["spacing"] > prev["spacing"]:
                errs.append("ramp: spacing grows at gate %d" % k)
            if r["delta"] < prev["delta"] or r["speed"] < prev["speed"] or r["bob"] < prev["bob"]:
                errs.append("ramp: delta/speed/bob drops at gate %d" % k)
        prev = r
        if len(errs) > 5:
            return
    if R["gapMin"] < 5 * 2 * W["birdR"]:
        errs.append("ramp: gapMin %d is under 5x the bird's diameter" % R["gapMin"])
    if R["spacingMin"] < T["gates"]["capW"] + 6 * W["birdR"]:
        errs.append("ramp: spacingMin leaves no room between gates")
    if R["speedMax"] > 260 or T["bob"]["chanceMax"] > 0.6:
        errs.append("ramp: speed/bob ceiling out of the tested range")


def check_geometry(T, course, label, errs):
    W, G, B = T["world"], T["gates"], T["bob"]
    lo_band, hi_band = W["marginTop"], W["floorY"] - W["marginBottom"]
    prev = None
    for g in course:
        k = g["k"]
        r = gc.ramp(T, k)
        if g["gap"] != r["gap"]:
            errs.append("%s gate %d: gap %s != ramp %s" % (label, k + 1, g["gap"], r["gap"]))
        top, bot = g["c"] - g["gap"] / 2 - g["amp"], g["c"] + g["gap"] / 2 + g["amp"]
        if top < lo_band - 0.5 or bot > hi_band + 0.5:
            errs.append("%s gate %d: gap leaves the sky band (%.1f..%.1f)" % (label, k + 1, top, bot))
        if prev is not None:
            if g["x"] - prev["x"] != r["spacing"]:
                errs.append("%s gate %d: spacing mismatch" % (label, k + 1))
            if abs(g["c"] - prev["c"]) + g["amp"] + prev["amp"] > r["delta"] + 1:
                errs.append("%s gate %d: vertical jump %d exceeds ramp %d" % (
                    label, k + 1, abs(g["c"] - prev["c"]) + g["amp"] + prev["amp"], r["delta"]))
        f = g["feather"]
        if f:
            px = prev["x"] if prev else 0
            clear = G["capW"] / 2 + W["birdR"]
            if not (px + clear <= f[0] <= g["x"] - clear):
                errs.append("%s gate %d: feather inside a gate column" % (label, k + 1))
            if not (W["birdR"] <= f[1] <= W["floorY"] - W["birdR"] - 4):
                errs.append("%s gate %d: feather out of reach (y=%s)" % (label, k + 1, f[1]))
        prev = g
        if len(errs) > 20:
            return


def fly_or_fail(T, course, n, label, errs, **kw):
    r = gc.fly(T, course, max_gates=n, **kw)
    if not r["ok"]:
        errs.append("%s: autopilot crashed at gate %d (%s) — gap not passable at human tap rate"
                    % (label, r["gates"] + 1, r["why"]))
    return r


def check_parity(T, errs, warns, pin):
    seeds = ["1", "12345", "4294967295", "2654435761", "day:0", "day:287", "day:400", "day:729"]
    node = shutil.which("node")
    fp = fingerprint()
    if node:
        try:
            out = subprocess.run([node, str(TEST / "parity.js"), "220"] + seeds,
                                 capture_output=True, text=True, timeout=120)
            js = json.loads(out.stdout)
        except Exception as e:  # pragma: no cover
            errs.append("parity: node run failed: %s" % e)
            return
        for s in seeds:
            seed = gc.daily_seed(int(s[4:])) if s.startswith("day:") else int(s) & gc.U32
            if js[s]["seed"] != seed:
                errs.append("parity: seed mismatch for %s" % s)
                continue
            py = gc.gen_course(T, seed, 220)
            for g, j in zip(py, js[s]["gates"]):
                want = [g["x"], g["c"], g["gap"], g["amp"], g["phase"],
                        list(g["feather"]) if g["feather"] else None]
                if want != j:
                    errs.append("parity: %s gate %d differs JS %s vs Python %s" % (s, g["k"] + 1, j, want))
                    break
        if not any(e.startswith("parity") for e in errs):
            if pin or not FINGERPRINT.exists():
                FINGERPRINT.write_text(json.dumps({"sha256": fp, "note": "FW_TUNING + FW_GEN + mulberry32, verified JS==Python by parity.js"}, indent=2) + "\n")
            elif json.loads(FINGERPRINT.read_text()).get("sha256") != fp:
                warns.append("parity OK but gen_fingerprint.json is stale — run with --pin")
    else:
        if not FINGERPRINT.exists():
            errs.append("parity: node unavailable and no pinned fingerprint")
        elif json.loads(FINGERPRINT.read_text()).get("sha256") != fp:
            errs.append("parity: generator changed since the last JS/Python parity pass "
                        "(install node and run with --pin)")


def main(argv):
    quick = "--quick" in argv
    pin = "--pin" in argv
    errs, warns = [], []
    try:
        T = gc.load_tuning()
    except Exception as e:
        print("✗ %s: cannot read FW_TUNING from game.html: %s" % (APP, e))
        return 1
    check_ramp(T, errs)

    # endless flights: random seeds through the ramp + long max-difficulty tail
    n_seeds, n_gates = (25, 200) if quick else (110, 260)
    flown = 0
    for i in range(n_seeds):
        seed = (gc.imul(i + 1, 0x9E3779B1) ^ 0xA5A5A5A5) & gc.U32
        course = gc.gen_course(T, seed, n_gates + 3)
        check_geometry(T, course, "seed %d" % seed, errs)
        fly_or_fail(T, course, n_gates, "endless seed %d" % seed, errs)
        if i < 12:
            fly_or_fail(T, course, 10, "first gates (relaxed) seed %d" % seed, errs,
                        min_tap_ticks=14, plan_interval=18, margin=10.0)
        flown += n_gates
        if len(errs) > 25:
            break

    # daily courses: every day of 2026-2027, to target + 15
    days = range(0, 730, 7 if quick else 1)
    seen = {}
    for d in days:
        s1, s2 = gc.daily_seed(d), gc.daily_seed(d)
        if s1 != s2:
            errs.append("daily: seed for day %d not deterministic" % d)
        if s1 in seen:
            errs.append("daily: day %d reuses day %d's course" % (d, seen[s1]))
        seen[s1] = d
        tgt = gc.daily_target(T, d)
        n = tgt + 15
        c1 = gc.gen_course(T, s1, n + 3)
        c2 = gc.gen_course(T, s2, n + 3)
        if c1 != c2:
            errs.append("daily: course for day %d not deterministic" % d)
        check_geometry(T, c1, "daily %d" % d, errs)
        fly_or_fail(T, c1, n, "daily day %d (target %d)" % (d, tgt), errs)
        flown += n
        if len(errs) > 25:
            break
    tg = T["daily"]["targets"]
    week = [tg[(i + 1) % 7] for i in range(7)]  # Mon..Sun
    if any(b < a for a, b in zip(week, week[1:])):
        errs.append("daily: targets do not ramp Mon -> Sun (%s)" % week)
    if min(tg) < 5 or max(tg) > 60:
        errs.append("daily: targets outside 5..60 (%s)" % tg)

    check_parity(T, errs, warns, pin)

    for w in warns:
        print("!  %s: %s" % (APP, w))
    if errs:
        for e in errs[:30]:
            print("✗ %s: %s" % (APP, e))
        return 1
    print("[flappywings fair] OK — %d gates flown (%d endless seeds, %d daily courses), "
          "ramp monotonic, daily seeds deterministic, JS/Python parity %s"
          % (flown, n_seeds, len(days), "verified" if shutil.which("node") else "pinned"))
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a not in (APP,)]
    os.nice(5) if hasattr(os, "nice") else None
    sys.exit(main(args))
