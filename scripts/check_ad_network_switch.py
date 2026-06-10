#!/usr/bin/env python3
"""Pre-publish gate: the AppLovin/AdMob auto-switch can't select a network
with empty ad unit IDs.

MaxInterstitialAd/MaxRewardedAd/MaxAdView throw
`IllegalArgumentException: Empty ad unit ID specified` at construction, so
`USE_APPLOVIN == true` while MAX_* IDs are empty crashes the app a few
seconds after launch (as soon as initAppLovin's callback fires).

Blocks when:
  - USE_APPLOVIN is derived from MAX_SDK_KEY with a placeholder-only test
    (e.g. `!MAX_SDK_KEY.startsWith("ENTER_")`) — an empty "" key flips the
    switch to AppLovin. The safe forms are a literal `false` or
    `!MAX_SDK_KEY.isEmpty()` (optionally combined with placeholder tests).
  - USE_APPLOVIN is literally `true` while any MAX_*_UNIT_ID is "".

Memorialized June 2026: PipeConnect shipped prep builds with
`USE_APPLOVIN = !MAX_SDK_KEY.startsWith("ENTER_")` and MAX_SDK_KEY = "",
crashing on every launch in the emulator.
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
    f = find_main_activity(app)
    if not f:
        warnings.append(f"{app}: MainActivity.java not found")
        return blockers, warnings
    s = f.read_text(encoding="utf-8")
    m = re.search(r"boolean\s+USE_APPLOVIN\s*=\s*([^;]+);", s)
    if not m:
        return blockers, warnings  # no switch — nothing to check
    expr = m.group(1).strip()
    key = re.search(r'String\s+MAX_SDK_KEY\s*=\s*"([^"]*)"', s)
    key_val = key.group(1) if key else None

    if expr == "false":
        return blockers, warnings
    if expr == "true":
        empties = re.findall(r'String\s+(MAX_\w*UNIT_ID)\s*=\s*""', s)
        if empties or key_val == "":
            blockers.append(
                f"{app}: USE_APPLOVIN=true but {', '.join(empties) or 'MAX_SDK_KEY'} empty — "
                "MaxAd* throws 'Empty ad unit ID specified' at launch"
            )
        return blockers, warnings
    # Derived expression: must include an isEmpty() guard so "" → AdMob.
    if "isEmpty()" not in expr:
        blockers.append(
            f"{app}: USE_APPLOVIN = {expr!r} lacks an isEmpty() guard — "
            'empty MAX_SDK_KEY ("") selects AppLovin with empty unit IDs and crashes'
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
    if apps == ["--all"]:
        apps = sorted(
            p.name
            for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith(("_", "."))
            and (p / "android/app/src/main/java/com/pegasusgames").is_dir()
        )
    fail = 0
    for app in apps:
        b, w = check_app(app)
        for line in b:
            print(f"BLOCKER: {line}")
            fail = 1
        for line in w:
            print(f"WARN:    {line}")
    if not fail:
        print(f"[ad network switch] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
