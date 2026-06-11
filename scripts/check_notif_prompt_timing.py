#!/usr/bin/env python3
"""Pre-publish gate: the POST_NOTIFICATIONS runtime prompt must not fire at
launch.

Growth spec (CLAUDE.md §A): the notification permission pre-prompt happens
AFTER the first level clear, via the JS shim → the
`requestNotificationPermission()` bridge method. A `requestPermissions(...
POST_NOTIFICATIONS...)` call anywhere OUTSIDE that bridge method (typically
copy-pasted into onCreate) throws the system dialog at first launch — the
single highest-churn moment to ask.

Memorialized June 2026: 5 of 6 apps carried the onCreate request from an
old template; only WaterSortPuzzle had been cleaned up.
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


def enclosing_method(src: str, idx: int) -> str:
    """Name of the nearest method declaration above idx (heuristic)."""
    decls = list(re.finditer(r"(?:public|private|protected)[^\n;{]*?\b(\w+)\s*\([^)]*\)\s*\{", src[:idx]))
    return decls[-1].group(1) if decls else "?"


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    ma = find_main_activity(app)
    if not ma:
        return blockers, warnings
    src = ma.read_text(encoding="utf-8")
    for m in re.finditer(r"requestPermissions\s*\(\s*new String\[\]\s*\{\s*Manifest\.permission\.POST_NOTIFICATIONS", src):
        meth = enclosing_method(src, m.start())
        if meth != "requestNotificationPermission":
            blockers.append(
                f"{app}: POST_NOTIFICATIONS requested inside {meth}() — the "
                "system dialog fires at launch; only the JS-gated "
                "requestNotificationPermission() bridge may request it"
            )
    return blockers, warnings


def main():
    apps = sys.argv[1:] or [
        "WaterSortPuzzle",
        "Nonogram",
        "Puzzle2048",
        "UnblockPuzzle",
        "PipeConnect",
        "Afterimage",
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
        print(f"[notif prompt timing] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
