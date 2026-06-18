#!/usr/bin/env python3
"""Pre-publish gate: every game with discrete levels ships >=500 on release.

CLAUDE.md "Level count floor". A `const CAMPAIGN`/`LEVELS` array literal in
game.html under 500 entries BLOCKS for any app not yet live; already-live
apps released under the old bar are grandfathered to a WARN (expand on the
next content update — never regress a live level set in a rush).

Non-leveled games (no CAMPAIGN/LEVELS array — e.g. 2048 score-chase,
FlappyBird) have nothing to count and are skipped.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
THRESHOLD = 500

# Live apps released under the old bar — grandfathered to WARN.
GRANDFATHERED = {"WaterSortPuzzle", "Nonogram", "Puzzle2048", "UnblockPuzzle"}


def _array_len(html: str, name: str):
    """Count top-level elements of `const <name> = [ ... ];`. None if absent."""
    m = re.search(r"(?:const|var|let)\s+" + name + r"\s*=\s*\[", html)
    if not m:
        return None
    i = m.end() - 1            # at '['
    depth = 0
    commas = 0
    nonempty = False           # any non-space char between the outer [ ]
    n = len(html)
    while i < n:
        c = html[i]
        if c in "[{(":
            depth += 1
        elif c in ")}]":
            depth -= 1
            if depth == 0:
                break
        elif depth == 1 and c == ",":
            commas += 1
        if depth >= 1 and not c.isspace() and c != "[":
            nonempty = True
        i += 1
    if not nonempty:
        return 0
    return commas + 1


def _level_count(html: str):
    best = None
    for name in ("CAMPAIGN", "LEVELS"):
        c = _array_len(html, name)
        if c is not None:
            best = c if best is None else max(best, c)
    return best


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blockers, warnings
    count = _level_count(game.read_text(encoding="utf-8"))
    if count is None:
        return blockers, warnings          # not a campaign-style level game
    if count >= THRESHOLD:
        return blockers, warnings
    msg = (f"{app}: campaign has {count} levels — the release bar is "
           f"{THRESHOLD} (CLAUDE.md 'Level count floor'). Expand via the "
           f"game's own seed generator + acceptance test.")
    if app in GRANDFATHERED:
        warnings.append(msg + " [grandfathered live app — expand on next "
                        "content update]")
    else:
        blockers.append(msg)
    return blockers, warnings


def main():
    apps = sys.argv[1:]
    if not apps or apps == ["--all"]:
        apps = sorted(
            p.name for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith(("_", "."))
            and (p / "android/app/src/main/assets/game.html").exists())
    fail = 0
    for app in apps:
        b, w = check_app(app)
        for line in b:
            print(f"✗ {line}")
            fail = 1
        for line in w:
            print(f"!  {line}")
    if not fail:
        print(f"[min levels] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
