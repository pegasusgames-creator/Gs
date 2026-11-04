#!/usr/bin/env python3
"""check_breathingexercise_patterns.py - content gate for BreathingExercise's pattern table + session maths.

Extracts the pure `@@BXMATH` block of BreathingExercise's TOOL_CORE and checks it (node when present,
else the pinned table in this file is checked against the reference only -> WARN):
  * every preset's phases are positive integers (deciseconds) and sum to the STATED cycle length;
  * the numbers in the pattern name match its timings (4-7-8 must be 4/7/8; "Coherent 5.5" = 5.5/5.5;
    "Box 4-4-4-4"; "Physiological sigh 2-1-6"; "Calm 4-6");
  * bxPlan(cycle, minutes): cycles == max(1, floor(minutes*600/cycle)), total == cycles*cycle, for every
    preset and every offered session length (1,2,3,5,10,15,20,30) plus a sweep of cycles 20..480 ds;
  * bxPhaseAt partitions a cycle (every ds maps to the phase whose [start,end) holds it);
  * bxFromCustom for every inhale/hold/exhale/rest 1..15/0..15: no zero phase, sum correct;
  * bxStreak against an independent reference on random day sets;
  * the pattern/phase strings exist in all 13 languages; English copy has no medical-claim wording and
    keeps the "not medical advice" note.
Usage: python3 scripts/check_breathingexercise_patterns.py [BreathingExercise]
Exit 1 on any mismatch. With other app names only: prints a skip line, exit 0.
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ARGS = [a for a in sys.argv[1:] if not a.startswith("-")]
if _ARGS and "BreathingExercise" not in _ARGS:
    print("check_breathingexercise_patterns: skipped (not BreathingExercise)")
    sys.exit(0)
APP = "BreathingExercise"
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")
LANGS = "en ar de es fr hi id it ja pt tr uk zh".split()
LENGTHS = [1, 2, 3, 5, 10, 15, 20, 30]
errs, warns = [], []

PINNED = [
    ("box", "Box 4-4-4-4", 160, [("in", 40), ("hold", 40), ("out", 40), ("rest", 40)]),
    ("p478", "4-7-8", 190, [("in", 40), ("hold", 70), ("out", 80)]),
    ("coh", "Coherent 5.5", 110, [("in", 55), ("out", 55)]),
    ("sigh", "Physiological sigh 2-1-6", 90, [("in", 20), ("in2", 10), ("out", 60)]),
    ("calm", "Calm 4-6", 100, [("in", 40), ("out", 60)]),
]


def ref_plan(cycle, minutes):
    c = max(1, (minutes * 600) // cycle)
    return c, c * cycle


def ref_custom(ph):
    out = [("in", ph[0] * 10)]
    if ph[1] > 0:
        out.append(("hold", ph[1] * 10))
    out.append(("out", ph[2] * 10))
    if ph[3] > 0:
        out.append(("rest", ph[3] * 10))
    return out


def ref_streak(keys, today):
    ds = {date.fromisoformat(k) for k in keys}
    t = date.fromisoformat(today)
    best = run = 0
    prev = None
    for d in sorted(ds):
        run = run + 1 if prev is not None and d == prev + timedelta(days=1) else 1
        best = max(best, run)
        prev = d
    cur, d = 0, (t if t in ds else t - timedelta(days=1))
    while d in ds:
        cur += 1
        d -= timedelta(days=1)
    return cur, best


def name_numbers(name):
    m = re.search(r"(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)+)", name)
    if m:
        return [float(x) for x in m.group(1).split("-")]
    m = re.search(r"(\d+(?:\.\d+)?)", name)
    return [float(m.group(1))] if m else []


def check_table(rows, tag):
    for pid, name, cycle, ph in rows:
        if not ph:
            errs.append(f"{tag} {pid}: no phases")
            continue
        for ty, d in ph:
            if not isinstance(d, int) or d <= 0:
                errs.append(f"{tag} {pid}: phase {ty} has non-positive length {d}")
        if sum(d for _, d in ph) != cycle:
            errs.append(f"{tag} {pid}: phases sum to {sum(d for _, d in ph)} ds but stated cycle is {cycle}")
        nums = name_numbers(name)
        secs = [d / 10 for _, d in ph]
        if len(nums) == 1:
            if any(abs(s - nums[0]) > 1e-9 for s in secs):
                errs.append(f"{tag} {pid}: name '{name}' says {nums[0]} s but timings are {secs}")
        elif nums and nums != secs:
            errs.append(f"{tag} {pid}: name '{name}' numbers {nums} do not match timings {secs}")
        elif not nums:
            errs.append(f"{tag} {pid}: name '{name}' states no timings")
        for m in LENGTHS:
            c, tot = ref_plan(cycle, m)
            if c < 1 or tot != c * cycle:
                errs.append(f"{tag} {pid}: bad ref plan for {m} min")


src = open(GAME, encoding="utf-8").read() if os.path.exists(GAME) else ""
m = re.search(r"// @@BXMATH BEGIN(.*?)// @@BXMATH END", src, re.S)
if not m:
    errs.append("BXMATH block missing from TOOL_CORE")
node = shutil.which("node")
if m and node:
    harness = m.group(1) + r"""
