#!/usr/bin/env python3
"""check_basicmathkids_items.py -- content gate for BasicMathKids.

Extracts the app's question generator (the block between /*@@MATHGEN_BEGIN*/
and /*@@MATHGEN_END*/ in game.html) and runs it under node (a pinned sample is
checked instead when node is missing), generating thousands of items for every
skill and level. BLOCKs when:
  * an answer is wrong (recomputed here from the item's operands),
  * an operand or result is outside the level's range (never negative, never
    above 20),
  * a distractor equals the answer, options repeat, or the answer is missing
    from the options,
  * the engine does not take its questions from MG.gen().
WARNs when a level never reaches the top of its range.

Gate contract: with no args or with BasicMathKids among the args check it;
with other app names only print a skip line and exit 0.

  python3 scripts/check_basicmathkids_items.py [BasicMathKids]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "BasicMathKids"
GAME = os.path.join(BASE, APP, "android", "app", "src", "main", "assets", "game.html")
N_PER = 2500          # items per (skill, level[, op])

# Independent spec of the ranges (do not import from the app).
MAXN = {1: 5, 2: 10, 3: 15, 4: 20}
LINE_MAX = {1: 10, 2: 10, 3: 20, 4: 20}
HARD_CAP = 20

HARNESS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/\/\*@@MATHGEN_BEGIN\*\/([\s\S]*?)\/\*@@MATHGEN_END\*\//);
if (!m) { console.error('NO_GENERATOR'); process.exit(3); }
const MG = (new Function(m[1] + '; return MG;'))();
let s = 20260101;
const r = () => { s = (s + 0x6D2B79F5) >>> 0; let x = s; x = Math.imul(x ^ (x >>> 15), x | 1); x ^= x + Math.imul(x ^ (x >>> 7), x | 61); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; };
const N = +process.argv[3], out = [];
for (const sk of MG.SKILLS) for (let lv = 1; lv <= 4; lv++) {
  const variants = sk === 'line' ? [undefined, { op: '+' }, { op: '-' }] : [undefined];
  for (const o of variants) for (let i = 0; i < N; i++) out.push(MG.gen(sk, lv, r, o));
}
// out-of-range level requests must clamp, not crash
out.push(MG.gen('add', 0, r), MG.gen('sub', 9, r));
process.stdout.write(JSON.stringify(out));
"""

# Pinned sample used only when node is not installed (checks the checker's logic
# and a fixed slice of real generator output, not the live generator).
PINNED = [
    {"skill": "count", "level": 1, "kind": "howmany", "a": 2, "b": 0, "op": "", "answer": 2, "options": [3, 2, 1]},
    {"skill": "count", "level": 4, "kind": "howmany", "a": 17, "b": 0, "op": "", "answer": 17, "options": [15, 17, 18, 19]},
    {"skill": "add", "level": 1, "kind": "add", "a": 3, "b": 1, "op": "+", "answer": 4, "options": [4, 3, 2]},
    {"skill": "add", "level": 4, "kind": "add", "a": 11, "b": 7, "op": "+", "answer": 18, "options": [18, 17, 19, 15]},
    {"skill": "sub", "level": 2, "kind": "sub", "a": 9, "b": 2, "op": "-", "answer": 7, "options": [7, 8, 4]},
    {"skill": "sub", "level": 4, "kind": "sub", "a": 16, "b": 16, "op": "-", "answer": 0, "options": [0, 1, 2, 3]},
    {"skill": "line", "level": 2, "kind": "hop", "a": 5, "b": 3, "op": "+", "answer": 8, "options": [6, 7, 8]},
    {"skill": "line", "level": 3, "kind": "before", "a": 11, "b": 1, "op": "-", "answer": 10, "options": [9, 10, 12, 13]},
    {"skill": "compare", "level": 1, "kind": "fewer", "a": 5, "b": 2, "op": "", "answer": "right", "options": ["left", "right"]},
    {"skill": "compare", "level": 4, "kind": "symbol", "a": 12, "b": 12, "op": "", "answer": "=", "options": ["<", "=", ">"]},
    {"skill": "compare", "level": 3, "kind": "bigger", "a": 7, "b": 13, "op": "", "answer": 13, "options": [13, 7]},
]


def expected(it):
    """Recompute the right answer from the operands alone."""
    k, a, b = it.get("kind"), it.get("a"), it.get("b")
    if k == "howmany":
        return a
    if k == "add" or (k == "hop" and it.get("op") == "+"):
        return a + b
    if k == "sub" or (k == "hop" and it.get("op") == "-"):
        return a - b
    if k == "after":
        return a + 1
    if k == "before":
        return a - 1
    if k == "bigger":
        return max(a, b)
    if k == "more":
        return "left" if a > b else "right"
    if k == "fewer":
        return "left" if a < b else "right"
    if k == "symbol":
        return "<" if a < b else ">" if a > b else "="
    return None


