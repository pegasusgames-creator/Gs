#!/usr/bin/env python3
"""Pre-publish gate: .game-footer adaptive override + +Npx buffer.

Asserts every shipping game.html has, INSIDE the "adaptive sizing via
clamp()" CSS block, a `.game-footer { ... }` rule whose padding
expression includes `env(safe-area-inset-bottom` AND a literal `+ Npx`
buffer (N >= 4) for AdMob anchor banner visual overflow.

Memorialized from May 2026: WaterSort 2.1.15 + Puzzle2048 1.2.15
shipped without the override; buttons were clipped by the banner.
The CSS comment promised "footer reserves room for the banner" but
the actual selector was missing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    f = REPO / app / "android/app/src/main/assets/game.html"
    if not f.exists():
        warnings.append(f"{app}: game.html missing")
        return blockers, warnings
    s = f.read_text(encoding="utf-8")
    # Locate the adaptive-sizing block (round-N).
    m = re.search(r"/\*\s*=+\s*[\d-]+\s*round-\d+:\s*adaptive sizing via clamp\(\)[\s\S]*?</style>", s)
    if not m:
        blockers.append(f"{app}: adaptive-sizing CSS block not found")
        return blockers, warnings
    block = m.group(0)
    # Find a .game-footer rule inside the block.
    fm = re.search(r"\.game-footer\s*\{[^}]*\}", block)
    if not fm:
        blockers.append(
            f"{app}: .game-footer adaptive override missing inside the round-N block"
        )
        return blockers, warnings
    rule = fm.group(0)
    if "env(safe-area-inset-bottom" not in rule:
        blockers.append(
            f"{app}: .game-footer override missing env(safe-area-inset-bottom)"
        )
    # Look for "+ Npx" buffer with N >= 4 inside the padding expression.
    buf = re.search(r"\+\s*(\d+)\s*px\b", rule)
    if not buf or int(buf.group(1)) < 4:
        blockers.append(
            f"{app}: .game-footer override missing +Npx buffer (N>=4) for adaptive AdMob banner overflow"
        )
    return blockers, warnings


def main():
    apps = sys.argv[1:] or [
        "WaterSortPuzzle",
        "Nonogram",
        "Puzzle2048",
        "UnblockPuzzle",
    ]
    if apps == ["--all"]:
        apps = sorted(
            p.name
            for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
            and (p / "android/app/src/main/assets/game.html").exists()
        )
    fail = 0
    for app in apps:
        b, w = check_app(app)
        for line in b:
            print(f"BLOCKER: {line}")
            fail = 1
        for line in w:
            print(f"WARN:    {line}")
    if not fail:
        print(f"[footer clearance] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
