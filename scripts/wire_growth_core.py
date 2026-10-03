#!/usr/bin/env python3
"""wire_growth_core.py — install the per-app GROWTH_CFG block + the shared
CORE growth shim (scripts/_growth_shim_core.html) immediately before Part A
in every shipping game.html.

Why (audit 2026-10-03): the growth shims probed generic localStorage keys
('save','state','gameState','progress') that no game uses, so notifications
permission, win-back coins, welcome bonus, streak shield, first-clear flow,
share text and Play Games score submission were silently inert. CORE gives
every shim one live-state adapter (window.gGame); GROWTH_CFG carries the few
per-app facts it needs.

Idempotent: re-running replaces both blocks in place. Run
reinject_all_shims.py afterwards (it keeps CORE in sync like any shim).

Usage:
    python3 scripts/wire_growth_core.py [--dry-run] [App ...]
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# Per-app facts. levelBase 0 = save.currentLevel is a 0-based index (the
# Continue button shows index+1); 1 = currentLevel is the level number.
# booster.field = the save field holding the game's main consumable booster;
# without a field, event rewards pay booster.coins per booster instead.
CFG = {
    "WaterSortPuzzle": dict(pkg="com.pegasusgames.watersortpuzzle", name="Water Sort Puzzle",
                            saveKey="watersort_save", levelBase=0, kind="levels", totalLevels=500, live=True,
                            booster=dict(field="hintCount", name="Color Reveal", emoji="💡", coins=30)),
    "Nonogram":        dict(pkg="com.pegasusgames.nonogram", name="Nonogram",
                            saveKey="nonogram_state", levelBase=1, kind="levels", totalLevels=500, live=True,
                            booster=dict(field="hintPack", name="Hint", emoji="💡", coins=30)),
    "Puzzle2048":      dict(pkg="com.pegasusgames.puzzle2048", name="2048 Puzzle",
                            saveKey="puzzle2048_save", levelBase=0, kind="score", totalLevels=0, live=True,
                            booster=dict(field="undoPack", name="Undo", emoji="↩️", coins=30)),
    "UnblockPuzzle":   dict(pkg="com.pegasusgames.unblockpuzzle", name="Unblock Puzzle",
                            saveKey="unblock_save", levelBase=1, kind="levels", totalLevels=500, live=True,
                            booster=dict(name="Hint", emoji="💡", coins=30)),
    "PipeConnect":     dict(pkg="com.pegasusgames.pipeconnect", name="Pipe Connect",
                            saveKey="pipeconnect_save", levelBase=0, kind="levels", totalLevels=500, live=False,
                            booster=dict(field="hintCount", name="Hint", emoji="💡", coins=25)),
    "Afterimage":      dict(pkg="com.pegasusgames.afterimage", name="Afterimage",
                            saveKey="afterimage_save", levelBase=0, kind="levels", totalLevels=500, live=False,
                            booster=dict(field="hintCount", name="Hint", emoji="💡", coins=25)),
    "Hunch":           dict(pkg="com.pegasusgames.hunch", name="Hunch",
                            saveKey="hunch_save", levelBase=0, kind="levels", totalLevels=500, live=False,
                            booster=dict(field="hintCount", name="Hint", emoji="💡", coins=25)),
    "Overlay":         dict(pkg="com.pegasusgames.overlay", name="Overlay",
                            saveKey="overlay_save", levelBase=0, kind="levels", totalLevels=500, live=False,
                            booster=dict(field="hintCount", name="Hint", emoji="💡", coins=25)),
}

CFG_RE = re.compile(r'<script data-growth-config>[\s\S]*?</script>\n?')
CORE_RE = re.compile(
    r'(?:<!-- Growth shim(?:(?!-->)[\s\S])*?-->\s*)*<script data-growth-shim="CORE">[\s\S]*?</script>\n?')
A_RE = re.compile(
    r'(?:<!-- Growth shim(?:(?!-->)[\s\S])*?-->\s*)*<script data-growth-shim="A">')


def cfg_block(app: str) -> str:
    c = dict(app=app, **CFG[app])
    return ('<script data-growth-config>window.GROWTH_CFG='
            + json.dumps(c, ensure_ascii=False, separators=(',', ':')) + ';</script>\n')


def process(app: str, dry: bool) -> None:
    p = BASE / app / "android/app/src/main/assets/game.html"
    s = p.read_text(encoding="utf-8")
    core = (BASE / "scripts/_growth_shim_core.html").read_text(encoding="utf-8").strip() + "\n"
    s2 = CFG_RE.sub("", s)
    s2 = CORE_RE.sub("", s2)
    m = A_RE.search(s2)
    if not m:
        print(f"  ! {app}: Part A shim not found — skipped")
        return
    s2 = s2[:m.start()] + cfg_block(app) + core + s2[m.start():]
    if s2 == s:
        print(f"  {app}: GROWTH_CFG + CORE current")
        return
    print(f"  {app}: {'would install' if dry else 'installed'} GROWTH_CFG + CORE before Part A")
    if not dry:
        p.write_text(s2, encoding="utf-8")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    for app in (args or list(CFG)):
        if app not in CFG:
            print(f"  ? {app}: no GROWTH_CFG entry — add one first")
            continue
        process(app, dry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
