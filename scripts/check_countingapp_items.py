#!/usr/bin/env python3
"""check_countingapp_items.py -- content gate for CountingApp ("Counting Fun").

Extracts the round generator (the block between `// @@GEN_BEGIN` and
`// @@GEN_END` in game.html, a pure object `CF`) and runs it under node (a
pinned sample of real generator output is checked instead when node is
missing), generating thousands of rounds for every game and level. BLOCKs when:
  * the number of objects/rods/cubes SHOWN differs from the answer (How many?),
  * a target/answer falls outside its level's range (independent spec below),
  * a skip-count row is not an arithmetic sequence with the level's step, the
    blank does not hold the answer, or a song row is not step*1..step*10,
  * a distractor equals the answer, options repeat, the answer is missing from
    the options, or a distractor already appears in the shown sequence,
  * the engine does not take its rounds from CF.round() / songs from
    CF.songSeq(), or the tap-to-count scene builds a different number of
    objects than its number.

Gate contract: with no args or with CountingApp among the args check it; with
other app names only print a skip line and exit 0.

  python3 scripts/check_countingapp_items.py [CountingApp]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "CountingApp"
GAME = os.path.join(BASE, APP, "android", "app", "src", "main", "assets", "game.html")
N_PER = 1500          # rounds per (game, level)

# Independent spec (do not import from the app).
RANGE = {
    "howmany": {1: (1, 5), 2: (6, 10), 3: (11, 20), 4: (11, 99)},
    "make": {1: (1, 5), 2: (6, 10), 3: (11, 20), 4: (11, 99)},
    "next": {1: (3, 20), 2: (6, 20), 3: (15, 100), 4: (30, 100)},
}
STEP = {1: 1, 2: 2, 3: 5, 4: 10}

HARNESS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/\/\/ @@GEN_BEGIN([\s\S]*?)\/\/ @@GEN_END/);
if (!m) { console.error('NO_GENERATOR'); process.exit(3); }
const CF = (new Function(m[1] + '; return CF;'))();
const N = +process.argv[3], out = [];
for (const g of ['howmany', 'make', 'next']) for (let lv = 1; lv <= 4; lv++) for (let i = 0; i < N; i++) {
  const r = CF.mulberry(1000 + i * 7 + lv);
  const ex = i % 3 === 0 ? [] : [((i * 5) % 20) + 1];
  out.push(CF.round(g, lv, r, ex));
}
out.push(CF.round('howmany', 0, CF.mulberry(1)), CF.round('next', 9, CF.mulberry(2)));   // out-of-range level clamps
process.stdout.write(JSON.stringify({ rounds: out, songs: CF.SONG_STEPS.map(s => [s, CF.songSeq(s)]) }));
"""

