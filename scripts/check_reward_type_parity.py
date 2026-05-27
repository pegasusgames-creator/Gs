#!/usr/bin/env python3
"""check_reward_type_parity.py — every Android.showRewarded('X') string
in game.html must have a matching branch in window.onAdReward.

If you change the reward string on one side and forget the other, the
user watches an ad and gets nothing (the UnblockPuzzle 'extra_life'
incident, 2026-05-27).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


SHOW_RE = re.compile(
    r"""(?:window\.)?Android\.showRewarded\(\s*['"]([a-zA-Z0-9_]+)['"]\s*\)"""
)
# Identify the onAdReward function body & extract the strings tested in if/else if/case branches.
BRANCH_RE = re.compile(
    r"""(?:rewardType|type)\s*===?\s*['"]([a-zA-Z0-9_]+)['"]"""
)
CASE_RE = re.compile(
    r"""case\s*['"]([a-zA-Z0-9_]+)['"]"""
)


def check_app(app: str):
    blocking, warnings = [], []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")

    triggers = set(SHOW_RE.findall(src))
    # Find onAdReward body.
    m = re.search(
        r"(?:window\.)?onAdReward\s*=\s*function\([^)]*\)\s*\{([\s\S]*?)\n\s*\};",
        src,
    )
    if not m:
        warnings.append(f"{app}: no window.onAdReward found — every Android.showRewarded() will be a no-op")
        return blocking, warnings
    body = m.group(1)
    handled = set(BRANCH_RE.findall(body)) | set(CASE_RE.findall(body))

    # Callback-queue model: if onAdReward drains a `_pendingAdCallbacks` /
    # `_pendingRewardCbs` queue, the reward is delivered by the queued
    # callback regardless of the reward-type string — so any showRewarded
    # site that uses the callback-based wrapper (showRewardedAd / safeShowRewardedCb)
    # is fine. Bare Android.showRewarded(type) calls still need a type
    # branch unless ALL of them route through the wrapper at their call
    # site. We approximate: if the body drains a callback queue, accept
    # type strings that ALSO have a wrapper call site nearby.
    queue_drain = (
        "_pendingAdCallbacks" in body or "_pendingRewardCbs" in body
    )
    if queue_drain:
        # In queue-drain apps, only flag a reward type if it appears as a
        # bare `Android.showRewarded('X')` AND there is no matching
        # `showRewardedAd('X'` or `safeShowRewardedCb('X'` call anywhere.
        wrapped_re = re.compile(
            r"""(?:showRewardedAd|safeShowRewardedCb)\(\s*['"]([a-zA-Z0-9_]+)['"]"""
        )
        wrapped = set(wrapped_re.findall(src))
        missing = (triggers - handled) - wrapped
    else:
        missing = triggers - handled
    for t in sorted(missing):
        blocking.append(
            f"{app}: rewarded-ad trigger '{t}' has no matching onAdReward branch — user watches the ad and gets nothing"
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
        if not _is_app(app):
            print(f"  ? {app}: skipped"); continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: reward parity OK")
        if b: any_block = True
    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
