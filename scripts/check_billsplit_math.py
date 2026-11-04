#!/usr/bin/env python3
"""check_billsplit_math.py - content gate for BillSplit's split engine.

The pure money block of BillSplit's TOOL_CORE (between `// @@SPLITMATH BEGIN`
and `// @@SPLITMATH END`) is run under node on a table of edge cases plus a
seeded random sweep, and every result is compared with an independent
pure-Python reference built on `decimal.Decimal` / `fractions.Fraction`.
BLOCKS on any mismatch, and - independently of the reference - whenever the
per-person totals do not add up EXACTLY to the bill total (to the minor unit),
or a component (items / tax / tip) column does not add up to its own total.

Method the app states and the reference encodes:
  * amounts are integer minor units (cents); shares are integer weights;
  * an item is divided by weight; each person's exact item subtotal is a
    rational number; tax and tip are rounded half-up to a whole cent from a
    percentage (or entered as an amount), then split either in proportion to
    each person's item subtotal or evenly between everybody;
  * LARGEST-REMAINDER rounding is applied to each column (items, tax, tip):
    every person gets floor(exact), the leftover cents go one each to the
    largest fractional remainders, ties to the person listed first;
  * a person's total = items + tax + tip, so every column and the grand total
    add up exactly.
It also checks the amount / percent text parsers.

Without node the reference is only checked against a pinned table (WARN - the
JS is not executed).

Usage: python3 scripts/check_billsplit_math.py [BillSplit]
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
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from fractions import Fraction

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# pre_publish_check passes every app in the run; this gate only applies to
# BillSplit (any other app name is skipped as OK).
_ARGS = [a for a in sys.argv[1:] if not a.startswith("-")]
if _ARGS and "BillSplit" not in _ARGS:
    print("check_billsplit_math: skipped (not BillSplit)")
    sys.exit(0)
APP = "BillSplit"
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")

MAX_C = 10 ** 9
MAX_W = 99

# --------------------------------------------------------------------------
# Independent reference
# --------------------------------------------------------------------------


def ref_money(s, exp):
    """Spec: digits and . , only; last separator is the decimal point when
    1..exp digits follow it, a thousands mark when exactly 3 follow (and a
    head exists); trailing separator ignored; anything else invalid."""
    s = re.sub(r"\s", "", s or "")
    if not s or re.fullmatch(r"[0-9.,]+", s) is None or re.search(r"[0-9]", s) is None:
        return None
    ks = [i for i, ch in enumerate(s) if ch in ".,"]
    if not ks:
        d = Decimal(s)
    else:
        k = ks[-1]
        tail, head = s[k + 1:], re.sub(r"[.,]", "", s[:k])
        if 1 <= len(tail) <= exp:
            d = Decimal((head or "0") + "." + tail)
        elif len(tail) == 3 and head:
            d = Decimal(head + tail)
        elif len(tail) == 0:
            d = Decimal(head or "0")
        else:
            return None
    v = d * (Decimal(10) ** exp)
    if v != v.to_integral_value():
        return None
    v = int(v)
    return v if v <= MAX_C else None


def ref_pct(s):
    """Percent text -> Decimal percent (0..100, up to 3 decimals) or None."""
    s = re.sub(r"\s", "", s or "").replace(",", ".", 1)
    if re.fullmatch(r"(\d{1,3}(\.\d{0,3})?|\.\d{1,3})", s) is None:
        return None
    d = Decimal(s)
    return d if d <= 100 else None


def lr(total, exact):
    """Largest remainder over Fractions whose sum is exactly `total`."""
    assert sum(exact) == total, (total, exact)
    fl = [math.floor(x) for x in exact]
    left = total - sum(fl)
    order = sorted(range(len(exact)), key=lambda i: (-(exact[i] - fl[i]), i))
    for j in range(left):
        fl[order[j]] += 1
    return fl


def pct_cents(base, pct):
    return int((Decimal(base) * pct / Decimal(100)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def ref_split(n, items, tax, tip):
    """items: [(cents, [weights])]; tax/tip: dict(total=None|cents-or-Decimal-pct,
    kind 'pct'|'amt', dist, base). Returns dict like the JS result."""
    act, unassigned = [], 0
    for c, w in items:
        w = [max(0, min(MAX_W, x)) for x in (list(w) + [0] * n)[:n]]
        if sum(w) == 0:
            unassigned += 1
        elif c > 0:
            act.append((c, w))
    sub = sum(c for c, _ in act)
    exact_items = [sum((Fraction(c * w[p], sum(w)) for c, w in act), Fraction(0)) for p in range(n)]
    items_out = lr(sub, exact_items)

    def comp(spec, basev):
        total = pct_cents(basev, spec["val"]) if spec["kind"] == "pct" else spec["val"]
        if spec["dist"] == "even" or sub == 0:
            ex = [Fraction(total, n)] * n
        else:
            ex = [Fraction(total) * x / sub for x in exact_items]
        return total, lr(total, ex)

    tx_total, tx = comp(tax, sub)
    tp_total, tp = comp(tip, sub + tx_total if tip.get("base") == "post" else sub)
    persons = [{"items": items_out[i], "tax": tx[i], "tip": tp[i], "total": items_out[i] + tx[i] + tp[i]} for i in range(n)]
    return {"subtotal": sub, "tax": tx_total, "tip": tp_total, "total": sub + tx_total + tp_total,
            "unassigned": unassigned, "persons": persons}


# --------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------
def fmt_money(c, exp, rnd):
    """Render minor units as the text a user could type (varied styles)."""
    if exp == 0:
        return str(c)
    s = "%d.%0*d" % (c // 10 ** exp, exp, c % 10 ** exp)
    style = rnd.random()
    if style < 0.2:
        s = s.replace(".", ",")
    elif style < 0.3 and c >= 10 ** (exp + 3):
        ip, fp = s.split(".")
        s = "{:,}".format(int(ip)) + "." + fp          # 1,234.56
    elif style < 0.4 and c >= 10 ** (exp + 3):
        ip, fp = s.split(".")
        s = "{:,}".format(int(ip)).replace(",", ".") + "," + fp   # 1.234,56
    return s


def mk(n, items, exp=2, tax=("amt", "0", "prop"), tip=("amt", "0", "prop", "pre")):
    return {"n": n, "exp": exp, "items": [{"p": p, "w": w} for p, w in items],
            "tax": {"kind": tax[0], "val": tax[1], "dist": tax[2]},
            "tip": {"kind": tip[0], "val": tip[1], "dist": tip[2], "base": tip[3]}}


EDGE = [
    mk(3, [("0.01", [1, 1, 1])]),
    mk(2, [("0.01", [1, 1])]),
    mk(3, [("100.00", [1, 1, 1])]),
    mk(3, [("10.00", [1, 1, 1])], tax=("pct", "8.875", "prop"), tip=("pct", "18", "even", "post")),
    mk(1, [("12.34", [1])], tax=("pct", "20", "prop"), tip=("pct", "15", "prop", "pre")),
    mk(2, [], tax=("amt", "3.50", "prop"), tip=("amt", "2.00", "even", "pre")),
    mk(2, [("5.00", [0, 0])], tax=("amt", "1.00", "prop")),
    mk(4, [("0.00", [1, 1, 1, 1]), ("7.77", [1, 2, 3, 0])]),
    mk(3, [("10.00", [2, 1, 0]), ("5.55", [0, 1, 1]), ("9.99", [1, 1, 1])], tax=("pct", "7.5", "prop"), tip=("pct", "20", "prop", "post")),
    mk(3, [("10.00", [2, 1, 0])], tax=("amt", "50.00", "prop"), tip=("pct", "100", "even", "post")),
    mk(5, [("0.05", [1, 1, 1, 1, 1]), ("0.07", [1, 0, 1, 0, 1])], tax=("pct", "0.001", "even"), tip=("pct", "0.001", "prop", "pre")),
    mk(3, [("1.00", [99, 98, 1])], tax=("pct", "99.999", "prop"), tip=("pct", "100", "prop", "post")),
    mk(20, [("%d.%02d" % (i + 1, (i * 7) % 100), [1 if (i + j) % 3 else 0 for j in range(20)]) for i in range(40)],
       tax=("pct", "8.875", "prop"), tip=("pct", "17.5", "prop", "post")),
    mk(2, [("10000000.00", [1, 1]), ("10000000.00", [1, 2]), ("9999999.99", [3, 1])], tax=("pct", "100", "prop"), tip=("amt", "10000000.00", "even", "pre")),
    mk(3, [("1000", [1, 1, 1]), ("333", [1, 1, 0])], exp=0, tax=("pct", "10", "prop"), tip=("amt", "100", "even", "pre")),
    mk(3, [("1.001", [1, 1, 1]), ("2.5", [1, 0, 1])], exp=3, tax=("pct", "5", "prop"), tip=("pct", "12.5", "even", "post")),
    mk(2, [("1,234.56", [1, 1]), ("1.234,56", [2, 1]), ("12,5", [1, 0])], tax=("pct", "8,25", "prop")),
    mk(2, [("1,5", [1, 1])], exp=0),
    mk(2, [("abc", [1, 1])]),
    mk(2, [("1.2.3", [1, 1])]),
    mk(2, [("12.345", [1, 1])]),
    mk(2, [("", [1, 1])]),
    mk(2, [("10000000.01", [1, 1])]),
    mk(2, [("10", [1, 1])], tax=("pct", "100.001", "prop")),
    mk(2, [("10", [1, 1])], tax=("pct", "12.3456", "prop")),
    mk(2, [("10", [1, 1])], tip=("pct", ".5", "prop", "pre")),
    mk(2, [("10", [1, 1])], tip=("pct", "", "prop", "pre")),
]


def build_random(seed, count):
    rnd = random.Random(seed)
    out = []
    for _ in range(count):
        exp = rnd.choice([2, 2, 2, 2, 0, 3])
        n = rnd.choice([1, 2, 2, 3, 3, 4, 5, 6, 8, 12, 20])
        k = rnd.choice([0, 1, 1, 2, 3, 5, 8, 15, 40])
        items = []
        for _i in range(k):
            mag = rnd.choice([1, 10, 100, 1000, 10 ** 5, 10 ** 7, MAX_C])
            c = rnd.randint(0 if rnd.random() < 0.05 else 1, mag)
            r = rnd.random()
            if r < 0.4:
                w = [1 if rnd.random() < 0.6 else 0 for _j in range(n)]
            elif r < 0.7:
                w = [rnd.randint(0, 4) for _j in range(n)]
            elif r < 0.8:
                w = [rnd.randint(0, 99) for _j in range(n)]
            elif r < 0.9:
                w = [1] * n
            else:
                w = [0] * n
            items.append((fmt_money(c, exp, rnd), w))

        def spec(is_tip):
            kind = rnd.choice(["pct", "pct", "amt", "amt", "none"])
            dist = rnd.choice(["prop", "even"])
            if kind == "none":
                kind, val = "amt", "0"
            elif kind == "pct":
                val = rnd.choice(["0", "5", "7.25", "8.875", "10", "12.5", "15", "18", "20", "22.5", "0.001", "99.999", "100",
                                  "%d.%03d" % (rnd.randint(0, 40), rnd.randint(0, 999))])
            else:
                val = fmt_money(rnd.randint(0, rnd.choice([100, 10 ** 4, 10 ** 6, MAX_C])), exp, rnd)
            return (kind, val, dist, rnd.choice(["pre", "post"])) if is_tip else (kind, val, dist)
        out.append(mk(n, items, exp=exp, tax=spec(False), tip=spec(True)))
    return out


def reference(case):
    """Reference result for a case, or None when any text is invalid (the app
    must reject it, never compute with it)."""
    exp = case["exp"]
    items = []
    for it in case["items"]:
        c = ref_money(it["p"], exp)
        if c is None:
            return None
        items.append((c, it["w"]))
    specs = {}
    for key in ("tax", "tip"):
        s = case[key]
        if s["kind"] == "pct":
            v = ref_pct(s["val"])
        else:
            v = ref_money(s["val"], exp)
        if v is None:
            return None
        specs[key] = {"kind": s["kind"], "val": v, "dist": s["dist"], "base": s.get("base", "pre")}
    return ref_split(case["n"], items, specs["tax"], specs["tip"])


NODE_DRIVER = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const a = html.indexOf('// @@SPLITMATH BEGIN'), b = html.indexOf('// @@SPLITMATH END');
if (a < 0 || b < a) { console.log(JSON.stringify({error: 'SPLITMATH block not found'})); process.exit(0); }
let SM;
try { SM = new Function(html.slice(a, b) + '\nreturn SM;')(); } catch (e) { console.log(JSON.stringify({error: 'block failed to load: ' + e.message})); process.exit(0); }
const cases = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = cases.map(c => {
  try {
    const items = [];
    for (const it of c.items) { const v = SM.parseMoney(it.p, c.exp); if (v === null) return null; items.push({c: v, w: it.w}); }
    const spec = s => {
      if (s.kind === 'pct') { const mp = SM.parsePct(s.val); return mp === null ? null : {mode: 'pct', mp: mp, dist: s.dist, base: s.base}; }
      const v = SM.parseMoney(s.val, c.exp); return v === null ? null : {mode: 'amt', c: v, dist: s.dist, base: s.base};
    };
    const tax = spec(c.tax), tip = spec(c.tip);
    if (!tax || !tip) return null;
    return SM.split({n: c.n, items: items, tax: tax, tip: tip});
  } catch (e) { return {error: String(e && e.message || e)}; }
});
console.log(JSON.stringify({results: out}));
"""


