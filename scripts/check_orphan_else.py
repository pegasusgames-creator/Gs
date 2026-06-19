#!/usr/bin/env python3
"""check_orphan_else.py — BLOCK an orphaned `else` left behind by a botched
save-migration edit (the class that broke UnblockPuzzle: a portfolio migration
replaced `if (raw) state = ...` with `state = migrateSave(...)` but kept the
trailing `else state = defaultState();`). An `else` with no matching `if` is a
SyntaxError ("Unexpected token 'else'") that aborts the ENTIRE <script> block,
so showScreen / state / all game logic silently never define and the app only
"works" via its growth shims. check_dead_handlers does not catch this.

Heuristic (no JS engine available): flag a line that is just `else ...` whose
immediately-preceding non-blank, non-comment line is an ASSIGNMENT statement
ending in `;` that does NOT itself contain `if (`/`if(`. Valid forms are NOT
flagged: `if (c) a(); else b();` (prev line has `if(`), `} else {` (prev ends
in `}`). Matches the style of check_java_arglist_comma / check_dead_handlers.

Usage: python3 scripts/check_orphan_else.py <AppName> [<AppName> ...]
Exit 1 (BLOCK) if any orphan else found.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ELSE_RE = re.compile(r"^\s*else\b")
ASSIGN_RE = re.compile(r"[A-Za-z_$][\w$.\[\]']*\s*=\s*.*;\s*$")
IF_RE = re.compile(r"\bif\s*\(")


def check(app: str) -> int:
    p = REPO / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        return 0
    lines = p.read_text(encoding="utf-8").splitlines()
    prev = ""
    bad = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith("//") or s.startswith("/*") or s.startswith("*"):
            continue
        if ELSE_RE.match(ln):
            # orphan if the previous statement is a bare assignment (no if() guard)
            if ASSIGN_RE.search(prev) and not IF_RE.search(prev):
                bad.append((i + 1, prev.strip()[:70], s[:40]))
        prev = ln
    if bad:
        print(f"  ✗ {app}: orphaned else (no matching if) — SyntaxError aborts the script:")
        for n, pv, el in bad:
            print(f"      line {n}:  prev: {pv}")
            print(f"               else: {el}")
        return 1
    print(f"  ✓ {app}: no orphaned else")
    return 0


def main() -> int:
    apps = sys.argv[1:]
    if not apps:
        print("usage: check_orphan_else.py <AppName> [...]")
        return 0
    rc = 0
    for app in apps:
        rc |= check(app)
    return rc


if __name__ == "__main__":
    sys.exit(main())
