#!/usr/bin/env python3
"""check_level_cap.py — progress pointers must be capped by the real level
count, never by a stale numeric literal.

Bug class (audit 2026-10-03): UnblockPuzzle grew from 150 to 500 levels but
its win path still did `state.currentLevel = Math.min(state.currentLevel,
150)`, so after clearing level 150 every later win reset the pointer and
levels 151-500 stayed locked in Level Select (a live progression blocker).
Same family: copy like "Level N of 150" / "All 150" medals.

BLOCKS on `currentLevel = Math.min(<expr>, <literal>)` where the literal is
smaller than the game's level count (CAMPAIGN / LEVELS / LEVEL_SEEDS
length, else the 500 release floor), and on "of <N>" / "All <N>" progress
copy with N below the level count.

Standalone:  python3 scripts/check_level_cap.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
CAP = re.compile(r'currentLevel\s*=\s*Math\.min\([^;\n]*?,\s*(\d+)\s*\)')
COPY = re.compile(r"""(?:Level\s*'\s*\+[^+]+\+\s*'\s*of\s+|\bAll\s+)(\d{2,4})\b""")


def level_count(s: str) -> int:
    try:
        sys.path.insert(0, str(BASE / "scripts"))
        import check_min_levels as cml  # noqa: E402
        for fn in ("_level_count", "count_levels", "level_count"):
            f = getattr(cml, fn, None)
            if f:
                n = f(s)
                if isinstance(n, int) and n > 0:
                    return n
    except Exception:
        pass
    return 500


def check_app(app: str):
    p = BASE / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        return [], []
    s = p.read_text(encoding="utf-8", errors="replace")
    if not re.search(r'\b(LEVELS|CAMPAIGN|LEVEL_SEEDS)\b', s):
        return [], []
    n = level_count(s)
    bad = []
    for m in CAP.finditer(s):
        lit = int(m.group(1))
        if lit < n:
            line = s.count("\n", 0, m.start()) + 1
            bad.append(f"{app}:{line}: currentLevel capped at literal {lit} (< {n} levels) — use LEVELS.length")
    # Copy checks run on code only — comments may legitimately cite counts.
    code = re.sub(r'/\*[\s\S]*?\*/', lambda m: '\n' * m.group(0).count('\n'), s)
    code = re.sub(r'(?m)^\s*//[^\n]*', '', code)
    for m in COPY.finditer(code):
        lit = int(m.group(1))
        if 100 <= lit < n:
            line = code.count("\n", 0, m.start()) + 1
            bad.append(f"{app}:{line}: progress copy says {lit} but the game has {n} levels")
    return bad, []


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    bad = []
    for a in apps:
        b, _ = check_app(a)
        bad.extend(b)
    for line in bad:
        print("  ✗", line)
    if bad:
        print(f"level-cap check: {len(bad)} blocker(s)")
        return 1
    print("level-cap check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
