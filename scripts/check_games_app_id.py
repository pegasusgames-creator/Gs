#!/usr/bin/env python3
"""Pre-publish gate: Play Games Services APP_ID string must be a clean number.

For every app whose AndroidManifest declares the
`com.google.android.gms.games.APP_ID` meta-data, asserts that
res/values/strings.xml defines `games_app_id` and that its value is
pure digits — no whitespace, no XML escapes (`\\ `), no placeholder
text (`ENTER_*`, `YOUR_*`, `REPLACE`).

Play Games Services v2 rejects an APP_ID with any leading/trailing
whitespace at init, so sign-in and leaderboards silently no-op into
the synthetic fallback — no crash, no log a user would ever report.

Memorialized June 2026 after all 4 shipping apps carried
`\\ 225819574531` (escaped leading space) from the original Growth
Part G wiring, killing real PGS sign-in portfolio-wide.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

PLACEHOLDER = re.compile(r"ENTER_|YOUR_|REPLACE|XXXX", re.IGNORECASE)


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    manifest = REPO / app / "android/app/src/main/AndroidManifest.xml"
    strings = REPO / app / "android/app/src/main/res/values/strings.xml"
    if not manifest.exists():
        warnings.append(f"{app}: AndroidManifest.xml missing")
        return blockers, warnings
    if "com.google.android.gms.games.APP_ID" not in manifest.read_text(
        encoding="utf-8"
    ):
        return blockers, warnings  # app doesn't wire PGS — nothing to check
    if not strings.exists():
        blockers.append(f"{app}: manifest wires games APP_ID but strings.xml missing")
        return blockers, warnings
    s = strings.read_text(encoding="utf-8")
    m = re.search(
        r'<string\s+name="games_app_id"[^>]*>(.*?)</string>', s, re.DOTALL
    )
    if not m:
        blockers.append(
            f"{app}: manifest wires games APP_ID but strings.xml has no games_app_id"
        )
        return blockers, warnings
    raw = m.group(1)
    if PLACEHOLDER.search(raw):
        blockers.append(f"{app}: games_app_id is a placeholder: {raw!r}")
    elif not re.fullmatch(r"\d+", raw):
        blockers.append(
            f"{app}: games_app_id must be pure digits, got {raw!r} "
            "(whitespace/escapes make PGS reject the id at init)"
        )
    if 'translatable="false"' not in m.group(0).split(">")[0]:
        warnings.append(f"{app}: games_app_id should be translatable=\"false\"")
    return blockers, warnings


def main():
    apps = sys.argv[1:] or [
        "WaterSortPuzzle",
        "Nonogram",
        "Puzzle2048",
        "UnblockPuzzle",
    ]
    if apps == ["--all"]:
        apps = sorted(
            p.name
            for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
            and (p / "android/app/src/main/AndroidManifest.xml").exists()
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
        print(f"[games app id] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
