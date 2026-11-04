#!/usr/bin/env python3
"""check_bloodsugarlog_math.py - content gate for BloodSugarLog's glucose maths.

The pure `GL` block of BloodSugarLog's TOOL_CORE (between `// @@BSMATH BEGIN`
and `// @@BSMATH END`) is run under node on pinned cases plus a seeded sweep and
compared with an independent exact-rational Python reference (fractions).
BLOCKS on any mismatch.

Rules the reference encodes (and the app documents):
  * 1 mmol/L = 18.0156 mg/dL. A reading is stored as WHOLE mg/dL
    (mmol/L x 18.0156, rounded half up) and shown in mmol/L with one decimal
    (mg/dL / 18.0156, rounded half up); a 1-decimal mmol/L value therefore
    round-trips (5.5 -> 99 -> 5.5);
  * class limits are whole mg/dL; the target range's two ends are INSIDE it:
    very low < vlo <= low < lo <= in range <= hi < high <= vhi < very high;
    a meal context may carry its own lo/hi (inside vlo..vhi), else the general one;
  * time-of-day buckets by local hour: night 0-5, morning 6-10, midday 11-14,
    afternoon 15-18, evening 19-23;
  * averages: sum/n rounded half up to whole mg/dL; mmol/L = sum/n/18.0156,
    one decimal half up; percentages of readings rounded half up;
  * ADAG: eAG = 28.7 x A1C - 46.7  =>  eA1C = (mean mg/dL + 46.7) / 28.7,
    one decimal half up; shown only with >= 20 readings on >= 10 different days
    inside the last 90 days.

Without node the pinned table is only checked against the Python reference
(WARN - the JS is not executed).

Usage: python3 scripts/check_bloodsugarlog_math.py [BloodSugarLog]
Exit 1 on any mismatch. With only other app names it prints a skip line, exit 0.
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
if _ARGS and "BloodSugarLog" not in _ARGS:
    print("check_bloodsugarlog_math: skipped (not BloodSugarLog)")
    sys.exit(0)
APP = "BloodSugarLog"
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")

K = F(180156, 10000)          # mg/dL per mmol/L = 18.0156


def fr(x):
    return F(repr(x)) if isinstance(x, float) else F(x)


# --------------------------------------------------------------------------
# Independent reference (exact rationals)
# --------------------------------------------------------------------------
def half_up(x):                      # round half up to an integer
    return math.floor(F(x) + F(1, 2))


def ref_mmol_to_mg(x):
    return half_up(fr(x) * K)


def ref_mmol_tenths(total, n):       # (total / n) mg/dL in tenths of mmol/L
    return half_up(F(total, n) / K * 10)


def ref_valid_mg(mg):
    return isinstance(mg, int) and 20 <= mg <= 600


def ref_valid_range(r):
    return all(isinstance(r[k], int) for k in ("vlo", "lo", "hi", "vhi")) and 20 <= r["vlo"] <= r["lo"] < r["hi"] <= r["vhi"] <= 600


def ref_range_for(R, c):
    o = (R.get("ctx") or {}).get(c)
    if o and isinstance(o["lo"], int) and isinstance(o["hi"], int) and o["lo"] >= R["vlo"] and o["lo"] < o["hi"] and o["hi"] <= R["vhi"]:
        return {"lo": o["lo"], "hi": o["hi"], "vlo": R["vlo"], "vhi": R["vhi"]}
    return {"lo": R["lo"], "hi": R["hi"], "vlo": R["vlo"], "vhi": R["vhi"]}


def ref_classify(mg, r):
    if mg > r["vhi"]:
        return "vh"
    if mg > r["hi"]:
        return "h"
    if mg < r["vlo"]:
        return "vl"
    if mg < r["lo"]:
        return "l"
    return "in"


def ref_bucket(h):
    for lim, name in ((6, "ni"), (11, "mo"), (15, "md"), (19, "af")):
        if h < lim:
            return name
    return "ev"


def ref_stats(lst, R):
    o = {"n": 0, "sum": 0, "min": None, "max": None, "cls": dict.fromkeys(["vl", "l", "in", "h", "vh"], 0),
         "bucket": {k: {"n": 0, "sum": 0} for k in ["ni", "mo", "md", "af", "ev"]},
         "ctx": {k: {"n": 0, "sum": 0} for k in ["f", "b", "a", "n", "o"]}}
    for e in lst:
        o["n"] += 1
        o["sum"] += e["mg"]
        o["min"] = e["mg"] if o["min"] is None else min(o["min"], e["mg"])
        o["max"] = e["mg"] if o["max"] is None else max(o["max"], e["mg"])
        o["cls"][ref_classify(e["mg"], ref_range_for(R, e["c"]))] += 1
        o["bucket"][ref_bucket(e["h"])]["n"] += 1
        o["bucket"][ref_bucket(e["h"])]["sum"] += e["mg"]
        k = e["c"] if e["c"] in ("f", "b", "a", "n", "o") else "o"
        o["ctx"][k]["n"] += 1
        o["ctx"][k]["sum"] += e["mg"]
    return o


def ref_a1c_tenths(total, n):
    # A1C = (mean + 46.7) / 28.7, in tenths
    return half_up((F(total, n) + F(467, 10)) / F(287, 10) * 10)


def ref_parse(s):
    s = str(s)
    s = "".join(chr(ord(c) - 0x660 + 48) if "٠" <= c <= "٩" else
                chr(ord(c) - 0x6F0 + 48) if "۰" <= c <= "۹" else
                chr(ord(c) - 0x966 + 48) if "०" <= c <= "९" else c for c in s)
    s = s.replace("٫", ".").replace(",", ".")
    s = re.sub(r"[\s  ]", "", s)
    return float(s) if re.fullmatch(r"\d+\.?\d*|\.\d+", s) else None


# --------------------------------------------------------------------------
# Pinned, hand-verified expectations (also the no-node fallback)
# --------------------------------------------------------------------------
PINNED_MMOL = [(5.5, 99), (3.9, 70), (10.0, 180), (7.0, 126), (4.0, 72), (13.9, 250), (3.0, 54), (1.1, 20), (33.3, 600), (5.0, 90), (5.6, 101), (6.1, 110)]
PINNED_TENTHS = [(99, 55), (70, 39), (180, 100), (126, 70), (54, 30), (250, 139), (100, 56), (90, 50), (20, 11), (600, 333)]
PINNED_A1C = [(154, 7.0), (126, 6.0), (117, 5.7), (97, 5.0), (183, 8.0), (212, 9.0)]   # ADAG published eAG -> A1C table
DEF = {"lo": 70, "hi": 180, "vlo": 54, "vhi": 250, "ctx": {}}
PINNED_CLASS = [(53, "vl"), (54, "l"), (69, "l"), (70, "in"), (180, "in"), (181, "h"), (250, "h"), (251, "vh"), (20, "vl"), (600, "vh")]


def build_cases():
    rnd = random.Random(180156)
    c = {"mmol": [], "tenths": [], "cls": [], "stats": [], "a1c": [], "parse": [], "bucket": [], "valid": [], "pct": [], "elig": []}
    for x, _ in PINNED_MMOL:
        c["mmol"].append(x)
    for i in range(1, 400):                       # every 0.1 from 0.1 to 40 and 0.01 steps
        c["mmol"].append(round(i / 10, 1))
    for _ in range(1500):
        c["mmol"].append(round(rnd.uniform(0.5, 36), 2))
    for _ in range(300):                          # three decimals: exercises the rounding ties
        c["mmol"].append(round(rnd.uniform(1, 33), 3))
    for mg in range(15, 620):
        c["tenths"].append([mg, 1])
    for _ in range(1500):
        n = rnd.randint(1, 400)
        c["tenths"].append([rnd.randint(20, 600) * n + rnd.randint(0, n), n])
    ranges = [DEF,
              {"lo": 80, "hi": 130, "vlo": 54, "vhi": 250, "ctx": {"f": {"lo": 80, "hi": 130}, "a": {"lo": 80, "hi": 180}, "n": {"lo": 100, "hi": 140}}},
              {"lo": 72, "hi": 140, "vlo": 60, "vhi": 300, "ctx": {"b": {"lo": 50, "hi": 140}, "a": {"lo": 90, "hi": 400}, "f": {"lo": 100, "hi": 100}}},
              {"lo": 90, "hi": 110, "vlo": 90, "vhi": 110, "ctx": {}}]
    c["ranges"] = ranges
    for ri, R in enumerate(ranges):
        for mg in range(18, 605):
            for cx in ("f", "b", "a", "n", "o"):
                if (mg + ord(cx)) % 3 == 0 or mg in (53, 54, 69, 70, 71, 100, 129, 130, 131, 139, 140, 141, 179, 180, 181, 249, 250, 251):
                    c["cls"].append([ri, mg, cx])
    for _ in range(300):                          # list stats
        ri = rnd.randrange(len(ranges))
        n = rnd.choice([0, 1, 2, 5, 20, 60, 200])
        lst = [{"mg": rnd.randint(20, 600) if rnd.random() < .2 else rnd.randint(55, 260), "c": rnd.choice(["f", "b", "a", "n", "o", "o", "x"]), "h": rnd.randint(0, 23)} for _ in range(n)]
        c["stats"].append({"r": ri, "list": lst})
    for _ in range(1500):
        n = rnd.randint(1, 500)
        c["a1c"].append([rnd.randint(20, 600) * n + rnd.randint(0, n), n])
    for sm, n in [(154, 1), (308, 2), (126, 1), (117, 1), (97, 1), (183, 1), (212, 1), (100, 1), (120, 1), (140, 1), (180, 1)]:
        c["a1c"].append([sm, n])
    for s in ["99", "5.5", "5,5", "٥٫٥", "۹۹", "९९", " 99 ", "9 9", "5.5.1", "", "abc", "-5", "1e3", ".5", "5.", "5,", "1,234.5", "١٢٠"]:
        c["parse"].append(s)
    c["bucket"] = list(range(0, 24))
    c["valid"] = [19, 20, 21, 599, 600, 601, 99.5, "99", 0, -5]
    for cnt, tot in [(0, 0), (1, 3), (2, 3), (1, 8), (3, 8), (1, 200), (5, 6), (7, 7), (0, 5), (1, 2), (33, 66), (1, 6)] + [(rnd.randint(0, k), k) for k in range(1, 400) for _ in range(2)]:
        c["pct"].append([cnt, tot])
    for n, d in [(19, 10), (20, 9), (20, 10), (21, 11), (0, 0), (100, 90), (19, 9)]:
        c["elig"].append([n, d])
    return c


JS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/\/\/ @@BSMATH BEGIN[^\n]*\n([\s\S]*?)\/\/ @@BSMATH END/);
if (!m) { console.log(JSON.stringify({ error: 'BSMATH block not found' })); process.exit(0); }
const GL = new Function(m[1] + '\nreturn GL;')();
const C = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = {};
out.mmol = C.mmol.map(x => GL.mmolToMg(x));
out.tenths = C.tenths.map(([s, n]) => GL.mmolTenths(s, n));
out.mean = C.tenths.map(([s, n]) => GL.meanR0(s, n));
out.cls = C.cls.map(([ri, mg, cx]) => GL.classify(mg, GL.rangeFor(C.ranges[ri], cx)));
out.stats = C.stats.map(s => GL.stats(s.list, C.ranges[s.r]));
out.a1c = C.a1c.map(([s, n]) => GL.a1cTenths(s, n));
out.parse = C.parse.map(s => { const v = GL.parseNum(s); return isNaN(v) ? null : v; });
out.bucket = C.bucket.map(h => GL.bucket(h));
out.valid = C.valid.map(v => GL.validMg(v));
out.pct = C.pct.map(([a, b]) => GL.pctInt(a, b));
out.elig = C.elig.map(([n, d]) => GL.a1cEligible(n, d));
out.vr = [[54, 70, 180, 250], [70, 70, 180, 180], [20, 20, 21, 600], [54, 70, 70, 250], [10, 70, 180, 250], [54, 70, 180, 700], [54, 70.5, 180, 250], [80, 70, 180, 250], [54, 70, 180, 150]]
  .map(([vlo, lo, hi, vhi]) => GL.validRange({ vlo: vlo, lo: lo, hi: hi, vhi: vhi }));
out.consts = [GL.MGMMOL, GL.A1C_WINDOW, GL.A1C_MIN_READINGS, GL.A1C_MIN_DAYS, GL.MIN_MG, GL.MAX_MG];
console.log(JSON.stringify(out));
"""