def check_item(it, errs):
    sk, lv, k = it.get("skill"), it.get("level"), it.get("kind")
    tag = "%s L%s %s %s" % (sk, lv, k, json.dumps({x: it.get(x) for x in ("a", "b", "op", "answer")}))
    if sk not in ("count", "add", "sub", "line", "compare") or lv not in (1, 2, 3, 4):
        errs.append("unknown skill/level: " + tag)
        return
    if k not in ("howmany", "add", "sub", "hop", "after", "before", "bigger", "more", "fewer", "symbol"):
        errs.append("unknown kind: " + tag)
        return
    exp = expected(it)
    if it.get("answer") != exp:
        errs.append("WRONG ANSWER (expected %r): %s" % (exp, tag))
    cap = min(HARD_CAP, LINE_MAX[lv] if sk == "line" else MAXN[lv])
    numeric_vals = [it.get("a"), it.get("b")]
    if k not in ("more", "fewer", "symbol", "bigger"):
        numeric_vals.append(it.get("answer"))
    if k == "bigger":
        numeric_vals.append(it.get("answer"))
    for v in numeric_vals:
        if not isinstance(v, int) or isinstance(v, bool) or v < 0 or v > cap:
            errs.append("OUT OF RANGE 0..%d (%r): %s" % (cap, v, tag))
    if k in ("more", "fewer", "bigger") and it.get("a") == it.get("b"):
        errs.append("EQUAL operands in a which-is-more question: " + tag)
    if k in ("add", "sub") and (it["b"] < 1):
        errs.append("zero/negative second operand: " + tag)
    if k == "sub" and it["b"] > it["a"]:
        errs.append("NEGATIVE result: " + tag)
    # level floor: a level-L question must not exceed the level's own ceiling (checked above)
    opts = it.get("options")
    if not isinstance(opts, list) or len(opts) < 2:
        errs.append("options missing: " + tag)
        return
    if len(set(map(json.dumps, opts))) != len(opts):
        errs.append("DUPLICATE options %r: %s" % (opts, tag))
    if opts.count(it.get("answer")) != 1:
        errs.append("answer appears %d times in options %r: %s" % (opts.count(it.get("answer")), opts, tag))
    for d in opts:
        if d == it.get("answer"):
            continue
        if isinstance(d, int) and (d < 0 or d > cap):
            errs.append("DISTRACTOR out of range 0..%d (%r): %s" % (cap, d, tag))
    if sk in ("count", "add", "sub", "line"):
        want = 3 if lv <= 2 else 4
        if len(opts) != want:
            errs.append("expected %d options at level %d, got %d: %s" % (want, lv, len(opts), tag))
        if any(not isinstance(o, int) for o in opts):
            errs.append("non-numeric option: " + tag)
    if k in ("more", "fewer") and sorted(opts) != ["left", "right"]:
        errs.append("bad options for " + k + ": " + tag)
    if k == "symbol" and sorted(opts) != sorted(["<", "=", ">"]):
        errs.append("bad options for symbol: " + tag)
    if k == "bigger" and sorted(opts) != sorted([it["a"], it["b"]]):
        errs.append("bigger options must be the two numbers: " + tag)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args and APP not in args:
        print("check_basicmathkids_items: skip (checks %s only)" % APP)
        return 0
    if not os.path.isfile(GAME):
        print("BLOCK: %s missing" % GAME)
        return 1
    src = open(GAME, encoding="utf-8").read()
    errs, warns = [], []
    if "/*@@MATHGEN_BEGIN*/" not in src or "/*@@MATHGEN_END*/" not in src:
        print("BLOCK: generator markers /*@@MATHGEN_BEGIN*/ ... /*@@MATHGEN_END*/ not found in game.html")
        return 1
    # the engine must take every question from the checked generator
    engine = src.split("//@@REGION CONTENT_ENGINE", 1)[-1]
    if "MG.gen(" not in engine:
        errs.append("engine never calls MG.gen(): its questions are not covered by this gate")
    if re.search(r"\banswer\s*[:=]\s*[^=;\n]*[+\-*]\s*\w", re.sub(r"/\*@@MATHGEN_BEGIN\*/.*?/\*@@MATHGEN_END\*/", "", engine, flags=re.S)):
        warns.append("engine computes an 'answer' arithmetic expression outside MG.gen -- check it by hand")
    items, mode = None, ""
    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(HARNESS)
            hp = f.name
        try:
            r = subprocess.run([node, hp, GAME, str(N_PER)], capture_output=True, text=True, timeout=300)
        finally:
            os.unlink(hp)
        if r.returncode != 0:
            print("BLOCK: generator did not run under node:\n" + r.stderr[-800:])
            return 1
        items, mode = json.loads(r.stdout), "node"
    else:
        items, mode = PINNED, "pinned sample (node not installed)"
        warns.append("node not found: only the pinned sample was checked, not the live generator")
    seen = {}
    for it in items:
        if len(errs) > 25:
            break
        check_item(it, errs)
        seen.setdefault((it.get("skill"), it.get("level")), []).append(it)
    if mode == "node":
        for (sk, lv), its in sorted(seen.items()):
            cap = LINE_MAX[lv] if sk == "line" else MAXN[lv]
            top = max(max(i["a"], i["b"], i["answer"] if isinstance(i["answer"], int) else 0) for i in its)
            if sk != "compare" or True:
                if top < cap - 1:
                    warns.append("%s level %d never reaches the top of its range (max seen %d of %d)" % (sk, lv, top, cap))
        kinds = {}
        for it in items:
            kinds.setdefault((it["skill"], it["level"]), set()).add(it["kind"])
        for key, ks in sorted(kinds.items()):
            if key[0] == "compare" and len(ks) < 2:
                warns.append("compare level %d has only one question kind" % key[1])
    for w in warns:
        print("WARN: " + w)
    if errs:
        for e in errs[:25]:
            print("BLOCK: " + e)
        print("check_basicmathkids_items: FAIL (%d problem%s)" % (len(errs), "" if len(errs) == 1 else "s"))
        return 1
    print("check_basicmathkids_items: OK -- %d items (%s), answers/ranges/distractors all valid" % (len(items), mode))
    return 0


if __name__ == "__main__":
    sys.exit(main())
