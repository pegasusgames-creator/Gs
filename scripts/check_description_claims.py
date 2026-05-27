#!/usr/bin/env python3
"""check_description_claims.py — store descriptions must state only true
capability.

Flags (WARN, not BLOCK):
  - "global rank" / "leaderboard" / "global ranking" anywhere — synthetic
    weekly brackets are NOT a global leaderboard; Play flags it.
  - "unique solution" / "no guessing" / "exactly one solution" — only true
    for Nonogram + Sudoku-likes if the build carries a solver-verified marker.
  - "N+ languages" where N exceeds the actual locale directory count.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

LEADERBOARD_HINTS = [
    "leaderboard", "global rank", "globaler rang", "classement global",
    "global sıralama", "全球排名", "classifica globale", "ranking global",
    "клав рейтинг", "глобальний рейтинг", "tablón de líderes",
]
UNIQUE_HINTS = [
    "exactly one valid picture", "exactly one solution", "no guessing",
    "uniquely solvable", "unique solution",
]
# A build that has earned the unique claim sets this marker in CLAUDE.md
# or in the app's metadata/app_info.json.
SOLVER_VERIFIED_APPS = {"Nonogram"}  # passes scripts/check_nonogram_unique.py


def _is_app(app: str) -> bool:
    return (REPO / app / "android" / "app" / "build.gradle").exists()


def _count_locales(app: str) -> int:
    md = REPO / app / "metadata"
    if not md.is_dir(): return 0
    count = 0
    for child in md.iterdir():
        if not child.is_dir(): continue
        if (child / "full_description.txt").exists(): count += 1
    return count


LANGS_RE = re.compile(r"(\d+)\+?\s*(?:languages|idiomas|langues|Sprachen|lingue|بلغة|भाषा|bahasa|言語|мов|种语)")


def check_app(app: str):
    blocking, warnings = [], []
    md = REPO / app / "metadata"
    if not md.is_dir(): return blocking, warnings
    locales = _count_locales(app)

    for child in sorted(md.iterdir()):
        if not child.is_dir(): continue
        fd = child / "full_description.txt"
        if not fd.exists(): continue
        src = fd.read_text(encoding="utf-8", errors="replace")
        lo = src.lower()

        for hint in LEADERBOARD_HINTS:
            if hint.lower() in lo:
                warnings.append(
                    f"{app}/{child.name}: contains '{hint}' — synthetic bracket is not a real leaderboard"
                )
                break

        if app not in SOLVER_VERIFIED_APPS:
            for hint in UNIQUE_HINTS:
                if hint.lower() in lo:
                    warnings.append(
                        f"{app}/{child.name}: claims '{hint}' but {app} is not in SOLVER_VERIFIED_APPS"
                    )
                    break

        for m in LANGS_RE.finditer(src):
            n = int(m.group(1))
            if n > locales and n != 0:
                warnings.append(
                    f"{app}/{child.name}: claims '{n} languages' but only {locales} locale dirs exist"
                )
                break

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
    any_warn = False
    for app in apps:
        if not _is_app(app): continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: description claims OK")
        if b: any_warn = True
    sys.exit(1 if any_warn else 0)


if __name__ == "__main__":
    main()
