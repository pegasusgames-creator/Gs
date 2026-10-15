#!/usr/bin/env python3
"""shell_region.py — read or replace one marked region of an app's game.html.

Regions are wrapped by scripts/mark_shell_regions.py (contract:
docs/GAME_SHELL.md). Builders use this instead of loading the ~500 KB shell.

Usage:
    python3 scripts/shell_region.py App                  # list regions + sizes
    python3 scripts/shell_region.py App NAME             # print region body
    python3 scripts/shell_region.py App NAME --set FILE  # replace body (markers kept)
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PAT = r"(?P<open>(?:/\*|<!--|//)@@REGION {name}(?:\*/|-->)?\n)(?P<body>.*?)(?P<close>(?:/\*|<!--|//)@@END {name}(?:\*/|-->)?\n)"


def main() -> int:
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    p = BASE / a[0] / "android/app/src/main/assets/game.html"
    s = p.read_text(encoding="utf-8")
    if len(a) == 1:
        for m in re.finditer(r"@@REGION ([A-Z_]+)", s):
            r = re.search(PAT.format(name=m.group(1)), s, re.S)
            print(f"{m.group(1):14s} {len(r.group('body')) if r else -1:8d} B")
        return 0
    name = a[1]
    m = re.search(PAT.format(name=re.escape(name)), s, re.S)
    if not m:
        print(f"{a[0]}: region {name} not found", file=sys.stderr)
        return 1
    if "--set" in a:
        body = Path(a[a.index("--set") + 1]).read_text(encoding="utf-8")
        if not body.endswith("\n"):
            body += "\n"
        s = s[:m.start("body")] + body + s[m.end("body"):]
        p.write_text(s, encoding="utf-8")
        print(f"{a[0]}: {name} replaced ({len(body)} B)")
        return 0
    sys.stdout.write(m.group("body"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
