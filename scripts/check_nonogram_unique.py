#!/usr/bin/env python3
"""check_nonogram_unique.py — pre-publish gate that every shipped
Nonogram level has exactly one solution.

Delegates to the self-contained Python verifier scripts/verify_nonogram.py
(no node dependency). It reconstructs ALL 500 campaign boards exactly as
buildLevels() does — curated PATTERNS_5/PATTERNS_10 INCLUDED — derives the
clues and counts solutions (capped at 2) with a line-solver + bounded search.

History: this gate used to verify only the PREGEN arrays via a node solver
and explicitly TRUSTED the curated PATTERNS_* ("hand-written and audited").
That trust was misplaced — PATTERNS_5 levels 30/45/46/50 each had two
solutions (2026-06-23) because buildLevels() uses the curated arrays directly,
bypassing the runtime _generateUnique gate. The verifier now checks them too.

Returns ([blocking], [warnings]) per app.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app: str):
    blocking, warnings = [], []
    if app != "Nonogram":
        return blocking, warnings
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        import verify_nonogram as V
    except Exception as e:
        blocking.append(f"{app}: cannot import verify_nonogram ({e})")
        return blocking, warnings
    if not V.GAME.exists():
        blocking.append(f"{app}: game.html not found for nonogram verify")
        return blocking, warnings
    try:
        levels, _ = V.build_levels(V.GAME.read_text(encoding="utf-8"))
    except Exception as e:
        blocking.append(f"{app}: failed to reconstruct nonogram levels ({e})")
        return blocking, warnings
    if len(levels) != 500:
        blocking.append(f"{app}: expected 500 nonogram levels, got {len(levels)}")
        return blocking, warnings
    bad = []
    for lvl, n, grid in levels:
        rc, cc = V.clues(grid, n)
        if V.count_solutions(rc, cc, n, cap=2) != 1:
            bad.append(lvl)
    if bad:
        blocking.append(
            f"{app}: {len(bad)} non-unique nonogram level(s): "
            f"{bad[:12]}{'…' if len(bad) > 12 else ''} — run "
            f"scripts/verify_nonogram.py")
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
