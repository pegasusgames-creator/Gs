#!/usr/bin/env python3
"""check_agecalculator_dates.py - content gate for AgeCalculator's date maths.

The pure calendar block of AgeCalculator's TOOL_CORE (between
`// @@AGEMATH BEGIN` and `// @@AGEMATH END`) is run under node on a fixed table
of tricky cases (leap days, month-end borrows, century rules, year
boundaries, invalid input) plus a seeded random sweep, and every result is
compared with an independent pure-Python reference built on `datetime` /
`calendar`. BLOCKS on any mismatch.

Rules the reference encodes (and the app documents):
  * age = whole months added to the birth date with the day clamped to the
    month end (Jan 31 + 1 month = Feb 28/29), then the leftover days;
  * a Feb 29 birthday is celebrated on Feb 28 in common years;
  * day / second milestones count from the start of the birth date;
  * Chinese zodiac changes at that year's Chinese New Year (pinned 1990-2026
    here; the app's 1900-2100 table is also cross-checked against node's ICU).

Without node the pinned table is only checked against the Python reference
(WARN - the JS is not executed).

Usage: python3 scripts/check_agecalculator_dates.py [AgeCalculator]
Exit 1 on any mismatch.
"""
import calendar
import datetime as dt
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = sys.argv[1] if len(sys.argv) > 1 else "AgeCalculator"
GAME = os.path.join(BASE, APP, "android/app/src/main/assets/game.html")

# --------------------------------------------------------------------------
# Independent reference
# --------------------------------------------------------------------------
D = dt.date