# Pinned sample (real generator output) used only when node is not installed.
PINNED = json.loads(r'''[{"game":"howmany","level":1,"answer":1,"lo":1,"hi":5,"kind":5,"shown":[{"k":"obj","v":1,"t":5}],"options":[1,2,3]},{"game":"howmany","level":1,"answer":4,"lo":1,"hi":5,"kind":0,"shown":[{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0}],"options":[3,4,2]},{"game":"howmany","level":1,"answer":2,"lo":1,"hi":5,"kind":7,"shown":[{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7}],"options":[1,2,3]},{"game":"howmany","level":2,"answer":8,"lo":6,"hi":10,"kind":0,"shown":[{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0},{"k":"obj","v":1,"t":0}],"options":[6,8,9,7]},{"game":"howmany","level":2,"answer":7,"lo":6,"hi":10,"kind":1,"shown":[{"k":"obj","v":1,"t":1},{"k":"obj","v":1,"t":1},{"k":"obj","v":1,"t":1},{"k":"obj","v":1,"t":1},{"k":"obj","v":1,"t":1},{"k":"obj","v":1,"t":1},{"k":"obj","v":1,"t":1}],"options":[7,8,9,5]},{"game":"howmany","level":2,"answer":6,"lo":6,"hi":10,"kind":2,"shown":[{"k":"obj","v":1,"t":2},{"k":"obj","v":1,"t":2},{"k":"obj","v":1,"t":2},{"k":"obj","v":1,"t":2},{"k":"obj","v":1,"t":2},{"k":"obj","v":1,"t":2}],"options":[7,6,5,4]},{"game":"howmany","level":3,"answer":19,"lo":11,"hi":20,"kind":4,"shown":[{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4},{"k":"obj","v":1,"t":4}],"options":[20,21,18,19]},{"game":"howmany","level":3,"answer":11,"lo":11,"hi":20,"kind":7,"shown":[{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7}],"options":[11,12,13,10]},{"game":"howmany","level":3,"answer":12,"lo":11,"hi":20,"kind":7,"shown":[{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7},{"k":"obj","v":1,"t":7}],"options":[12,14,13,10]},{"game":"howmany","level":4,"answer":91,"lo":11,"hi":99,"kind":7,"shown":[{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"one","v":1}],"options":[90,91,93,82]},{"game":"howmany","level":4,"answer":17,"lo":11,"hi":99,"kind":5,"shown":[{"k":"ten","v":10},{"k":"one","v":1},{"k":"one","v":1},{"k":"one","v":1},{"k":"one","v":1},{"k":"one","v":1},{"k":"one","v":1},{"k":"one","v":1}],"options":[8,17,16,15]},{"game":"howmany","level":4,"answer":84,"lo":11,"hi":99,"kind":4,"shown":[{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"ten","v":10},{"k":"one","v":1},{"k":"one","v":1},{"k":"one","v":1},{"k":"one","v":1}],"options":[85,48,83,84]},{"game":"make","level":1,"answer":1,"lo":1,"hi":5,"kind":5,"shown":[],"options":null},{"game":"make","level":1,"answer":4,"lo":1,"hi":5,"kind":0,"shown":[],"options":null},{"game":"make","level":1,"answer":2,"lo":1,"hi":5,"kind":7,"shown":[],"options":null},{"game":"make","level":2,"answer":8,"lo":6,"hi":10,"kind":0,"shown":[],"options":null},{"game":"make","level":2,"answer":7,"lo":6,"hi":10,"kind":1,"shown":[],"options":null},{"game":"make","level":2,"answer":6,"lo":6,"hi":10,"kind":2,"shown":[],"options":null},{"game":"make","level":3,"answer":19,"lo":11,"hi":20,"kind":4,"shown":[],"options":null},{"game":"make","level":3,"answer":11,"lo":11,"hi":20,"kind":7,"shown":[],"options":null},{"game":"make","level":3,"answer":12,"lo":11,"hi":20,"kind":7,"shown":[],"options":null},{"game":"make","level":4,"answer":91,"lo":11,"hi":99,"kind":7,"shown":[],"options":null},{"game":"make","level":4,"answer":17,"lo":11,"hi":99,"kind":5,"shown":[],"options":null},{"game":"make","level":4,"answer":84,"lo":11,"hi":99,"kind":4,"shown":[],"options":null},{"game":"next","level":1,"answer":5,"lo":3,"hi":20,"step":1,"seq":[1,2,3,4,5],"blank":4,"shown":[1,2,3,4],"options":[5,6,7]},{"game":"next","level":1,"answer":15,"lo":3,"hi":20,"step":1,"seq":[13,14,15,16,17],"blank":2,"shown":[13,14,16,17],"options":[15,11,21]},{"game":"next","level":1,"answer":9,"lo":3,"hi":20,"step":1,"seq":[5,6,7,8,9],"blank":4,"shown":[5,6,7,8],"options":[11,9,10]},{"game":"next","level":2,"answer":10,"lo":6,"hi":20,"step":2,"seq":[6,8,10,12,14],"blank":2,"shown":[6,8,12,14],"options":[10,9,15,11]},{"game":"next","level":2,"answer":8,"lo":6,"hi":20,"step":2,"seq":[4,6,8,10,12],"blank":2,"shown":[4,6,10,12],"options":[7,8,13,9]},{"game":"next","level":2,"answer":6,"lo":6,"hi":20,"step":2,"seq":[2,4,6,8,10],"blank":2,"shown":[2,4,8,10],"options":[6,11,5,7]},{"game":"next","level":3,"answer":80,"lo":15,"hi":100,"step":5,"seq":[65,70,75,80,85],"blank":3,"shown":[65,70,75,85],"options":[90,80,81,79]},{"game":"next","level":3,"answer":25,"lo":15,"hi":100,"step":5,"seq":[5,10,15,20,25],"blank":4,"shown":[5,10,15,20],"options":[25,35,24,30]},{"game":"next","level":3,"answer":35,"lo":15,"hi":100,"step":5,"seq":[15,20,25,30,35],"blank":4,"shown":[15,20,25,30],"options":[35,34,45,36]},{"game":"next","level":4,"answer":100,"lo":30,"hi":100,"step":10,"seq":[60,70,80,90,100],"blank":4,"shown":[60,70,80,90],"options":[100,99,94,96]},{"game":"next","level":4,"answer":50,"lo":30,"hi":100,"step":10,"seq":[10,20,30,40,50],"blank":4,"shown":[10,20,30,40],"options":[70,49,60,50]},{"game":"next","level":4,"answer":80,"lo":30,"hi":100,"step":10,"seq":[50,60,70,80,90],"blank":3,"shown":[50,60,70,90],"options":[100,81,79,80]}]''')