def extract_block():
    src = open(GAME, encoding="utf8").read()
    m = re.search(r"// @@BSMATH BEGIN[^\n]*\n(.*?)// @@BSMATH END", src, re.S)
    return m.group(1) if m else None


def main():
    warns, bad = [], []
    if not os.path.isfile(GAME):
        print("BLOCKER: %s missing" % GAME)
        return 1
    if extract_block() is None:
        print("BLOCKER: no `// @@BSMATH BEGIN/END` block in %s" % GAME)
        return 1
    # 1. the reference against the hand-pinned expectations
    for x, mg in PINNED_MMOL:
        if ref_mmol_to_mg(x) != mg:
            bad.append("reference: %s mmol/L -> %s, pinned %s" % (x, ref_mmol_to_mg(x), mg))
    for mg, ten in PINNED_TENTHS:
        if ref_mmol_tenths(mg, 1) != ten:
            bad.append("reference: %s mg/dL -> %s tenths mmol/L, pinned %s" % (mg, ref_mmol_tenths(mg, 1), ten))
    for mg, a1c in PINNED_A1C:
        if ref_a1c_tenths(mg, 1) != round(a1c * 10):
            bad.append("reference: eAG %s -> A1C %s, ADAG table says %s" % (mg, ref_a1c_tenths(mg, 1) / 10, a1c))
    for mg, k in PINNED_CLASS:
        if ref_classify(mg, DEF) != k:
            bad.append("reference class of %s = %s, pinned %s" % (mg, ref_classify(mg, DEF), k))
    cases = build_cases()
    # round trip: one-decimal mmol/L survives storage as whole mg/dL
    for i in range(11, 334):
        x = i / 10
        if ref_mmol_tenths(ref_mmol_to_mg(x), 1) != i:
            bad.append("reference round trip %s mmol/L -> %s mg/dL -> %s tenths" % (x, ref_mmol_to_mg(x), ref_mmol_tenths(ref_mmol_to_mg(x), 1)))
            break
    node = shutil.which("node")
    if not node:
        warns.append("node not found - JS not executed; only the pinned table vs the Python reference was checked")
    else:
        td = tempfile.mkdtemp(prefix="bsgate_")
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

        chk("constants [18.0156, 90, 20, 10, 20, 600]", res["consts"], [18.0156, 90, 20, 10, 20, 600])
        for x, got in zip(cases["mmol"], res["mmol"]):
            chk("mmolToMg(%s)" % x, got, ref_mmol_to_mg(x))
        for (s, n), got, mean in zip(cases["tenths"], res["tenths"], res["mean"]):
            chk("mmolTenths(%s,%s)" % (s, n), got, ref_mmol_tenths(s, n))
            chk("meanR0(%s,%s)" % (s, n), mean, half_up(F(s, n)))
        for (ri, mg, cx), got in zip(cases["cls"], res["cls"]):
            chk("classify(%s, ctx %s, range #%s)" % (mg, cx, ri), got, ref_classify(mg, ref_range_for(cases["ranges"][ri], cx)))
        for s, got in zip(cases["stats"], res["stats"]):
            want = ref_stats(s["list"], cases["ranges"][s["r"]])
            chk("stats(n=%d, range #%d)" % (len(s["list"]), s["r"]), got, want)
        for (s, n), got in zip(cases["a1c"], res["a1c"]):
            chk("a1cTenths(%s,%s)" % (s, n), got, ref_a1c_tenths(s, n))
        for s, got in zip(cases["parse"], res["parse"]):
            w = ref_parse(s)
            if (got is None) != (w is None) or (got is not None and abs(got - w) > 1e-12):
                bad.append("parseNum(%r): JS %r != %r" % (s, got, w))
        for h, got in zip(cases["bucket"], res["bucket"]):
            chk("bucket(%s)" % h, got, ref_bucket(h))
        for v, got in zip(cases["valid"], res["valid"]):
            chk("validMg(%r)" % (v,), got, ref_valid_mg(v))
        for (a, b), got in zip(cases["pct"], res["pct"]):
            chk("pctInt(%s,%s)" % (a, b), got, half_up(F(100 * a, b)) if b else 0)
        for (n, d), got in zip(cases["elig"], res["elig"]):
            chk("a1cEligible(%s,%s)" % (n, d), got, n >= 20 and d >= 10)
        vr_in = [[54, 70, 180, 250], [70, 70, 180, 180], [20, 20, 21, 600], [54, 70, 70, 250], [10, 70, 180, 250], [54, 70, 180, 700], [54, 70.5, 180, 250], [80, 70, 180, 250], [54, 70, 180, 150]]
        want_vr = [ref_valid_range(dict(zip(("vlo", "lo", "hi", "vhi"), r))) for r in vr_in]
        chk("validRange table", res["vr"], want_vr)
    for w in warns:
        print("WARN:", w)
    if bad:
        for b in bad[:40]:
            print("BLOCKER:", b)
        if len(bad) > 40:
            print("... and %d more" % (len(bad) - 40))
        return 1
    print("check_bloodsugarlog_math: OK (%d mmol/L conversions, %d mean/tenths, %d classifications, %d list stats, %d A1C cases)" % (
        len(cases["mmol"]), len(cases["tenths"]), len(cases["cls"]), len(cases["stats"]), len(cases["a1c"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
