#!/usr/bin/env python3
"""
replace_fake_admob.py — revert fake/shared AdMob IDs to placeholders.

Background (May 2026): the publisher account `ca-app-pub-2759523698880843`
was never registered with AdMob. ~150 apps in the portfolio carry IDs from
that account in AndroidManifest.xml + MainActivity.java that look
plausible but resolve to nothing. Only the `ca-app-pub-5695494884863768`
account (used by WaterSort and Nonogram) is real.

This script replaces every fake reference with the canonical SHIP_GAME
Phase 2 placeholders so `pre_publish_check.py` blocks until the human
creates a real AdMob app and pastes the actual IDs in.

Replacements:
  AndroidManifest.xml:
    ca-app-pub-2759523698880843~<digits>  →  __ADMOB_APP_ID_PLACEHOLDER__

  MainActivity.java (per-line, based on which constant the line assigns):
    ADMOB_BANNER_UNIT_ID       = "ca-app-pub-2759523698880843/<digits>"
        →  __ADMOB_BANNER_UNIT_PLACEHOLDER__
    ADMOB_INTERSTITIAL_UNIT_ID = "ca-app-pub-2759523698880843/<digits>"
        →  __ADMOB_INTERSTITIAL_UNIT_PLACEHOLDER__
    ADMOB_REWARDED_UNIT_ID     = "ca-app-pub-2759523698880843/<digits>"
        →  __ADMOB_REWARDED_UNIT_PLACEHOLDER__

Apps using the real publisher account (`ca-app-pub-5695494884863768`)
are skipped. Currently those are WaterSortPuzzle and Nonogram.

Usage:
  python3 scripts/replace_fake_admob.py             # apply
  python3 scripts/replace_fake_admob.py --dry-run   # preview, no writes
"""

import argparse
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

FAKE_PUBLISHER = "ca-app-pub-2759523698880843"
REAL_PUBLISHER = "ca-app-pub-5695494884863768"

APP_ID_PLACEHOLDER = "__ADMOB_APP_ID_PLACEHOLDER__"
UNIT_PLACEHOLDERS = {
    "BANNER":       "__ADMOB_BANNER_UNIT_PLACEHOLDER__",
    "INTERSTITIAL": "__ADMOB_INTERSTITIAL_UNIT_PLACEHOLDER__",
    "REWARDED":     "__ADMOB_REWARDED_UNIT_PLACEHOLDER__",
}

MANIFEST_PATTERN = re.compile(rf'{re.escape(FAKE_PUBLISHER)}~\d+')
UNIT_LINE_PATTERN = re.compile(
    r'(ADMOB_(BANNER|INTERSTITIAL|REWARDED)_UNIT_ID\s*=\s*")'
    + re.escape(FAKE_PUBLISHER) + r'/\d+(")'
)


def fix_manifest(path: Path, dry: bool) -> int:
    text = path.read_text()
    new = MANIFEST_PATTERN.sub(APP_ID_PLACEHOLDER, text)
    if new == text:
        return 0
    if not dry:
        path.write_text(new)
    return MANIFEST_PATTERN.findall(text).__len__()


def fix_main_activity(path: Path, dry: bool) -> int:
    text = path.read_text()
    count = 0

    def replace(match: re.Match) -> str:
        nonlocal count
        count += 1
        kind = match.group(2)
        return f'{match.group(1)}{UNIT_PLACEHOLDERS[kind]}{match.group(3)}'

    new = UNIT_LINE_PATTERN.sub(replace, text)
    if count and not dry:
        path.write_text(new)
    return count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would change, don't write")
    args = ap.parse_args()

    apps_with_real_admob = set()
    for app_dir in sorted(p for p in BASE.iterdir()
                          if p.is_dir() and not p.name.startswith(("_", "."))
                          and p.name not in ("scripts", "docs")):
        manifest = app_dir / "android/app/src/main/AndroidManifest.xml"
        if not manifest.exists():
            continue
        if REAL_PUBLISHER in manifest.read_text():
            apps_with_real_admob.add(app_dir.name)

    print(f"Apps with real AdMob ({REAL_PUBLISHER}) — skipped:")
    for name in sorted(apps_with_real_admob):
        print(f"  - {name}")
    print()

    total_apps_changed = 0
    total_replacements = 0
    for app_dir in sorted(p for p in BASE.iterdir()
                          if p.is_dir() and not p.name.startswith(("_", "."))
                          and p.name not in ("scripts", "docs")):
        if app_dir.name in apps_with_real_admob:
            continue

        manifest = app_dir / "android/app/src/main/AndroidManifest.xml"
        java_dir = app_dir / "android/app/src/main/java/com/pegasusgames"
        manifest_count = 0
        unit_count = 0
        if manifest.exists():
            manifest_count = fix_manifest(manifest, args.dry_run)
        if java_dir.exists():
            for main_activity in java_dir.rglob("MainActivity.java"):
                unit_count += fix_main_activity(main_activity, args.dry_run)

        if manifest_count or unit_count:
            total_apps_changed += 1
            total_replacements += manifest_count + unit_count
            tag = "[DRY-RUN] would update" if args.dry_run else "updated"
            print(f"  {tag} {app_dir.name}: "
                  f"{manifest_count} manifest, {unit_count} unit IDs")

    print()
    print(f"Total: {total_apps_changed} apps, {total_replacements} replacements")
    if args.dry_run:
        print("(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
