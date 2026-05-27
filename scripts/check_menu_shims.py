#!/usr/bin/env python3
"""check_menu_shims.py — pre-publish gate against the 2026-05-27
"competing runtime shims" regression. Blocks if game.html contains:

  - More than ONE menu-targeting setInterval injector
    (e.g. injectMenuChips / injectButton / injectFreeCoins called from
    setInterval). The consolidated MENU shim renders ONCE on
    showScreen('menuScreen'); polling injectors fight each other.
  - position:absolute inside a top-bar context. Causes the floating
    leaderboard pill to land on top of the settings gear.
  - More than ONE leaderboard/tournament entry point (the user gets
    confused; in the canonical layout it's a single 🏆 Ranks icon
    opening a 2-tab sheet).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Polling injectors that target the menu's structure. The behavioral half
# of shim D (maybeRestoreStreak) and shim G (submitScore) do NOT touch
# the menu DOM, so they're allowed — we only count the ones in this list.
FORBIDDEN_POLLERS = [
    "injectMenuChips",   # shim D used to do this
    "injectButton",      # shim G's PGS pill / medal injector
    "injectFreeCoins",   # legacy menu inject path
    "injectFreeCoinsBtn",
    "injectThemeStrip",  # theme strip relocates, not polls
    "injectPassPromo",   # pass promo lives in shop/no-lives only
    "updateTournamentBanner",  # replaced by Ranks sheet
]

# Anything that opens a leaderboard or tournament UI.
RANK_OPENERS = [
    r'data-growth-leaderboard-btn',
    r'data-menu-icon="ranks"',
    r'data-menu-icon="tournament"',
]


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app: str):
    blocking, warnings = [], []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")

    # 1. menu-targeting polling injectors
    pollers_found = []
    for name in FORBIDDEN_POLLERS:
        if re.search(r"setInterval\s*\(\s*" + re.escape(name) + r"\b", src):
            pollers_found.append(name)
    if len(pollers_found) > 0:
        blocking.append(
            f"{app}: menu-targeting setInterval injector(s) present: {pollers_found} — "
            "consolidate into the MENU shim's renderMenu() called from showScreen"
        )

    # 2. data-growth-leaderboard-btn (the rogue absolute pill — should not exist)
    if 'data-growth-leaderboard-btn' in src:
        blocking.append(
            f"{app}: rogue floating leaderboard button (data-growth-leaderboard-btn) present — "
            "PGS leaderboard belongs in the MENU shim's Ranks sheet"
        )

    # 3. exactly one ranks entry point.
    rank_hits = 0
    for pat in RANK_OPENERS:
        rank_hits += len(re.findall(pat, src))
    # The MENU shim defines exactly one [data-menu-icon="ranks"] in script
    # text — accept counts 1-2 (script + maybe a runtime-rendered duplicate
    # marker). Block on 3+.
    if rank_hits > 2:
        blocking.append(
            f"{app}: multiple leaderboard/tournament UI entry points (count={rank_hits}) — "
            "expected exactly one 🏆 Ranks icon"
        )

    # 4. position:absolute inside a [data-menu-icons] block — the top-bar
    # container must stay in-flow. Approximate: flag if the top-bar
    # container's inline cssText contains position:absolute.
    if re.search(r"data-menu-icons[^>]*\bposition\s*:\s*absolute", src):
        blocking.append(
            f"{app}: top-bar container [data-menu-icons] is position:absolute — must be in-flow flex"
        )

    return blocking, warnings


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    apps = args.apps or (["WaterSortPuzzle","Nonogram","Puzzle2048","UnblockPuzzle"] if not args.all else
                         sorted(p.name for p in REPO.iterdir()
                                if (p / "android" / "app" / "build.gradle").exists()))
    any_block = False
    for app in apps:
        if not _is_app(app): print(f"  ? {app}: skipped"); continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: menu shim hygiene OK")
        if b: any_block = True
    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