def compare(case, ref, got, label, blockers):
    if ref is None:
        if got is not None:
            blockers.append("%s: invalid input accepted by the app: %s" % (label, json.dumps(case)[:200]))
        return
    if got is None:
        blockers.append("%s: valid input rejected by the app: %s" % (label, json.dumps(case)[:200]))
        return
    if "error" in got:
        blockers.append("%s: engine threw: %s" % (label, got["error"]))
        return
    # Invariants that must hold on the APP's own numbers, whatever the reference says.
    ps = got["persons"]
    if sum(p["total"] for p in ps) != got["total"]:
        blockers.append("%s: per-person totals %d != bill total %d" % (label, sum(p["total"] for p in ps), got["total"]))
    for col, tot in (("items", "subtotal"), ("tax", "tax"), ("tip", "tip")):
        if sum(p[col] for p in ps) != got[tot]:
            blockers.append("%s: %s column sums to %d, expected %d" % (label, col, sum(p[col] for p in ps), got[tot]))
    if got["total"] != got["subtotal"] + got["tax"] + got["tip"]:
        blockers.append("%s: total != subtotal + tax + tip" % label)
    if any(min(p["items"], p["tax"], p["tip"]) < 0 for p in ps):
        blockers.append("%s: negative share" % label)
    if got != ref:
        diff = [k for k in ref if ref[k] != got.get(k)]
        blockers.append("%s: mismatch in %s\n      case: %s\n      app : %s\n      ref : %s" % (
            label, ",".join(diff), json.dumps(case)[:240], json.dumps(got)[:240], json.dumps(ref)[:240]))


