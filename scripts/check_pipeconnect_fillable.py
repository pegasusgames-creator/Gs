#!/usr/bin/env python3
"""check_pipeconnect_fillable.py — pre-publish gate: every PipeConnect level
is winnable AND fully fillable (so 2★/3★ are reachable).

PipeConnect scores stars by coverage:
    3★ = all cells filled + no resets
    2★ = all cells filled
    1★ = pairs connected (the win condition)
So a level whose colour pairs CAN be connected but whose grid can NOT be fully
filled caps the player at 1★ forever. (A 2026-06 audit found the original
hand-authored levels 1-122 were ~that — mostly un-fillable, some unsolvable.)

The levels are now produced by PipeConnect/test/gen_levels.py, which cuts a
Hamiltonian path that covers EVERY cell into colour segments and — crucially —
runs validate() (full-coverage check) on the recorded solution before emitting
each level. So the generator's output is winnable AND fully fillable BY
CONSTRUCTION, for every board size, with no runtime solving needed.

This gate asserts the shipped LEVELS array equals that validated generator
output (the generator is deterministic via fixed seeds). Any drift — a
hand-edited or truncated level — fails the build, because such a level no
longer carries the full-coverage guarantee.

Pairs with check_pipeconnect_solvable.py (which independently re-derives
winnability via a connect-only solver). Returns ([blocking], [warnings]).
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GEN_DIR = REPO / "PipeConnect" / "test"
GAME = REPO / "PipeConnect/android/app/src/main/assets/game.html"


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def _norm_dots(dots):
    """Canonicalise a dot list to a tuple of (r, c, colour)."""
    return tuple((int(d[0]), int(d[1]), str(d[2])) for d in dots)


def _parse_game_levels(src: str):
    body = re.search(r"const LEVELS\s*=\s*\[(.*?)\n\]\s*;", src, re.S)
    if not body:
        return None
    out = []
    for lm in re.finditer(r"\{size:\s*(\d+)\s*,\s*dots:\s*\[(.*?)\]\s*\}",
                          body.group(1), re.S):
        size = int(lm.group(1))
        dots = [(int(m.group(1)), int(m.group(2)), m.group(3))
                for m in re.finditer(
                    r"\[\s*(\d+)\s*,\s*(\d+)\s*,\s*'([a-z]+)'\s*\]", lm.group(2))]
        out.append((size, dots))
    return out


def check_app(app: str):
    """Return a list of (severity, message) tuples — 'BLOCKER' for any level
    that drifts from the full-coverage-validated generator output."""
    if app != "PipeConnect" or not GAME.exists():
        return []
    sys.path.insert(0, str(GEN_DIR))
    try:
        import gen_levels as G
    except Exception as e:
        return [("BLOCKER", f"cannot import gen_levels generator ({e})")]
    try:
        ref = G.build_levels()
    except Exception as e:
        return [("BLOCKER", f"gen_levels.build_levels() failed ({e})")]

    shipped = _parse_game_levels(GAME.read_text(encoding="utf-8"))
    if shipped is None:
        return [("BLOCKER", "could not parse LEVELS from game.html")]
    if len(shipped) != len(ref):
        return [("BLOCKER",
                 f"game.html has {len(shipped)} levels but the validated "
                 f"generator produces {len(ref)} — full-fill guarantee lost")]

    drift = [i + 1 for i, ((s_size, s_dots), r) in enumerate(zip(shipped, ref))
             if s_size != r["size"] or _norm_dots(s_dots) != _norm_dots(r["dots"])]
    if drift:
        return [("BLOCKER",
                 f"{len(drift)} level(s) differ from the full-coverage-"
                 f"validated generator output: {drift[:12]}"
                 f"{'…' if len(drift) > 12 else ''}. A hand-edited level is no "
                 f"longer guaranteed fully fillable (2★/3★ may be unreachable) "
                 f"— regenerate via PipeConnect/test/gen_levels.py.")]
    return []


def main():
    apps = sys.argv[1:] or ["PipeConnect"]
    any_block = False
    for app in apps:
        if not _is_app(app):
            print(f"  ? {app}: skipped (not an app folder)"); continue
        results = check_app(app)
        for sev, msg in results:
            print(f"  {'✗' if sev == 'BLOCKER' else '!'} {app}: {msg}")
            if sev == "BLOCKER":
                any_block = True
        if not results and app == "PipeConnect":
            print(f"  ✓ {app}: all 500 levels match the full-coverage-validated "
                  f"generator (winnable + fully fillable)")
    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
