#!/usr/bin/env python3
"""check_aspectratio_math.py - content gate for AspectRatio's maths.

The pure calculation block of AspectRatio's TOOL_CORE (between
`// @@ARMATH BEGIN` and `// @@ARMATH END`) is run under node on a table of
tricky cases (exact and half-way roundings, huge values, lock modes, clamping,
unit conversions, invalid input) plus a seeded random sweep, and every result
is compared with an independent pure-Python reference built on `fractions`.
BLOCKS on any mismatch. Also pins the built-in preset table (ids, groups,
reduced ratios, the physical A-/US paper sizes).

Rules the reference encodes (and the app states on screen):
  * ratios are reduced with the GCD;
  * every derived pixel size is rounded half up to a whole pixel (e.g. 1000 px
    wide at 16:9 is 562.5 -> 563 high); an exact result is flagged exact;
  * 1 in = 2.54 cm = 25.4 mm exactly; inches shown to 3 decimals, cm to 2,
    mm to 1, rounded half up; px from a physical size = round(size * dpi);
  * crops are the largest centred rectangle of the target ratio and round DOWN;
  * 1..100,000 px per side, DPI 1..2400, ratio terms 1..100,000.

Without node the Python reference is only self-checked on known answers
(WARN - the JS is not executed).

Usage: python3 scripts/check_aspectratio_math.py [AspectRatio]   (other app names only: skipped, exit 0)
Exit 1 on any mismatch.
"""
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "AspectRatio"
ARGS = [a for a in sys.argv[1:] if not a.startswith("-")]
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")

MAXPX, MAXMILLI, MAXDPI, MAXRATIO, MAXLIST = 100000, 100000000, 2400, 100000, 50

# --------------------------------------------------------------------------
# Independent reference (Fractions, no shared code with the JS)
# --------------------------------------------------------------------------


def half_up(fr):
    """Round a non-negative Fraction half up."""
    return math.floor(fr + Fraction(1, 2))


def okint(n, lo, hi):
    return isinstance(n, int) and not isinstance(n, bool) and lo <= n <= hi


