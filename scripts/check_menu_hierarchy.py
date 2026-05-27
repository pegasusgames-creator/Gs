#!/usr/bin/env python3
"""check_menu_hierarchy.py — pre-publish check that every shipping game
ships the 2026-05-27 menu-hierarchy restructure (Tier 1 dominant button,
Tier 2 Daily, Tier 3 icon row, top-bar Free Coins + Tournament icons,
full-width menu banners suppressed).

Standalone:
    python3 scripts/check_menu_hierarchy.py <App>
    python3 scripts/check_menu_hierarchy.py --all

Wired into pre_publish_check.py.

Returns ([blocking_msgs], [warning_msgs]) per app.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "release_aabs", "docs", "scripts",
        "BLOCKED_APPS", "__pycache__", ".git", ".idea", "node_modules"}

# The menu shim marker — runtime-injected restructure lives here.
SHIM_MARKER = 'data-growth-shim="MENU"'

# Full-width banner element IDs that the menu shim must SUPPRESS on the
# menu (allowed in shop / themes / no-lives overlay; the shim wraps the
# inject functions). If any of these is hard-coded into the static menu
# markup (i.e. inside #menuScreen), that's a regression — the shim can
# hide it at runtime but the principle is "no full-width banners on the
# menu", and a static one is much harder to remove cleanly.
FORBIDDEN_STATIC_IN_MENU = [
    'id="xFreeCoinsBtn"',
    'id="xThemeStrip"',
    'id="xPassPromo"',
    'id="weeklyEventBanner"',
]


def _read(p: Path):
    try: return p.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, IsADirectoryError): return None


MENU_ID_CANDIDATES = ['menuScreen', 'screen-menu']


def _menu_block(html: str) -> str:
    """Return the substring of game.html that is inside the menu screen
    container. Each app names this container differently (`menuScreen` or
    `screen-menu`), so we try both. We scan from the opening `id="..."`
    until the next top-level screen container starts."""
    start = -1
    for mid in MENU_ID_CANDIDATES:
        i = html.find(f'id="{mid}"')
        if i >= 0:
            start = i
            break
    if start < 0: return ""
    rest = html[start:]
    # Stop at the next screen container — id="...Screen", id="screen-..." or
    # a fresh <section id=...>.
    m = re.search(r'(<section\s+id=|<div\s+id="(?:[A-Za-z]+Screen|screen-[a-z]+)")', rest[1:])
    if m:
        return rest[: m.start() + 1]
    return rest


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app: str):
    blocking, warnings = [], []

    game_html = REPO / app / "android" / "app" / "src" / "main" / "assets" / "game.html"
    hsrc = _read(game_html)
    if hsrc is None:
        blocking.append(f"{app}: game.html not found")
        return blocking, warnings

    # 1. Shim must be present and idempotent.
    if SHIM_MARKER not in hsrc:
        blocking.append(
            f"{app}: game.html missing menu-hierarchy shim — re-inject scripts/_growth_shim_menu.html"
        )
        return blocking, warnings

    # 2. Forbidden static full-width banners INSIDE #menuScreen.
    mblock = _menu_block(hsrc)
    if mblock:
        for forbidden in FORBIDDEN_STATIC_IN_MENU:
            if forbidden in mblock:
                blocking.append(
                    f"{app}: #menuScreen contains static full-width banner {forbidden} — move out + let the shim host its top-bar icon variant"
                )
    else:
        warnings.append(f"{app}: could not locate #menuScreen block to audit; verify manually")

    # 3. Tier 1 primary button must exist (Play / Continue). Shim
    # selector list: #menuPlayBtn / .btn-primary / .menu-primary /
    # .menu-tile-primary / .btn-play. If none present the label never patches.
    tier1_markers = [
        'id="menuPlayBtn"', 'btn-primary', 'menu-primary',
        'menu-tile-primary', 'btn-play',
    ]
    if not any(t in mblock for t in tier1_markers):
        blocking.append(
            f"{app}: menu screen has no Tier 1 button "
            "(.btn-primary / .menu-primary / .menu-tile-primary / .btn-play / #menuPlayBtn) "
            "— shim cannot patch the Continue/Play label"
        )

    # 4. Daily Challenge button must exist (Tier 2). The shim bakes
    # streak into its label.
    if 'id="dailyChallengeBtn"' not in mblock and \
       "DailyChallenge" not in mblock and \
       "startDailyChallenge" not in mblock and \
       'id="dailyBtn"' not in mblock:
        warnings.append(f"{app}: no Daily Challenge button on menu — Tier 2 will be missing")

    # 5. Tier 3 icon row must exist.
    if "menu-icon-row" not in mblock and "icon-btn" not in mblock and "menu-pair" not in mblock:
        warnings.append(f"{app}: no Tier 3 icon row (.menu-icon-row / .icon-btn / .menu-pair) on menu")

    return blocking, warnings


def find_all_apps():
    apps = []
    for p in sorted(REPO.iterdir()):
        if not p.is_dir(): continue
        if p.name in SKIP: continue
        if p.name.startswith("."): continue
        if (p / "android" / "app" / "build.gradle").exists():
            apps.append(p.name)
    return apps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    targets = find_all_apps() if args.all else (args.apps or ["WaterSortPuzzle","Nonogram","Puzzle2048","UnblockPuzzle"])

    any_block = False
    for app in targets:
        if not _is_app(app):
            print(f"  ? {app}: skipped (not an Android app folder)"); continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: menu hierarchy OK")
        if b: any_block = True

    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