def check_round(r, errs):
    g, lv, ans = r.get("game"), r.get("level"), r.get("answer")
    if g not in RANGE or lv not in RANGE[g]:
        errs.append("unknown game/level %r/%r" % (g, lv)); return
    lo, hi = RANGE[g][lv]
    tag = "%s L%d answer %r" % (g, lv, ans)
    if not isinstance(ans, int) or ans < lo or ans > hi:
        errs.append("%s: outside the level range %d-%d" % (tag, lo, hi)); return
    opts = r.get("options")
    if g == "howmany":
        shown = r.get("shown") or []
        total = sum(s.get("v", 0) for s in shown)
        if total != ans:
            errs.append("%s: shows %d, not %d" % (tag, total, ans))
        if lv < 4:
            if len(shown) != ans or any(s.get("k") != "obj" or s.get("v") != 1 for s in shown):
                errs.append("%s: object count %d != answer" % (tag, len(shown)))
        else:
            tens = sum(1 for s in shown if s.get("k") == "ten" and s.get("v") == 10)
            ones = sum(1 for s in shown if s.get("k") == "one" and s.get("v") == 1)
            if (tens, ones) != (ans // 10, ans % 10) or tens + ones != len(shown):
                errs.append("%s: %d tens + %d ones does not make the answer" % (tag, tens, ones))
    if g == "make":
        if r.get("shown"):
            errs.append("%s: make round must not pre-fill the basket" % tag)
        return
    if not isinstance(opts, list) or len(opts) < 3:
        errs.append("%s: needs at least 3 options" % tag); return
    if opts.count(ans) != 1:
        errs.append("%s: answer appears %d times in options %r" % (tag, opts.count(ans), opts))
    if len(set(opts)) != len(opts):
        errs.append("%s: duplicate options %r" % (tag, opts))
    if any((not isinstance(o, int)) or o < 1 or o > 100 for o in opts):
        errs.append("%s: option outside 1-100 in %r" % (tag, opts))
    if g == "next":
        seq, blank, step = r.get("seq"), r.get("blank"), r.get("step")
        if step != STEP[lv]:
            errs.append("%s: step %r, expected %d" % (tag, step, STEP[lv])); return
        if not seq or len(seq) != 5 or any(seq[i + 1] - seq[i] != STEP[lv] for i in range(4)):
            errs.append("%s: sequence %r is not step %d" % (tag, seq, STEP[lv])); return
        if min(seq) < 1 or max(seq) > 100:
            errs.append("%s: sequence %r leaves 1-100" % (tag, seq))
        if not isinstance(blank, int) or blank < 2 or blank > 4 or seq[blank] != ans:
            errs.append("%s: blank %r does not hold the answer in %r" % (tag, blank, seq))
        if STEP[lv] > 1 and seq[0] % STEP[lv]:
            errs.append("%s: row %r does not start on a multiple of %d" % (tag, seq, STEP[lv]))
        shown = r.get("shown") or []
        if shown != [v for i, v in enumerate(seq) if i != blank]:
            errs.append("%s: shown numbers differ from the row" % tag)
        bad = [o for o in opts if o != ans and o in seq]
        if bad:
            errs.append("%s: distractor %r already appears in the row %r" % (tag, bad, seq))


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    if args and APP not in args:
        print("check_countingapp_items: skipped (%s not in run)" % APP)
        return 0
    if not os.path.exists(GAME):
        print("BLOCK: %s missing" % GAME)
        return 1
    src = open(GAME, encoding="utf8").read()
    errs, warns = [], []
    rounds, songs, mode = PINNED, [[2, [2 * i for i in range(1, 11)]], [5, [5 * i for i in range(1, 11)]], [10, [10 * i for i in range(1, 11)]]], "pinned sample"
    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(HARNESS); hp = f.name
        try:
            p = subprocess.run([node, hp, GAME, str(N_PER)], capture_output=True, text=True, timeout=300)
        finally:
            os.unlink(hp)
        if p.returncode != 0:
            print("BLOCK: generator could not run: " + (p.stderr.strip()[:300] or "exit %d" % p.returncode))
            return 1
        data = json.loads(p.stdout)
        rounds, songs, mode = data["rounds"], data["songs"], "node, %d rounds" % len(data["rounds"])
    for r in rounds:
        check_round(r, errs)
        if len(errs) > 25:
            break
    # skip-count songs: step * 1..10, exactly the 2s / 5s / 10s
    if [s[0] for s in songs] != [2, 5, 10]:
        errs.append("song steps are %r, expected [2, 5, 10]" % [s[0] for s in songs])
    for step, seq in songs:
        if seq != [step * i for i in range(1, 11)]:
            errs.append("song x%d row is %r" % (step, seq))
    # coverage: every level reaches both ends of its range
    seen = {}
    for r in rounds:
        if r.get("game") in RANGE and r.get("level") in RANGE[r["game"]]:
            seen.setdefault((r["game"], r["level"]), set()).add(r.get("answer"))
    if node:
        for (g, lv), vals in sorted(seen.items()):
            lo, hi = RANGE[g][lv]
            if min(vals) != lo or max(vals) != hi:
                warns.append("%s L%d only reaches %d-%d of %d-%d" % (g, lv, min(vals), max(vals), lo, hi))
    # engine wiring
    eng = re.search(r"@@REGION CONTENT_ENGINE\s*(.*?)@@END CONTENT_ENGINE", src, re.S)
    eng = eng.group(1) if eng else ""
    if "CF.round(" not in eng:
        errs.append("engine does not take rounds from CF.round()")
    if "CF.songSeq(" not in eng:
        errs.append("engine does not take song rows from CF.songSeq()")
    if "rd.shown.map" not in eng or "rd.options.map" not in eng:
        errs.append("How many? does not render exactly rd.shown / rd.options")
    if not re.search(r"Array\.from\(\{ length: n \}[^)]*\)\s*=>\s*'<button class=\"obj\"", eng):
        errs.append("tap-to-count scene must build exactly n objects (Array.from({length: n}))")
    for w in warns:
        print("WARN: " + w)
    for e in errs[:30]:
        print("BLOCK: " + e)
    if errs:
        print("check_countingapp_items: %d problem(s) (%s)" % (len(errs), mode))
        return 1
    print("check_countingapp_items: OK (%s)" % mode)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