def r_reduce(w, h):
    if not (okint(w, 1, MAXPX) and okint(h, 1, MAXPX)):
        return None
    g = math.gcd(w, h)
    return {"rw": w // g, "rh": h // g, "g": g}


def r_info(w, h):
    r = r_reduce(w, h)
    if not r:
        return None
    return {"rw": r["rw"], "rh": r["rh"], "g": r["g"],
            "dec": half_up(Fraction(w * 10000, h)) / 10000,
            "mp": half_up(Fraction(w * h, 10000)) / 100}


def r_fromW(w, rw, rh):
    if not (okint(w, 1, MAXPX) and okint(rw, 1, MAXRATIO) and okint(rh, 1, MAXRATIO)):
        return None
    x = Fraction(w * rh, rw)
    return {"v": half_up(x), "exact": x.denominator == 1, "raw": half_up(x * 1000) / 1000}


def r_fromH(h, rw, rh):
    if not (okint(h, 1, MAXPX) and okint(rw, 1, MAXRATIO) and okint(rh, 1, MAXRATIO)):
        return None
    x = Fraction(h * rw, rh)
    return {"v": half_up(x), "exact": x.denominator == 1, "raw": half_up(x * 1000) / 1000}


def r_parsePx(s):
    s = "" if s is None else str(s)
    m = re.fullmatch(r"\s*([0-9]{1,6})\s*", s)
    if not m:
        return None
    n = int(m.group(1))
    return n if 1 <= n <= MAXPX else None


def r_parseDec(s):
    s = "" if s is None else str(s).strip(" \t\n\r\f\v")
    m = re.fullmatch(r"([0-9]{0,6})(?:[.,]([0-9]{1,3}))?", s)
    if not m or (m.group(1) == "" and m.group(2) is None):
        return None
    ip = int(m.group(1) or "0")
    fp = int((m.group(2) or "").ljust(3, "0")[:3] or "0")
    n = ip * 1000 + fp
    return n if 1 <= n <= MAXMILLI else None


def clampfix(v):
    return (1, True) if v < 1 else (MAXPX, True) if v > MAXPX else (v, False)


def r_resolve(st, ed):
    bad = dict(st, ok=False, clamped=False)
    if (not okint(st.get("w"), 1, MAXPX) or not okint(st.get("h"), 1, MAXPX) or
            not okint(st.get("rw"), 1, MAXRATIO) or not okint(st.get("rh"), 1, MAXRATIO) or
            st.get("lock") not in ("ratio", "w", "h")):
        return bad
    w, h, rw, rh, lock, c = st["w"], st["h"], st["rw"], st["rh"], st["lock"], False
    f = ed.get("f")
    if f == "w":
        if not okint(ed.get("v"), 1, MAXPX):
            return bad
        w = ed["v"]
        if lock == "h":
            r = r_reduce(w, h); rw, rh = r["rw"], r["rh"]
        else:
            h, c = clampfix(r_fromW(w, rw, rh)["v"])
    elif f == "h":
        if not okint(ed.get("v"), 1, MAXPX):
            return bad
        h = ed["v"]
        if lock == "w":
            r = r_reduce(w, h); rw, rh = r["rw"], r["rh"]
        else:
            w, c = clampfix(r_fromH(h, rw, rh)["v"])
    elif f == "ratio":
        if not (okint(ed.get("rw"), 1, MAXRATIO) and okint(ed.get("rh"), 1, MAXRATIO)):
            return bad
        g = math.gcd(ed["rw"], ed["rh"]); rw, rh = ed["rw"] // g, ed["rh"] // g
        if lock == "h":
            w, c = clampfix(r_fromH(h, rw, rh)["v"])
        else:
            h, c = clampfix(r_fromW(w, rw, rh)["v"])
    elif f == "lock":
        if ed.get("v") not in ("ratio", "w", "h"):
            return bad
        lock = ed["v"]
    else:
        return bad
    return {"w": w, "h": h, "rw": rw, "rh": rh, "lock": lock, "ok": True, "clamped": c}


def r_crop(w, h, rw, rh):
    if not (okint(w, 1, MAXPX) and okint(h, 1, MAXPX) and okint(rw, 1, MAXRATIO) and okint(rh, 1, MAXRATIO)):
        return None
    if Fraction(w, h) <= Fraction(rw, rh):
        cw, ch = w, max(1, (w * rh) // rw)
    else:
        ch, cw = h, max(1, (h * rw) // rh)
    return {"w": cw, "h": ch, "x": (w - cw) // 2, "y": (h - ch) // 2}


UN = {"in": (1, 1), "cm": (254, 100), "mm": (254, 10)}
DPS = {"in": 3, "cm": 2, "mm": 1}


def r_toPx(milli, unit, dpi):
    if not (okint(milli, 1, MAXMILLI) and okint(dpi, 1, MAXDPI)):
        return None
    if unit == "px":
        px = half_up(Fraction(milli, 1000))
    elif unit in UN:
        a, b = UN[unit]                     # size_in = value * b / a ... (value in unit) / (a/b) inches
        px = half_up(Fraction(milli, 1000) * dpi * Fraction(b, a))
    else:
        return None
    return px if 1 <= px <= MAXPX else None


def r_fromPx(px, unit, dpi):
    if not (okint(px, 1, MAXPX) and okint(dpi, 1, MAXDPI)):
        return None
    if unit == "px":
        return px
    if unit not in UN:
        return None
    a, b = UN[unit]
    val = Fraction(px, dpi) * Fraction(a, b)
    return half_up(val * 10 ** DPS[unit]) / 10 ** DPS[unit]


def r_parseList(s):
    parts = [p for p in re.split(r"[\s,;]+", "" if s is None else str(s)) if p]
    vals, bad = [], 0
    for p in parts:
        n = r_parsePx(p)
        if n is None:
            bad += 1
        elif len(vals) < MAXLIST and n not in vals:
            vals.append(n)
    return {"vals": vals, "bad": bad}


def r_batch(lst, rw, rh, by):
    if not (okint(rw, 1, MAXRATIO) and okint(rh, 1, MAXRATIO)) or by not in ("w", "h"):
        return None
    out = []
    for v in lst:
        o = r_fromW(v, rw, rh) if by == "w" else r_fromH(v, rw, rh)
        o2, cl = clampfix(o["v"])
        out.append({"w": v if by == "w" else o2, "h": o2 if by == "w" else v, "exact": o["exact"] and not cl, "clamped": cl})
    return out


FUNCS = {"reduce": r_reduce, "info": r_info, "fromW": r_fromW, "fromH": r_fromH, "parsePx": r_parsePx,
         "parseDec": r_parseDec, "resolve": r_resolve, "crop": r_crop, "toPx": r_toPx, "fromPx": r_fromPx,
         "parseList": r_parseList, "batch": r_batch}

# id -> (group, reduced rw, reduced rh); physical sizes for print presets: id -> (w, h, unit, divisor)
PRESET_PIN = {
    "sq": ("social", 1, 1), "p45": ("social", 4, 5), "story": ("social", 9, 16), "wide": ("social", 16, 9),
    "link": ("social", 191, 100), "p23": ("social", 2, 3), "banner": ("social", 3, 1),
    "hd": ("video", 16, 9), "vert": ("video", 9, 16), "cl43": ("video", 4, 3), "uw": ("video", 7, 3),
    "scope": ("video", 239, 100), "flat": ("video", 37, 20), "film": ("video", 3, 2),
    "a5": ("print", 74, 105), "a4": ("print", 70, 99), "a3": ("print", 99, 140),
    "letter": ("print", 17, 22), "legal": ("print", 17, 28), "p46": ("print", 2, 3), "p57": ("print", 5, 7),
    "p810": ("print", 4, 5), "p1114": ("print", 11, 14),
}
PRESET_SIZE = {"a5": (148, 210, "mm", 1), "a4": (210, 297, "mm", 1), "a3": (297, 420, "mm", 1),
               "letter": (85, 110, "in", 10), "legal": (85, 140, "in", 10), "p46": (40, 60, "in", 10),
               "p57": (50, 70, "in", 10), "p810": (80, 100, "in", 10), "p1114": (110, 140, "in", 10)}

# --------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------


def build_cases():
    C = []
    add = lambda *a: C.append(list(a))
    # reduce / info
    for wh in [(1920, 1080), (1, 1), (100000, 1), (100000, 99999), (1080, 1350), (1200, 628), (0, 5), (5, 0), (100001, 5),
               (7, 13), (4096, 2160), (3840, 2160), (210, 297), (-4, 6), (2.5, 3), (None, 3)]:
        add("reduce", *wh); add("info", *wh)
    # half-way and exact scaling
    for a in [(1000, 16, 9), (1, 16, 9), (3, 1, 2), (5, 1, 2), (1080, 4, 5), (1920, 191, 100), (99999, 7, 3), (100000, 100000, 1),
              (1, 100000, 1), (640, 3, 2), (641, 3, 2), (0, 1, 1), (800, 0, 1), (333, 239, 100), (12345, 99, 140)]:
        add("fromW", *a); add("fromH", *a)
    for s in ["1920", " 12 ", "0", "100000", "100001", "007", "1.5", "-3", "", None, "1e3", "1 2", "1234567", "٣"]:
        add("parsePx", s)
    for s in ["8.5", "8,5", ".5", "5.", "0", "0.000", "0.001", "100000", "100000.001", "12.3456", "1,234", "abc", "", None, " 11 ", "8.50", "0,0005", "999999.999"]:
        add("parseDec", s)
    # resolve: every lock x edit
    base = {"w": 1920, "h": 1080, "rw": 16, "rh": 9}
    for lock in ["ratio", "w", "h"]:
        st = dict(base, lock=lock)
        for ed in [{"f": "w", "v": 1000}, {"f": "w", "v": 1}, {"f": "w", "v": 100000}, {"f": "w", "v": 0}, {"f": "w", "v": 100001},
                   {"f": "h", "v": 1000}, {"f": "h", "v": 1}, {"f": "h", "v": 100000}, {"f": "h", "v": 7},
                   {"f": "ratio", "rw": 4, "rh": 5}, {"f": "ratio", "rw": 8, "rh": 10}, {"f": "ratio", "rw": 100000, "rh": 1},
                   {"f": "ratio", "rw": 1, "rh": 100000}, {"f": "ratio", "rw": 0, "rh": 5}, {"f": "lock", "v": "w"}, {"f": "lock", "v": "x"}, {"f": "nope"}]:
            add("resolve", st, ed)
    add("resolve", {"w": 0, "h": 5, "rw": 1, "rh": 1, "lock": "w"}, {"f": "w", "v": 3})
    add("resolve", {"w": 5, "h": 5, "rw": 1, "rh": 1, "lock": "zz"}, {"f": "w", "v": 3})
    # crop
    for a in [(1920, 1080, 1, 1), (1080, 1920, 1, 1), (1920, 1080, 4, 5), (1920, 1080, 9, 16), (1000, 1000, 191, 100), (1, 1, 1, 1),
              (5, 3, 16, 9), (3, 5, 16, 9), (1921, 1081, 16, 9), (4000, 3000, 3, 2), (100000, 100000, 100000, 1), (10, 10, 0, 1)]:
        add("crop", *a)
    # units
    for a in [(8500, "in", 300), (21590, "cm", 300), (210000, "mm", 300), (1, "in", 1), (1, "px", 72), (1500, "px", 72), (100000000, "in", 2400),
              (2540, "cm", 72), (254, "mm", 254), (25400, "mm", 1), (5500, "cm", 96), (5, "cm", 1), (1, "cm", 1), (100000000, "px", 96),
              (100000000, "cm", 1), (8500, "ft", 300), (8500, "in", 0), (8500, "in", 2401), (0, "in", 300)]:
        add("toPx", *a)
    for px in [1, 2550, 3300, 99999, 100000, 1920, 0, 100001]:
        for u in ["px", "in", "cm", "mm", "yd"]:
            for dpi in [1, 72, 96, 300, 2400, 0]:
                add("fromPx", px, u, dpi)
    for s in ["320, 640, 1280", "320 640\n640;1280,,", "", None, "1 2 x 3 0 100001", ",".join(str(i + 1) for i in range(60)), "5,5,5"]:
        add("parseList", s)
    add("batch", [320, 641, 1], 16, 9, "w")
    add("batch", [180, 1081, 100000], 16, 9, "h")
    add("batch", [100000], 1, 100000, "w")
    add("batch", [1], 1, 100000, "w")
    add("batch", [5], 16, 9, "z")
    # seeded random sweep
    rnd = random.Random(20261103)
    for _ in range(600):
        w, h = rnd.randint(1, 20000), rnd.randint(1, 20000)
        rw, rh = rnd.randint(1, 400), rnd.randint(1, 400)
        add("reduce", w, h); add("info", w, h); add("fromW", w, rw, rh); add("fromH", h, rw, rh); add("crop", w, h, rw, rh)
        lock = rnd.choice(["ratio", "w", "h"])
        ed = rnd.choice([{"f": "w", "v": rnd.randint(1, 30000)}, {"f": "h", "v": rnd.randint(1, 30000)},
                         {"f": "ratio", "rw": rnd.randint(1, 500), "rh": rnd.randint(1, 500)}])
        add("resolve", {"w": w, "h": h, "rw": rw, "rh": rh, "lock": lock}, ed)
        add("toPx", rnd.randint(1, 5000000), rnd.choice(["px", "in", "cm", "mm"]), rnd.randint(1, 2400))
        add("fromPx", rnd.randint(1, 100000), rnd.choice(["px", "in", "cm", "mm"]), rnd.randint(1, 2400))
        add("parseDec", "%d%s%s" % (rnd.randint(0, 99999), rnd.choice([".", ","]), "%0*d" % (rnd.randint(1, 3), rnd.randint(0, 99))))
        add("batch", [rnd.randint(1, 99999) for _ in range(3)], rw, rh, rnd.choice("wh"))
    return C


def known_answers():
    """Hand-computed answers - guards the reference itself."""
    assert r_fromW(1000, 16, 9)["v"] == 563 and not r_fromW(1000, 16, 9)["exact"]            # 562.5 rounds up
    assert r_fromW(1920, 16, 9) == {"v": 1080, "exact": True, "raw": 1080.0}
    assert r_fromH(1350, 4, 5)["v"] == 1080
    assert r_reduce(1920, 1080) == {"rw": 16, "rh": 9, "g": 120}
    assert r_reduce(210, 297) == {"rw": 70, "rh": 99, "g": 3}
    assert r_toPx(8500, "in", 300) == 2550 and r_toPx(21590, "cm", 300) == 2550 and r_toPx(210000, "mm", 300) == 2480
    assert r_fromPx(2550, "cm", 300) == 21.59 and r_fromPx(2480, "mm", 300) == 210.0
    assert r_crop(1920, 1080, 1, 1) == {"w": 1080, "h": 1080, "x": 420, "y": 0}
    assert r_parseDec("8,5") == 8500 and r_parseDec("0") is None and r_parseDec("1.2345") is None
    r = r_resolve({"w": 1920, "h": 1080, "rw": 16, "rh": 9, "lock": "w"}, {"f": "h", "v": 1350})
    assert (r["w"], r["h"], r["rw"], r["rh"]) == (1920, 1350, 64, 45)
    r = r_resolve({"w": 1920, "h": 1080, "rw": 16, "rh": 9, "lock": "ratio"}, {"f": "w", "v": 100000})
    assert r["h"] == 56250 and not r["clamped"]
    r = r_resolve({"w": 1920, "h": 1080, "rw": 16, "rh": 9, "lock": "ratio"}, {"f": "ratio", "rw": 100000, "rh": 1})
    assert r["h"] == 1 and r["clamped"]


def same(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    return a == b


def extract_block(src):
    m = re.search(r"// @@ARMATH BEGIN.*?\n(.*?)// @@ARMATH END", src, re.S)
    return m.group(0) if m else None


def run_js(block, cases):
    node = shutil.which("node")
    if not node:
        return None
    prog = block + "\nconst cases = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));\n" \
        "const out = cases.map(c => { try { return JSON.stringify(AR[c[0]](...c.slice(1))); } catch (e) { return JSON.stringify({__error: String(e)}); } });\n" \
        "console.log('[' + out.map(x => x === undefined ? 'null' : x).join(',') + ']');\n"
    with tempfile.TemporaryDirectory() as d:
        pj, cj = os.path.join(d, "run.js"), os.path.join(d, "cases.json")
        open(pj, "w", encoding="utf-8").write(prog)
        open(cj, "w", encoding="utf-8").write(json.dumps(cases))
        r = subprocess.run([node, pj, cj], capture_output=True, text=True, timeout=120, cwd=d)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-600:])
    return json.loads(r.stdout)


def main():
    if ARGS and APP not in ARGS:
        print("skip: check_aspectratio_math only checks AspectRatio")
        return 0
    known_answers()
    if not os.path.exists(GAME):
        print("BLOCK: %s not found" % GAME)
        return 1
    src = open(GAME, encoding="utf-8").read()
    block = extract_block(src)
    if not block:
        print("BLOCK: no `// @@ARMATH BEGIN … // @@ARMATH END` calculation block in %s" % GAME)
        return 1
    cases = build_cases()
    fails = []
    try:
        got = run_js(block, cases)
    except Exception as e:  # noqa: BLE001
        print("BLOCK: calculation block failed to run: %s" % e)
        return 1
    if got is None:
        print("WARN: node not found - reference self-check only (%d cases); the JS was NOT executed" % len(cases))
    else:
        for c, g in zip(cases, got):
            want = FUNCS[c[0]](*c[1:])
            if not same(want, g):
                fails.append((c, want, g))
    # preset table
    node = shutil.which("node")
    if node:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "p.js")
            open(p, "w", encoding="utf-8").write(block + "\nconsole.log(JSON.stringify(AR.PRESETS.map(p => Object.assign({}, p, {r: AR.reduce(p.w, p.h)}))));\n")
            presets = json.loads(subprocess.run([node, p], capture_output=True, text=True, cwd=d, timeout=60).stdout)
        ids = [p["id"] for p in presets]
        if sorted(ids) != sorted(PRESET_PIN) or len(set(ids)) != len(ids):
            fails.append(("presets ids", sorted(PRESET_PIN), sorted(ids)))
        for p in presets:
            pin = PRESET_PIN.get(p["id"])
            if pin and (p["g"], p["r"]["rw"], p["r"]["rh"]) != pin:
                fails.append(("preset " + p["id"], pin, (p["g"], p["r"]["rw"], p["r"]["rh"])))
            sz = PRESET_SIZE.get(p["id"])
            if sz and (p["w"], p["h"], p.get("u"), p.get("d")) != sz:
                fails.append(("preset size " + p["id"], sz, (p["w"], p["h"], p.get("u"), p.get("d"))))
            if p["g"] == "print" and p["id"] not in PRESET_SIZE:
                fails.append(("print preset without pinned size", p["id"], None))
    if fails:
        print("BLOCK: %d aspect-ratio maths mismatch(es) over %d cases" % (len(fails), len(cases)))
        for c, want, g in fails[:15]:
            print("MISMATCH %s: reference=%s app=%s" % (json.dumps(c)[:160], json.dumps(want), json.dumps(g)))
        return 1
    print("OK: %d cases, JS == Python reference; %d presets pinned" % (len(cases), len(PRESET_PIN)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
