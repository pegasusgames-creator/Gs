#!/usr/bin/env python3
"""check_menu_consistency.py — soft-warn when the four shipping apps
diverge on menu structure (top-bar icons, Tier-3 row content).

The MENU shim renders identical [data-menu-icons] across all four —
this script verifies each app's game.html actually carries the
canonical icon set after re-injection, and warns if not.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Canonical top-bar icon set (2026-05-28 round-15): the top bar carries
# Free Coins only; Ranks moved DOWN into the Tier-3 icon row alongside
# Levels · Shop · Games · Settings, and is declared via the
# [data-menu-tier3-ranks] attribute by the MENU shim's
# injectRanksIntoTier3 helper. Settings has never been a top-bar icon.
CANONICAL_TOP_BAR_ICONS = ['freecoins']
TIER3_RANKS_ATTR = 'data-menu-tier3-ranks'


def _is_app(app):
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app):
    blocking, warnings = [], []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")
    # Top-bar icons live under [data-menu-icons] and carry data-menu-icon="<name>".
    found_top = []
    for icon in CANONICAL_TOP_BAR_ICONS:
        pat = r'data-menu-icon="' + icon + r'"'
        if re.search(pat, src):
            found_top.append(icon)
    missing_top = [i for i in CANONICAL_TOP_BAR_ICONS if i not in found_top]
    if missing_top:
        warnings.append(
            f"{app}: top-bar missing icon(s): {missing_top} — MENU shim should declare all of {CANONICAL_TOP_BAR_ICONS}"
        )
    # Tier-3 Ranks tile (Round-15+) — must be injected by the MENU shim.
    if TIER3_RANKS_ATTR not in src:
        warnings.append(
            f"{app}: Tier-3 row missing Ranks tile ([{TIER3_RANKS_ATTR}]) — MENU shim's injectRanksIntoTier3 should run"
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
    for app in apps:
        if not _is_app(app): continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: menu consistency OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
