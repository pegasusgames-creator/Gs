#!/usr/bin/env python3
"""check_bmicalculator_math.py - content gate for BMICalculator's BMI maths.

The pure `BM` block of BMICalculator's TOOL_CORE (between `// @@BMIMATH BEGIN`
and `// @@BMIMATH END`) is run under node on a table of cases (WHO band edges
18.5 / 25 / 30, healthy-weight range, unit conversions, Deurenberg body fat,
gauge, goal progress, number parsing) plus a seeded sweep, and every result is
compared with an independent exact-rational Python reference
(fractions.Fraction). BLOCKS on any mismatch.

Rules the reference encodes (and the app documents):
  * BMI = kg / (cm/100)^2; it is rounded half-up to 1 decimal (as displayed)
    BEFORE banding, so 18.5, 25, 30, 35, 40 start the upper WHO band;
  * bands (WHO adult): <16 severe thinness, 16-16.99 moderate, 17-18.49 mild,
    18.5-24.99 normal, 25-29.99 pre-obese, 30-34.99 / 35-39.99 / >=40 obese I/II/III;
  * healthy weight = BMI 18.5 .. 24.9 at the height, min rounded UP and max
    DOWN to 0.1 (kg or lb) so both ends stay inside the normal band;
  * 1 lb = 0.45359237 kg, 1 in = 2.54 cm exactly;
  * Deurenberg 1991: BF% = 1.20*BMI + 0.23*age - 10.8*sex - 5.4 (male = 1),
    adults 18-99 only.

Without node the pinned table is only checked against the Python reference
(WARN - the JS is not executed).

Usage: python3 scripts/check_bmicalculator_math.py [BMICalculator]
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
from fractions import Fraction as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ARGS = [a for a in sys.argv[1:] if not a.startswith("-")]
if _ARGS and "BMICalculator" not in _ARGS:
    print("check_bmicalculator_math: skipped (not BMICalculator)")
    sys.exit(0)
APP = "BMICalculator"
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")

LB = F(45359237, 100000000)
INCH = F(254, 100)


def fr(x):
    return F(repr(x)) if isinstance(x, float) else F(x)


# --------------------------------------------------------------------------
# Independent reference (exact rationals)
# --------------------------------------------------------------------------
def r1_exact(x):                       # round half up to 1 decimal
    return F(math.floor(x * 10 + F(1, 2)), 10)


def ref_bmi(kg, cm):
    m = fr(cm) / 100
    return fr(kg) / (m * m)


def ref_band(b):
    v = r1_exact(b)
    for lim, name in ((16, "u3"), (17, "u2"), (F(37, 2), "u1"), (25, "n"), (30, "o"), (35, "o1"), (40, "o2")):
        if v < lim:
            return name
    return "o3"


def ref_healthy(cm, lb):
    m = fr(cm) / 100
    f = 1 / LB if lb else F(1)
    lo, hi = F(37, 2) * m * m * f * 10, F(249, 10) * m * m * f * 10
    return float(F(math.ceil(lo), 10)), float(F(math.floor(hi), 10))


def ref_bodyfat(b, age, male):
    if not isinstance(age, int) or age < 18 or age > 99:
        return None
    p = F(12, 10) * fr(b) + F(23, 100) * age - F(108, 10) * (1 if male else 0) - F(54, 10)
    return float(p) if 3 <= p <= 60 else None


def ref_gauge(b):
    return float((min(F(40), max(F(15), fr(b))) - 15) / 25)


def ref_progress(s, c, t):
    s, c, t = fr(s), fr(c), fr(t)
    tot = s - t
    if tot == 0:
        return 1.0 if c == t else 0.0
    return float(min(F(1), max(F(0), (s - c) / tot)))


def ref_reached(s, c, t):
    s, c, t = fr(s), fr(c), fr(t)
    return c <= t if s > t else c >= t if s < t else c == t


def ref_ftin(cm):
    total = math.floor(fr(cm) / INCH + F(1, 2))
    return {"ft": total // 12, "inch": total - (total // 12) * 12}


def ref_parse(s):
    s = str(s)
    s = "".join(chr(ord(c) - 0x660 + 48) if "٠" <= c <= "٩" else
                chr(ord(c) - 0x6F0 + 48) if "۰" <= c <= "۹" else
                chr(ord(c) - 0x966 + 48) if "०" <= c <= "९" else c for c in s)
    s = s.replace("٫", ".").replace(",", ".")
    s = re.sub(r"[\s  ]", "", s)
    return float(s) if re.fullmatch(r"\d+\.?\d*|\.\d+", s) else None


# --------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------
# Pinned, hand-verified expectations (also the fallback without node)
PINNED_BANDS = [  # (kg, cm, rounded bmi, band)
    (18.5, 100, 18.5, "n"), (18.4, 100, 18.4, "u1"), (18.45, 100, 18.5, "n"), (18.44, 100, 18.4, "u1"),
    (25, 100, 25.0, "o"), (24.9, 100, 24.9, "n"), (24.95, 100, 25.0, "o"), (24.94, 100, 24.9, "n"),
    (30, 100, 30.0, "o1"), (29.9, 100, 29.9, "o"), (35, 100, 35.0, "o2"), (40, 100, 40.0, "o3"),
    (39.9, 100, 39.9, "o2"), (16, 100, 16.0, "u2"), (15.9, 100, 15.9, "u3"), (17, 100, 17.0, "u1"),
    (16.99, 100, 17.0, "u1"), (74, 200, 18.5, "n"), (100, 200, 25.0, "o"), (120, 200, 30.0, "o1"),
    (70, 175, 22.9, "n"), (80, 180, 24.7, "n"), (90, 170, 31.1, "o1"),
]
PINNED_RANGE = [(170, 53.5, 71.9, 117.9, 158.6), (160, 47.4, 63.7, 104.5, 140.5), (180, 60.0, 80.6, 132.2, 177.8)]


def build_cases():
    c = {"bmi": [], "healthy": [], "bf": [], "gauge": [], "prog": [], "ftin": [], "parse": [], "conv": []}
    pairs = [(k, h) for k, h, _, _ in PINNED_BANDS]
    rnd = random.Random(1859)
    for _ in range(1500):
        pairs.append((round(rnd.uniform(2, 250), 1), round(rnd.uniform(50, 250), 1)))
    for _ in range(600):   # edge hunting: weights at exactly BMI 18.5 / 25 / 30 / 35 / 40 for whole-cm heights
        h = rnd.randint(100, 220)
        for b in (F(37, 2), F(25), F(30), F(35), F(40), F(249, 10), F(1845, 100), F(2495, 100)):
            kg = float(b * F(h, 100) ** 2)
            pairs.append((kg, h))
            pairs.append((round(kg, 1), h))
    for kg, cm in pairs:
        c["bmi"].append([kg, cm])
    for cm in list(range(50, 261)) + [150.5, 172.5, 183.7, 99.9]:
        c["healthy"].append([cm, False])
        c["healthy"].append([cm, True])
    for _ in range(1500):
        c["bf"].append([round(rnd.uniform(10, 50), 2), rnd.choice([17, 18, 19, 30, 45, 80, 99, 100, 18.5, 0]), rnd.random() < .5])
    c["bf"] += [[22.0, 30, True], [22.0, 30, False], [14.0, 18, True], [60.0, 99, False], [10.0, 20, True]]
    for b in [10, 14.9, 15, 15.1, 18.5, 25, 30, 39.9, 40, 41, 55]:
        c["gauge"].append([b])
    for s, cu, t in [(90, 85, 80), (90, 90, 80), (90, 80, 80), (90, 70, 80), (90, 95, 80), (60, 65, 70), (60, 70, 70), (60, 55, 70), (70, 70, 70), (70, 69, 70), (70, 71, 70), (80.5, 79.2, 75.0)]:
        c["prog"].append([s, cu, t])
    for cm in [150, 152.4, 152.39, 152.41, 170, 175.26, 180.34, 182.88, 187.96, 50, 260, 157.48, 154.94]:
        c["ftin"].append([cm])
    for _ in range(300):
        c["ftin"].append([round(rnd.uniform(50, 260), 1)])
    for s in ["70", "70.5", "70,5", "٧٠٫٥", "۷۰.۵", "७०.५", "  70 ", "7 0", "70.5.1", "", "abc", "-5", "1e3", ".5", "5.", "70,", "1,234.5", "٧٠", "१५२"]:
        c["parse"].append([s])
    for v in [0, 1, 2.2046, 70, 154.3, 500, 1102.3]:
        c["conv"].append([v])
    return c


JS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/\/\/ @@BMIMATH BEGIN[^\n]*\n([\s\S]*?)\/\/ @@BMIMATH END/);
if (!m) { console.log(JSON.stringify({ error: 'BMIMATH block not found' })); process.exit(0); }
const BM = new Function(m[1] + '\nreturn BM;')();
const C = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = {};
out.bmi = C.bmi.map(([k, h]) => { const b = BM.bmi(k, h); return [b, BM.r1(b), BM.band(b)]; });
out.healthy = C.healthy.map(([h, lb]) => { const r = BM.healthy(h, lb); return [r.min, r.max]; });
out.bf = C.bf.map(([b, a, male]) => BM.bodyFat(b, a, male));
out.gauge = C.gauge.map(([b]) => BM.gaugePos(b));
out.prog = C.prog.map(([s, c, t]) => [BM.goalProgress(s, c, t), BM.goalReached(s, c, t)]);
out.ftin = C.ftin.map(([cm]) => BM.cmToFtIn(cm));
out.parse = C.parse.map(([s]) => { const v = BM.parseNum(s); return isNaN(v) ? null : v; });
out.conv = C.conv.map(([v]) => [BM.kgToLb(v), BM.lbToKg(v), BM.ftInToCm(5, 7), BM.validKg(v), BM.validCm(v)]);
out.edges = [BM.band(18.5), BM.band(25), BM.band(30), BM.band(35), BM.band(40), BM.band(18.44), BM.band(24.94), BM.band(29.94), BM.band(18.49), BM.band(29.99)];
console.log(JSON.stringify(out));
"""


