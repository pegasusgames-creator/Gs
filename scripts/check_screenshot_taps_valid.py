#!/usr/bin/env python3
"""Pre-publish gate: test/screenshot_taps.json must target THIS app.

Memorialized 2026-06-16 after Afterimage, Hunch and Overlay shipped a
`test/screenshot_taps.json` that was a verbatim copy of PipeConnect's:
its `_comment` literally said "PipeConnect screenshot capture", and its
slots called `loadLevel(72..120)` — indices that don't exist in those
60-level games, so the capture produced empty boards (or, on a clamping
game, near-identical slots that fail the uniqueness gate). The copied
config also applied PipeConnect's dot palettes, which do nothing on a
different game, so every slot rendered the same default theme.

Two independent tells, both checked here:

  BLOCK  any loadLevel(N) in the tap file references N >= the app's
         level-array length (out-of-range -> broken / empty board).
  WARN   the `_comment` names a *different* portfolio app than the
         folder (the copy-paste fingerprint), even when the level
         indices happen to be in range.

Only applies to apps that actually ship test/screenshot_taps.json.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Apps whose names, if they appear in a *different* app's tap _comment,
# betray a copy-paste. Kept small + explicit (the real games with configs).
KNOWN_APPS = [
    "PipeConnect", "WaterSortPuzzle", "Nonogram", "Puzzle2048",
    "UnblockPuzzle", "Afterimage", "Hunch", "Overlay", "Sokoban",
    "FlappyBird",
]


def _level_count(game_html: str) -> int | None:
    """Length of the campaign/levels array literal in game.html.

    Handles `const LEVELS = [ {..}, .. ];`, `const CAMPAIGN = [ .. ];`
    and the `const LEVELS = CAMPAIGN;` alias (counts CAMPAIGN). Returns
    None when no array literal can be located (caller WARNs, never blocks
    on an undeterminable count).
    """
    best = None
    for name in ("CAMPAIGN", "LEVELS"):
        m = re.search(r"(?:const|var|let)\s+" + name + r"\s*=\s*\[", game_html)
        if not m:
            continue
        i = m.end() - 1  # at the '['
        depth = 0
        count = 0
        n = len(game_html)
        while i < n:
            c = game_html[i]
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    break
            elif c == "{" and depth == 1:
                count += 1
            i += 1
        if count > 0:
            best = count if best is None else max(best, count)
    return best


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    taps = REPO / app / "test" / "screenshot_taps.json"
    if not taps.exists():
        return blockers, warnings  # not every app ships a tap config
    try:
        raw = taps.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        blockers.append(f"{app}: screenshot_taps.json is unparseable ({e})")
        return blockers, warnings

    # --- copy-paste fingerprint: _comment names a different app ---
    comment = (data.get("_comment", "") if isinstance(data, dict) else "") or ""
    for other in KNOWN_APPS:
        if other != app and re.search(r"\b" + re.escape(other) + r"\b", comment):
            warnings.append(
                f"{app}: screenshot_taps.json _comment names '{other}' — "
                f"looks copied from another app; rewrite for {app}")
            break

    # --- out-of-range loadLevel(N) vs the app's level count ---
    indices = [int(n) for n in re.findall(r"loadLevel\((\d+)\)", raw)]
    if indices:
        game = REPO / app / "android/app/src/main/assets/game.html"
        if not game.exists():
            warnings.append(f"{app}: game.html missing — cannot validate level indices")
        else:
            count = _level_count(game.read_text(encoding="utf-8"))
            if count is None:
                warnings.append(
                    f"{app}: could not locate a LEVELS/CAMPAIGN array literal "
                    f"to validate loadLevel() indices")
            else:
                bad = sorted({n for n in indices if n >= count})
                if bad:
                    blockers.append(
                        f"{app}: screenshot_taps.json calls loadLevel{bad} but the "
                        f"game has only {count} levels (valid 0..{count - 1}) — "
                        f"out-of-range slots render empty/broken boards")
    return blockers, warnings


def main():
    apps = sys.argv[1:]
    if not apps or apps == ["--all"]:
        apps = sorted(
            p.name for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith(("_", "."))
            and (p / "test" / "screenshot_taps.json").exists()
        )
    fail = 0
    for app in apps:
        b, w = check_app(app)
        for line in b:
            print(f"✗ {line}")
            fail = 1
        for line in w:
            print(f"!  {line}")
    if not fail:
        print(f"[screenshot taps valid] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
