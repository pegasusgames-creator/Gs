#!/usr/bin/env python3
"""
sync_package_names.py — add `package_name` (Назва пакета) to every
app's metadata/app_info.json from its android/app/build.gradle
applicationId.

The Play Console identifies apps by their package name (Назва пакета),
not by store-listing title — so it lives in metadata/ alongside other
listing-stable values rather than being implied by the gradle file.

Usage:
  python3 scripts/sync_package_names.py             # apply
  python3 scripts/sync_package_names.py --dry-run   # preview
"""

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APPLICATION_ID_RE = re.compile(r'applicationId\s*["\']([^"\']+)["\']')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    changed = mismatched = missing = 0
    for app_dir in sorted(p for p in BASE.iterdir()
                          if p.is_dir() and not p.name.startswith(("_", "."))
                          and p.name not in ("scripts", "docs")):
        gradle = app_dir / "android/app/build.gradle"
        info_path = app_dir / "metadata/app_info.json"
        if not gradle.exists() or not info_path.exists():
            continue

        match = APPLICATION_ID_RE.search(gradle.read_text())
        if not match:
            print(f"  SKIP {app_dir.name}: no applicationId in build.gradle")
            missing += 1
            continue
        package_name = match.group(1)

        info = json.loads(info_path.read_text())
        existing = info.get("package_name")
        if existing == package_name:
            continue
        if existing and existing != package_name:
            print(f"  MISMATCH {app_dir.name}: app_info has {existing!r}, "
                  f"build.gradle has {package_name!r} — keeping build.gradle value")
            mismatched += 1

        new_info = {}
        inserted = False
        for k, v in info.items():
            new_info[k] = v
            # Place package_name right after copyright (before keystore fields)
            if k == "copyright" and not inserted:
                new_info["package_name"] = package_name
                inserted = True
        if not inserted:
            new_info["package_name"] = package_name

        if not args.dry_run:
            info_path.write_text(
                json.dumps(new_info, indent=2, ensure_ascii=False) + "\n")
        tag = "[DRY-RUN] would set" if args.dry_run else "set"
        print(f"  {tag} {app_dir.name}: package_name = {package_name}")
        changed += 1

    print()
    print(f"Total: {changed} updated, {mismatched} mismatched, {missing} missing")
    if args.dry_run:
        print("(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