def add_months(d, n):
    tot = d.year * 12 + d.month - 1 + n
    y, m = divmod(tot, 12)
    m += 1
    return D(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def ref_diff(a, b):
    lo, hi = 0, (b.year - a.year) * 12 + (b.month - a.month) + 1
    while lo < hi:                       # largest tm with add_months(a, tm) <= b
        mid = (lo + hi + 1) // 2
        try:
            fits = add_months(a, mid) <= b
        except ValueError:      # year > 9999 is past b by definition
            fits = False
        if fits:
            lo = mid
        else:
            hi = mid - 1
    anchor = add_months(a, lo)
    return {"years": lo // 12, "months": lo % 12, "days": (b - anchor).days,
            "totalMonths": lo, "totalDays": (b - a).days}


def ref_weekdays(a, b):
    n = (b - a).days
    if n <= 0:
        return 0
    c = 0
    for i in range(n):
        if (a.toordinal() + i) % 7 not in (0, 6):    # ordinal%7: 0=Sun, 6=Sat
            c += 1
    return c


def occurrence(b, y):
    if b.month == 2 and b.day == 29 and not calendar.isleap(y):
        return D(y, 2, 28)
    return D(y, b.month, b.day)


def ref_next_birthday(b, ref):
    if b > ref:
        return None
    o = occurrence(b, ref.year)
    if o < ref:
        o = occurrence(b, ref.year + 1)
    return {"date": o.isoformat(), "days": (o - ref).days, "turning": o.year - b.year, "today": o == ref}


def ref_half(b, ref):
    k = 1
    while True:
        o = add_months(b, 6 * k)
        if o >= ref:
            return {"date": o.isoformat(), "days": (o - ref).days, "age": k / 2}
        k += 2


def ref_milestones(b):
    out = []
    for n in (1000, 5000, 10000, 15000, 20000, 25000, 30000):
        out.append(("d%d" % n, (b + dt.timedelta(days=n))))
    out.append(("w1000", b + dt.timedelta(days=7000)))
    for s in (10 ** 9, 15 * 10 ** 8, 2 * 10 ** 9, 25 * 10 ** 8, 3 * 10 ** 9):
        out.append(("s%d" % s, b + dt.timedelta(days=s // 86400)))
    out.sort(key=lambda x: (x[1], x[0]))
    return [{"id": i, "date": d.isoformat()} for i, d in out]


def ref_custom(b, n, unit):
    if not isinstance(n, int) or n < 1 or n > 99999:
        return None
    try:
        if unit == "d":
            d = b + dt.timedelta(days=n)
        elif unit == "w":
            d = b + dt.timedelta(days=7 * n)
        elif unit == "m":
            d = add_months(b, n)
        elif unit == "y":
            d = add_months(b, 12 * n)
        else:
            return None
    except (ValueError, OverflowError):
        return None
    return d.isoformat()


SIGNS = [  # (index, (m,d) start, (m,d) end) in the app's order Aries..Pisces
    (0, (3, 21), (4, 19)), (1, (4, 20), (5, 20)), (2, (5, 21), (6, 20)), (3, (6, 21), (7, 22)),
    (4, (7, 23), (8, 22)), (5, (8, 23), (9, 22)), (6, (9, 23), (10, 22)), (7, (10, 23), (11, 21)),
    (8, (11, 22), (12, 21)), (9, (12, 22), (1, 19)), (10, (1, 20), (2, 18)), (11, (2, 19), (3, 20)),
]


def ref_west(d):
    md = (d.month, d.day)
    for i, s, e in SIGNS:
        if s <= e:
            if s <= md <= e:
                return i
        elif md >= s or md <= e:         # Capricorn wraps the year end
            return i
    raise AssertionError(md)


# Chinese New Year (month, day) 1990-2026, pinned independently of the app.
CNY = {
    1990: (1, 27), 1991: (2, 15), 1992: (2, 4), 1993: (1, 23), 1994: (2, 10), 1995: (1, 31),
    1996: (2, 19), 1997: (2, 7), 1998: (1, 28), 1999: (2, 16), 2000: (2, 5), 2001: (1, 24),
    2002: (2, 12), 2003: (2, 1), 2004: (1, 22), 2005: (2, 9), 2006: (1, 29), 2007: (2, 18),
    2008: (2, 7), 2009: (1, 26), 2010: (2, 14), 2011: (2, 3), 2012: (1, 23), 2013: (2, 10),
    2014: (1, 31), 2015: (2, 19), 2016: (2, 8), 2017: (1, 28), 2018: (2, 16), 2019: (2, 5),
    2020: (1, 25), 2021: (2, 12), 2022: (2, 1), 2023: (1, 22), 2024: (2, 10), 2025: (1, 29),
    2026: (2, 17),
}


def ref_animal(d):
    if d.year not in CNY:
        return None
    cy = d.year if (d.month, d.day) >= CNY[d.year] else d.year - 1
    return (cy - 4) % 12            # 0 Rat, 1 Ox, 2 Tiger, 3 Rabbit, 4 Dragon ...


# --------------------------------------------------------------------------
# Pinned, hand-verified expectations (also the fallback without node)
# --------------------------------------------------------------------------
PINNED_DIFF = [  # a, b, years, months, days, totalDays
    ("2000-01-31", "2000-03-01", 0, 1, 1, 30),     # leap Feb: Jan 31 + 1 month = Feb 29
    ("2023-01-31", "2023-03-01", 0, 1, 1, 29),     # common Feb: -> Feb 28
    ("2000-02-29", "2001-02-28", 1, 0, 0, 365),    # Feb 29 anniversary falls on Feb 28
    ("2024-02-29", "2025-03-01", 1, 0, 1, 366),
    ("2000-01-01", "2026-11-03", 26, 10, 2, 9803),
    ("1970-01-01", "2000-01-01", 30, 0, 0, 10957),
    ("2020-12-31", "2021-01-01", 0, 0, 1, 1),
    ("2021-03-15", "2021-03-15", 0, 0, 0, 0),
    ("1999-12-31", "2000-02-29", 0, 2, 0, 60),     # month-end clamps: Dec 31 + 2 months = Feb 29
    ("1900-02-28", "1900-03-01", 0, 0, 1, 1),      # 1900 is not a leap year
    ("2000-02-28", "2000-03-01", 0, 0, 2, 2),      # 2000 is
]

FIXED_PAIRS = [
    ("2000-02-29", "2026-11-03"), ("2000-02-29", "2027-02-27"), ("2000-02-29", "2027-02-28"),
    ("2000-02-29", "2028-02-28"), ("2000-02-29", "2028-02-29"), ("2000-02-29", "2028-03-01"),
    ("1996-02-29", "2100-02-28"), ("1996-02-29", "2100-03-01"),
    ("1988-01-31", "1988-02-29"), ("1988-01-31", "1988-03-01"), ("1987-01-31", "1987-03-01"),
    ("2001-03-31", "2001-04-30"), ("2001-03-31", "2001-05-01"), ("2001-05-31", "2001-06-30"),
    ("2001-10-31", "2001-11-30"), ("2001-12-31", "2002-02-28"), ("2001-12-31", "2002-03-01"),
    ("2023-12-31", "2024-02-29"), ("2023-12-31", "2024-03-01"), ("2024-01-30", "2024-02-29"),
    ("1900-01-01", "2026-11-03"), ("1583-01-01", "9999-12-31"), ("1700-02-28", "1700-03-01"),
    ("1800-02-28", "1800-03-01"), ("2100-02-28", "2100-03-01"), ("1600-02-29", "2000-02-29"),
    ("2026-11-03", "2026-11-03"), ("2026-11-02", "2026-11-03"), ("2025-11-03", "2026-11-03"),
    ("2025-11-04", "2026-11-03"), ("2025-11-30", "2026-11-03"), ("2026-10-31", "2026-11-30"),
    ("1999-12-31", "2000-01-01"), ("2020-02-29", "2024-02-29"), ("2020-02-29", "2023-03-01"),
    ("2015-08-31", "2016-02-29"), ("2015-08-31", "2016-03-01"), ("2012-12-31", "2013-02-28"),
]

FIXED_REFS = ["2026-11-03", "2026-02-28", "2024-02-29", "2025-02-28", "2025-03-01", "2000-12-31",
              "2026-01-01", "2026-12-31", "2028-02-28", "2028-02-29", "1999-12-31"]
FIXED_BIRTHS = ["2000-02-29", "1996-02-29", "1990-01-01", "1990-12-31", "1985-08-31", "1999-03-31",
                "2004-02-28", "1900-02-28", "1950-06-15", "2026-11-03", "2026-11-02", "1583-01-01"]

INVALID = ["", "abc", "2023-02-29", "2023-13-01", "2023-00-10", "2023-04-31", "2023-1-1", "23-01-01",
           "2023/01/01", "1582-12-31", "0000-01-01", "10000-01-01", "2023-01-32", "2100-02-29",
           "1900-02-29", " 2023-01-01", "2023-01-01 ", "2023-01-01T00:00"]
VALID_EDGE = ["2024-02-29", "2000-02-29", "1600-02-29", "1583-01-01", "9999-12-31", "2023-12-31"]
CUSTOM_CASES = [(1, "d"), (99999, "d"), (1, "w"), (52, "w"), (1, "m"), (6, "m"), (18, "m"), (1, "y"),
                (100, "y"), (0, "d"), (100000, "d"), (-1, "d"), (1.5, "d"), (3, "x")]


def pd(s):
    y, m, d = map(int, s.split("-"))
    return D(y, m, d)


def build_cases():
    rnd = random.Random(20261103)
    pairs = list(FIXED_PAIRS)
    while len(pairs) < len(FIXED_PAIRS) + 1500:
        y = rnd.randint(1583, 2200)
        m = rnd.randint(1, 12)
        dmax = calendar.monthrange(y, m)[1]
        a = D(y, m, rnd.choice([1, dmax, dmax - 1, rnd.randint(1, dmax)]))
        b = a + dt.timedelta(days=rnd.choice([rnd.randint(0, 40), rnd.randint(0, 800), rnd.randint(0, 40000)]))
        if b.year <= 9999:
            pairs.append((a.isoformat(), b.isoformat()))
    births = list(FIXED_BIRTHS)
    for _ in range(200):
        y = rnd.randint(1900, 2026)
        m = rnd.randint(1, 12)
        dmax = calendar.monthrange(y, m)[1]
        births.append(D(y, m, rnd.choice([1, dmax, rnd.randint(1, dmax)])).isoformat())
    refs = list(FIXED_REFS)
    for _ in range(40):
        refs.append((D(2020, 1, 1) + dt.timedelta(days=rnd.randint(0, 3000))).isoformat())
    zodiac = []
    d = D(1990, 1, 1)
    while d <= D(2026, 12, 31):                            # every day 1990-2026
        zodiac.append(d.isoformat())
        d += dt.timedelta(days=1)
    return pairs, births, refs, zodiac


NODE_DRIVER = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const m = src.match(/\/\/ @@AGEMATH BEGIN[^\n]*\n([\s\S]*?)\/\/ @@AGEMATH END/);
if (!m) { console.log(JSON.stringify({ error: 'AGEMATH block not found' })); process.exit(0); }
const AM = new Function(m[1] + '; return AM;')();
const C = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const iso = o => o ? AM.iso(o) : null;
const P = s => AM.parse(s);
const out = { diff: [], wd: [], nb: [], half: [], ms: [], custom: [], parse: [], zod: [], cnyIntl: [], misc: {} };
for (const [a, b] of C.pairs) {
  const A = P(a), B = P(b), r = AM.diff(A, B);
  out.diff.push([r.years, r.months, r.days, r.totalMonths, r.totalDays, AM.dow(A), (AM.addDays(A, 12345).y <= 9999 ? iso(AM.addDays(A, 12345)) : null), (AM.addMonths(A, 13).y <= 9999 ? iso(AM.addMonths(A, 13)) : null)]);
  out.wd.push(AM.weekdaysBetween(A, B));
}
for (const b of C.births) for (const rf of C.refs) {
  const B = P(b), R = P(rf), n = AM.nextBirthday(B, R), h = AM.cmp(B, R) <= 0 ? AM.nextHalf(B, R) : null;
  out.nb.push(n ? { date: iso(n.date), days: n.days, turning: n.turning, today: n.today } : null);
  out.half.push(h ? { date: iso(h.date), days: h.days, age: h.age } : null);
}
for (const b of C.births) out.ms.push(AM.milestones(P(b)).map(x => ({ id: x.id, date: iso(x.date) })));
for (const b of C.customBirths) for (const [n, u] of C.custom) out.custom.push(iso(AM.custom(P(b), n, u)));
for (const s of C.invalid.concat(C.validEdge)) out.parse.push(AM.parse(s) ? AM.iso(AM.parse(s)) : null);
for (const s of C.zodiac) { const o = P(s); out.zod.push([AM.westIdx(o), AM.animalIdx(o)]); }
try {
  const f = new Intl.DateTimeFormat('en-u-ca-chinese', { year: 'numeric', month: 'numeric', day: 'numeric' });
  for (let y = 1900; y <= 2100; y++) {
    for (const [mm, d0, d1] of [[0, 15, 31], [1, 1, 28]]) {
      let hit = null;
      for (let d = d0; d <= d1 && !hit; d++) {
        const p = {}; f.formatToParts(new Date(Date.UTC(y, mm, d, 12))).forEach(x => p[x.type] = x.value);
        if (p.month === '1' && p.day === '1' && +p.relatedYear === y) hit = [mm + 1, d];
      }
      if (hit) { out.cnyIntl.push([y, hit[0], hit[1]]); break; }
    }
  }
} catch (e) { out.misc.noIntl = String(e); }
out.misc.edge = [
  AM.animalIdx(AM.D(1900, 1, 1)), AM.animalIdx(AM.D(2100, 12, 31)), AM.animalIdx(AM.D(1899, 12, 31)), AM.animalIdx(AM.D(2101, 1, 1)),
  AM.nextBirthday(AM.D(2030, 1, 1), AM.D(2026, 1, 1)),
];
out.misc.tableCny = [];
for (let y = 1900; y <= 2100; y++) { const o = AM.fromDays(AM.toDays(AM.D(y, 1, 1))); out.misc.tableCny.push(AM.chineseYear(AM.D(y, 12, 31))); }
console.log(JSON.stringify(out));
"""


def extract_block():
    src = open(GAME, encoding="utf-8").read()
    m = re.search(r"// @@AGEMATH BEGIN[^\n]*\n(.*?)// @@AGEMATH END", src, re.S)
    return m is not None


def main():
    blockers, warns = [], []
    if not os.path.isfile(GAME):
        print("BLOCKER: %s missing" % GAME)
        return 1
    if not extract_block():
        print("BLOCKER: no `// @@AGEMATH BEGIN/END` block in %s" % GAME)
        return 1

    # 1. The reference must agree with the hand-pinned table (guards the reference itself).
    for a, b, y, mo, d, tot in PINNED_DIFF:
        r = ref_diff(pd(a), pd(b))
        if (r["years"], r["months"], r["days"], r["totalDays"]) != (y, mo, d, tot):
            blockers.append("reference disagrees with pinned %s -> %s: %r" % (a, b, r))
    assert ref_animal(D(2000, 2, 4)) == 3 and ref_animal(D(2000, 2, 5)) == 4   # Rabbit -> Dragon
    assert ref_west(D(2000, 1, 19)) == 9 and ref_west(D(2000, 1, 20)) == 10

    node = shutil.which("node")
    if not node:
        warns.append("node not found - JS not executed; only the pinned table vs the Python reference was checked")
        return report(blockers, warns, 0)

    pairs, births, refs, zodiac = build_cases()
    cases = {"pairs": pairs, "births": births, "refs": refs, "zodiac": zodiac, "custom": CUSTOM_CASES,
             "customBirths": ["2000-02-29", "1985-08-31", "9990-06-15", "2026-11-03"],
             "invalid": INVALID, "validEdge": VALID_EDGE}
    tmp = tempfile.mkdtemp(prefix="agecheck_")
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

    bad = []

    def chk(label, got, want):
        if got != want and len(bad) < 25:
            bad.append("%s: js=%r ref=%r" % (label, got, want))
        elif got != want:
            bad.append(None)

    # 2. diff / totals / weekday / add maths
    for (a, b), g, wd in zip(pairs, out["diff"], out["wd"]):
        A, B = pd(a), pd(b)
        r = ref_diff(A, B)
        try:
            plus = (A + dt.timedelta(days=12345)).isoformat()
        except OverflowError:
            plus = None
        try:
            am13 = add_months(A, 13).isoformat()
        except ValueError:
            am13 = None
        want = [r["years"], r["months"], r["days"], r["totalMonths"], r["totalDays"],
                A.toordinal() % 7, plus, am13]
        chk("diff %s -> %s" % (a, b), g, want)
        n = (B - A).days
        if n <= 60000:                                      # brute force reference for the sane range
            chk("weekdays %s -> %s" % (a, b), wd, ref_weekdays(A, B))
    # 3. next birthday + half birthday
    i = 0
    for b in births:
        for rf in refs:
            B, R = pd(b), pd(rf)
            nb = ref_next_birthday(B, R)
            want = None if nb is None else {"date": nb["date"], "days": nb["days"], "turning": nb["turning"], "today": nb["today"]}
            chk("nextBirthday %s @ %s" % (b, rf), out["nb"][i], want)
            hw = ref_half(B, R) if B <= R else None
            chk("halfBirthday %s @ %s" % (b, rf), out["half"][i], hw)
            i += 1
    # 4. milestones, custom
    for b, g in zip(births, out["ms"]):
        chk("milestones " + b, g, [m for m in ref_milestones(pd(b)) if int(m["date"][:4]) <= 9999])
    i = 0
    for b in cases["customBirths"]:
        for n, u in CUSTOM_CASES:
            w = ref_custom(pd(b), n, u)
            if w is not None and int(w[:4]) > 9999:
                w = None
            chk("custom %s +%s%s" % (b, n, u), out["custom"][i], w)
            i += 1
    # 5. invalid / valid input
    for s, g in zip(INVALID + VALID_EDGE, out["parse"]):
        want = None
        if re.fullmatch(r"\d{4}-\d\d-\d\d", s):
            try:
                d = pd(s)
                if 1583 <= d.year <= 9999:
                    want = d.isoformat()
            except ValueError:
                want = None
        chk("parse %r" % s, g, want)
    # 6. zodiac, every day 1990-2026
    for s, (w, a) in zip(zodiac, out["zod"]):
        d = pd(s)
        chk("western " + s, w, ref_west(d))
        chk("chinese " + s, a, ref_animal(d))
    # 7. app's CNY table vs node ICU (1900-2100) and the animal edges
    if out["cnyIntl"]:
        for y, mo, dd in out["cnyIntl"]:
            cy = out["misc"]["tableCny"][y - 1900]
            if cy != y:      # 31 Dec of year y is always after that year's New Year
                chk("table year %d" % y, cy, y)
        src = open(GAME, encoding="utf-8").read()
        m = re.search(r"const CNY1900 = \[([0-9,]+)\]", src)
        tbl = [int(x) for x in m.group(1).split(",")] if m else []
        want = [mo * 100 + dd for _, mo, dd in out["cnyIntl"]]
        chk("CNY table vs ICU", tbl, want)
    else:
        warns.append("node has no Intl chinese calendar - CNY table not cross-checked against ICU")
    e = out["misc"]["edge"]
    chk("edge animal 1900-01-01 (before CNY -> out of table)", e[0], None)
    chk("edge animal 2100-12-31", e[1] is not None, True)
    chk("edge animal 1899/2101", [e[2], e[3]], [None, None])
    chk("future birth has no next birthday", e[4], None)

    bad_n = len(bad)
    shown = [b for b in bad if b]
    for b in shown:
        blockers.append(b)
    if bad_n > len(shown):
        blockers.append("... and %d more mismatches" % (bad_n - len(shown)))
    total = len(pairs) + len(births) * len(refs) * 2 + len(zodiac) * 2 + len(INVALID) + len(VALID_EDGE)
    return report(blockers, warns, total)


def report(blockers, warns, total):
    for w in warns:
        print("WARN: " + w)
    if blockers:
        for b in blockers:
            print("BLOCKER: " + b)
        print("check_agecalculator_dates: FAIL (%d)" % len(blockers))
        return 1
    print("check_agecalculator_dates: OK (%d JS-vs-reference comparisons, %d pinned cases)" % (total, len(PINNED_DIFF)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
