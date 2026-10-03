#!/usr/bin/env python3
"""check_app_version_display.py — the version a game shows the player must
be the version it ships as.

Bug class (audit 2026-10-03): every shipping game hard-coded a stale
version in Settings (Nonogram "1.0.0" at v1.2.20, UnblockPuzzle "1.1.1",
PipeConnect "v1.0" at v1.8.2) and the PipeConnect family printed
"v1.0.0 • com.pegasusgames.<pkg>" on the MAIN MENU. Support requests and
reviews quote the wrong build; the package name on the menu reads as
debug UI.

Rules:
  - every element marked `data-app-version` must contain build.gradle's
    versionName (with or without a leading "v");
  - no "vX.Y.Z • com.pegasusgames." debug footer anywhere in game.html.

Standalone:  python3 scripts/check_app_version_display.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
MARK = re.compile(r'<span[^>]*\bdata-app-version\b[^>]*>\s*v?([0-9][0-9A-Za-z.\-]*)\s*</span>')
DEBUG = re.compile(r'v\d+\.\d+(?:\.\d+)?\s*•\s*com\.pegasusgames\.')


def version_name(app: str) -> str:
    g = BASE / app / "android/app/build.gradle"
    if not g.exists():
        return ""
    m = re.search(r'versionName\s+"([^"]+)"', g.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else ""


def check_app(app: str):
    p = BASE / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        return [], []
    s = p.read_text(encoding="utf-8", errors="replace")
    bad = []
    vn = version_name(app)
    for m in MARK.finditer(s):
        if vn and m.group(1) != vn:
            line = s.count("\n", 0, m.start()) + 1
            bad.append(f"{app}:{line}: shows version {m.group(1)} but build.gradle versionName is {vn}")
    for m in DEBUG.finditer(s):
        line = s.count("\n", 0, m.start()) + 1
        bad.append(f"{app}:{line}: debug-style 'vX • package' string in the UI")
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
        print(f"app-version-display check: {len(bad)} blocker(s)")
        return 1
    print("app-version-display check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
