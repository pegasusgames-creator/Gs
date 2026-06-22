#!/usr/bin/env python3
"""Pre-publish gate: cross-promo install reward must read the right field.

A game.html's PROMO_GAMES entries declare the target package under a field
name (`packageId:` or `pkg:`). The functions that render the More Games panel
and auto-grant the install reward (renderMoreGames / claimPromo /
checkCrossPromoInstalls) must read that SAME field. When the entries use
`packageId` but the code reads `g.pkg`, every `isAppInstalled(undefined)`
returns false, so the +200-per-install reward silently never auto-claims —
the player installs a sister app and gets nothing.

Memorialized 2026-06-22: Nonogram + Puzzle2048 declared `packageId` but read
`g.pkg`, so cross-promo auto-claim was dead (WaterSort already read
g.packageId; UnblockPuzzle uses a `pkg` field — both fine). Fixed by adding a
`g.pkg = g.pkg || g.packageId` normaliser after the array.

BLOCKS when a game.html has a PROMO_GAMES array whose entries use `packageId:`
AND the code references `g.pkg` AND there is no normaliser bridging the two.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Normaliser forms that bridge packageId -> pkg (either order / spacing).
_NORMALISER = re.compile(r"\.pkg\s*=\s*[^;]*\.packageId|\.packageId\s*=\s*[^;]*\.pkg")


def _is_app(app: Path) -> bool:
    return (app / "android/app/build.gradle").exists()


def check_app(app: str):
    """Return (blocking, warnings) lists for one app."""
    blocking: list[str] = []
    warnings: list[str] = []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")

    # Only relevant when the promo list declares the `packageId` field.
    if "packageId:" not in src:
        return blocking, warnings
    # ...and the consuming code reads g.pkg.
    if not re.search(r"\bg\.pkg\b", src):
        return blocking, warnings
    # Safe if the code reads g.packageId at all — either the install-reward
    # functions read the right field directly (WaterSort), or a normaliser
    # (`g.pkg = g.pkg || g.packageId`, which contains `g.packageId`) bridges it.
    # A stray g.pkg can also belong to a SEPARATE promo array that legitimately
    # uses a `pkg:` field (WaterSort's ALL_PROMO block) — that's not the bug.
    if re.search(r"\bg\.packageId\b", src) or _NORMALISER.search(src):
        return blocking, warnings

    blocking.append(
        f"{app}: cross-promo PROMO_GAMES entries declare `packageId` but the "
        f"code reads `g.pkg` with no `g.pkg = g.pkg || g.packageId` normaliser "
        f"— isAppInstalled(undefined) is always false, so the install reward "
        f"never auto-claims."
    )
    return blocking, warnings


def main(argv):
    apps = argv[1:] or sorted(
        p.name for p in REPO.iterdir() if p.is_dir() and _is_app(p)
    )
    blocking, warnings = [], []
    for app in apps:
        b, w = check_app(app)
        blocking += b
        warnings += w
    for w in warnings:
        print(f"  ! {w}")
    for b in blocking:
        print(f"  ✗ {b}")
    if not blocking:
        print("  cross-promo pkg field… ok")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
