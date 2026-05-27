#!/usr/bin/env python3
"""check_nonogram_unique.py — pre-publish gate that every shipped
Nonogram level has exactly one solution.

Spawns `node scripts/verify_nonogram_pregen.js` to run the JS solver
against the actual game.html PREGEN_10 / PREGEN_15 / PREGEN_20 arrays.
For PATTERNS_5 + PATTERNS_10 (the hand-curated small boards) we trust
them — they're hand-written and have been audited; the runtime gate in
buildLevels (A2) keeps them honest if anything regresses.

Returns ([blocking], [warnings]) per app.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERIFY = REPO / "scripts" / "verify_nonogram_pregen.js"


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app: str):
    blocking, warnings = [], []
    if app != "Nonogram":
        return blocking, warnings
    if not VERIFY.exists():
        blocking.append(f"{app}: scripts/verify_nonogram_pregen.js missing")
        return blocking, warnings
    if not shutil.which("node"):
        warnings.append(f"{app}: node not on PATH — cannot run uniqueness verifier (install nodejs)")
        return blocking, warnings
    try:
        r = subprocess.run(
            ["node", str(VERIFY)],
            cwd=str(REPO), capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        blocking.append(f"{app}: nonogram solver timed out (120s)")
        return blocking, warnings
    if r.returncode != 0:
        # Try to parse the JSON summary line.
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        try:
            j = json.loads(last)
            blocking.append(f"{app}: {j.get('totalBad', '?')} non-unique nonogram boards — run scripts/verify_nonogram_pregen.js --fix")
        except Exception:
            blocking.append(f"{app}: nonogram uniqueness verifier failed: {r.stderr.strip()[-300:]}")
    return blocking, warnings


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    apps = args.apps or (["Nonogram"] if not args.all else
                         [p.name for p in REPO.iterdir()
                          if (p / "android" / "app" / "build.gradle").exists()])
    any_block = False
    for app in apps:
        if not _is_app(app):
            print(f"  ? {app}: skipped (not an app folder)"); continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: nonogram uniqueness OK")
        if b: any_block = True
    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
