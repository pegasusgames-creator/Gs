#!/usr/bin/env python3
"""check_release_notes_match.py — WARN if release_notes.txt promises menu
cleanup but the menu inject chain still appends full-width promo banners
(`injectFreeCoins`, `injectThemeStrip`, `injectPassPromo`,
`updateTournamentBanner` called against the menu screen).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MENU_BANNER_FNS = [
    "injectFreeCoins", "injectFreeCoinsBtn", "injectThemeStrip",
    "injectPassPromo", "updateTournamentBanner",
]
# These hint that release notes are talking about menu cleanup.
MENU_CLAIM_HINTS = [
    "cleaner main menu", "menu hierarchy", "main menu",
    "menu mais limpo", "menú principal", "ana menü", "menu utama",
    "메인 메뉴", "menu principal",
]


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app: str):
    blocking, warnings = [], []
    rn = REPO / app / "metadata" / "en-US" / "release_notes.txt"
    if not rn.exists(): return blocking, warnings
    notes = rn.read_text(encoding="utf-8", errors="replace").lower()
    claims_menu = any(h.lower() in notes for h in MENU_CLAIM_HINTS)
    if not claims_menu:
        return blocking, warnings

    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists(): return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")

    # Find the showScreen wrapper / menu-screen branch and check for the
    # menu-banner inject calls inside the menu branch.
    m = re.search(
        r"(?:Game|window)\.showScreen\s*=\s*function\([^)]+\)\s*\{[^}]*?(?:if\s*\([^)]*menuScreen[^)]*\)\s*\{[^}]*?\}|if\s*\([^)]*screen-menu[^)]*\)\s*\{[^}]*?\})",
        src, re.DOTALL,
    )
    if m:
        branch = m.group(0)
        # Find which menu-banner fns are still invoked.
        leaked = [fn for fn in MENU_BANNER_FNS if fn + "(" in branch]
        if leaked:
            warnings.append(
                f"{app}: release_notes promise menu cleanup but the showScreen('menuScreen') branch still calls: {leaked}"
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
            print(f"  ✓ {app}: release notes match")
    sys.exit(0)


if __name__ == "__main__":
    main()