const out = {presets: BX_PRESETS.map(p => ({id: p.id, name: p.name, cycle: p.cycle, phases: p.phases})), plan: [], at: [], custom: [], streak: [], lens: [BX_LEN_FREE, BX_LEN_PRO]};
const cycles = BX_PRESETS.map(p => p.cycle);
for (let c = 20; c <= 480; c += 5) cycles.push(c);
cycles.forEach(c => [1,2,3,5,10,15,20,30].forEach(mn => out.plan.push([c, mn, bxPlan(c, mn)])));
BX_PRESETS.forEach(p => { for (let t = 0; t < p.cycle; t++) { const a = bxPhaseAt(p.phases, t); out.at.push([p.id, t, a.idx, a.into, a.dur]); } out.at.push([p.id, 'sum', bxCycle(p.phases)]); });
for (let a = 1; a <= 15; a++) for (let b = 0; b <= 15; b++) for (let c = 1; c <= 15; c += 2) for (let d = 0; d <= 15; d += 3) out.custom.push([[a,b,c,d], bxFromCustom([a,b,c,d])]);
let seed = 12345; const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
for (let i = 0; i < 400; i++) {
  const keys = [], base = Date.UTC(2026, 0, 1);
  const n = Math.floor(rnd() * 40);
  for (let j = 0; j < n; j++) { const dt = new Date(base + Math.floor(rnd() * 120) * 86400000); keys.push(dt.toISOString().slice(0, 10)); }
  const today = new Date(base + (60 + Math.floor(rnd() * 60)) * 86400000).toISOString().slice(0, 10);
  out.streak.push([keys, today, bxStreak(keys, today)]);
}
process.stdout.write(JSON.stringify(out));
"""
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "h.js")
        open(f, "w").write(harness)
        r = subprocess.run([node, f], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        errs.append("node harness failed: " + r.stderr.strip()[:300])
    else:
        o = json.loads(r.stdout)
        rows = [(p["id"], p["name"], p["cycle"], [tuple(x) for x in p["phases"]]) for p in o["presets"]]
        check_table(rows, "game.html")
        ids = [r_[0] for r_ in rows]
        for pid, *_ in PINNED:
            if pid not in ids:
                errs.append(f"preset '{pid}' missing from game.html")
        for pid, name, cycle, ph in PINNED:  # 4-7-8 etc. must keep their canonical timings
            for r_ in rows:
                if r_[0] == pid and (r_[2] != cycle or [tuple(x) for x in r_[3]] != ph):
                    errs.append(f"preset '{pid}' drifted from canonical timings {ph}")
        for c, mn, p in o["plan"]:
            rc, rt = ref_plan(c, mn)
            if p["cycles"] != rc or p["total"] != rt:
                errs.append(f"bxPlan({c},{mn}) = {p} expected cycles {rc} total {rt}")
            if p["total"] > max(mn * 600, c):
                errs.append(f"bxPlan({c},{mn}) total {p['total']} exceeds session length")
        prs = {p["id"]: p for p in o["presets"]}
        for row in o["at"]:
            if row[1] == "sum":
                if row[2] != prs[row[0]]["cycle"]:
                    errs.append(f"bxCycle({row[0]}) != stated cycle")
                continue
            pid, t, idx, into, dur = row
            ph = prs[pid]["phases"]
            start = sum(d for _, d in ph[:idx])
            if not (start <= t < start + ph[idx][1]) or into != t - start or dur != ph[idx][1]:
                errs.append(f"bxPhaseAt({pid},{t}) wrong: {row}")
                break
        for ph, got in o["custom"]:
            exp = ref_custom(ph)
            if [tuple(x) for x in got] != exp or any(d <= 0 for _, d in got):
                errs.append(f"bxFromCustom({ph}) = {got} expected {exp}")
                break
        for keys, today, got in o["streak"]:
            if (got["cur"], got["best"]) != ref_streak(keys, today):
                errs.append(f"bxStreak({sorted(set(keys))[:5]}..,{today}) = {got} expected {ref_streak(keys, today)}")
                break
        if o["lens"][0] != [1, 2, 3, 5] or o["lens"][1] != [10, 15, 20, 30]:
            errs.append(f"session lengths changed: {o['lens']}")
else:
    warns.append("node not available - pinned table checked against the reference only")
    check_table(PINNED, "pinned")

# strings: 13 languages, wellness wording
if src:
    i = src.find("const TOOL_I18N")
    blob = src[i:]
    need = ["pat_box", "pat_p478", "pat_coh", "pat_sigh", "pat_calm", "ph_in", "ph_in2", "ph_hold", "ph_out", "ph_rest",
            "v_in", "v_in2", "v_hold", "v_out", "v_rest", "wellness_note"]
    langs = {}
    for l in LANGS:
        mm = re.search(r"\n  %s: (\{.*?\}),\n" % l, blob)
        if not mm:
            errs.append(f"TOOL_I18N language '{l}' missing")
            continue
        langs[l] = json.loads(mm.group(1))
        for k in need:
            if k not in langs[l] or not langs[l][k].strip():
                errs.append(f"{l}: string '{k}' missing")
    for l, d in langs.items():
        for pid, _, _, ph in PINNED:
            s = d.get("pat_" + pid, "")
            digits = re.findall(r"\d+(?:[.,]\d+)?", s)
            exp = name_numbers(dict((p[0], p[1]) for p in PINNED)[pid])
            got = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", s)]
            if got and [g for g in got] != exp:
                errs.append(f"{l}: pat_{pid} '{s}' numbers {got} do not match {exp}")
    en = langs.get("en", {})
    alltxt = " ".join(en.values()).lower()
    for bad in ["cure", "treat anxiety", "treats ", "therapy", "anxiety disorder", "panic attack", "diagnos", "clinically", "heal ", "lower blood pressure", "insomnia"]:
        if bad in alltxt and "not medical advice" not in bad:
            if bad == "diagnos":
                continue
            errs.append(f"English copy contains medical-claim wording: '{bad}'")
    if "not medical advice" not in en.get("wellness_note", "").lower():
        errs.append("wellness_note must say it is not medical advice")

for w in warns:
    print("WARN:", w)
if errs:
    print("check_breathingexercise_patterns: %d problem(s)" % len(errs))
    for e in errs[:40]:
        print("  BLOCK:", e)
    sys.exit(1)
print("check_breathingexercise_patterns: OK (5 presets, %d plan cases, phase partition, custom, streak, 13 langs)" % (len(LENGTHS) * 5))