def extract_block():
    src = open(GAME, encoding="utf8").read()
    m = re.search(r"// @@BMIMATH BEGIN[^\n]*\n(.*?)// @@BMIMATH END", src, re.S)
    return m.group(1) if m else None


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a is b
    return abs(a - b) <= tol * max(1.0, abs(b))


def main():
    warns, bad = [], []
    if not os.path.isfile(GAME):
        print("BLOCKER: %s missing" % GAME)
        return 1
    if extract_block() is None:
        print("BLOCKER: no `// @@BMIMATH BEGIN/END` block in %s" % GAME)
        return 1
    # 1. the reference against the hand-pinned expectations
    for kg, cm, r, band in PINNED_BANDS:
        b = ref_bmi(kg, cm)
        if float(r1_exact(b)) != r or ref_band(b) != band:
            bad.append("reference vs pinned band mismatch at %s kg / %s cm" % (kg, cm))
    for cm, lo, hi, llo, lhi in PINNED_RANGE:
        if ref_healthy(cm, False) != (lo, hi) or ref_healthy(cm, True) != (llo, lhi):
            bad.append("reference healthy range for %s cm: %s / %s, pinned %s %s %s %s" % (cm, ref_healthy(cm, False), ref_healthy(cm, True), lo, hi, llo, lhi))
    cases = build_cases()
    node = shutil.which("node")
    if not node:
        warns.append("node not found - JS not executed; only the pinned table vs the Python reference was checked")
    else:
        td = tempfile.mkdtemp(prefix="bmigate_")
        try:
            dj, cj = os.path.join(td, "run.js"), os.path.join(td, "cases.json")
            open(dj, "w").write(JS)
            json.dump(cases, open(cj, "w"))
            p = subprocess.run([node, dj, GAME, cj], capture_output=True, text=True, timeout=300)
            if p.returncode != 0:
                print("BLOCKER: node failed:\n" + p.stderr[-1500:])
                return 1
            res = json.loads(p.stdout)
        finally:
            shutil.rmtree(td, ignore_errors=True)
        if "error" in res:
            print("BLOCKER: " + res["error"])
            return 1

        def chk(label, got, want):
            if got != want:
                bad.append("%s: JS %r != reference %r" % (label, got, want))

        for (kg, cm), (b, r, band) in zip(cases["bmi"], res["bmi"]):
            eb = ref_bmi(kg, cm)
            if not close(b, float(eb)):
                bad.append("bmi(%s,%s): JS %r != %r" % (kg, cm, b, float(eb)))
            chk("r1(bmi(%s,%s))" % (kg, cm), r, float(r1_exact(eb)))
            chk("band(bmi(%s,%s)) [bmi %s]" % (kg, cm, float(eb)), band, ref_band(eb))
        for (cm, lb), (lo, hi) in zip(cases["healthy"], res["healthy"]):
            chk("healthy(%s,lb=%s)" % (cm, lb), [lo, hi], list(ref_healthy(cm, lb)))
        for (b, a, male), got in zip(cases["bf"], res["bf"]):
            w = ref_bodyfat(b, a, male)
            if not close(got, w):
                bad.append("bodyFat(%s,%s,%s): JS %r != %r" % (b, a, male, got, w))
        for (b,), got in zip(cases["gauge"], res["gauge"]):
            if not close(got, ref_gauge(b)):
                bad.append("gaugePos(%s): JS %r != %r" % (b, got, ref_gauge(b)))
        for (s, c, t), (pg, rc) in zip(cases["prog"], res["prog"]):
            if not close(pg, ref_progress(s, c, t)):
                bad.append("goalProgress(%s,%s,%s): JS %r != %r" % (s, c, t, pg, ref_progress(s, c, t)))
            chk("goalReached(%s,%s,%s)" % (s, c, t), rc, ref_reached(s, c, t))
        for (cm,), got in zip(cases["ftin"], res["ftin"]):
            chk("cmToFtIn(%s)" % cm, got, ref_ftin(cm))
        for (s,), got in zip(cases["parse"], res["parse"]):
            if not close(got, ref_parse(s)):
                bad.append("parseNum(%r): JS %r != %r" % (s, got, ref_parse(s)))
        for (v,), (lb, kg, cm57, vk, vc) in zip(cases["conv"], res["conv"]):
            if not close(lb, float(fr(v) / LB)) or not close(kg, float(fr(v) * LB)):
                bad.append("kg/lb conversion of %s: JS %r %r" % (v, lb, kg))
            if not close(cm57, float((5 * 12 + 7) * INCH)):
                bad.append("ftInToCm(5,7) = %r" % cm57)
            chk("validKg(%s)" % v, vk, 2 <= v <= 500)
            chk("validCm(%s)" % v, vc, 50 <= v <= 260)
        chk("WHO band edges 18.5/25/30/35/40 (+ rounded 18.44/24.94/29.94/18.49/29.99)", res["edges"], ["n", "o", "o1", "o2", "o3", "u1", "n", "o", "n", "o1"])
    for w in warns:
        print("WARN:", w)
    if bad:
        for b in bad[:40]:
            print("BLOCKER:", b)
        if len(bad) > 40:
            print("... and %d more" % (len(bad) - 40))
        return 1
    print("check_bmicalculator_math: OK (%d BMI cases, %d healthy-range heights, %d body-fat cases)" % (len(cases["bmi"]), len(cases["healthy"]), len(cases["bf"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
