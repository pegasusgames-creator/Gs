#!/usr/bin/env python3
"""Pre-publish gate: Play Games Services v2 must be initialized.

If build.gradle pulls play-services-games-v2, MainActivity must call
PlayGamesSdk.initialize(...). Without it every PlayGames.* client call
throws IllegalStateException — swallowed by the defensive try/catch, so
sign-in and leaderboards silently no-op forever (no crash, nothing to
see in reviews).

Memorialized June 2026: all 4 live apps shipped the PGS bridge methods
for weeks with no initialize call — real leaderboards were dead code.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def find_main_activity(app: str) -> Path | None:
    base = REPO / app / "android/app/src/main/java/com/pegasusgames"
    if not base.is_dir():
        return None
    hits = list(base.glob("*/MainActivity.java"))
    return hits[0] if hits else None


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    gradle = REPO / app / "android/app/build.gradle"
    if not gradle.exists():
        return blockers, warnings
    if "play-services-games" not in gradle.read_text(encoding="utf-8"):
        return blockers, warnings  # no PGS dep — nothing to check
    ma = find_main_activity(app)
    if not ma:
        warnings.append(f"{app}: MainActivity.java not found")
        return blockers, warnings
    src = ma.read_text(encoding="utf-8")
    # Strip string literals and comments first — the defensive catch logs
    # "PlayGamesSdk.initialize no-op", which would mask a missing call.
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', src)
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    if not re.search(r"PlayGamesSdk\s*\.\s*initialize\s*\(", code):
        blockers.append(
            f"{app}: play-services-games dependency present but MainActivity "
            "never calls PlayGamesSdk.initialize — every PGS bridge method "
            "throws and silently no-ops"
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
        print(f"[pgs init] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
