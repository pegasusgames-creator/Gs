#!/usr/bin/env python3
"""check_budgetplanner_math.py - content gate for BudgetPlanner's envelope engine.

The pure money block of BudgetPlanner's TOOL_CORE (between `// @@BUDGETMATH BEGIN`
and `// @@BUDGETMATH END`) is run under node on a table of edge cases plus a
seeded random sweep of multi-month budgets, and every result is compared with an
independent pure-Python reference built on `decimal.Decimal` / `fractions.Fraction`
(whole currency units with two decimals; the engine works in integer cents).

BLOCKS on any mismatch and - independently of the reference - whenever
  * assigned + left is anything other than the money available to assign
    (= income for the first month; income + the amount freed from earlier months
    afterwards), or the "left to assign" figure is not pool - assigned;
  * the money in the budget (sum of envelope balances + left to assign) is not
    exactly all income minus all spending, to the cent;
  * a rollover rule (carry <-> reset on every envelope) or any number of
    move-money transfers changes that total, or a transfer changes anything
    except the two envelopes it touches;
  * a savings goal's monthly amount is not ceil(remaining / months left), its
    schedule does not add up to the remaining amount exactly, or the months
    differ by more than one cent;
  * a largest-remainder spread leaves a cent unaccounted for;
  * a bill's due day is not clamped to the month length (31 -> 30, 29 Feb in leap years);
  * the amount parser disagrees with the stated rules.

Method the app states and the reference encodes:
  * amounts are integer minor units; "left to assign" = income (+ money freed from
    earlier months) - assigned to envelopes;
  * envelope available = carried-in + planned + moved-in - moved-out - spent;
  * 'carry' envelopes hand their available (even a negative one) to next month,
    'reset' envelopes hand it back to the pool, unassigned money stays in the pool;
  * goal monthly amount = ceil((target - saved) / months left, both months
    inclusive); the schedule spreads the cents largest-remainder, earliest first.

Without node the reference is only checked against a pinned table (WARN - the
JS is not executed).

Usage: python3 scripts/check_budgetplanner_math.py [BudgetPlanner]
Exit 1 on any mismatch.
"""
import calendar
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal, ROUND_CEILING
from fractions import Fraction

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# pre_publish_check passes every app in the run; this gate only applies to
# BudgetPlanner (any other app name is skipped as OK).
_ARGS = [a for a in sys.argv[1:] if not a.startswith("-")]
if _ARGS and "BudgetPlanner" not in _ARGS:
    print("check_budgetplanner_math: skipped (not BudgetPlanner)")
    sys.exit(0)
APP = "BudgetPlanner"
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")
MAX_C = 10 ** 9

# --------------------------------------------------------------------------
# Independent reference (whole units as Decimal, not cents)
# --------------------------------------------------------------------------


def D(c):
    return Decimal(c) / Decimal(100)


def C(d):
    v = d * 100
    assert v == v.to_integral_value(), "fractional cent in reference: %s" % d
    return int(v)


def ref_money(s, exp):
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
    minor = d * (Decimal(10) ** exp)
    return int(minor) if minor <= MAX_C else None


def ref_spread(total, weights):
    n = len(weights)
    w = [max(0, int(x)) for x in weights]
    if sum(w) == 0:
        w = [1] * n
    sign = -1 if total < 0 else 1
    exact = [Fraction(abs(total) * x, sum(w)) for x in w]
    fl = [int(e) for e in exact]
    left = abs(total) - sum(fl)
    order = sorted(range(n), key=lambda i: (-(exact[i] - fl[i]), i))
    for j in range(left):
        fl[order[j]] += 1
    return [sign * x for x in fl]


def ymi(k):
    y, m = k.split("-")
    return int(y) * 12 + int(m) - 1


