#!/usr/bin/env python3
"""check_version_not_lower.py — a rebuilt app never ships a lower version.

Bug class (2026-11-04): AspectRatio and BillSplit were rebuilt on the
utility shell with versionName "1.0.0" although their previous listing
builds were "1.7.1" — a visible downgrade for every existing user (and a
confusing changelog). versionCode was bumped correctly; the name was not.

BLOCKS when, versus the app's build.gradle at BASELINE (the commit before
the 2026-10 portfolio rebuild):
  * versionCode is lower (Play rejects a code below one it has seen), or
  * versionName compares lower (dotted-number comparison).
(An unchanged app keeps its old values; the scaffold bumps the code of every
rebuilt app, so equal is allowed here.)
Apps that did not exist at BASELINE are skipped. Renamed folders are mapped
(FlappyWings was FlappyBird).

    python3 scripts/check_version_not_lower.py [App ...]
"""
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BASELINE = "3c62c1ae~1"
RENAMED = {"FlappyWings": "FlappyBird", "BlockDrop": "TetrisGame", "WordGuess": "WordleClone",
           "TiltGuess": "HeadsUpGame", "MythQuiz": "HarryPotterFan", "SymbolQuiz": "LogoQuiz",
           "WordGroups": "Connections", "WordHive": "SpellingBee", "CodeBreaker": "Mastermind"}
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "__pycache__", "node_modules"}


def versions(text):
    vc = re.search(r"versionCode\s+(\d+)", text or "")
    vn = re.search(r'versionName\s+["\']([^"\']+)["\']', text or "")
    return (int(vc.group(1)) if vc else None), (vn.group(1) if vn else None)


def key(vn):
    return tuple(int(x) for x in re.findall(r"\d+", vn or "0"))


def old_gradle(app):
    src = RENAMED.get(app, app)
    try:
        return subprocess.run(["git", "show", f"{BASELINE}:{src}/android/app/build.gradle"], cwd=BASE,
                              capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return ""


def check_app(app):
    g = BASE / app / "android/app/build.gradle"
    if not g.exists():
        return []
    ovc, ovn = versions(old_gradle(app))
    if ovc is None:
        return []
    vc, vn = versions(g.read_text(encoding="utf-8"))
    out = []
    if vc is None or vc < ovc:
        out.append(f"{app}: versionCode {vc} is below the previous build's {ovc}")
    if vn and ovn and key(vn) < key(ovn):
        out.append(f"{app}: versionName {vn} is lower than the previous build's {ovn} (users see a downgrade)")
    return out


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir() if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    bad = [line for a in apps for line in check_app(a)]
    for line in bad:
        print("  ✗", line)
    print(f"version-not-lower: {len(bad)} blocker(s)" if bad else "version-not-lower: OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
