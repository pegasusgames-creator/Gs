#!/usr/bin/env python3
"""check_bloodpressurelog_categories.py - content gate for BloodPressureLog's category maths.

The pure `BP` block of BloodPressureLog's TOOL_CORE (between `// @@BPMATH BEGIN` and
`// @@BPMATH END`) is run under node over EVERY systolic/diastolic pair of a grid
(systolic 40..320 x diastolic 20..220, all integers) plus averaging cases, and each
result is compared with an independent Python reference of the 2017 ACC/AHA adult
guideline. BLOCKS on any mismatch, especially at each category boundary.

Reference (2017 ACC/AHA, adults):
  Normal              SBP < 120  and DBP < 80
  Elevated            SBP 120-129 and DBP < 80
  Stage 1             SBP 130-139 or DBP 80-89
  Stage 2             SBP >= 140 or DBP >= 90
  Hypertensive crisis SBP > 180 and/or DBP > 120
(the higher category wins when systolic and diastolic fall in different ones).
The calm "seek medical help" note shows at SBP >= 180 or DBP >= 120 (the brief's threshold,
one mmHg earlier than the crisis category - deliberate, safe side).
Averages: arithmetic mean of whole mmHg, rounded half up (exact Fractions); pulse mean over the
readings that have a pulse. Morning = 04:00-11:59, evening = 17:00-23:59, otherwise neither.
Validity: SBP 50-300, DBP 30-200, SBP > DBP, pulse 20-250 (integers).

It also checks that the five category names + the crisis note exist in all 13 languages and the
English copy names the 2017 ACC/AHA guideline and says "not a diagnosis"/"not medical advice".

Without node the pinned boundary table is checked against the Python reference only (WARN).

Usage: python3 scripts/check_bloodpressurelog_categories.py [BloodPressureLog]
Exit 1 on any mismatch. With other app names only: prints a skip line, exit 0.
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
if _ARGS and "BloodPressureLog" not in _ARGS:
    print("check_bloodpressurelog_categories: skipped (not BloodPressureLog)")
    sys.exit(0)
APP = "BloodPressureLog"
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")


def ref_cat(s, d):
    if s > 180 or d > 120:
        return "crisis"
    if s >= 140 or d >= 90:
        return "s2"
    if s >= 130 or d >= 80:
        return "s1"
    if s >= 120:
        return "elev"
    return "norm"


def ref_alert(s, d):
    return s >= 180 or d >= 120


def ref_valid(s, d):
    return 50 <= s <= 300 and 30 <= d <= 200 and s > d


def ref_slot(h):
    return "am" if 4 <= h < 12 else "pm" if 17 <= h <= 23 else None


def ref_mean(vals):
    if not vals:
        return None
    return math.floor(F(sum(vals), len(vals)) + F(1, 2))


def ref_avg(rows):
    ps = [r[2] for r in rows if r[2] is not None]
    return {"n": len(rows), "s": ref_mean([r[0] for r in rows]), "d": ref_mean([r[1] for r in rows]),
            "p": ref_mean(ps), "pn": len(ps)}


# Hand-verified boundary table (also the no-node fallback)
PINNED = [
    (119, 79, "norm"), (119, 80, "s1"), (120, 79, "elev"), (120, 80, "s1"), (129, 79, "elev"), (129, 80, "s1"),
    (130, 79, "s1"), (130, 70, "s1"), (139, 89, "s1"), (139, 90, "s2"), (140, 70, "s2"), (140, 89, "s2"),
    (150, 85, "s2"), (110, 90, "s2"), (180, 100, "s2"), (181, 100, "crisis"), (170, 120, "s2"), (170, 121, "crisis"),
    (180, 120, "s2"), (181, 121, "crisis"), (200, 130, "crisis"), (118, 76, "norm"), (124, 76, "elev"), (60, 40, "norm"),
]


def build_cases():
    c = {"grid": [], "avg": [], "slot": list(range(24))}
    for s in range(40, 321):
        for d in range(20, 221):
            c["grid"].append([s, d])
    rnd = random.Random(2017)
    for _ in range(1500):
        n = rnd.randint(1, 14)
        rows = [[rnd.randint(90, 190), rnd.randint(50, 110), rnd.choice([None, rnd.randint(45, 110)])] for _ in range(n)]
        c["avg"].append(rows)
    # exact .5 cases
    for rows in ([[120, 80, 70], [121, 81, 71]], [[119, 79, None], [120, 80, 70]], [[100, 60, 60], [101, 61, 61], [100, 60, 62], [101, 61, 63]],
                 [[130, 85, 75]], [[129, 79, None], [130, 80, None]]):
        c["avg"].append(rows)
    return c


JS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/\/\/ @@BPMATH BEGIN[^\n]*\n([\s\S]*?)\/\/ @@BPMATH END/);
if (!m) { console.log(JSON.stringify({ error: 'BPMATH block not found' })); process.exit(0); }
const BP = new Function(m[1] + '\nreturn BP;')();
const C = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = {};
out.grid = C.grid.map(([s, d]) => [BP.cat(s, d), BP.alert(s, d), BP.valid(s, d)]);
out.avg = C.avg.map(rows => { const a = BP.avg(rows.map(r => ({ s: r[0], d: r[1], p: r[2] }))); return [a.n, a.s, a.d, a.p, a.pn, BP.cat(a.s, a.d)]; });
out.slot = C.slot.map(h => BP.slot(h));
console.log(JSON.stringify(out));
"""


