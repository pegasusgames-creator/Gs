#!/usr/bin/env python3
"""check_free_coins_single_source.py — the 'free_coins' rewarded grant must
have exactly ONE source of truth.

The Free Coins menu surface awards coins through a queued callback
(safeShowRewardedCb('free_coins', cb) / showRewardedAd('free_coins', cb)),
which onAdReward drains. If onAdReward ALSO grants coins in a base
if/else-if/switch branch for 'free_coins', one of two bugs results:

  * the base grant runs AND the queue drains  -> the player is paid twice
    (Nonogram shipped +25 then drained the queue = +50, 2026-06-17); or
  * the base grant runs and `return`s before the drain -> the queued
    callback is orphaned, so its cooldown / UI refresh never fire and Free
    Coins becomes repeatable with no 4h gate (Puzzle2048, same date).

The fix (WaterSort's model): onAdReward NEVER mutates coins for 'free_coins';
it only drains the callback queue, and the shim callback is the single grant.

This gate BLOCKS if onAdReward's body contains a 'free_coins' branch that
mutates a coins balance.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


# onAdReward body (assignment-style or function-declaration style).
ONADREWARD_RE = re.compile(
    r"(?:window\.)?onAdReward\s*=\s*function\s*\([^)]*\)\s*\{([\s\S]*?)\n\s*\};",
)
# A coins mutation: coins += N / coins = ...+ / coinsAdd( / addCoins(
COINS_MUTATE_RE = re.compile(
    r"""(?:\.|\b)coins\s*(?:\+=|=)|coinsAdd\s*\(|addCoins\s*\(""",
    re.IGNORECASE,
)


def _free_coins_branch_grants(body: str) -> bool:
    """True if a free_coins if/else-if/case branch mutates coins before the
    next branch boundary."""
    for m in re.finditer(r"""['"]free_coins['"]""", body):
        # Look at the slice from this branch label to the next branch
        # boundary (next case/else-if/break/return-less switch fallthrough).
        tail = body[m.end():]
        # Cut at the next branch boundary so we only inspect THIS branch.
        boundary = re.search(
            r"""\bcase\s*['"]|\belse\s+if\b|\n\s*\}\s*else\b""", tail)
        segment = tail[: boundary.start()] if boundary else tail[:400]
        # A bare fall-through case 'free_coins': (no body before the next
        # case:) is the SAFE pattern — it shares the queue-drain path.
        if re.match(r"""\s*:\s*\n?\s*case\s*['"]""", segment):
            continue
        if COINS_MUTATE_RE.search(segment):
            return True
    return False


def _free_coins_callback_grants(src: str) -> bool:
    """True if a free_coins rewarded callback body mutates coins — i.e. the
    callback is itself a grant source (Nono/P2048's safeShowRewardedCb cb).
    A callback that only stamps the cooldown / saves (UnblockPuzzle) is NOT
    a grant source."""
    for m in re.finditer(
        r"""(?:showRewardedAd|safeShowRewardedCb)\s*\(\s*['"]free_coins['"]\s*,\s*function\s*\([^)]*\)\s*\{""",
        src):
        # balance-extract the callback body
        i = m.end() - 1
        d = 0; instr = None; esc = False; j = i; n = len(src)
        while j < n:
            c = src[j]
            if instr:
                if esc: esc = False
                elif c == "\\": esc = True
                elif c == instr: instr = None
            else:
                if c in "\"'`": instr = c
                elif c == "{": d += 1
                elif c == "}":
                    d -= 1
                    if d == 0:
                        break
            j += 1
        cb_body = src[i + 1:j]
        if COINS_MUTATE_RE.search(cb_body):
            return True
    return False


def check_app(app: str):
    blocking, warnings = [], []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")

    # The double-grant only exists when BOTH sources pay out: an onAdReward
    # 'free_coins' branch that mutates coins, AND a 'free_coins' rewarded
    # callback whose body also mutates coins. Either one alone is a valid
    # single source (UnblockPuzzle grants in onAdReward + a cooldown-only
    # callback; WaterSort drains a queue + a granting callback).
    onadreward_grants = any(
        _free_coins_branch_grants(m.group(1))
        for m in ONADREWARD_RE.finditer(src)
    )
    if onadreward_grants and _free_coins_callback_grants(src):
        blocking.append(
            f"{app}: 'free_coins' is granted in BOTH an onAdReward branch AND a "
            f"rewarded callback body — double-grant / orphaned cooldown. Keep "
            f"one source: let the queued callback be the single grant and have "
            f"onAdReward only drain the queue (see WaterSort)."
        )
    return blocking, warnings


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    apps = args.apps or (
        ["WaterSortPuzzle", "Nonogram", "Puzzle2048", "UnblockPuzzle"]
        if not args.all
        else sorted(p.name for p in REPO.iterdir()
                    if (p / "android" / "app" / "build.gradle").exists()))
    any_block = False
    for app in apps:
        if not _is_app(app):
            print(f"  ? {app}: skipped"); continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for msg in b: print(f"  ✗ {msg}")
            for msg in w: print(f"  ! {msg}")
        else:
            print(f"  ✓ {app}: free_coins single source OK")
        if b:
            any_block = True
    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
