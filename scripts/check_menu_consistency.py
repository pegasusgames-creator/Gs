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
CANONICAL_ICONS = ['freecoins', 'ranks', 'settings']


def _is_app(app):
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app):
    blocking, warnings = [], []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")
    # Find each top-bar icon by its data-menu-icon attribute.
    found = []
    for icon in CANONICAL_ICONS:
        pat = r'data-menu-icon="' + icon + r'"'
        if re.search(pat, src):
            found.append(icon)
    missing = [i for i in CANONICAL_ICONS if i not in found]
    if missing:
        warnings.append(
            f"{app}: top-bar missing icon(s): {missing} — MENU shim should declare all of {CANONICAL_ICONS}"
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
