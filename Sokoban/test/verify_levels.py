#!/usr/bin/env python3
"""verify_levels.py — offline acceptance test for Sokoban's shipped content.

Reads game.html (never trusts the build caches) and BLOCKS (exit 1) unless:
  * LEVELS has >= 500 distinct maps, each with exactly one keeper, at least
    one crate, crates == docks, and a closed room (no floor on the edge);
  * SOLUTIONS[i] (run-length LURD) replays legally on LEVELS[i] — every
    lower-case step walks onto free floor, every upper-case step pushes a
    crate onto free floor — and ends with every crate docked;
  * the same holds for every DAILY tier board and its DAILY_SOL line;
  * no daily board duplicates a campaign level;
  * the solver block embedded in game.html (SOKO-SOLVER-BEGIN/END, used by
    the in-game hint fallback) is byte-identical to test/solver_core.js, the
    solver that produced the stored lines.
Par shown in game = len(solution), so a valid replay is also a valid par.

    python3 Sokoban/test/verify_levels.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAME = HERE.parent / "android/app/src/main/assets/game.html"
D = {"u": (0, -1), "d": (0, 1), "l": (-1, 0), "r": (1, 0)}


def unrle(s):
    return re.sub(r"(\d+)([udlrUDLR])", lambda m: m.group(2) * int(m.group(1)), s)


def parse(m):
    walls, goals, boxes, player = set(), set(), set(), []
    rows = m.split("\n")
    for y, line in enumerate(rows):
        for x, ch in enumerate(line):
            c = (x, y)
            if ch == "#": walls.add(c)
            elif ch == "$": boxes.add(c)
            elif ch == "*": boxes.add(c); goals.add(c)
            elif ch == ".": goals.add(c)
            elif ch == "@": player.append(c)
            elif ch == "+": player.append(c); goals.add(c)
            elif ch != " ": raise ValueError(f"bad char {ch!r}")
    return walls, goals, boxes, player, rows


def closed(walls, player, rows):
    """Flood from the keeper through non-walls; must never leave the map."""
    h = len(rows)
    seen, st = {player}, [player]
    while st:
        x, y = st.pop()
        for dx, dy in D.values():
            n = (x + dx, y + dy)
            if n in walls or n in seen:
                continue
            if not (0 <= n[1] < h and 0 <= n[0] < len(rows[n[1]])):
                return False
            seen.add(n); st.append(n)
    return True


def replay(m, sol):
    walls, goals, boxes, player, rows = parse(m)
    if len(player) != 1:
        return f"{len(player)} keepers"
    if not boxes:
        return "no crates"
    if len(boxes) != len(goals):
        return f"{len(boxes)} crates vs {len(goals)} docks"
    if not closed(walls, player[0], rows):
        return "room is open to the edge"
    p = player[0]
    boxes = set(boxes)
    for k, ch in enumerate(unrle(sol)):
        dx, dy = D[ch.lower()]
        n = (p[0] + dx, p[1] + dy)
        if n in walls:
            return f"step {k} '{ch}' walks into a wall"
        if ch.islower():
            if n in boxes:
                return f"step {k} '{ch}' walks into a crate (should be a push)"
        else:
            if n not in boxes:
                return f"step {k} '{ch}' pushes nothing"
            b2 = (n[0] + dx, n[1] + dy)
            if b2 in walls or b2 in boxes:
                return f"step {k} '{ch}' push is blocked"
            boxes.discard(n); boxes.add(b2)
        p = n
    if boxes != goals:
        return "line ends with crates off their docks"
    return None


def arr(html, name, maps=True):
    m = re.search(r"const " + name + r"\s*=\s*\[(.*?)\n\];", html, re.S)
    if not m:
        return None
    return re.findall(r"`([^`]*)`" if maps else r"'([^']*)'", m.group(1))


def main():
    html = GAME.read_text(encoding="utf-8")
    errs = []
    levels, sols = arr(html, "LEVELS"), arr(html, "SOLUTIONS", maps=False)
    if not levels or not sols:
        sys.exit("✗ LEVELS / SOLUTIONS arrays not found in game.html")
    if len(levels) < 500:
        errs.append(f"only {len(levels)} levels (< 500)")
    if len(set(levels)) != len(levels):
        errs.append("duplicate maps in LEVELS")
    if len(sols) != len(levels):
        errs.append(f"{len(sols)} solutions for {len(levels)} levels")
    for i, (m, s) in enumerate(zip(levels, sols)):
        e = replay(m, s)
        if e:
            errs.append(f"level {i + 1}: {e}")
    dm = re.search(r"const DAILY\s*=\s*\[(.*?)\n\];", html, re.S)
    ds = re.search(r"const DAILY_SOL\s*=\s*\[(.*?)\n\];", html, re.S)
    if not dm or not ds:
        errs.append("DAILY / DAILY_SOL arrays not found")
    else:
        tiers = [re.findall(r"`([^`]*)`", t) for t in re.findall(r"\[(.*?)\n\]", dm.group(1), re.S)]
        tsol = [re.findall(r"'([^']*)'", t) for t in re.findall(r"\[(.*?)\]", ds.group(1), re.S)]
        if len(tiers) != 3 or len(tsol) != 3:
            errs.append(f"expected 3 daily tiers, got {len(tiers)}/{len(tsol)}")
        for t, (tm, tl) in enumerate(zip(tiers, tsol)):
            if len(tm) != len(tl) or len(tm) < 30:
                errs.append(f"daily tier {t}: {len(tm)} boards / {len(tl)} lines")
            for i, (m, s) in enumerate(zip(tm, tl)):
                e = replay(m, s)
                if e:
                    errs.append(f"daily tier {t} board {i}: {e}")
            if set(tm) & set(levels):
                errs.append(f"daily tier {t} repeats a campaign level")
    core = (HERE / "solver_core.js").read_text(encoding="utf-8")
    blk = re.search(r"/\*SOKO-SOLVER-BEGIN\*/.*?/\*SOKO-SOLVER-END\*/", core, re.S).group(0)
    if blk not in html:
        errs.append("game.html solver block drifted from test/solver_core.js")
    for e in errs[:40]:
        print("✗ " + e)
    if errs:
        print(f"✗ {len(errs)} problem(s)")
        sys.exit(1)
    print(f"✓ Sokoban: {len(levels)} levels + {sum(len(t) for t in tiers)} daily boards "
          f"replay to solved; solver block in sync")


if __name__ == "__main__":
    main()