def ymk(i):
    return "%04d-%02d" % (i // 12, i % 12 + 1)


def ref_compute(model, key):
    envs = [(e["id"], e["roll"]) for e in model["envs"]]
    ids = {i for i, _ in envs}
    months = model["months"]
    tgt = ymi(key)
    first = min([tgt] + [ymi(k) for k in months])
    bal = {i: Decimal(0) for i in ids}        # carried-in per envelope
    freed = Decimal(0)
    out = None
    for i in range(first, tgt + 1):
        m = months.get(ymk(i), {})
        income = sum((D(c) for c in m.get("income", [])), Decimal(0))
        rows = {}
        for eid, roll in envs:
            planned = D(m.get("plan", {}).get(eid, 0))
            spent = sum((D(s["c"]) for s in m.get("spend", []) if s["e"] == eid), Decimal(0))
            mi = sum((D(v["c"]) for v in m.get("moves", []) if v["t"] == eid and v["f"] in ids and v["f"] != eid), Decimal(0))
            mo = sum((D(v["c"]) for v in m.get("moves", []) if v["f"] == eid and v["t"] in ids and v["t"] != eid), Decimal(0))
            rows[eid] = dict(carry=bal[eid], planned=planned, spent=spent, mi=mi, mo=mo,
                             avail=bal[eid] + planned + mi - mo - spent, roll=roll)
        assigned = sum((r["planned"] for r in rows.values()), Decimal(0))
        left = income + freed - assigned
        nb, nf = {}, left
        for eid, r in rows.items():
            if r["roll"] == "carry":
                nb[eid] = r["avail"]
            else:
                nb[eid] = Decimal(0)
                nf += r["avail"]
        out = dict(income=income, freed=freed, assigned=assigned, left=left,
                   spent=sum((r["spent"] for r in rows.values()), Decimal(0)), rows=rows,
                   total=sum((r["avail"] for r in rows.values()), Decimal(0)) + left)
        bal, freed = nb, nf
    return out


def ref_goal(target, saved, cur, due):
    rem = max(0, target - saved)
    months = due - cur + 1
    if rem == 0:
        return dict(remaining=0, monthly=0, schedule=[], months=max(months, 0))
    if months < 1:
        return dict(remaining=rem, monthly=rem, schedule=[rem], months=0)
    monthly = int((Decimal(rem) / Decimal(months)).to_integral_value(rounding=ROUND_CEILING))
    return dict(remaining=rem, monthly=monthly, schedule=ref_spread(rem, [1] * months), months=months)


# --------------------------------------------------------------------------
# Case generation
# --------------------------------------------------------------------------


def rand_model(rng):
    n_env = rng.randint(1, 8)
    envs = [dict(id="e%d" % i, roll=rng.choice(["carry", "reset"])) for i in range(n_env)]
    start = rng.randint(2024 * 12, 2028 * 12 + 11)
    n_m = rng.randint(1, 5)
    months = {}
    idxs = sorted(rng.sample(range(start, start + n_m + 3), n_m))
    big = rng.random() < 0.15
    for ix in idxs:
        top = 10 ** 9 // 20 if big else rng.choice([5000, 250000, 4000000])
        m = dict(income=[rng.randint(0, top) for _ in range(rng.randint(0, 3))],
                 plan={}, spend=[], moves=[])
        for e in envs:
            if rng.random() < 0.8:
                m["plan"][e["id"]] = rng.randint(0, top // 2 + 1)
        for _ in range(rng.randint(0, 10)):
            m["spend"].append(dict(e=rng.choice(envs)["id"], c=rng.randint(1, max(2, top // 4))))
        if n_env > 1:
            for _ in range(rng.randint(0, 4)):
                f, t = rng.sample([e["id"] for e in envs], 2)
                m["moves"].append(dict(f=f, t=t, c=rng.randint(1, max(2, top // 5))))
        months[ymk(ix)] = m
    key = ymk(idxs[-1] + rng.choice([0, 0, 1, 2, 13]))
    return dict(envs=envs, months=months), key


def rand_ops(seed, count):
    rng = random.Random(seed)
    ops = []
    for _ in range(count):
        model, key = rand_model(rng)
        ops.append(dict(op="compute", model=model, key=key))
    for _ in range(count // 2):
        n = rng.randint(1, 12)
        ops.append(dict(op="spread", total=rng.choice([0, rng.randint(-10 ** 9, 10 ** 9), rng.randint(0, 200)]),
                        weights=[rng.choice([0, 1, 1, 2, 3, 7, 99]) for _ in range(n)]))
    for _ in range(count):
        cur = rng.randint(2024 * 12, 2030 * 12)
        ops.append(dict(op="goal", target=rng.choice([0, rng.randint(1, 10 ** 9), rng.randint(1, 5000)]),
                        saved=rng.choice([0, rng.randint(0, 10 ** 9), rng.randint(0, 5000)]),
                        cur=cur, due=cur + rng.randint(-3, 120)))
    for _ in range(300):
        ops.append(dict(op="due", y=rng.randint(1999, 2104), m0=rng.randint(0, 11), day=rng.randint(1, 31)))
    pool = ["12", "12.5", "12,5", "1,234.56", "1.234,56", "1.234", "1,234", "0.01", "", ".", "abc", "12.345", "1.2.3", "9,999,999.99",
            "10000000", "10000000.01", "٣", " 4 5 ", "0", "00.50", "12.", ",5"]
    for s in pool:
        for ex in (0, 2, 3):
            ops.append(dict(op="money", s=s, exp=ex))
    return ops


def edge_ops():
    e = []
    one = dict(envs=[dict(id="a", roll="carry")], months={})
    e.append(dict(op="compute", model=one, key="2026-01"))
    # over-assigned, overspent, reset vs carry, year boundary
    m = dict(envs=[dict(id="a", roll="carry"), dict(id="b", roll="reset")], months={
        "2026-12": dict(income=[100000], plan=dict(a=70000, b=50000), spend=[dict(e="a", c=80000)], moves=[dict(f="b", t="a", c=10000)]),
        "2027-01": dict(income=[100000], plan=dict(a=1), spend=[], moves=[])})
    e += [dict(op="compute", model=m, key="2026-12"), dict(op="compute", model=m, key="2027-01"), dict(op="compute", model=m, key="2027-06")]
    e.append(dict(op="goal", target=10000, saved=0, cur=2026 * 12 + 10, due=2026 * 12 + 12))
    e.append(dict(op="goal", target=1, saved=0, cur=5, due=5))
    e.append(dict(op="goal", target=1000, saved=1000, cur=5, due=5))
    e.append(dict(op="goal", target=1000, saved=1, cur=5, due=4))
    e += [dict(op="due", y=2024, m0=1, day=31), dict(op="due", y=2100, m0=1, day=29), dict(op="due", y=2000, m0=1, day=29),
          dict(op="due", y=2026, m0=3, day=31), dict(op="due", y=2026, m0=0, day=31)]
    e.append(dict(op="spread", total=100, weights=[1, 1, 1]))
    e.append(dict(op="spread", total=1, weights=[0, 0, 0]))
    e.append(dict(op="spread", total=-7, weights=[1, 2]))
    return e


# --------------------------------------------------------------------------
# Node driver
# --------------------------------------------------------------------------
NODE_DRIVER = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const a = html.indexOf('// @@BUDGETMATH BEGIN'), b = html.indexOf('// @@BUDGETMATH END');
if (a < 0 || b < a) { console.log(JSON.stringify({ error: 'no BUDGETMATH block' })); process.exit(0); }
const BE = (new Function(html.slice(a, b) + '\nreturn BE;'))();
const ops = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const res = ops.map(o => {
  try {
    if (o.op === 'compute') return BE.compute(o.model, o.key);
    if (o.op === 'spread') return BE.spread(o.total, o.weights);
    if (o.op === 'goal') return BE.goalNeed(o.target, o.saved, o.cur, o.due);
    if (o.op === 'due') return BE.dueDay(o.y, o.m0, o.day);
    if (o.op === 'money') return BE.parseMoney(o.s, o.exp);
    if (o.op === 'raw') return BE.compute(o.model, o.key);
  } catch (e) { return { error: String(e) }; }
});
console.log(JSON.stringify({ results: res }));
"""


def run_node(node, ops):
    tmp = tempfile.mkdtemp(prefix="budgetplanner_")
    try:
        cj, dj = os.path.join(tmp, "cases.json"), os.path.join(tmp, "driver.js")
        json.dump(ops, open(cj, "w"))
        open(dj, "w").write(NODE_DRIVER)
        p = subprocess.run([node, dj, GAME, cj], capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            return None, "node failed:\n" + p.stderr[-1500:]
        out = json.loads(p.stdout)
        if "error" in out:
            return None, out["error"]
        return out["results"], None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def strip_moves(model):
    return dict(envs=model["envs"], months={k: dict(v, moves=[]) for k, v in model["months"].items()})


def flip_rolls(model):
    return dict(envs=[dict(e, roll="reset" if e["roll"] == "carry" else "carry") for e in model["envs"]], months=model["months"])


def check_compute(case, got, extra, blockers, label):
    model, key = case["model"], case["key"]
    if isinstance(got, dict) and "error" in got:
        blockers.append("%s: engine threw %s" % (label, got["error"]))
        return
    ref = ref_compute(model, key)
    # 1. against the reference
    pairs = [("income", got["income"], C(ref["income"])), ("assigned", got["assigned"], C(ref["assigned"])),
             ("left", got["left"], C(ref["left"])), ("freed", got["freed"], C(ref["freed"])),
             ("spent", got["spent"], C(ref["spent"])), ("total", got["total"], C(ref["total"]))]
    for name, g, r in pairs:
        if g != r:
            blockers.append("%s: %s = %s, reference %s (%s)" % (label, name, g, r, key))
    byid = {r["id"]: r for r in got["rows"]}
    for eid, r in ref["rows"].items():
        g = byid.get(eid)
        if not g or g["avail"] != C(r["avail"]) or g["carry"] != C(r["carry"]):
            blockers.append("%s: envelope %s available/carry %s vs reference %s/%s" % (label, eid, g and g["avail"], C(r["avail"]), C(r["carry"])))
    # 2. invariants, independent of the reference
    if got["assigned"] + got["left"] != got["income"] + got["freed"]:
        blockers.append("%s: assigned %d + left %d != income %d + freed %d" % (label, got["assigned"], got["left"], got["income"], got["freed"]))
    first = min([ymi(key)] + [ymi(k) for k in model["months"]])
    if ymi(key) == first and got["assigned"] + got["left"] != got["income"]:
        blockers.append("%s: first month assigned + left != income" % label)
    cum_in = sum(sum(m.get("income", [])) for k, m in model["months"].items() if ymi(k) <= ymi(key))
    cum_sp = sum(sum(s["c"] for s in m.get("spend", [])) for k, m in model["months"].items() if ymi(k) <= ymi(key))
    if got["total"] != cum_in - cum_sp:
        blockers.append("%s: money in the budget %d != income %d - spending %d" % (label, got["total"], cum_in, cum_sp))
    if sum(r["avail"] for r in got["rows"]) + got["left"] != got["total"]:
        blockers.append("%s: envelope balances + left != total" % label)
    for r in got["rows"]:
        if r["carry"] + r["planned"] + r["moveIn"] - r["moveOut"] - r["spent"] != r["avail"]:
            blockers.append("%s: envelope %s row does not add up" % (label, r["id"]))
    # 3. extras: no-moves and flipped-rollover runs must keep the total
    nomv, flip = extra
    if nomv["total"] != got["total"] or flip["total"] != got["total"]:
        blockers.append("%s: move-money/rollover changed the total (%d vs %d no-moves vs %d flipped)" % (label, got["total"], nomv["total"], flip["total"]))
    if sum(r["moveIn"] for r in got["rows"]) != sum(r["moveOut"] for r in got["rows"]):
        blockers.append("%s: moves in != moves out" % label)


def main():
    blockers, warns = [], []
    if not os.path.isfile(GAME):
        print("BLOCKER: %s missing" % GAME)
        return 1
    html = open(GAME, encoding="utf8").read()
    if "// @@BUDGETMATH BEGIN" not in html or "// @@BUDGETMATH END" not in html:
        print("BLOCKER: no `// @@BUDGETMATH BEGIN/END` block in %s" % GAME)
        return 1

    # 1. The reference against hand-checked values.
    pm = dict(envs=[dict(id="a", roll="carry"), dict(id="b", roll="reset")], months={
        "2026-10": dict(income=[100000], plan=dict(a=50000, b=30000), spend=[dict(e="a", c=60000)], moves=[]),
        "2026-11": dict(income=[100000], plan=dict(a=50000), spend=[], moves=[])})
    r = ref_compute(pm, "2026-11")
    if (C(r["left"]), C(r["freed"]), C(r["total"])) != (100000, 50000, 140000) or C(r["rows"]["a"]["avail"]) != 40000:
        blockers.append("reference disagrees with the pinned two-month case: %s" % {k: str(v) for k, v in r.items() if k != "rows"})
    if ref_goal(10000, 0, 0, 2)["schedule"] != [3334, 3333, 3333] or ref_goal(10000, 0, 0, 2)["monthly"] != 3334:
        blockers.append("reference disagrees with the pinned goal case")
    if ref_spread(100, [1, 1, 1]) != [34, 33, 33] or ref_money("1,234.56", 2) != 123456 or ref_money("1.234", 2) != 123400:
        blockers.append("reference disagrees with the pinned spread/parse cases")

    node = shutil.which("node")
    if not node:
        warns.append("node not found - the JS engine was not executed; only the pinned table vs the Python reference was checked")
        return report(blockers, warns, 0)

    base_ops = edge_ops() + rand_ops(20261104, 1500)
    # follow-up compute runs for the invariants: same model without moves, and with every rollover flipped
    follow = []
    for o in base_ops:
        if o["op"] == "compute":
            follow.append(dict(op="compute", model=strip_moves(o["model"]), key=o["key"]))
            follow.append(dict(op="compute", model=flip_rolls(o["model"]), key=o["key"]))
    res, err = run_node(node, base_ops + follow)
    if err:
        print("BLOCKER: " + err)
        return 1
    if len(res) != len(base_ops) + len(follow):
        print("BLOCKER: node returned %d results for %d cases" % (len(res), len(base_ops) + len(follow)))
        return 1
    got_main, got_follow = res[:len(base_ops)], res[len(base_ops):]
    fi = 0
    n_edge = len(edge_ops())
    for i, (o, g) in enumerate(zip(base_ops, got_main)):
        label = ("edge[%d]" % i) if i < n_edge else ("random[%d]" % (i - n_edge))
        if o["op"] == "compute":
            extra = (got_follow[fi], got_follow[fi + 1])
            fi += 2
            if isinstance(g, dict) and "error" not in g and not any(isinstance(x, dict) and "error" in x for x in extra):
                check_compute(o, g, extra, blockers, label)
            else:
                blockers.append("%s: engine threw %s" % (label, g))
        elif o["op"] == "spread":
            ref = ref_spread(o["total"], o["weights"])
            if g != ref:
                blockers.append("%s: spread(%s, %s) = %s, reference %s" % (label, o["total"], o["weights"], g, ref))
            if sum(g) != o["total"]:
                blockers.append("%s: spread leaves %d cent(s) unaccounted for" % (label, o["total"] - sum(g)))
        elif o["op"] == "goal":
            ref = ref_goal(o["target"], o["saved"], o["cur"], o["due"])
            if g["monthly"] != ref["monthly"] or g["schedule"] != ref["schedule"] or g["remaining"] != ref["remaining"] or g["months"] != ref["months"]:
                blockers.append("%s: goal %s -> monthly %s schedule %s, reference monthly %s schedule %s" %
                                (label, {k: o[k] for k in ("target", "saved", "cur", "due")}, g["monthly"], g["schedule"][:3], ref["monthly"], ref["schedule"][:3]))
            if sum(g["schedule"]) != ref["remaining"]:
                blockers.append("%s: goal schedule is %d cent(s) off the remaining amount" % (label, ref["remaining"] - sum(g["schedule"])))
            if g["schedule"] and (max(g["schedule"]) - min(g["schedule"]) > 1 or g["monthly"] != max(g["schedule"])):
                blockers.append("%s: goal schedule is uneven or monthly is not the largest month" % label)
            if not g["overdue"] and not g["done"] and g["monthly"] * g["months"] < g["remaining"]:
                blockers.append("%s: monthly amount x months falls short of the goal" % label)
        elif o["op"] == "due":
            ref = min(o["day"], calendar.monthrange(o["y"], o["m0"] + 1)[1])
            if g != ref:
                blockers.append("%s: dueDay(%d,%d,%d) = %s, reference %d" % (label, o["y"], o["m0"], o["day"], g, ref))
        elif o["op"] == "money":
            ref = ref_money(o["s"], o["exp"])
            if g != ref:
                blockers.append("%s: parseMoney(%r,%d) = %s, reference %s" % (label, o["s"], o["exp"], g, ref))
        if len(blockers) > 12:
            break
    return report(blockers, warns, len(base_ops))


def report(blockers, warns, ncases):
    for w in warns:
        print("WARN: " + w)
    if blockers:
        for b in blockers[:12]:
            print("BLOCKER: " + b)
        print("check_budgetplanner_math: FAIL (%d problem(s))" % len(blockers))
        return 1
    print("check_budgetplanner_math: OK (%d engine cases vs the Decimal/Fraction reference; assigned + left = income, money conserved through rollover and moves, goal schedules exact to the cent)" % ncases)
    return 0


if __name__ == "__main__":
    sys.exit(main())
