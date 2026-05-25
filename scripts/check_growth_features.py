#!/usr/bin/env python3
"""check_growth_features.py — pre-publish check that every shipping game
carries the 2026-05-25 growth/DAU baseline (notifications, cross-promo
flywheel, streak freeze, share virality, PGS leaderboard hooks).

Standalone:
    python3 scripts/check_growth_features.py <App>
    python3 scripts/check_growth_features.py --all

Wired into pre_publish_check.py at the bottom of the existing section()
sequence — see that file for integration.

Returns ([blocking_msgs], [warning_msgs]) per app.
"""

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "release_aabs", "docs", "scripts",
        "BLOCKED_APPS", "__pycache__", ".git", ".idea", "node_modules"}

# Apps still pre-release — must NOT appear as cross-promo targets in
# anyone else's CROSS_PROMO_PACKAGES set / <queries> / PROMO_GAMES list.
# Edit this list when a pre-release app goes live.
PRE_RELEASE = {
    "com.pegasusgames.unblockpuzzle",
    "com.pegasusgames.pipeconnect",
}

# Java NativeBridge methods every shipping game.html must call into.
REQUIRED_BRIDGE = [
    "scheduleDailyReminder",
    "scheduleStreakAtRisk",
    "scheduleLivesRefilled",
    "scheduleWinBack",
    "cancelAllNotifications",
    "setNotificationsEnabled",
    "shareText",
    "submitScore",
    "showLeaderboard",
]

# JS-side shim markers (one per Part).
REQUIRED_SHIMS = ["A", "B", "D", "E", "F", "G"]


def _read(p: Path):
    try: return p.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, IsADirectoryError): return None


def _java_path(app: str):
    base = REPO / app / "android" / "app" / "src" / "main" / "java" / "com" / "pegasusgames"
    if not base.is_dir(): return None
    subs = [p for p in base.iterdir() if p.is_dir()]
    if len(subs) != 1: return None
    return subs[0] / "MainActivity.java"


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app: str):
    blocking, warnings = [], []

    java = _java_path(app)
    if not java or not java.exists():
        blocking.append(f"{app}: MainActivity.java not found")
        return blocking, warnings
    jsrc = _read(java) or ""

    # 1. Notification + share + PGS bridge methods.
    for m in REQUIRED_BRIDGE:
        if m not in jsrc:
            blocking.append(f"{app}: NativeBridge missing {m} — re-run scripts/_port_notif_suite.py / Part F / Part G")

    # 2. CROSS_PROMO_PACKAGES — must NOT include pre-release pkgs.
    # The app's OWN package may appear in `package com.pegasusgames.foo;` at the
    # top of the file; we only inspect lines inside the CROSS_PROMO_PACKAGES
    # block to avoid that false positive.
    if "CROSS_PROMO_PACKAGES" in jsrc:
        # Extract the (...) inside `CROSS_PROMO_PACKAGES = new HashSet<>(Arrays.asList(...))`.
        import re as _re
        m = _re.search(
            r"CROSS_PROMO_PACKAGES\s*=\s*new HashSet<>\(Arrays\.asList\(([^)]*)\)\)",
            jsrc, _re.DOTALL,
        )
        block = m.group(1) if m else ""
        for pkg in PRE_RELEASE:
            for line in block.splitlines():
                if pkg in line and not line.strip().startswith("//"):
                    blocking.append(
                        f"{app}: CROSS_PROMO_PACKAGES contains pre-release pkg '{pkg}' — remove or comment out"
                    )
                    break
    else:
        warnings.append(f"{app}: CROSS_PROMO_PACKAGES not defined")

    # 3. Manifest <queries> — same exclusion.
    manifest = REPO / app / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
    msrc = _read(manifest) or ""
    if "<queries>" not in msrc:
        blocking.append(f"{app}: AndroidManifest.xml missing <queries> block — cross-promo install detect won't work")
    else:
        for pkg in PRE_RELEASE:
            # Allow inside a comment; fail only on a live <package> tag.
            for line in msrc.splitlines():
                if pkg in line:
                    s = line.strip()
                    if s.startswith("<!--") or s.startswith("//"): continue
                    if "<package" in s:
                        blocking.append(f"{app}: AndroidManifest <queries> contains pre-release pkg '{pkg}'")

    # 4. JS-side shim markers.
    game_html = REPO / app / "android" / "app" / "src" / "main" / "assets" / "game.html"
    hsrc = _read(game_html) or ""
    for marker in REQUIRED_SHIMS:
        if f'data-growth-shim="{marker}"' not in hsrc:
            blocking.append(f"{app}: game.html missing growth shim Part {marker} — re-inject from scripts/_growth_shim_{marker.lower()}.html")

    # 5. PGS placeholder ID — warning until Play Console wired.
    if "TODO_FROM_PLAY_CONSOLE" in hsrc:
        warnings.append(f"{app}: PGS LEADERBOARD_ID still placeholder — see scripts/growth_open_items.md §B")
    games_app_id = REPO / app / "android" / "app" / "src" / "main" / "res" / "values" / "strings.xml"
    sxsrc = _read(games_app_id) or ""
    if "0000000000000" in sxsrc:
        warnings.append(f"{app}: games_app_id still placeholder in strings.xml — see scripts/growth_open_items.md §B")

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
            print(f"  ✓ {app}: growth baseline OK")
        if b: any_block = True

    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