def extract_block():
    src = open(GAME, encoding="utf8").read()
    m = re.search(r"// @@BPMATH BEGIN[^\n]*\n(.*?)// @@BPMATH END", src, re.S)
    return m.group(1) if m else None


def main():
    errs, warns = [], []
    # 0. pinned table vs reference (always)
    for s, d, want in PINNED:
        if ref_cat(s, d) != want:
            errs.append("reference self-check failed for %d/%d: %s != %s" % (s, d, ref_cat(s, d), want))
    if not os.path.exists(GAME):
        print("check_bloodpressurelog_categories: %s missing" % GAME)
        return 1
    if extract_block() is None:
        errs.append("BPMATH block not found in game.html")
    cases = build_cases()
    node = shutil.which("node")
    if node and not errs:
        with tempfile.TemporaryDirectory() as td:
            cf = os.path.join(td, "cases.json")
            jf = os.path.join(td, "run.js")
            json.dump(cases, open(cf, "w"))
            open(jf, "w").write(JS)
            r = subprocess.run([node, jf, GAME, cf], capture_output=True, text=True, timeout=240)
            try:
                out = json.loads(r.stdout.strip().splitlines()[-1])
            except Exception:
                out = {"error": "node failed: " + (r.stderr or r.stdout)[:300]}
        if "error" in out:
            errs.append(out["error"])
        else:
            bad = 0
            for (s, d), (cat, al, val) in zip(cases["grid"], out["grid"]):
                exp = (ref_cat(s, d), ref_alert(s, d), ref_valid(s, d))
                if (cat, al, val) != exp:
                    bad += 1
                    if bad <= 8:
                        errs.append("%d/%d: app %s alert=%s valid=%s, reference %s alert=%s valid=%s" % (s, d, cat, al, val, exp[0], exp[1], exp[2]))
            if bad > 8:
                errs.append("... %d grid mismatches in total" % bad)
            for rows, got in zip(cases["avg"], out["avg"]):
                a = ref_avg(rows)
                exp = [a["n"], a["s"], a["d"], a["p"], a["pn"], ref_cat(a["s"], a["d"])]
                if got != exp:
                    errs.append("average mismatch for %s: app %s, reference %s" % (rows[:3], got, exp))
                    break
            for h, got in zip(cases["slot"], out["slot"]):
                if got != ref_slot(h):
                    errs.append("slot(%d): app %s, reference %s" % (h, got, ref_slot(h)))
    elif not node:
        warns.append("node not found - the JS was NOT executed (pinned table checked against the reference only)")
    # 1. strings: categories + crisis note in all 13 languages; guideline + disclaimer in English
    src = open(GAME, encoding="utf8").read()
    langs = ["en", "ar", "de", "es", "fr", "hi", "id", "it", "ja", "pt", "tr", "uk", "zh"]
    i = src.find("const TOOL_I18N")
    tail = src[i:]
    for l in langs:
        m = re.search(r"\n  %s: (\{.*?\}),\n" % l, tail)
        if not m:
            errs.append("TOOL_I18N language %s missing" % l)
            continue
        try:
            d = json.loads(m.group(1))
        except Exception as e:
            errs.append("TOOL_I18N %s not valid JSON: %s" % (l, e))
            continue
        for k in ("cat_norm", "cat_elev", "cat_s1", "cat_s2", "cat_crisis", "cat_line", "crisis_t", "crisis_b", "disc_short", "cat_note"):
            if not d.get(k):
                errs.append("%s: missing %s" % (l, k))
        if "{cat}" not in d.get("cat_line", "{cat}"):
            errs.append("%s: cat_line lacks {cat}" % l)
        if len({d.get(k) for k in ("cat_norm", "cat_elev", "cat_s1", "cat_s2", "cat_crisis")}) != 5:
            errs.append("%s: category names are not 5 distinct strings" % l)
        if l == "en":
            blob = json.dumps(d)
            if "2017 ACC/AHA" not in d["cat_line"] or "180/120" not in d["crisis_b"]:
                errs.append("en: cat_line must name the 2017 ACC/AHA guideline and crisis_b the 180/120 threshold")
            if not re.search(r"not (a )?(medical advice|diagnosis)", blob, re.I):
                errs.append("en: disclaimer wording missing")
            if re.search(r"\b(diagnos(e|es|ed) you|you have hypertension|you are hypertensive)\b", blob, re.I):
                errs.append("en: diagnostic wording found")
    for w in warns:
        print("WARN:", w)
    if errs:
        print("check_bloodpressurelog_categories: FAIL")
        for e in errs[:30]:
            print("  -", e)
        return 1
    print("check_bloodpressurelog_categories: OK (%d grid pairs, %d averaging cases, 13 languages)" % (len(cases["grid"]), len(cases["avg"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
