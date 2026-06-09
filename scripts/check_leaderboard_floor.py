#!/usr/bin/env python3
"""Pre-publish gate: synthetic leaderboard 1000-row floor + override hook.

Asserts every shipping game.html's `buildStandings` synthetic weekly
leaderboard uses `var total = Math.max(1000, ...)` AND references
`LEADERBOARD_TOTAL_OVERRIDE` so the native side can lift it via the
`setLeaderboardSize(int)` bridge method.

Blocks if either marker is missing OR if a smaller hardcoded literal
floor (e.g., `var total = 200`) is found.

Memorialized May 2026 after the synthetic leaderboard shipped with
total=200, which read as a thin ladder and didn't justify the
"more players to climb past" copy.
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
    m = re.search(r"function\s+buildStandings\s*\(\s*\)\s*\{([\s\S]*?)\n\s*\}", s)
    if not m:
        warnings.append(f"{app}: buildStandings() not found (game without leaderboard?)")
        return blockers, warnings
    body = m.group(1)
    if "Math.max(1000," not in body:
        blockers.append(f"{app}: buildStandings missing `Math.max(1000, ...)` floor")
    if "LEADERBOARD_TOTAL_OVERRIDE" not in body:
        blockers.append(
            f"{app}: buildStandings missing window.LEADERBOARD_TOTAL_OVERRIDE hook"
        )
    # Catch smaller hardcoded floors that would override the 1000.
    small = re.findall(r"var\s+total\s*=\s*(\d+)\s*;", body)
    for n in small:
        if int(n) < 1000:
            blockers.append(
                f"{app}: buildStandings has hardcoded `var total = {n};` below 1000 floor"
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
        print(f"[leaderboard floor] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
