#!/usr/bin/env python3
"""Pre-publish gate: no illegal trailing comma before ')' in Java.

Java (unlike JS/JSON) rejects a trailing comma in an argument list —
`Arrays.asList("a", "b",)` is "illegal start of expression" and fails
compilation. The 2026 cross-promo edit removed entries from
CROSS_PROMO_PACKAGES and left a dangling comma, silently breaking the
debug/release build of all 8 AdMob apps (uncaught because nobody rebuilt).
This greps every MainActivity.java for a comma immediately preceding a
closing paren and BLOCKS.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# comma, then only whitespace/newlines, then ')'
_TRAILING = re.compile(r",\s*\)")


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    for java in (REPO / app).glob("android/app/src/main/java/**/*.java"):
        text = java.read_text(encoding="utf-8", errors="replace")
        for m in _TRAILING.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            blockers.append(
                f"{app}: {java.name}:{line} illegal trailing comma before ')' "
                f"— Java won't compile (e.g. Arrays.asList(..., ))")
    return blockers, warnings


def main():
    apps = sys.argv[1:]
    if not apps or apps == ["--all"]:
        apps = sorted(
            p.name for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith(("_", "."))
            and (p / "android").is_dir())
    fail = 0
    for app in apps:
        b, _ = check_app(app)
        for line in b:
            print(f"✗ {line}")
            fail = 1
    if not fail:
        print(f"[java arglist comma] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
