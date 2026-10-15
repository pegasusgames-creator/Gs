#!/usr/bin/env python3
"""check_level_select_coverage.py — Level Select must reach every level.

Bug class (2026-10-15): Afterimage, Hunch and Overlay ship 500 levels but
their buildLevelSelect() listed hard-coded sections ending at level 60, so a
player past 60 could never pick a later level (only Continue reached them).
Fix pattern: derive chapters from LEVELS/CAMPAIGN length.

BLOCKS when buildLevelSelect() contains literal `range:[a,b]` sections whose
highest end is below the game's level count (check_min_levels counting).

Standalone:  python3 scripts/check_level_select_coverage.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
sys.path.insert(0, str(BASE / "scripts"))


def level_count(s: str) -> int:
    try:
        import check_min_levels as cml  # noqa: E402
        for fn in ("_level_count", "count_levels", "level_count"):
            f = getattr(cml, fn, None)
            if f:
                n = f(s)
                if isinstance(n, int) and n > 0:
                    return n
    except Exception:
        pass
    return 0


def check_app(app: str):
    gh = BASE / app / "android/app/src/main/assets/game.html"
    if not gh.exists():
        return [], []
    s = gh.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"function buildLevelSelect\(\)\{([\s\S]*?)\n\}", s)
    if not m:
        return [], []
    ends = [int(b) for _, b in re.findall(r"range:\[(\d+),(\d+)\]", m.group(1))]
    n = level_count(s)
    if ends and n and max(ends) < n:
        return [f"{app}: Level Select sections stop at level {max(ends)} but the game has {n} levels — "
                f"derive chapters from LEVELS.length"], []
    return [], []


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    bad = []
    for a in apps:
        bad.extend(check_app(a)[0])
    for line in bad:
        print("  ✗", line)
    if bad:
        print(f"level-select coverage: {len(bad)} blocker(s)")
        return 1
    print("level-select coverage: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
