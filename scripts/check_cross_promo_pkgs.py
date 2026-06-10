#!/usr/bin/env python3
"""Pre-publish gate: every cross-promo package name must be a real
Pegasus Games package.

Scans MainActivity's CROSS_PROMO_PACKAGES, the AndroidManifest <queries>
block, and game.html promo lists (MORE_GAMES / ALL_PROMO / PROMO_GAMES /
CROSS_PROMO) for com.pegasusgames.* ids and blocks anything outside the
canonical set. A typo'd package fails open: store links 404 and
isAppInstalled() never matches, so install rewards can never be earned.

Memorialized June 2026: PipeConnect shipped prep builds with
com.pegasusgames.watersort / com.pegasusgames.unblock (real ids are
watersortpuzzle / unblockpuzzle) — cross-promo was silently dead.

Update CANONICAL when a new app gets a package id.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CANONICAL = {
    "com.pegasusgames.watersortpuzzle",
    "com.pegasusgames.nonogram",
    "com.pegasusgames.puzzle2048",
    "com.pegasusgames.unblockpuzzle",
    "com.pegasusgames.pipeconnect",
}

PKG_RE = re.compile(r"com\.pegasusgames\.[a-z0-9_]+")


def own_package(app: str) -> str | None:
    g = REPO / app / "android/app/build.gradle"
    if not g.exists():
        return None
    m = re.search(r'applicationId\s+"([^"]+)"', g.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    own = own_package(app)
    sources = []
    base = REPO / app / "android/app/src/main"
    ma = list((base / "java/com/pegasusgames").glob("*/MainActivity.java")) if (base / "java/com/pegasusgames").is_dir() else []
    if ma:
        sources.append(("MainActivity", ma[0]))
    manifest = base / "AndroidManifest.xml"
    if manifest.exists():
        sources.append(("AndroidManifest", manifest))
    game = base / "assets/game.html"
    if game.exists():
        sources.append(("game.html", game))
    for label, path in sources:
        text = path.read_text(encoding="utf-8")
        for pkg in sorted(set(PKG_RE.findall(text))):
            if pkg == own:
                continue
            if pkg not in CANONICAL:
                blockers.append(
                    f"{app}: unknown package {pkg!r} in {label} — typo'd "
                    "cross-promo ids 404 and never match isAppInstalled()"
                )
    return blockers, warnings


def main():
    apps = sys.argv[1:] or [
        "WaterSortPuzzle",
        "Nonogram",
        "Puzzle2048",
        "UnblockPuzzle",
        "PipeConnect",
    ]
    fail = 0
    for app in apps:
        b, w = check_app(app)
        for line in b:
            print(f"BLOCKER: {line}")
            fail = 1
        for line in w:
            print(f"WARN:    {line}")
    if not fail:
        print(f"[cross-promo pkgs] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
