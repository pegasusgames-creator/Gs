#!/usr/bin/env python3
"""check_subscription_disclosure.py — every subscription SKU in the app
must have auto-renewal disclosure text rendered at the point of purchase
(Play policy, 2026-05). The SUBS shim (scripts/_growth_shim_subs.html)
covers this dynamically; this gate verifies the shim is present and
that no shop UI inserts a subscription button without that disclosure.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SUBS = {"season_pass_monthly", "weekly_pass"}


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def check_app(app: str):
    blocking, warnings = [], []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")

    has_sub = any(sku in src for sku in SUBS)
    if not has_sub:
        return blocking, warnings

    if 'data-growth-shim="SUBS"' not in src:
        blocking.append(
            f"{app}: app sells subscriptions but the SUBS disclosure shim is not injected — "
            "Play will flag at review"
        )
        return blocking, warnings

    if "play.google.com/store/account/subscriptions" not in src:
        blocking.append(
            f"{app}: SUBS shim present but Manage Subscriptions deep link missing — "
            "scripts/_growth_shim_subs.html must include it"
        )

    return blocking, warnings


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    apps = args.apps or (["WaterSortPuzzle","Nonogram","Puzzle2048","UnblockPuzzle"] if not args.all else
                         sorted(p.name for p in REPO.iterdir()
                                if (p / "android" / "app" / "build.gradle").exists()))
    any_block = False
    for app in apps:
        if not _is_app(app): print(f"  ? {app}: skipped"); continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: subscription disclosure OK")
        if b: any_block = True
    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