# Hand-checked values (guard the reference itself).
PINNED = [
    # 3 people, $10.00 even -> 3.34 / 3.33 / 3.33 (leftover cent to the first of the tied remainders)
    (mk(3, [("10.00", [1, 1, 1])]), [334, 333, 333], 1000),
    # $0.01 between 2 -> the first person
    (mk(2, [("0.01", [1, 1])]), [1, 0], 1),
    # 2:1 shares of $10.00 -> 6.67 / 3.33
    (mk(2, [("10.00", [2, 1])]), [667, 333], 1000),
    # $10.00 even + 10 % tax (1.00) + $1.00 tip even = 12.00 -> 4.00 each
    (mk(3, [("10.00", [1, 1, 1])], tax=("pct", "10", "prop"), tip=("amt", "1.00", "even", "pre")), [401, 400, 399], 1200),
]


def main():
    blockers, warns = [], []
    if not os.path.isfile(GAME):
        print("BLOCKER: %s missing" % GAME)
        return 1
    html = open(GAME, encoding="utf8").read()
    if "// @@SPLITMATH BEGIN" not in html or "// @@SPLITMATH END" not in html:
        print("BLOCKER: no `// @@SPLITMATH BEGIN/END` block in %s" % GAME)
        return 1

    # 1. The reference against hand-checked values.
    for case, persons, total in PINNED:
        r = reference(case)
        if r is None or [p["total"] for p in r["persons"]] != persons or r["total"] != total:
            blockers.append("reference disagrees with pinned case %s -> %s" % (json.dumps(case)[:120], r and [p["total"] for p in r["persons"]]))

    node = shutil.which("node")
    if not node:
        warns.append("node not found - the JS engine was not executed; only the pinned table vs the Python reference was checked")
        return report(blockers, warns, 0)

    cases = EDGE + build_random(20261104, 4000)
    tmp = tempfile.mkdtemp(prefix="billsplit_")
    try:
        cj, dj = os.path.join(tmp, "cases.json"), os.path.join(tmp, "driver.js")
        json.dump(cases, open(cj, "w"))
        open(dj, "w").write(NODE_DRIVER)
        p = subprocess.run([node, dj, GAME, cj], capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            print("BLOCKER: node failed:\n" + p.stderr[-1500:])
            return 1
        out = json.loads(p.stdout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if "error" in out:
        print("BLOCKER: " + out["error"])
        return 1
    res = out["results"]
    if len(res) != len(cases):
        print("BLOCKER: node returned %d results for %d cases" % (len(res), len(cases)))
        return 1

    # 2. Pinned cases through the app.
    pinned_run(node, blockers)

    nvalid = 0
    for i, case in enumerate(cases):
        ref = reference(case)
        if ref is not None:
            nvalid += 1
        compare(case, ref, res[i], "edge[%d]" % i if i < len(EDGE) else "random[%d]" % (i - len(EDGE)), blockers)
        if len(blockers) > 12:
            break
    if nvalid < len(cases) * 0.8:
        blockers.append("too few valid cases generated (%d of %d) - the sweep is not testing the engine" % (nvalid, len(cases)))
    return report(blockers, warns, len(cases))


def pinned_run(node, blockers):
    tmp = tempfile.mkdtemp(prefix="billsplit_pin_")
    try:
        cj, dj = os.path.join(tmp, "cases.json"), os.path.join(tmp, "driver.js")
        json.dump([c for c, _, _ in PINNED], open(cj, "w"))
        open(dj, "w").write(NODE_DRIVER)
        p = subprocess.run([node, dj, GAME, cj], capture_output=True, text=True, timeout=60)
        out = json.loads(p.stdout)
        for (case, persons, total), got in zip(PINNED, out.get("results", [])):
            if not got or [x["total"] for x in got["persons"]] != persons or got["total"] != total:
                blockers.append("app disagrees with pinned case %s -> %s" % (json.dumps(case)[:120], got and [x["total"] for x in got["persons"]]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def report(blockers, warns, ncases):
    for w in warns:
        print("WARN: " + w)
    if blockers:
        for b in blockers[:12]:
            print("BLOCKER: " + b)
        print("check_billsplit_math: FAIL (%d problem(s))" % len(blockers))
        return 1
    print("check_billsplit_math: OK (%d engine cases vs the Decimal/Fraction reference; every per-person total adds up to the bill exactly)" % ncases)
    return 0


if __name__ == "__main__":
    sys.exit(main())
